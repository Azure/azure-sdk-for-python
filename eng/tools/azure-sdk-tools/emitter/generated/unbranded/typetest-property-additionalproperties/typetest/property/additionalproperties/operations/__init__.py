# coding=utf-8
# pylint: disable=wrong-import-position

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ._patch import *  # pylint: disable=unused-wildcard-import

from ._operations import ExtendsUnknownOperations  # type: ignore
from ._operations import ExtendsUnknownDerivedOperations  # type: ignore
from ._operations import ExtendsUnknownDiscriminatedOperations  # type: ignore
from ._operations import IsUnknownOperations  # type: ignore
from ._operations import IsUnknownDerivedOperations  # type: ignore
from ._operations import IsUnknownDiscriminatedOperations  # type: ignore
from ._operations import ExtendsStringOperations  # type: ignore
from ._operations import IsStringOperations  # type: ignore
from ._operations import SpreadStringOperations  # type: ignore
from ._operations import ExtendsFloatOperations  # type: ignore
from ._operations import IsFloatOperations  # type: ignore
from ._operations import SpreadFloatOperations  # type: ignore
from ._operations import ExtendsModelOperations  # type: ignore
from ._operations import IsModelOperations  # type: ignore
from ._operations import SpreadModelOperations  # type: ignore
from ._operations import ExtendsModelArrayOperations  # type: ignore
from ._operations import IsModelArrayOperations  # type: ignore
from ._operations import SpreadModelArrayOperations  # type: ignore
from ._operations import SpreadDifferentStringOperations  # type: ignore
from ._operations import SpreadDifferentFloatOperations  # type: ignore
from ._operations import SpreadDifferentModelOperations  # type: ignore
from ._operations import SpreadDifferentModelArrayOperations  # type: ignore
from ._operations import ExtendsDifferentSpreadStringOperations  # type: ignore
from ._operations import ExtendsDifferentSpreadFloatOperations  # type: ignore
from ._operations import ExtendsDifferentSpreadModelOperations  # type: ignore
from ._operations import ExtendsDifferentSpreadModelArrayOperations  # type: ignore
from ._operations import MultipleSpreadOperations  # type: ignore
from ._operations import SpreadRecordUnionOperations  # type: ignore
from ._operations import SpreadRecordNonDiscriminatedUnionOperations  # type: ignore
from ._operations import SpreadRecordNonDiscriminatedUnion2Operations  # type: ignore
from ._operations import SpreadRecordNonDiscriminatedUnion3Operations  # type: ignore

from ._patch import __all__ as _patch_all
from ._patch import *
from ._patch import patch_sdk as _patch_sdk

__all__ = [
    "ExtendsUnknownOperations",
    "ExtendsUnknownDerivedOperations",
    "ExtendsUnknownDiscriminatedOperations",
    "IsUnknownOperations",
    "IsUnknownDerivedOperations",
    "IsUnknownDiscriminatedOperations",
    "ExtendsStringOperations",
    "IsStringOperations",
    "SpreadStringOperations",
    "ExtendsFloatOperations",
    "IsFloatOperations",
    "SpreadFloatOperations",
    "ExtendsModelOperations",
    "IsModelOperations",
    "SpreadModelOperations",
    "ExtendsModelArrayOperations",
    "IsModelArrayOperations",
    "SpreadModelArrayOperations",
    "SpreadDifferentStringOperations",
    "SpreadDifferentFloatOperations",
    "SpreadDifferentModelOperations",
    "SpreadDifferentModelArrayOperations",
    "ExtendsDifferentSpreadStringOperations",
    "ExtendsDifferentSpreadFloatOperations",
    "ExtendsDifferentSpreadModelOperations",
    "ExtendsDifferentSpreadModelArrayOperations",
    "MultipleSpreadOperations",
    "SpreadRecordUnionOperations",
    "SpreadRecordNonDiscriminatedUnionOperations",
    "SpreadRecordNonDiscriminatedUnion2Operations",
    "SpreadRecordNonDiscriminatedUnion3Operations",
]
__all__.extend([p for p in _patch_all if p not in __all__])  # pyright: ignore
_patch_sdk()
