# coding=utf-8

from typing import Optional
from typing_extensions import Required, TypedDict


class SafeintAsStringProperty(TypedDict, total=False):
    """SafeintAsStringProperty.

    :ivar value: Required.
    :vartype value: int
    """

    value: Required[int]
    """Required."""


class Uint32AsStringProperty(TypedDict, total=False):
    """Uint32AsStringProperty.

    :ivar value:
    :vartype value: int
    """

    value: Optional[int]


class Uint8AsStringProperty(TypedDict, total=False):
    """Uint8AsStringProperty.

    :ivar value: Required.
    :vartype value: int
    """

    value: Required[int]
    """Required."""
