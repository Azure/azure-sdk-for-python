# coding=utf-8

import datetime
from typing_extensions import Required, TypedDict


class DefaultDatetimeProperty(TypedDict, total=False):
    """DefaultDatetimeProperty.

    :ivar value: Required.
    :vartype value: ~datetime.datetime
    """

    value: Required[datetime.datetime]
    """Required."""


class Rfc3339DatetimeProperty(TypedDict, total=False):
    """Rfc3339DatetimeProperty.

    :ivar value: Required.
    :vartype value: ~datetime.datetime
    """

    value: Required[datetime.datetime]
    """Required."""


class Rfc7231DatetimeProperty(TypedDict, total=False):
    """Rfc7231DatetimeProperty.

    :ivar value: Required.
    :vartype value: ~datetime.datetime
    """

    value: Required[datetime.datetime]
    """Required."""


class UnixTimestampArrayDatetimeProperty(TypedDict, total=False):
    """UnixTimestampArrayDatetimeProperty.

    :ivar value: Required.
    :vartype value: list[~datetime.datetime]
    """

    value: Required[list[datetime.datetime]]
    """Required."""


class UnixTimestampDatetimeProperty(TypedDict, total=False):
    """UnixTimestampDatetimeProperty.

    :ivar value: Required.
    :vartype value: ~datetime.datetime
    """

    value: Required[datetime.datetime]
    """Required."""
