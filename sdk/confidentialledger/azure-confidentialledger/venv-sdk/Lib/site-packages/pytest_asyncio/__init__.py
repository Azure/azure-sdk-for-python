"""The main point for importing pytest-asyncio items."""

from __future__ import annotations

from ._version import version as __version__  # noqa: F401
from .plugin import fixture, is_async_test

__all__ = ("fixture", "is_async_test")
