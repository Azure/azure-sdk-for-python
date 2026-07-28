# coding=utf-8

from typing_extensions import Required, TypedDict


class WithItemsRequest(TypedDict, total=False):
    """WithItemsRequest.

    :ivar items: Required.
    :vartype items: list[str]
    """

    items: Required[list[str]]
    """Required."""
