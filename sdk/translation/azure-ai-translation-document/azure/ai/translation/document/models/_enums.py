# coding=utf-8

from enum import Enum
from azure.core import CaseInsensitiveEnumMeta


class FileFormatType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
    """Format types."""

    DOCUMENT = "document"
    """Document type file format"""
    GLOSSARY = "glossary"
    """Glossary type file format"""


class Status(str, Enum, metaclass=CaseInsensitiveEnumMeta):
    """List of possible statuses for job or document."""

    NOT_STARTED = "NotStarted"
    """NotStarted"""
    RUNNING = "Running"
    """Running"""
    SUCCEEDED = "Succeeded"
    """Succeeded"""
    FAILED = "Failed"
    """Failed"""
    CANCELED = "Cancelled"
    """Cancelled"""
    CANCELING = "Cancelling"
    """Cancelling"""
    VALIDATION_FAILED = "ValidationFailed"
    """ValidationFailed"""


class StorageInputType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
    """Storage type of the input documents source string."""

    FOLDER = "Folder"
    """Folder storage input type"""
    FILE = "File"
    """File storage input type"""


class TranslationErrorCode(str, Enum, metaclass=CaseInsensitiveEnumMeta):
    """Enums containing high level error codes."""

    INVALID_REQUEST = "InvalidRequest"
    """InvalidRequest"""
    INVALID_ARGUMENT = "InvalidArgument"
    """InvalidArgument"""
    INTERNAL_SERVER_ERROR = "InternalServerError"
    """InternalServerError"""
    SERVICE_UNAVAILABLE = "ServiceUnavailable"
    """ServiceUnavailable"""
    RESOURCE_NOT_FOUND = "ResourceNotFound"
    """ResourceNotFound"""
    UNAUTHORIZED = "Unauthorized"
    """Unauthorized"""
    REQUEST_RATE_TOO_HIGH = "RequestRateTooHigh"
    """RequestRateTooHigh"""


class TranslationStorageSource(str, Enum, metaclass=CaseInsensitiveEnumMeta):
    """Storage Source."""

    AZURE_BLOB = "AzureBlob"
    """Azure blob storage source"""
