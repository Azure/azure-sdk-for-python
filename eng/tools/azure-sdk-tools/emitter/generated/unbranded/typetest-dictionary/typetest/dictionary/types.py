# coding=utf-8

from typing_extensions import Required, TypedDict


class InnerModel(TypedDict, total=False):
    """Dictionary inner model.

    :ivar property: Required string property. Required.
    :vartype property: str
    :ivar children:
    :vartype children: dict[str, "InnerModel"]
    """

    property: Required[str]
    """Required string property. Required."""
    children: dict[str, "InnerModel"]
