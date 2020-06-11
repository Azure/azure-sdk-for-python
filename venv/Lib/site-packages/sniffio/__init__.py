"""Top-level package for sniffio."""

from ._version import __version__

from ._impl import (
    current_async_library,
    AsyncLibraryNotFoundError,
    current_async_library_cvar,
)

__all__ = [
    "current_async_library", "UnknownAsyncLibraryError",
    "current_async_library_cvar"
]
