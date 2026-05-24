# coding=utf-8
# pylint: disable=wrong-import-position

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ._patch import *  # pylint: disable=unused-wildcard-import

from ._operations import StringOperations  # type: ignore
from ._operations import BooleanOperations  # type: ignore
from ._operations import UnknownOperations  # type: ignore
from ._operations import DecimalTypeOperations  # type: ignore
from ._operations import Decimal128TypeOperations  # type: ignore
from ._operations import DecimalVerifyOperations  # type: ignore
from ._operations import Decimal128VerifyOperations  # type: ignore

from ._patch import __all__ as _patch_all
from ._patch import *
from ._patch import patch_sdk as _patch_sdk

__all__ = [
    "StringOperations",
    "BooleanOperations",
    "UnknownOperations",
    "DecimalTypeOperations",
    "Decimal128TypeOperations",
    "DecimalVerifyOperations",
    "Decimal128VerifyOperations",
]
__all__.extend([p for p in _patch_all if p not in __all__])  # pyright: ignore
_patch_sdk()
