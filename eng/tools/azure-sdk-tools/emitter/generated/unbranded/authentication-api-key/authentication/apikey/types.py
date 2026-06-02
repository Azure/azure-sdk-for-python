# coding=utf-8

from typing_extensions import Required, TypedDict


class InvalidAuth(TypedDict, total=False):
    """InvalidAuth.

    :ivar error: Required.
    :vartype error: str
    """

    error: Required[str]
    """Required."""
