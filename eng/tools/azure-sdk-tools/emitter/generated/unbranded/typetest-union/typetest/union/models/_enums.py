# coding=utf-8

from enum import Enum
from corehttp.utils import CaseInsensitiveEnumMeta


class StringExtensibleNamedUnion(str, Enum, metaclass=CaseInsensitiveEnumMeta):
    """Type of StringExtensibleNamedUnion."""

    OPTION_B = "b"
    """OPTION_B."""
    C = "c"
    """C."""
