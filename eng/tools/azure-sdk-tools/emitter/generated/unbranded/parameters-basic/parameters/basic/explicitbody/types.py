# coding=utf-8

from typing_extensions import Required, TypedDict


class User(TypedDict, total=False):
    """This is a simple model.

    :ivar name: Required.
    :vartype name: str
    """

    name: Required[str]
    """Required."""
