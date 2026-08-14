# coding=utf-8

from typing_extensions import Required, TypedDict


class RetrievalRequest(TypedDict, total=False):
    """RetrievalRequest.

    :ivar query: Required.
    :vartype query: str
    """

    query: Required[str]
    """Required."""
