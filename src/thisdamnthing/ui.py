"""On-demand, session-owned loopback interviews. No workspace static serving."""
from contextlib import contextmanager
from copy import deepcopy
import fcntl
from importlib.resources import files
from http.server import BaseHTTPRequestHandler, HTTPServer
import json
import math
import os
from pathlib import Path
import re
import secrets
import subprocess
import sys
import time
from urllib.request import Request, build_opener, ProxyHandler
from urllib.error import URLError, HTTPError
import webbrowser

from .brain import save_json
from .workspace import WorkspaceError, managed_path, read_json, resource_text, resolve_workspace

LIMIT = 262144
ID = re.compile(r"[a-zA-Z0-9_-]{1,64}\Z")
TYPES = ('text', 'multiline', 'single', 'multiple', 'boolean', 'number', 'scale')


class SessionBusy(ValueError):
    """A live server holds this session's ownership lock."""



def require(ok, message):
    if not ok:
        raise ValueError(message)


def ident(value):
    require(isinstance(value, str) and ID.fullmatch(value), 'Invalid ID')
    return value


def string(value, maximum=4000):
    require(isinstance(value, str) and len(value) <= maximum, 'Invalid or oversized text')
    return value


def finite(value):
    try:
        return type(value) in (int, float) and math.isfinite(value)
    except OverflowError:
        return False


def validate_page(page):
    require(isinstance(page, dict) and not set(page) - {'version', 'title', 'description', 'steps', 'actions', 'custom_html'}, 'Unknown page fields')
    require(type(page.get('version')) is int and page['version'] == 1, 'Expected page version 1')
    string(page.get('title'), 160)
    string(page.get('description', ''))
    actions = page.get('actions', [])
    require(isinstance(actions, list) and len(actions) <= 12 and len(set(map(str, actions))) == len(actions), 'Invalid actions')
    for action in actions:
        require(ident(action) not in ('submit', 'cancel'), 'Reserved action')
    if 'custom_html' in page:
        string(page['custom_html'], 180000)
    steps = page.get('steps', [])
    require(isinstance(steps, list) and len(steps) <= 12, 'Expected at most 12 steps')
    require(steps or 'custom_html' in page, 'Provide steps or custom_html')
    seen = set()
    for step in steps:
        require(isinstance(step, dict) and not set(step) - {'title', 'fields'}, 'Invalid step')
        string(step.get('title'), 160)
        require(isinstance(step.get('fields'), list), 'Expected fields')
        for field in step['fields']:
            require(isinstance(field, dict) and not set(field) - {'id', 'type', 'label', 'help', 'required', 'options', 'alternative', 'default', 'min', 'max', 'step'}, 'Unknown field property')
            name = ident(field.get('id'))
            require(name not in seen and len(seen) < 60, 'Duplicate field or more than 60 fields')
            seen.add(name)
            require(field.get('type') in TYPES, 'Unknown control type')
            string(field.get('label'), 300)
            string(field.get('help', ''))
            for key in ('required', 'alternative'):
                require(type(field.get(key, False)) is bool, 'Expected boolean flag')
            if field['type'] in ('single', 'multiple'):
                options = field.get('options')
                require(isinstance(options, list) and 1 <= len(options) <= 40 and all(isinstance(o, str) and 0 < len(o) <= 200 for o in options) and len(set(options)) == len(options), 'Invalid options')
            for key in ('min', 'max', 'step'):
                if key in field:
                    require(finite(field[key]), 'Expected finite numeric bound')
            require(field.get('min', 0) <= field.get('max', field.get('min', 0)), 'Reversed numeric bounds')
            require(field.get('step', 1) > 0, 'Step must be positive')
            if field['type'] == 'scale':
                require('min' in field and 'max' in field, 'Scale requires min/max')
            if 'default' in field:
                validate_value(field, field['default'])
    return page


def validate_value(field, value):
    kind = field['type']
    if value is None or value == '' or value == []:
        require(not field.get('required'), 'Required field')
        return
    if kind in ('text', 'multiline'):
        string(value)
        require(not field.get('required') or value.strip(), 'Required field')
    elif kind == 'boolean':
        require(type(value) is bool, 'Expected true or false')
    elif kind in ('number', 'scale'):
        require(finite(value), 'Expected finite number')
        require(field.get('min', value) <= value <= field.get('max', value), 'Number outside bounds')
        if 'step' in field:
            ratio = (value - field.get('min', 0)) / field['step']
            require(finite(ratio) and abs(ratio - round(ratio)) < 1e-8, 'Number must match step')
    else:
        values = value if kind == 'multiple' else [value]
        require(isinstance(values, list) and len(values) <= 41, 'Expected choices')
        for choice in values:
            string(choice, 200)
            require(choice in field['options'] or (field.get('alternative') and choice.strip()), 'Unknown choice')
        require(len(set(values)) == len(values), 'Duplicate choices')


def validate_answers(page, answers, action):
    require(isinstance(answers, dict), 'Expected answer object')
    fields = {f['id']: f for s in page.get('steps', []) for f in s['fields']}
    require(not set(answers) - fields.keys(), 'Unknown answer field')
    errors = {}
    for name, field in fields.items():
        try:
            if action == 'submit' or name in answers:
                validate_value(field, answers.get(name))
        except ValueError as exc:
            errors[name] = str(exc)
    return errors


def directory(root, sid):
    require(isinstance(sid, str) and re.fullmatch('[a-f0-9]{32}', sid), 'Invalid session ID')
    return managed_path(root, '.tdt/state/ui/' + sid)


def relative(sid, name):
    return f'.tdt/state/ui/{sid}/{name}'


def read(root, sid):
    directory(root, sid)
    return read_json(root, relative(sid, 'session.json'))


def save(root, state):
    require(len(json.dumps(state).encode()) <= 8 * 1024 * 1024, 'Session storage limit reached; start another session')
    save_json(root, relative(state['session_id'], 'session.json'), state)


@contextmanager
def ownership(root, sid):
    path = managed_path(root, relative(sid, 'server.lock'))
    with path.open('a') as stream:
        try:
            fcntl.flock(stream, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError as exc:
            raise SessionBusy('Session server is running') from exc
        try:
            yield
        finally:
            fcntl.flock(stream, fcntl.LOCK_UN)


def request(root, sid, route, payload=None):
    directory(root, sid)
    try:
        with ownership(root, sid):
            raise ValueError('Session disconnected; resume with tdt ui start --session ID')
    except SessionBusy:
        pass
    state = read(root, sid)
    require(type(state.get('port')) is int, 'Session disconnected; resume with tdt ui start --session ID')
    req = Request(f"http://127.0.0.1:{state['port']}/api/{route}",
                  data=json.dumps(payload).encode() if payload is not None else None,
                  headers={'Authorization': 'Bearer ' + state['token'], 'Content-Type': 'application/json'})
    try:
        with build_opener(ProxyHandler({})).open(req, timeout=3) as response:
            return json.load(response)
    except HTTPError as exc:
        raise ValueError(json.load(exc).get('error', str(exc))) from exc
    except (URLError, TimeoutError, KeyError) as exc:
        if isinstance(getattr(exc, 'reason', None), PermissionError):
            raise ValueError('Loopback access denied by the host runtime; request normal runtime permission') from exc
        raise ValueError('Session disconnected; resume with tdt ui start --session ID') from exc


def start(root, sid=None, idle=1800, no_open=False):
    require(30 <= idle <= 3600, 'Idle expiry must be 30–3600 seconds')
    if sid is None:
        sid = secrets.token_hex(16)
        folder = directory(root, sid)
        folder.mkdir(parents=True, mode=0o700)
        save(root, {'version': 1, 'session_id': sid, 'token': secrets.token_urlsafe(32),
                    'port': None, 'status': 'waiting', 'round_id': None, 'page': None,
                    'events': [], 'rounds': {}, 'ack': 0, 'idle': idle, 'activity': time.time()})
    state = read(root, sid)
    require(state['status'] not in ('finished', 'cancelled'), 'Closed session; start a new one')
    try:
        with ownership(root, sid):
            state = read(root, sid)
            require(state['status'] not in ('finished', 'cancelled'), 'Closed session; start a new one')
            state['port'] = None  # Never probe a stale, potentially recycled port on restart.
            save(root, state)
    except SessionBusy:
        # The actual authenticated server, never a recycled process ID, proves readiness.
        request(root, sid, 'status')
    else:
        process = subprocess.Popen([sys.executable, '-m', 'thisdamnthing.ui', str(root), sid],
                                   stdin=subprocess.DEVNULL, stdout=subprocess.DEVNULL,
                                   stderr=subprocess.DEVNULL, start_new_session=True)
        for _ in range(60):
            try:
                request(root, sid, 'status')
                break
            except (ValueError, TypeError):
                if process.poll() is not None:
                    raise ValueError('UI server failed to start; no readiness claimed')
                time.sleep(.1)
        else:
            process.terminate()
            process.wait(timeout=3)
            raise ValueError('UI startup timed out')
    state = read(root, sid)
    url = f"http://127.0.0.1:{state['port']}/#{state['token']}"
    opened = False
    if not no_open:
        try:
            opened = webbrowser.open(url)
        except (webbrowser.Error, OSError):
            pass
    return {'session_id': sid, 'url': url, 'browser_opened': opened, 'status': state['status']}


def serve(root, sid):
    with ownership(root, sid):
        state = read(root, sid)
        if state['status'] in ('finished', 'cancelled'):
            return
        stop = None

        class Handler(BaseHTTPRequestHandler):
            def log_message(self, *args):
                pass

            def respond(self, status, body, content_type='application/json', custom=False):
                raw = json.dumps(body, allow_nan=False).encode() if content_type == 'application/json' else body if isinstance(body, bytes) else body.encode()
                self.send_response(status)
                self.send_header('Content-Type', content_type + '; charset=utf-8')
                self.send_header('Content-Length', str(len(raw)))
                self.send_header('Cache-Control', 'no-store')
                self.send_header('X-Content-Type-Options', 'nosniff')
                self.send_header('Referrer-Policy', 'no-referrer')
                self.send_header('Content-Security-Policy', ("sandbox allow-scripts; default-src 'none'; script-src 'unsafe-inline'; style-src 'unsafe-inline'; img-src data:; base-uri 'none'; form-action 'none'; frame-ancestors 'self'" if custom else "default-src 'none'; script-src 'self'; style-src 'self'; img-src 'self'; connect-src 'self'; frame-src 'self' about:; frame-ancestors 'none'; base-uri 'none'; form-action 'none'"))
                self.end_headers()
                self.wfile.write(raw)

            def do_GET(self):
                self.handle_request(False)

            def do_POST(self):
                self.handle_request(True)

            def handle_request(self, post):
                nonlocal state, stop
                previous = deepcopy(state) if post else None
                previous_stop = stop
                committed = False
                try:
                    authority = f'127.0.0.1:{self.server.server_port}'
                    require(self.headers.get('Host') == authority, 'Invalid Host')
                    origin = self.headers.get('Origin')
                    require(origin is None or origin == 'http://' + authority, 'Invalid Origin')
                    if not self.path.startswith('/api/') and not post:
                        if self.path.startswith('/custom/'):
                            require(state.get('custom_key') and self.path == '/custom/' + state['custom_key'] and state['page'] and 'custom_html' in state['page'], 'Unknown custom asset')
                            bridge = 'const key=' + json.dumps(state['custom_key']) + ',round=' + json.dumps(state['round_id']) + ';' + resource_text('ui/bridge.js')
                            html = '<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><style>' + resource_text('ui/tokens.css') + '</style><script>' + bridge + '</script></head><body class="tdt-custom">' + state['page']['custom_html'] + '</body></html>'
                            self.respond(200, html, 'text/html', custom=True)
                            return
                        assets = {'/': ('shell.html', 'text/html'), '/shell.js': ('shell.js', 'text/javascript'),
                                  '/tokens.css': ('tokens.css', 'text/css'), '/logo.svg': ('logo.svg', 'image/svg+xml')}
                        require(self.path in assets, 'Unknown asset')
                        name, mime = assets[self.path]
                        self.respond(200, files('thisdamnthing').joinpath('resources', 'ui', name).read_bytes(), mime)
                        return
                    require(secrets.compare_digest(self.headers.get('Authorization', ''), 'Bearer ' + state['token']), 'Invalid credentials')
                    require(self.headers.get('Sec-Fetch-Site', 'same-origin') in ('same-origin', 'none'), 'Cross-site request refused')
                    if not post:
                        require(self.path in ('/api/status', '/api/page', '/api/events'), 'Unknown endpoint')
                        if self.path == '/api/events':
                            result = {'events': state['events'], 'ack': state['ack'], 'status': state['status']}
                        else:
                            result = {k: state[k] for k in ('session_id', 'round_id', 'page', 'status', 'ack')}
                        result['custom_key'] = state.get('custom_key')
                        self.respond(200, result)
                        return
                    require(self.headers.get('Content-Type', '').split(';')[0] == 'application/json', 'Expected JSON')
                    require(not self.headers.get('Transfer-Encoding'), 'Transfer encoding refused')
                    length = int(self.headers.get('Content-Length', '-1'))
                    require(0 <= length <= LIMIT, 'Payload exceeds 256 KiB')
                    payload = json.loads(self.rfile.read(length), parse_constant=lambda s: (_ for _ in ()).throw(ValueError('Nonfinite JSON')))
                    require(isinstance(payload, dict), 'Expected object')
                    if self.path == '/api/present':
                        require(state['status'] not in ('finished', 'cancelled'), 'Session closed')
                        require(len(state['events']) < 1000, 'Session full; start another')
                        page = validate_page(payload)
                        require(len(state.get('rounds', {})) < 100, 'Round limit reached; start another session')
                        state.update(page=page, round_id=secrets.token_hex(16), custom_key=secrets.token_urlsafe(32), status='waiting')
                        state.setdefault('rounds', {})[state['round_id']] = page
                        result = {'round_id': state['round_id'], 'status': 'waiting'}
                    elif self.path == '/api/submit':
                        require(not set(payload) - {'round_id', 'submission_id', 'action', 'answers', 'data'}, 'Unknown submission property')
                        ident(payload.get('submission_id'))
                        # A retry has the same result only when its complete original payload matches.
                        duplicate = next((e for e in state['events'] if e['submission_id'] == payload['submission_id']), None)
                        if duplicate:
                            require(json.dumps(duplicate['request'], sort_keys=True) == json.dumps(payload, sort_keys=True), 'Submission ID reused with different content')
                            self.respond(200, {'event': {k: v for k, v in duplicate.items() if k != 'request'}, 'duplicate': True})
                            return
                        require(state['page'] is not None and payload.get('round_id') == state['round_id'], 'Stale round')
                        require(state['status'] == 'waiting', 'Round already answered or closed')
                        action = payload.get('action')
                        require(action in ['submit', 'cancel', *state['page'].get('actions', [])], 'Unknown action')
                        answers = payload.get('answers', {})
                        require(isinstance(answers, dict), 'Expected answer object')
                        if action == 'cancel':
                            require(not answers and 'data' not in payload, 'Cancel must not include answers or data')
                        errors = validate_answers(state['page'], answers, action) if action != 'cancel' else {}
                        if errors:
                            self.respond(422, {'error': 'Please check your answers', 'fields': errors})
                            return
                        require('data' not in payload or 'custom_html' in state['page'], 'Custom data requires custom page')
                        event = {'version': 1, 'session_id': sid, 'round_id': state['round_id'], 'event_id': len(state['events']) + 1,
                                 'submission_id': payload['submission_id'], 'action': action, 'answers': answers,
                                 'data': payload.get('data'), 'created': time.time(), 'request': payload}
                        state['events'].append(event)
                        state['status'] = 'cancelled' if action == 'cancel' else 'received'
                        if action == 'cancel':
                            stop = time.time() + 3
                        result = {'event': {k: v for k, v in event.items() if k != 'request'}, 'duplicate': False}
                    elif self.path == '/api/ack':
                        cursor = payload.get('event_id')
                        require(type(cursor) is int and state['ack'] <= cursor <= len(state['events']), 'Invalid acknowledgement cursor')
                        state['ack'] = cursor
                        result = {'ack': cursor}
                    elif self.path == '/api/close':
                        state['status'] = 'finished'
                        stop = time.time() + 3
                        result = {'status': 'finished'}
                    else:
                        raise ValueError('Unknown endpoint')
                    state['activity'] = time.time()
                    save(root, state)
                    committed = True
                    self.respond(200, result)
                except (ValueError, WorkspaceError, OSError, RecursionError, OverflowError) as exc:
                    if previous is not None and not committed:
                        state = previous
                        stop = previous_stop
                    try:
                        self.respond(400, {'error': str(exc)})
                    except OSError:
                        pass  # A dropped response must never undo a committed event.

        class Server(HTTPServer):
            def get_request(self):
                sock, address = super().get_request()
                sock.settimeout(2)
                return sock, address

        with Server(('127.0.0.1', 0), Handler) as server:
            server.timeout = .5
            state.update(port=server.server_port, activity=time.time())
            save(root, state)
            while (stop is None or time.time() < stop) and time.time() - state['activity'] < state['idle']:
                server.handle_request()
            state['port'] = None
            save(root, state)


def cli(root, args):
    if args.action == 'start':
        return start(root, args.session, args.idle, args.no_open)
    sid = args.session
    directory(root, sid)
    if args.action == 'cleanup':
        with ownership(root, sid):
            folder = directory(root, sid)
            require({p.name for p in folder.iterdir()} <= {'session.json', 'server.lock'}, 'Unexpected session files; preserved')
            for name in ('session.json', 'server.lock'):
                path = managed_path(root, relative(sid, name))
                path.unlink(missing_ok=True)
            folder.rmdir()
        return {'deleted': sid}
    if args.action == 'status':
        state = read(root, sid)
        try:
            result = request(root, sid, 'status')
            result['connected'] = True
            return result
        except (ValueError, TypeError):
            return {'session_id': sid, 'status': state['status'], 'connected': False,
                    'round_id': state['round_id'], 'ack': state['ack']}
    if args.action in ('read', 'wait'):
        require(0 <= args.after <= 1000, 'Invalid event cursor')
        seconds = args.timeout if args.action == 'wait' else 0
        require(0 <= seconds <= 30, 'Wait timeout must be 0–30 seconds')
        deadline = time.monotonic() + seconds
        while True:
            state = read(root, sid)
            events = [{k: v for k, v in e.items() if k != 'request'} for e in state['events'] if e['event_id'] > args.after]
            if events or time.monotonic() >= deadline or state['status'] in ('finished', 'cancelled'):
                return {'events': events, 'prompts': {e['round_id']: state.get('rounds', {}).get(e['round_id']) for e in events}, 'ack': state['ack'], 'status': state['status'], 'timed_out': not events and seconds > 0}
            time.sleep(.2)
    if args.action == 'present':
        path = Path(args.page)
        require(path.stat().st_size <= LIMIT and not path.is_symlink(), 'Invalid or oversized page file')
        return request(root, sid, 'present', validate_page(json.loads(path.read_text())))
    payload = {'event_id': args.event_id} if args.action == 'ack' else {}
    try:
        with ownership(root, sid):
            state = read(root, sid)
            if args.action == 'ack':
                require(type(args.event_id) is int and state['ack'] <= args.event_id <= len(state['events']), 'Invalid acknowledgement cursor')
                state['ack'] = args.event_id
                result = {'ack': state['ack']}
            else:
                state.update(status='finished', port=None)
                result = {'status': 'finished'}
            save(root, state)
            return result
    except SessionBusy:
        result = request(root, sid, args.action, payload)
        if args.action == 'close':
            deadline = time.monotonic() + 5
            while time.monotonic() < deadline:
                try:
                    with ownership(root, sid):
                        return result
                except SessionBusy:
                    time.sleep(.1)
            raise ValueError('Session is finishing; retry cleanup shortly')
        return result


def add_parser(commands):
    ui = commands.add_parser('ui', help='local browser interviews')
    actions = ui.add_subparsers(dest='action', required=True)
    start_cmd = actions.add_parser('start')
    start_cmd.add_argument('--session')
    start_cmd.add_argument('--no-open', action='store_true')
    start_cmd.add_argument('--idle', type=int, default=1800)
    for name in ('present', 'status', 'read', 'wait', 'ack', 'close', 'cleanup'):
        command = actions.add_parser(name)
        command.add_argument('session')
        if name == 'present':
            command.add_argument('page', help='local page JSON file')
        if name in ('read', 'wait'):
            command.add_argument('--after', type=int, default=0)
        if name == 'wait':
            command.add_argument('--timeout', type=int, default=20)
        if name == 'ack':
            command.add_argument('event_id', type=int)


if __name__ == '__main__':
    serve(resolve_workspace(sys.argv[1]), sys.argv[2])
