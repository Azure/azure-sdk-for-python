# coding=utf-8

from typing_extensions import Required, TypedDict


class InnerModel(TypedDict, total=False):
    """Array inner model.

    :ivar property: Required string property. Required.
    :vartype property: str
    :ivar children:
    :vartype children: list["InnerModel"]
    """

    property: Required[str]
    """Required string property. Required."""
    children: list["InnerModel"]
