# coding=utf-8

from enum import Enum
from corehttp.utils import CaseInsensitiveEnumMeta


class ExtendedEnum(str, Enum, metaclass=CaseInsensitiveEnumMeta):
    """Type of ExtendedEnum."""

    ENUM_VALUE2 = "value2"
    """ENUM_VALUE2."""


class FixedInnerEnum(str, Enum, metaclass=CaseInsensitiveEnumMeta):
    """Enum that will be used as a property for model EnumProperty. Non-extensible."""

    VALUE_ONE = "ValueOne"
    """First value."""
    VALUE_TWO = "ValueTwo"
    """Second value."""


class InnerEnum(str, Enum, metaclass=CaseInsensitiveEnumMeta):
    """Enum that will be used as a property for model EnumProperty. Extensible."""

    VALUE_ONE = "ValueOne"
    """First value."""
    VALUE_TWO = "ValueTwo"
    """Second value."""
