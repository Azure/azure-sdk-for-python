#
# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
from enum import Enum

from azure.core import CaseInsensitiveEnumMeta


class LogsQueryStatus(str, Enum, metaclass=CaseInsensitiveEnumMeta):
    """The status of the result object."""

    PARTIAL = "PartialError"
    SUCCESS = "Success"
    FAILURE = "Failure"


class MetricAggregationType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
    """The aggregation type of the metric."""

    NONE = "None"
    AVERAGE = "Average"
    COUNT = "Count"
    MINIMUM = "Minimum"
    MAXIMUM = "Maximum"
    TOTAL = "Total"


class MetricClass(str, Enum, metaclass=CaseInsensitiveEnumMeta):
    """The class of the metric."""

    AVAILABILITY = "Availability"
    TRANSACTIONS = "Transactions"
    ERRORS = "Errors"
    LATENCY = "Latency"
    SATURATION = "Saturation"


class MetricNamespaceClassification(str, Enum, metaclass=CaseInsensitiveEnumMeta):
    """Kind of namespace"""

    PLATFORM = "Platform"
    CUSTOM = "Custom"
    QOS = "Qos"


class MetricUnit(str, Enum, metaclass=CaseInsensitiveEnumMeta):
    """The unit of the metric."""

    COUNT = "Count"
    BYTES = "Bytes"
    SECONDS = "Seconds"
    COUNT_PER_SECOND = "CountPerSecond"
    BYTES_PER_SECOND = "BytesPerSecond"
    PERCENT = "Percent"
    MILLI_SECONDS = "MilliSeconds"
    BYTE_SECONDS = "ByteSeconds"
    UNSPECIFIED = "Unspecified"
    CORES = "Cores"
    MILLI_CORES = "MilliCores"
    NANO_CORES = "NanoCores"
    BITS_PER_SECOND = "BitsPerSecond"
