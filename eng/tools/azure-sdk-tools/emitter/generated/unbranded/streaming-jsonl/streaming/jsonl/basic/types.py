# coding=utf-8

from typing_extensions import Required, TypedDict


class Info(TypedDict, total=False):
    """Info.

    :ivar desc: Required.
    :vartype desc: str
    """

    desc: Required[str]
    """Required."""
