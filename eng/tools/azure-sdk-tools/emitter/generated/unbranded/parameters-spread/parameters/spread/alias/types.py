# coding=utf-8

from typing_extensions import Required, TypedDict


class SpreadAsRequestBodyRequest(TypedDict, total=False):
    """SpreadAsRequestBodyRequest.

    :ivar name: Required.
    :vartype name: str
    """

    name: Required[str]
    """Required."""
