# coding=utf-8

from enum import Enum
from azure.core import CaseInsensitiveEnumMeta


class ReleaseDelay(str, Enum, metaclass=CaseInsensitiveEnumMeta):
    """Supported delays for release operation."""

    NO_DELAY = "0"
    """Release the event after 0 seconds."""
    TEN_SECONDS = "10"
    """Release the event after 10 seconds."""
    ONE_MINUTE = "60"
    """Release the event after 60 seconds."""
    TEN_MINUTES = "600"
    """Release the event after 600 seconds."""
    ONE_HOUR = "3600"
    """Release the event after 3600 seconds."""
