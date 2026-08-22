# Copyright (c) Microsoft Corporation.
# Licensed under the MIT license.
"""TypedDict model exports for Responses contracts."""

from .. import _unions as _unions_module
from .. import types as _types_module
from .._unions import *  # type: ignore # noqa: F401,F403
from ..types import *  # type: ignore # noqa: F401,F403


_TYPE_EXPORT_EXCLUDES = {
    "Any",
    "Literal",
    "Optional",
    "Required",
    "TYPE_CHECKING",
    "TypedDict",
    "Union",
}
__all__: list[str] = []

for _name in dir(_types_module):
    if _name.startswith("_") or _name in _TYPE_EXPORT_EXCLUDES:
        continue
    globals()[_name] = getattr(_types_module, _name)
    __all__.append(_name)

for _name in dir(_unions_module):
    if _name.startswith("_") or _name in __all__:
        continue
    globals()[_name] = getattr(_unions_module, _name)
    __all__.append(_name)
