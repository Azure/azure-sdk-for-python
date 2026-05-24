# coding=utf-8

from typing import TYPE_CHECKING, Union
from typing_extensions import Required, TypedDict

if TYPE_CHECKING:
    from . import _unions
    from .models import NewEnum


class NewModel(TypedDict, total=False):
    """NewModel.

    :ivar new_prop: Required.
    :vartype new_prop: str
    :ivar enum_prop: Required. "newEnumMember"
    :vartype enum_prop: str or ~versioning.renamedfrom.models.NewEnum
    :ivar union_prop: Required. Is either a str type or a int type.
    :vartype union_prop: str or int
    """

    newProp: Required[str]
    """Required."""
    enumProp: Required[Union[str, "NewEnum"]]
    """Required. \"newEnumMember\""""
    unionProp: Required["_unions.NewUnion"]
    """Required. Is either a str type or a int type."""
