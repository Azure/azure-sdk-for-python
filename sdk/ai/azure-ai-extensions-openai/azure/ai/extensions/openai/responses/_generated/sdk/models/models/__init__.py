# coding=utf-8
# --------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------
# pylint: disable=wrong-import-position

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ._patch import *  # pylint: disable=unused-wildcard-import

from ._patch import __all__ as _patch_all
from ._patch import *
from ._patch import patch_sdk as _patch_sdk
from .. import types as _types
from .._unions import *  # type: ignore # noqa: F401,F403
from ..types import *  # type: ignore # noqa: F401,F403
from ._models import __all__ as _models_all
from ._models import *  # type: ignore # noqa: F401,F403

_TYPE_EXPORT_EXCLUDES = {
    "Any",
    "Literal",
    "Optional",
    "Required",
    "TYPE_CHECKING",
    "TypedDict",
    "Union",
}
__all__ = [name for name in _models_all if name not in _TYPE_EXPORT_EXCLUDES]
__all__.extend([p for p in _patch_all if p not in __all__])  # pyright: ignore
_patch_sdk()
