# coding=utf-8

from enum import Enum
from corehttp.utils import CaseInsensitiveEnumMeta


class Status(str, Enum, metaclass=CaseInsensitiveEnumMeta):
    """Status values for the model with enum."""

    PENDING = "pending"
    """Pending status."""
    SUCCESS = "success"
    """Success status."""
    ERROR = "error"
    """Error status."""
