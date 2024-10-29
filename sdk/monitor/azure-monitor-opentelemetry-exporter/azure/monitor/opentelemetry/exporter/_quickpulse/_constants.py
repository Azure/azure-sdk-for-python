# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.
import sys

# cSpell:disable

# (OpenTelemetry metric name, Quickpulse metric name)
# Memory
_COMMITTED_BYTES_NAME = ("azuremonitor.memorycommittedbytes", "\\Memory\\Committed Bytes")
_PROCESS_PHYSICAL_BYTES_NAME = ("azuremonitor.processphysicalbytes", "\\Process\\Physical Bytes")
# CPU
_PROCESSOR_TIME_NAME = ("azuremonitor.processortotalprocessortime", "\\Processor(_Total)\\% Processor Time")
_PROCESS_TIME_NORMALIZED_NAME = ("azuremonitor.processtimenormalized", "\\% Process\\Processor Time Normalized")
# Request
_REQUEST_RATE_NAME = ("azuremonitor.requestssec", "\\ApplicationInsights\\Requests/Sec")
_REQUEST_FAILURE_RATE_NAME = ("azuremonitor.requestsfailedsec", "\\ApplicationInsights\\Requests Failed/Sec")
_REQUEST_DURATION_NAME = ("azuremonitor.requestduration", "\\ApplicationInsights\\Request Duration")
# Dependency
_DEPENDENCY_RATE_NAME = ("azuremonitor.dependencycallssec", "\\ApplicationInsights\\Dependency Calls/Sec")
_DEPENDENCY_FAILURE_RATE_NAME = (
    "azuremonitor.dependencycallsfailedsec",
    "\\ApplicationInsights\\Dependency Calls Failed/Sec",
)  # pylint: disable=line-too-long
_DEPENDENCY_DURATION_NAME = ("azuremonitor.dependencycallduration", "\\ApplicationInsights\\Dependency Call Duration")
# Exception
_EXCEPTION_RATE_NAME = ("azuremonitor.exceptionssec", "\\ApplicationInsights\\Exceptions/Sec")

_QUICKPULSE_METRIC_NAME_MAPPINGS = dict(
    [
        _COMMITTED_BYTES_NAME,
        _PROCESS_PHYSICAL_BYTES_NAME,
        _PROCESSOR_TIME_NAME,
        _PROCESS_TIME_NORMALIZED_NAME,
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

# Response Headers

_QUICKPULSE_ETAG_HEADER_NAME = "x-ms-qps-configuration-etag"
_QUICKPULSE_POLLING_HEADER_NAME = "x-ms-qps-service-polling-interval-hint"
_QUICKPULSE_REDIRECT_HEADER_NAME = "x-ms-qps-service-endpoint-redirect-v2"
_QUICKPULSE_SUBSCRIBED_HEADER_NAME = "x-ms-qps-subscribed"

# Projections (filtering)

_QUICKPULSE_PROJECTION_COUNT = "Count()"
_QUICKPULSE_PROJECTION_DURATION = "Duration"
_QUICKPULSE_PROJECTION_CUSTOM = "CustomDimensions."

_QUICKPULSE_PROJECTION_MAX_VALUE = sys.maxsize
_QUICKPULSE_PROJECTION_MIN_VALUE = -sys.maxsize - 1

# cSpell:enable
