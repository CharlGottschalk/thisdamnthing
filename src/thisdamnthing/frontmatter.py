"""Bounded YAML metadata without implicit scalar typing."""
import json
import re

import yaml


class NoteLoader(yaml.BaseLoader):
    """Compose basic YAML nodes only, without aliases or excessive nesting."""

    def compose_node(self, parent, index):
        if self.check_event(yaml.AliasEvent):
            raise ValueError("YAML aliases are not supported in note metadata")
        depth = getattr(self, '_note_depth', 0)
        if depth >= 16:
            raise ValueError("note metadata nesting exceeds 16 levels")
        self._note_depth = depth + 1
        try:
            return super().compose_node(parent, index)
        finally:
            self._note_depth = depth


def loads(text):
    try:
        node = yaml.compose(text, Loader=NoteLoader)
    except yaml.YAMLError as exc:
        mark = getattr(exc, 'problem_mark', None)
        location = f" at line {mark.line + 1}, column {mark.column + 1}" if mark else ""
        problem = getattr(exc, 'problem', None) or "invalid syntax"
        raise ValueError(f"invalid YAML{location}: {problem}") from exc

    def value(node):
        if node is None:
            return None
        if node.tag not in ('tag:yaml.org,2002:str', 'tag:yaml.org,2002:seq',
                            'tag:yaml.org,2002:map'):
            raise ValueError("explicit YAML type tags are not supported in note metadata")
        if isinstance(node, yaml.ScalarNode):
            # Treat unquoted null/empty values as absent optional metadata.
            if node.style is None and node.value in ('', '~', 'null', 'Null', 'NULL'):
                return None
            return node.value
        if isinstance(node, yaml.SequenceNode):
            return [value(item) for item in node.value]
        result = {}
        for key_node, item in node.value:
            if (not isinstance(key_node, yaml.ScalarNode)
                    or key_node.tag != 'tag:yaml.org,2002:str'):
                raise ValueError("note metadata keys must be strings")
            key = key_node.value
            if key in result:
                raise ValueError(f"duplicate metadata key: {key}")
            result[key] = value(item)
        return result

    result = value(node)
    if isinstance(result, dict) and result.get('format_version') == '1':
        result['format_version'] = 1
    if isinstance(result, dict) and result.get('kind') == 'reminder':
        # These are schema integers, never inferred types for arbitrary properties.
        for record in (result, result.get('claim')):
            if isinstance(record, dict):
                revision = record.get('revision')
                if isinstance(revision, str) and re.fullmatch(r'[0-9]+', revision):
                    record['revision'] = int(revision)
    return result


class NoteDumper(yaml.SafeDumper):
    """Stable block YAML with quoted string values and no generated aliases."""

    def ignore_aliases(self, data):
        return True

    def represent_str(self, data):
        return self.represent_scalar('tag:yaml.org,2002:str', data, style='"')

    def represent_dict(self, data):
        node = self.represent_mapping('tag:yaml.org,2002:map', data)
        for key, _ in node.value:
            key.style = None
        return node


NoteDumper.add_representer(str, NoteDumper.represent_str)
NoteDumper.add_representer(dict, NoteDumper.represent_dict)


def dumps(meta):
    text = yaml.dump(meta, Dumper=NoteDumper, allow_unicode=True,
                     sort_keys=False, default_flow_style=False, width=32768)
    # Refuse unsupported metadata rather than silently changing audit values.
    if json.dumps(loads(text), sort_keys=True) != json.dumps(meta, sort_keys=True):
        raise ValueError("note metadata cannot be written as YAML without changing its types")
    return text.rstrip('\n')
