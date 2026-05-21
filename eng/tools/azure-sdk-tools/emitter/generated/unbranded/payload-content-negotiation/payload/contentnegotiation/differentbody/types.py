# coding=utf-8

from typing_extensions import Required, TypedDict


class PngImageAsJson(TypedDict, total=False):
    """PngImageAsJson.

    :ivar content: Required.
    :vartype content: bytes
    """

    content: Required[bytes]
    """Required."""
