# Copyright (c) Microsoft Corporation.
# Licensed under the MIT license.
"""Azure AI Projects model contracts owned by Azure AI OpenAI extensions."""

from ._generated._unions import *  # type: ignore # noqa: F401,F403
from ._generated.types import *  # type: ignore # noqa: F401,F403

_TYPE_EXPORT_EXCLUDES = {
    "Any",
    "FileType",
    "Literal",
    "Optional",
    "Required",
    "TYPE_CHECKING",
    "TypedDict",
    "Union",
}

__all__ = [name for name in globals() if not name.startswith("_") and name not in _TYPE_EXPORT_EXCLUDES]

for _name in list(globals()):
    if not _name.startswith("_") and _name not in __all__:
        del globals()[_name]
