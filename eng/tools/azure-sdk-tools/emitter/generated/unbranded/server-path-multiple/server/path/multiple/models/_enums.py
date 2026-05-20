# coding=utf-8

from enum import Enum
from corehttp.utils import CaseInsensitiveEnumMeta


class Versions(str, Enum, metaclass=CaseInsensitiveEnumMeta):
    """Service versions."""

    V1_0 = "v1.0"
    """Version 1.0."""
