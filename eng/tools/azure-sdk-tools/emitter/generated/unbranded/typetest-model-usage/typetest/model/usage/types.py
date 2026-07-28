# coding=utf-8

from typing_extensions import Required, TypedDict


class InputOutputRecord(TypedDict, total=False):
    """Record used both as operation parameter and return type.

    :ivar requiredProp: Required.
    :vartype requiredProp: str
    """

    requiredProp: Required[str]
    """Required."""


class InputRecord(TypedDict, total=False):
    """Record used in operation parameters.

    :ivar requiredProp: Required.
    :vartype requiredProp: str
    """

    requiredProp: Required[str]
    """Required."""
