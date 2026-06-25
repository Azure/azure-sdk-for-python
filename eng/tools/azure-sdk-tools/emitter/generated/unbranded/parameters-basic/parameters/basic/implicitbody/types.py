# coding=utf-8

from typing_extensions import Required, TypedDict


class SimpleRequest(TypedDict, total=False):
    """SimpleRequest.

    :ivar name: Required.
    :vartype name: str
    """

    name: Required[str]
    """Required."""
