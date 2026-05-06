# coding=utf-8

from enum import Enum
from corehttp.utils import CaseInsensitiveEnumMeta


class EnumV2(str, Enum, metaclass=CaseInsensitiveEnumMeta):
    """Type of EnumV2."""

    ENUM_MEMBER_V2 = "enumMemberV2"
    """ENUM_MEMBER_V2."""


class EnumV3(str, Enum, metaclass=CaseInsensitiveEnumMeta):
    """Type of EnumV3."""

    ENUM_MEMBER_V1 = "enumMemberV1"
    """ENUM_MEMBER_V1."""
    ENUM_MEMBER_V2_PREVIEW = "enumMemberV2Preview"
    """ENUM_MEMBER_V2_PREVIEW."""


class Versions(str, Enum, metaclass=CaseInsensitiveEnumMeta):
    """The version of the API."""

    V1 = "v1"
    """The version v1."""
    V2_PREVIEW = "v2preview"
    """The V2 Preview version."""
    V2 = "v2"
    """The version v2."""
