"""Platform file primitives: non-blocking locks and opens that never follow links.

Unix keeps retained directory descriptors (dir_fd, O_NOFOLLOW). Windows cannot
open directories as descriptors, so it checks each component with lstat and
refuses symlinks and junctions before opening by path.
"""
from contextlib import contextmanager
import errno
import os
from pathlib import Path
import stat
import sys
import time

WINDOWS = os.name == 'nt'
if WINDOWS:
    import msvcrt
    LINK_TAGS = (stat.IO_REPARSE_TAG_SYMLINK, stat.IO_REPARSE_TAG_MOUNT_POINT)
else:
    import fcntl


class NotRegular(OSError):
    """The name exists but is not a regular file."""


def utf8_stdio():
    """Hosts and agents exchange UTF-8 JSON; Windows pipes default to the ANSI code page.

    stdin uses utf-8-sig: Windows PowerShell 5.1 prefixes piped text with a BOM.
    """
    for stream, accepted in ((sys.stdin, ('utf-8-sig',)), (sys.stdout, ('utf-8', 'utf8')),
                             (sys.stderr, ('utf-8', 'utf8'))):
        if hasattr(stream, 'reconfigure') and (stream.encoding or '').lower() not in accepted:
            stream.reconfigure(encoding=accepted[0])


def _fd(stream):
    return stream if isinstance(stream, int) else stream.fileno()


def lock(stream, *, shared=False):
    """Take a non-blocking lock; raise BlockingIOError when another holder has it."""
    if not WINDOWS:
        fcntl.flock(stream, (fcntl.LOCK_SH if shared else fcntl.LOCK_EX) | fcntl.LOCK_NB)
        return
    # ponytail: Windows has no shared lock, so readers serialize with each other there.
    fd = _fd(stream)
    os.lseek(fd, 0, os.SEEK_SET)
    try:
        msvcrt.locking(fd, msvcrt.LK_NBLCK, 1)
    except OSError as exc:
        if exc.errno in (errno.EACCES, errno.EDEADLK):
            raise BlockingIOError(exc.errno, 'File is locked') from exc
        raise


def unlock(stream):
    if not WINDOWS:
        fcntl.flock(stream, fcntl.LOCK_UN)
        return
    fd = _fd(stream)
    os.lseek(fd, 0, os.SEEK_SET)
    msvcrt.locking(fd, msvcrt.LK_UNLCK, 1)


def replace(source, target):
    """os.replace, retrying briefly on Windows while another process has target open."""
    for delay in (0.01, 0.02, 0.05, 0.1, 0.2, 0.3, 0.5) if WINDOWS else ():
        try:
            return os.replace(source, target)
        except PermissionError:
            time.sleep(delay)
    return os.replace(source, target)


def is_link(info):
    return stat.S_ISLNK(info.st_mode) or (
        WINDOWS and getattr(info, 'st_reparse_tag', 0) in LINK_TAGS)


def is_link_path(path):
    """Symlink or junction (Path.is_junction needs Python 3.12)."""
    try:
        return is_link(os.lstat(path))
    except (FileNotFoundError, NotADirectoryError):
        return False


def _checked(path, *, directory):
    """Windows: lstat one component, refusing links and the wrong file type."""
    info = os.lstat(path)
    if is_link(info):
        raise OSError(errno.ELOOP, 'Refusing symlink or junction', str(path))
    if directory and not stat.S_ISDIR(info.st_mode):
        raise NotADirectoryError(errno.ENOTDIR, 'Not a directory', str(path))
    if not directory and not stat.S_ISREG(info.st_mode):
        raise NotRegular(errno.EINVAL, 'Not a regular file', str(path))
    return info


def _read_open(fd, size):
    with os.fdopen(fd, 'rb') as stream:
        info = os.fstat(stream.fileno())
        if not stat.S_ISREG(info.st_mode):
            raise NotRegular(errno.EINVAL, 'Not a regular file')
        return stream.read(size), info


def _read_windows(path, size):
    # ponytail: the lstat check and the open are not atomic on Windows; a swap
    # in between is possible. The identity comparison narrows that window.
    before = _checked(path, directory=False)
    raw, info = _read_open(os.open(path, os.O_RDONLY | os.O_BINARY), size)
    if (info.st_dev, info.st_ino) != (before.st_dev, before.st_ino):
        raise OSError(errno.ELOOP, 'File changed while opening', str(path))
    return raw, info


def read_file(path, size):
    """Read at most size bytes from a regular file, refusing a final-component link."""
    if WINDOWS:
        return _read_windows(path, size)[0]
    return _read_open(os.open(path, os.O_RDONLY | os.O_NONBLOCK | os.O_NOFOLLOW), size)[0]


class Directory:
    """A directory reached without following links: a descriptor on Unix, a checked path on Windows."""

    def __init__(self, handle):
        self.handle = handle

    def __enter__(self):
        return self

    def __exit__(self, *exc):
        self.close()

    def close(self):
        if not WINDOWS and self.handle is not None:
            os.close(self.handle)
        self.handle = None

    def dup(self):
        return Directory(self.handle if WINDOWS else os.dup(self.handle))

    def child(self, name):
        if WINDOWS:
            path = self.handle / name
            _checked(path, directory=True)
            return Directory(path)
        return Directory(os.open(name, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW,
                                 dir_fd=self.handle))

    def lstat(self, name):
        if WINDOWS:
            return os.lstat(self.handle / name)
        return os.stat(name, dir_fd=self.handle, follow_symlinks=False)

    def scandir(self):
        return os.scandir(self.handle)

    def read(self, parts, size):
        """Read at most size bytes of a regular file below this directory: (bytes, fstat)."""
        parent = self.dup()
        try:
            for part in parts[:-1]:
                child = parent.child(part)
                parent.close()
                parent = child
            if WINDOWS:
                return _read_windows(parent.handle / parts[-1], size)
            return _read_open(os.open(parts[-1], os.O_RDONLY | os.O_NONBLOCK | os.O_NOFOLLOW,
                                      dir_fd=parent.handle), size)
        finally:
            parent.close()


@contextmanager
def directory(path):
    """Open each directory from the filesystem root without following links."""
    path = Path(path)
    if WINDOWS:
        # ponytail: each component is checked, then used by path; not atomic like dir_fd.
        current = Path(path.anchor)
        for part in path.parts[1:]:
            current = current / part
            _checked(current, directory=True)
        handle = Directory(current)
    else:
        handle = Directory(os.open('/', os.O_RDONLY | os.O_DIRECTORY))
        try:
            for part in path.parts[1:]:
                child = handle.child(part)
                handle.close()
                handle = child
        except BaseException:
            handle.close()
            raise
    try:
        yield handle
    finally:
        handle.close()
