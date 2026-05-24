# coding=utf-8

from enum import Enum
from corehttp.utils import CaseInsensitiveEnumMeta


class Colors(str, Enum, metaclass=CaseInsensitiveEnumMeta):
    """Type of Colors."""

    BLUE = "blue"
    """BLUE."""
    RED = "red"
    """RED."""
    GREEN = "green"
    """GREEN."""


class ColorsExtensibleEnum(str, Enum, metaclass=CaseInsensitiveEnumMeta):
    """Type of ColorsExtensibleEnum."""

    BLUE = "blue"
    """BLUE."""
    RED = "red"
    """RED."""
    GREEN = "green"
    """GREEN."""
