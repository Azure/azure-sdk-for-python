# coding=utf-8
# pylint: disable=wrong-import-position

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ._patch import *  # pylint: disable=unused-wildcard-import


from ._models import (  # type: ignore
    Cat,
    Dog,
    EnumsOnlyCases,
    GetResponse,
    GetResponse1,
    GetResponse2,
    GetResponse3,
    GetResponse4,
    GetResponse5,
    GetResponse6,
    GetResponse7,
    GetResponse8,
    GetResponse9,
    MixedLiteralsCases,
    MixedTypesCases,
    StringAndArrayCases,
)

from ._enums import (  # type: ignore
    StringExtensibleNamedUnion,
)
from ._patch import __all__ as _patch_all
from ._patch import *
from ._patch import patch_sdk as _patch_sdk

__all__ = [
    "Cat",
    "Dog",
    "EnumsOnlyCases",
    "GetResponse",
    "GetResponse1",
    "GetResponse2",
    "GetResponse3",
    "GetResponse4",
    "GetResponse5",
    "GetResponse6",
    "GetResponse7",
    "GetResponse8",
    "GetResponse9",
    "MixedLiteralsCases",
    "MixedTypesCases",
    "StringAndArrayCases",
    "StringExtensibleNamedUnion",
]
__all__.extend([p for p in _patch_all if p not in __all__])  # pyright: ignore
_patch_sdk()
