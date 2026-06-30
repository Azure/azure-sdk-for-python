# coding=utf-8

from typing_extensions import Required, TypedDict


class BodyModel(TypedDict, total=False):
    """BodyModel.

    :ivar name: Required.
    :vartype name: str
    """

    name: Required[str]
    """Required."""
