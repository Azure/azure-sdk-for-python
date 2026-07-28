# coding=utf-8

from typing import TYPE_CHECKING, Union
from typing_extensions import Required, TypedDict

if TYPE_CHECKING:
    from . import _unions
    from .models import NewEnum


class NewModel(TypedDict, total=False):
    """NewModel.

    :ivar newProp: Required.
    :vartype newProp: str
    :ivar enumProp: Required. "newEnumMember"
    :vartype enumProp: Union[str, "NewEnum"]
    :ivar unionProp: Required. Is either a str type or a int type.
    :vartype unionProp: "_unions.NewUnion"
    """

    newProp: Required[str]
    """Required."""
    enumProp: Required[Union[str, "NewEnum"]]
    """Required. \"newEnumMember\""""
    unionProp: Required["_unions.NewUnion"]
    """Required. Is either a str type or a int type."""
