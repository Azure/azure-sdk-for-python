# coding=utf-8

from typing_extensions import Required, TypedDict


class InputOutputRecord(TypedDict, total=False):
    """Record used both as operation parameter and return type.

    :ivar required_prop: Required.
    :vartype required_prop: str
    """

    requiredProp: Required[str]
    """Required."""


class InputRecord(TypedDict, total=False):
    """Record used in operation parameters.

    :ivar required_prop: Required.
    :vartype required_prop: str
    """

    requiredProp: Required[str]
    """Required."""


class OutputRecord(TypedDict, total=False):
    """Record used in operation return type.

    :ivar required_prop: Required.
    :vartype required_prop: str
    """

    requiredProp: Required[str]
    """Required."""
