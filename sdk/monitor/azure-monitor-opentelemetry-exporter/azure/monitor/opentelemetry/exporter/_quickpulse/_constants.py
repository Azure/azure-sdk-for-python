# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.
from enum import Enum

# cSpell:disable

# (OpenTelemetry metric name, Quickpulse metric name)
# Memory
_COMMITTED_BYTES_NAME = ("azuremonitor.memorycommittedbytes", "\\Memory\\Committed Bytes")
# CPU
_PROCESSOR_TIME_NAME = ("azuremonitor.processortotalprocessortime", "\\Processor(_Total)\\% Processor Time")
# Request
_REQUEST_RATE_NAME = ("azuremonitor.requestssec", "\\ApplicationInsights\\Requests/Sec")
_REQUEST_FAILURE_RATE_NAME = ("azuremonitor.requestsfailedsec", "\\ApplicationInsights\\Requests Failed/Sec")
_REQUEST_DURATION_NAME = ("azuremonitor.requestduration", "\\ApplicationInsights\\Request Duration")
# Dependency
_DEPENDENCY_RATE_NAME = ("azuremonitor.dependencycallssec", "\\ApplicationInsights\\Dependency Calls/Sec")
_DEPENDENCY_FAILURE_RATE_NAME = ("azuremonitor.dependencycallsfailedsec", "\\ApplicationInsights\\Dependency Calls Failed/Sec")  # pylint: disable=line-too-long
_DEPENDENCY_DURATION_NAME = ("azuremonitor.dependencycallduration", "\\ApplicationInsights\\Dependency Call Duration")
# Exception
_EXCEPTION_RATE_NAME = ("azuremonitor.exceptionssec", "\\ApplicationInsights\\Exceptions/Sec")

_QUICKPULSE_METRIC_NAME_MAPPINGS = dict(
    [
        _COMMITTED_BYTES_NAME,
        _PROCESSOR_TIME_NAME,
        _PROCESSOR_TIME_NAME,
        _REQUEST_RATE_NAME,
        _REQUEST_FAILURE_RATE_NAME,
        _REQUEST_DURATION_NAME,
        _DEPENDENCY_RATE_NAME,
        _DEPENDENCY_FAILURE_RATE_NAME,
        _DEPENDENCY_DURATION_NAME,
        _EXCEPTION_RATE_NAME,
    ]
)

# Quickpulse intervals
_SHORT_PING_INTERVAL_SECONDS = 5
_POST_INTERVAL_SECONDS = 1
_LONG_PING_INTERVAL_SECONDS = 60
_POST_CANCEL_INTERVAL_SECONDS = 20

# Live metrics data types
class _DocumentIngressDocumentType(Enum):
    Request = "Request"
    RemoteDependency = "RemoteDependency"
    Exception = "Exception"
    Event = "Event"
    Trace = "Trace"

# cSpell:enable
