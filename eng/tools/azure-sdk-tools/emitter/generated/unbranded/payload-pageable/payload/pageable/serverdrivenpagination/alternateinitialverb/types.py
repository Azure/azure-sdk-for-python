# coding=utf-8

from typing_extensions import Required, TypedDict


class Filter(TypedDict, total=False):
    """Filter.

    :ivar filter: Required.
    :vartype filter: str
    """

    filter: Required[str]
    """Required."""
