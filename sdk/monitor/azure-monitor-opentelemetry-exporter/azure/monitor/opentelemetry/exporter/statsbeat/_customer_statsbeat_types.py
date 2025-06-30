# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.
from enum import Enum
from azure.core import CaseInsensitiveEnumMeta
# Language constant for customer statsbeat
STATSBEAT_LANGUAGE = "python"

class DropCode(str, Enum, metaclass=CaseInsensitiveEnumMeta):
    CLIENT_READONLY = "CLIENT_READONLY"
    CLIENT_EXCEPTION = "CLIENT_EXCEPTION"
    CLIENT_STALE_DATA = "CLIENT_STALE_DATA"
    CLIENT_PERSISTENCE_CAPACITY = "CLIENT_PERSISTENCE_CAPACITY"
    NON_RETRYABLE_STATUS_CODE = "NON_RETRYABLE_STATUS_CODE"
    UNKNOWN = "UNKNOWN"

class RetryCode(str, Enum, metaclass=CaseInsensitiveEnumMeta):
    CLIENT_TIMEOUT = "CLIENT_TIMEOUT"
    RETRYABLE_STATUS_CODE = "RETRYABLE_STATUS_CODE"
    UNKNOWN = "UNKNOWN"

class CustomerStatsbeatMetricName(str, Enum, metaclass=CaseInsensitiveEnumMeta):
    ITEM_SUCCESS_COUNT = "preview.item.success.count"
    ITEM_DROP_COUNT = "preview.item.dropped.count"
    ITEM_RETRY_COUNT = "preview.item.retry.count"

class CustomerStatsbeatProperties:
    language: str
    version: str
    compute_type: str
    def __init__(self, language: str, version: str, compute_type: str):
        self.language = language
        self.version = version
        self.compute_type = compute_type
