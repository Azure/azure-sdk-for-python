# coding=utf-8

from typing_extensions import Required, TypedDict


class WithItemsRequest(TypedDict, total=False):
    """WithItemsRequest.

    :ivar items_property: Required.
    :vartype items_property: list[str]
    """

    items: Required[list[str]]
    """Required."""
