# coding=utf-8

from typing import Optional
from typing_extensions import Required, TypedDict


class InnerModel(TypedDict, total=False):
    """Array inner model.

    :ivar property: Required string property. Required.
    :vartype property: str
    :ivar children:
    :vartype children: list[~typetest.array.models.InnerModel]
    """

    property: Required[str]
    """Required string property. Required."""
    children: Optional[list["InnerModel"]]
