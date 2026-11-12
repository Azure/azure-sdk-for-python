# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.
# cspell:ignore ntdll RDONLY osfhandle NOINHERIT
"""Exclusive checkpoint output, anchored against directory replacement.

Failure retains partial files and directories. Deliberately never unlink paths:
even an identity check followed by unlink can delete a concurrent replacement.
"""

import os
import sys
from contextlib import ExitStack
from pathlib import Path
from stat import S_ISDIR, S_ISREG
from typing import BinaryIO, Optional

from typing_extensions import Self


def _is_directory(info: os.stat_result) -> bool:
    return S_ISDIR(info.st_mode) and not getattr(info, "st_file_attributes", 0) & 0x400


def _same_entry(left: os.stat_result, right: os.stat_result) -> bool:
    return (left.st_dev, left.st_ino) == (right.st_dev, right.st_ino)


def _close_windows_handle(handle: int) -> None:
    if sys.platform != "win32":
        raise NotImplementedError("Windows handle-relative output requires Windows")
    import ctypes
    from ctypes import wintypes

    close = ctypes.WinDLL("kernel32", use_last_error=True).CloseHandle
    close.argtypes = [wintypes.HANDLE]
    close.restype = wintypes.BOOL
    if not close(handle):
        raise ctypes.WinError(ctypes.get_last_error())


def _open_windows_entry(path: Path, parent: int | None, *, directory: bool, exclusive: bool = False) -> int:
    """Open one component relative to a pinned handle, never reparsing its ancestors.

    :param path: Component to open, or the filesystem root when parent is None.
    :type path: ~pathlib.Path
    :param parent: Pinned parent directory handle, or None for the root.
    :type parent: int or None
    :keyword bool directory: Whether the entry must be a directory.
    :keyword bool exclusive: Whether an existing entry must be rejected.
    :return: Owned native handle that must be closed by the caller.
    :rtype: int
    """
    if sys.platform != "win32":
        raise NotImplementedError("Windows handle-relative output requires Windows")
    import ctypes
    from ctypes import wintypes

    class UnicodeString(ctypes.Structure):
        _fields_ = [
            ("Length", wintypes.USHORT),
            ("MaximumLength", wintypes.USHORT),
            ("Buffer", wintypes.LPWSTR),
        ]

    class ObjectAttributes(ctypes.Structure):
        _fields_ = [
            ("Length", wintypes.ULONG),
            ("RootDirectory", wintypes.HANDLE),
            ("ObjectName", ctypes.POINTER(UnicodeString)),
            ("Attributes", wintypes.ULONG),
            ("SecurityDescriptor", wintypes.LPVOID),
            ("SecurityQualityOfService", wintypes.LPVOID),
        ]

    class IoStatusBlock(ctypes.Structure):
        _fields_ = [("Status", wintypes.LPVOID), ("Information", ctypes.c_size_t)]

    native = ctypes.WinDLL("ntdll")
    create = native.NtCreateFile
    create.argtypes = [
        ctypes.POINTER(wintypes.HANDLE),
        wintypes.DWORD,
        ctypes.POINTER(ObjectAttributes),
        ctypes.POINTER(IoStatusBlock),
        wintypes.LPVOID,
        wintypes.DWORD,
        wintypes.DWORD,
        wintypes.DWORD,
        wintypes.DWORD,
        wintypes.LPVOID,
        wintypes.DWORD,
    ]
    create.restype = wintypes.LONG
    error_code = native.RtlNtStatusToDosError
    error_code.argtypes = [wintypes.LONG]
    error_code.restype = wintypes.ULONG
    name = path.name
    if parent is None:
        # Only the volume/share root is opened by absolute NT name.
        name = str(path)
        if name.startswith("\\\\?\\"):
            name = name[4:]
        elif name.startswith("\\\\"):
            name = "UNC\\" + name[2:]
        name = "\\??\\" + name
    length = len(name.encode("utf-16-le"))
    if length > 65534:
        raise ctypes.WinError(206)
    buffer = ctypes.create_unicode_buffer(name)
    string = UnicodeString(length, length, ctypes.cast(buffer, wintypes.LPWSTR))
    attributes = ObjectAttributes(ctypes.sizeof(ObjectAttributes), parent, ctypes.pointer(string), 0x1040, None, None)
    handle = wintypes.HANDLE()
    status = IoStatusBlock()
    result = create(
        ctypes.byref(handle),
        0x100080 if directory else 0x100082,  # SYNCHRONIZE, READ_ATTRIBUTES; files also WRITE_DATA.
        ctypes.byref(attributes),  # OBJ_CASE_INSENSITIVE | OBJ_DONT_REPARSE.
        ctypes.byref(status),
        None,
        0x80,
        0x3,  # FILE_SHARE_READ | FILE_SHARE_WRITE, denying directory rename/deletion.
        1 if parent is None else 2 if exclusive else 3,  # FILE_OPEN / FILE_CREATE / FILE_OPEN_IF.
        0x200020 | (0x1 if directory else 0x40),  # OPEN_REPARSE_POINT, synchronous, directory/non-directory.
        None,
        0,
    )
    if result < 0:
        raise ctypes.WinError(error_code(result))
    if handle.value is None:
        raise OSError("Windows did not return a checkpoint output handle")
    return handle.value


class _Directory:
    """A pinned directory, with relative no-follow operations on POSIX."""

    def __init__(
        self, path: Path, resources: ExitStack, parent: Optional["_Directory"] = None, *, exclusive: bool = False
    ) -> None:
        self.path = path
        self.parent = parent
        self.fd: int | None = None
        self.handle: int | None = None
        if sys.platform == "win32":
            self.handle = _open_windows_entry(
                path, parent.handle if parent else None, directory=True, exclusive=exclusive
            )
            resources.callback(_close_windows_handle, self.handle)
            self.info = path.lstat()
        else:
            self.fd = os.open(
                path.name if parent else path,
                os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW,  # pylint: disable=no-member
                dir_fd=parent.fd if parent else None,
            )
            resources.callback(os.close, self.fd)
            self.info = os.fstat(self.fd)
        if not _is_directory(self.info):
            raise NotADirectoryError(f"Expected a directory: {path}")
        self.verify()

    def stat(self, name: str) -> os.stat_result:
        if self.fd is not None:
            return os.stat(name, dir_fd=self.fd, follow_symlinks=False)
        return (self.path / name).lstat()

    def verify(self) -> None:
        current = self.parent.stat(self.path.name) if self.parent else self.path.lstat()
        if not _is_directory(current) or not _same_entry(current, self.info):
            raise ValueError(f"Checkpoint output directory changed: {self.path}")

    def names(self) -> set[str]:
        return set(os.listdir(self.fd if self.fd is not None else self.path))

    def child(self, name: str, resources: ExitStack, *, exclusive: bool = False) -> "_Directory":
        self.verify()
        if self.handle is not None:
            return _Directory(self.path / name, resources, self, exclusive=exclusive)
        try:
            os.mkdir(name, mode=0o700, dir_fd=self.fd)
        except FileExistsError:
            if exclusive:
                raise
        return _Directory(self.path / name, resources, self)

    def open_file(self, name: str) -> BinaryIO:
        self.verify()
        if sys.platform == "win32":
            import msvcrt  # pylint: disable=import-error

            handle = _open_windows_entry(self.path / name, self.handle, directory=False, exclusive=True)
            try:
                fd = msvcrt.open_osfhandle(handle, os.O_WRONLY | os.O_BINARY | os.O_NOINHERIT)
            except BaseException:
                _close_windows_handle(handle)
                raise
        else:
            flags = os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW  # pylint: disable=no-member
            fd = os.open(name, flags, 0o600, dir_fd=self.fd)
        try:
            return os.fdopen(fd, "wb")
        except BaseException:
            os.close(fd)
            raise


class _CheckpointOutput:
    """Own only exclusive creations; verify the complete tree before reporting success."""

    def __init__(self, root: Path, session_id: str, checkpoint_id: str) -> None:
        self._root = root.absolute()
        self._resolved_root = self._root.resolve()
        self.path = self._resolved_root / session_id / checkpoint_id
        self._resources = ExitStack()
        self._ancestors: list[_Directory] = []
        self._directories: dict[tuple[str, ...], _Directory] = {}
        self._files: dict[tuple[str, ...], tuple[os.stat_result, int]] = {}

    def __enter__(self) -> Self:
        try:
            self._verify_root()
            directory = _Directory(Path(self.path.anchor), self._resources)
            for name in self.path.parts[1:]:
                self._ancestors.append(directory)
                directory = directory.child(name, self._resources)
            if directory.names():
                raise ValueError(f"Checkpoint directory must be empty: {self.path}")
            self._directories[()] = directory
            return self
        except BaseException:
            self._resources.close()
            raise

    def __exit__(self, *args: object) -> None:
        self._resources.close()

    def _verify_directories(self) -> None:
        self._verify_root()
        for directory in (*self._ancestors, *self._directories.values()):
            directory.verify()

    def _verify_root(self) -> None:
        if self._root.resolve() != self._resolved_root:
            raise ValueError(f"Checkpoint output root changed: {self._root}")

    def open_file(self, filename: str, size_bytes: int) -> BinaryIO:
        """Create a validated manifest filename, never adopting an existing nested entry.

        :param str filename: Validated relative filename from the inventory.
        :param int size_bytes: Exact expected size checked before success.
        :return: Exclusively created binary output stream.
        :rtype: typing.BinaryIO
        """
        self._verify_directories()
        components = tuple(filename.split("/"))
        for length in range(1, len(components)):
            prefix = components[:length]
            if prefix not in self._directories:
                self._directories[prefix] = self._directories[prefix[:-1]].child(
                    prefix[-1], self._resources, exclusive=True
                )
        stream = self._directories[components[:-1]].open_file(components[-1])
        try:
            self._files[components] = (os.fstat(stream.fileno()), size_bytes)
        except BaseException:
            stream.close()
            raise
        return stream

    def complete(self) -> None:
        """Check identities, sizes and the exact inventory, not merely successful GETs."""
        self._verify_directories()
        children: dict[tuple[str, ...], set[str]] = {prefix: set() for prefix in self._directories}
        for prefix in self._directories:
            if prefix:
                children[prefix[:-1]].add(prefix[-1])
        for components, (created, expected_size) in self._files.items():
            directory = self._directories[components[:-1]]
            current = directory.stat(components[-1])
            if not S_ISREG(current.st_mode) or not _same_entry(current, created) or current.st_size != expected_size:
                raise ValueError(f"Checkpoint output file changed: {directory.path / components[-1]}")
            children[components[:-1]].add(components[-1])
        for prefix, directory in self._directories.items():
            if directory.names() != children[prefix]:
                raise ValueError(f"Checkpoint output directory changed: {directory.path}")
