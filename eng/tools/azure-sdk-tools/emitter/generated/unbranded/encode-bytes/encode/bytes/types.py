# coding=utf-8

from typing_extensions import Required, TypedDict


class Base64BytesProperty(TypedDict, total=False):
    """Base64BytesProperty.

    :ivar value: Required.
    :vartype value: bytes
    """

    value: Required[bytes]
    """Required."""


class Base64urlArrayBytesProperty(TypedDict, total=False):
    """Base64urlArrayBytesProperty.

    :ivar value: Required.
    :vartype value: list[bytes]
    """

    value: Required[list[bytes]]
    """Required."""


class Base64urlBytesProperty(TypedDict, total=False):
    """Base64urlBytesProperty.

    :ivar value: Required.
    :vartype value: bytes
    """

    value: Required[bytes]
    """Required."""


class DefaultBytesProperty(TypedDict, total=False):
    """DefaultBytesProperty.

    :ivar value: Required.
    :vartype value: bytes
    """

    value: Required[bytes]
    """Required."""
