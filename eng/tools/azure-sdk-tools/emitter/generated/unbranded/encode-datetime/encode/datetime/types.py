# coding=utf-8

from typing_extensions import Required, TypedDict


class DefaultDatetimeProperty(TypedDict, total=False):
    """DefaultDatetimeProperty.

    :ivar value: Required.
    :vartype value: str
    """

    value: Required[str]
    """Required."""


class Rfc3339DatetimeProperty(TypedDict, total=False):
    """Rfc3339DatetimeProperty.

    :ivar value: Required.
    :vartype value: str
    """

    value: Required[str]
    """Required."""


class Rfc7231DatetimeProperty(TypedDict, total=False):
    """Rfc7231DatetimeProperty.

    :ivar value: Required.
    :vartype value: str
    """

    value: Required[str]
    """Required."""


class UnixTimestampArrayDatetimeProperty(TypedDict, total=False):
    """UnixTimestampArrayDatetimeProperty.

    :ivar value: Required.
    :vartype value: list[int]
    """

    value: Required[list[int]]
    """Required."""


class UnixTimestampDatetimeProperty(TypedDict, total=False):
    """UnixTimestampDatetimeProperty.

    :ivar value: Required.
    :vartype value: int
    """

    value: Required[int]
    """Required."""
