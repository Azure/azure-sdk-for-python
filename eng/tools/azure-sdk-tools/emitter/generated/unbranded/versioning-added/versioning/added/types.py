# coding=utf-8

from typing import TYPE_CHECKING, Union
from typing_extensions import Required, TypedDict

if TYPE_CHECKING:
    from . import _unions
    from .models import EnumV1, EnumV2


class ModelV1(TypedDict, total=False):
    """ModelV1.

    :ivar prop: Required.
    :vartype prop: str
    :ivar enum_prop: Required. Known values are: "enumMemberV1" and "enumMemberV2".
    :vartype enum_prop: str or ~versioning.added.models.EnumV1
    :ivar union_prop: Required. Is either a str type or a int type.
    :vartype union_prop: str or int
    """

    prop: Required[str]
    """Required."""
    enumProp: Required[Union[str, "EnumV1"]]
    """Required. Known values are: \"enumMemberV1\" and \"enumMemberV2\"."""
    unionProp: Required["_unions.UnionV1"]
    """Required. Is either a str type or a int type."""


class ModelV2(TypedDict, total=False):
    """ModelV2.

    :ivar prop: Required.
    :vartype prop: str
    :ivar enum_prop: Required. "enumMember"
    :vartype enum_prop: str or ~versioning.added.models.EnumV2
    :ivar union_prop: Required. Is either a str type or a int type.
    :vartype union_prop: str or int
    """

    prop: Required[str]
    """Required."""
    enumProp: Required[Union[str, "EnumV2"]]
    """Required. \"enumMember\""""
    unionProp: Required["_unions.UnionV2"]
    """Required. Is either a str type or a int type."""
