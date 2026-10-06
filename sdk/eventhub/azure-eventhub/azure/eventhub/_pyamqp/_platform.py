"""Platform compatibility."""

# pylint: skip-file

from typing import Tuple, cast
import platform
import re
import struct
import sys

# Jython does not have this attribute
try:
    from socket import SOL_TCP
except ImportError:  # pragma: no cover
    from socket import IPPROTO_TCP as SOL_TCP  # noqa


RE_NUM = re.compile(r"(\d+).+")


def _linux_version_to_tuple(s):
    # type: (str) -> Tuple[int, int, int]
    return cast(Tuple[int, int, int], tuple(map(_versionatom, s.split(".")[:3])))


def _versionatom(s):
    # type: (str) -> int
    if s.isdigit():
        return int(s)
    match = RE_NUM.match(s)
    return int(match.groups()[0]) if match else 0


# TCP socket options that are safe to set on this platform.
# Used by _transport.py to filter DEFAULT_SOCKET_SETTINGS — any option
# not in this set is skipped during socket configuration.
#
# Not all platforms support all TCP options via setsockopt(). For example,
# Windows only supports TCP_NODELAY, and macOS/BSD do not support
# TCP_USER_TIMEOUT. This set is trimmed per-platform below.
KNOWN_TCP_OPTS = {
    "TCP_KEEPCNT",
    "TCP_KEEPIDLE",
    "TCP_KEEPINTVL",
    "TCP_NODELAY",
    "TCP_USER_TIMEOUT",
}

LINUX_VERSION = None
if sys.platform.startswith("linux"):
    LINUX_VERSION = _linux_version_to_tuple(platform.release())
    if LINUX_VERSION < (2, 6, 37):
        KNOWN_TCP_OPTS.remove("TCP_USER_TIMEOUT")

    # Windows Subsystem for Linux is an edge-case: the Python socket library
    # returns most TCP_* enums, but they aren't actually supported
    if platform.release().endswith("Microsoft"):
        KNOWN_TCP_OPTS = {"TCP_NODELAY", "TCP_KEEPIDLE", "TCP_KEEPINTVL", "TCP_KEEPCNT"}

elif sys.platform.startswith("darwin"):
    KNOWN_TCP_OPTS.remove("TCP_USER_TIMEOUT")

elif "bsd" in sys.platform:
    KNOWN_TCP_OPTS.remove("TCP_USER_TIMEOUT")

elif sys.platform.startswith("win"):
    KNOWN_TCP_OPTS = {"TCP_NODELAY"}

elif sys.platform.startswith("cygwin"):
    KNOWN_TCP_OPTS = {"TCP_NODELAY"}

elif sys.platform.startswith("aix"):
    KNOWN_TCP_OPTS.remove("TCP_USER_TIMEOUT")

pack = struct.pack
pack_into = struct.pack_into
unpack = struct.unpack
unpack_from = struct.unpack_from

__all__ = [
    "LINUX_VERSION",
    "SOL_TCP",
    "KNOWN_TCP_OPTS",
    "pack",
    "pack_into",
    "unpack",
    "unpack_from",
]
