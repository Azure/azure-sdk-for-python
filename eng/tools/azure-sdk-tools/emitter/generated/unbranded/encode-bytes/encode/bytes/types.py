# coding=utf-8

from typing_extensions import Required, TypedDict


class Base64BytesProperty(TypedDict, total=False):
    """Base64BytesProperty.

    :ivar value: Required.
    :vartype value: str
    """

    value: Required[str]
    """Required."""


class Base64urlArrayBytesProperty(TypedDict, total=False):
    """Base64urlArrayBytesProperty.

    :ivar value: Required.
    :vartype value: list[str]
    """

    value: Required[list[str]]
    """Required."""


class Base64urlBytesProperty(TypedDict, total=False):
    """Base64urlBytesProperty.

    :ivar value: Required.
    :vartype value: str
    """

    value: Required[str]
    """Required."""


class DefaultBytesProperty(TypedDict, total=False):
    """DefaultBytesProperty.

    :ivar value: Required.
    :vartype value: str
    """

    value: Required[str]
    """Required."""
