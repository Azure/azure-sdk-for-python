# coding=utf-8

from enum import Enum
from azure.core import CaseInsensitiveEnumMeta


class ConfigurationSettingFields(str, Enum, metaclass=CaseInsensitiveEnumMeta):
    """Key-value fields."""

    KEY = "key"
    """Key field."""
    LABEL = "label"
    """Label field."""
    CONTENT_TYPE = "content_type"
    """Content type field."""
    VALUE = "value"
    """Value field."""
    LAST_MODIFIED = "last_modified"
    """Last modified field."""
    TAGS = "tags"
    """Tags field."""
    LOCKED = "locked"
    """Locked field."""
    ETAG = "etag"
    """Etag field."""


class LabelFields(str, Enum, metaclass=CaseInsensitiveEnumMeta):
    """Label fields."""

    NAME = "name"
    """Name field."""


class OperationState(str, Enum, metaclass=CaseInsensitiveEnumMeta):
    """Enum describing allowed operation states."""

    NOT_STARTED = "NotStarted"
    """The operation has not started."""
    RUNNING = "Running"
    """The operation is in progress."""
    SUCCEEDED = "Succeeded"
    """The operation has completed successfully."""
    FAILED = "Failed"
    """The operation has failed."""
    CANCELED = "Canceled"
    """The operation has been canceled by the user."""


class SnapshotComposition(str, Enum, metaclass=CaseInsensitiveEnumMeta):
    """Composition types."""

    KEY = "key"
    """The 'key' composition type."""
    KEY_LABEL = "key_label"
    """The 'key_label' composition type."""


class SnapshotFields(str, Enum, metaclass=CaseInsensitiveEnumMeta):
    """Snapshot fields."""

    NAME = "name"
    """Name field."""
    STATUS = "status"
    """Status field."""
    FILTERS = "filters"
    """Filters field."""
    COMPOSITION_TYPE = "composition_type"
    """Composition type field."""
    CREATED = "created"
    """Created field."""
    EXPIRES = "expires"
    """Expires field."""
    RETENTION_PERIOD = "retention_period"
    """Retention period field."""
    SIZE = "size"
    """Size field."""
    ITEMS_COUNT = "items_count"
    """Items count field."""
    TAGS = "tags"
    """Tags field."""
    ETAG = "etag"
    """Etag field."""


class SnapshotStatus(str, Enum, metaclass=CaseInsensitiveEnumMeta):
    """Snapshot status."""

    PROVISIONING = "provisioning"
    """Provisioning"""
    READY = "ready"
    """Ready"""
    ARCHIVED = "archived"
    """Archived"""
    FAILED = "failed"
    """Failed"""
