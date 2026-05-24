# coding=utf-8

from enum import Enum
from corehttp.utils import CaseInsensitiveEnumMeta


class Versions(str, Enum, metaclass=CaseInsensitiveEnumMeta):
    """The version of the API."""

    V1 = "v1"
    """The version v1."""
    V2 = "v2"
    """The version v2."""
