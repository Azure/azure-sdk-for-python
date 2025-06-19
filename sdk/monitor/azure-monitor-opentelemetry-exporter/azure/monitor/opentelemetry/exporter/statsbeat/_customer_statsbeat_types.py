# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.
from enum import Enum
from typing import Dict, Any, List, Optional, TypedDict

# Language constant for customer statsbeat
STATSBEAT_LANGUAGE = "python"
class TelemetryType(str, Enum):
    AVAILABILITY = "AVAILABILITY"
    CUSTOM_EVENT = "CUSTOM_EVENT"
    CUSTOM_METRIC = "CUSTOM_METRIC"
    DEPENDENCY = "DEPENDENCY"
    EXCEPTION = "EXCEPTION"
    PAGE_VIEW = "PAGE_VIEW"
    PERFORMANCE_COUNTER = "PERFORMANCE_COUNTER"
    REQUEST = "REQUEST"
    TRACE = "TRACE"
    UNKNOWN = "UNKNOWN"
class DropCode(str, Enum):
    CLIENT_EXCEPTION = "CLIENT_EXCEPTION"
    CLIENT_EXPIRED_DATA = "CLIENT_EXPIRED_DATA"
    CLIENT_READONLY = "CLIENT_READONLY"
    CLIENT_STALE_DATA = "CLIENT_STALE_DATA"
    CLIENT_PERSISTENCE_CAPACITY = "CLIENT_PERSISTENCE_CAPACITY"
    NON_RETRYABLE_STATUS_CODE = "NON_RETRYABLE_STATUS_CODE"
    UNKNOWN = "UNKNOWN"
class RetryCode(str, Enum):
    CLIENT_EXCEPTION = "CLIENT_EXCEPTION"
    CLIENT_STORAGE_DISABLED = "CLIENT_STORAGE_DISABLED"
    CLIENT_TIMEOUT = "CLIENT_TIMEOUT"
    RETRYABLE_STATUS_CODE = "RETRYABLE_STATUS_CODE"
    UNKNOWN = "UNKNOWN"
class CustomStatsbeatCounter(str, Enum):
    ITEM_SUCCESS_COUNT = "preview.item.success.count"
    ITEM_DROP_COUNT = "preview.item.dropped.count"
    ITEM_RETRY_COUNT = "preview.item.retry.count"
class ItemSuccessCount(TypedDict, total=False):
    count: int
    telemetry_type: TelemetryType
class ItemDropCount(TypedDict, total=False):
    count: int
    drop_code: DropCode
    # Dot notation will be handled at runtime
    drop_reason: Optional[str]
    exception_message: Optional[str]
    telemetry_type: Optional[TelemetryType]
class ItemRetryCount(TypedDict, total=False):
    count: int
    retry_code: RetryCode
    retry_reason: Optional[str]
    exception_message: Optional[str]
    telemetry_type: Optional[TelemetryType]
    # Note: Dot notation fields like "retry.code" will be handled at runtime
class CustomerStatsbeatProperties:
    language: str
    version: str
    compute_type: str
    def __init__(self, language: str, version: str, compute_type: str):
        self.language = language
        self.version = version
        self.compute_type = compute_type

class CustomerStatsbeat:
    def __init__(self):
        self.total_item_success_count: List[Dict[str, Any]] = []
        self.total_item_drop_count: List[Dict[str, Any]] = []
        self.total_item_retry_count: List[Dict[str, Any]] = []