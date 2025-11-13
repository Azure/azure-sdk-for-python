# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.

# (OpenTelemetry metric name, Breeze metric name)
_AVAILABLE_MEMORY = (
    "azuremonitor.performancecounter.memoryavailablebytes",
    "\\Memory\\Available Bytes"
)
_EXCEPTION_RATE = (
    "azuremonitor.performancecounter.exceptionssec",
    "\\.NET CLR Exceptions(??APP_CLR_PROC??)\\# of Exceps Thrown / sec"
)
_REQUEST_EXECUTION_TIME = (
    "azuremonitor.performancecounter.requestexecutiontime",
    "\\ASP.NET Applications(??APP_W3SVC_PROC??)\\Request Execution Time"
)
_REQUEST_RATE = (
    "azuremonitor.performancecounter.requestssec",
    "\\ASP.NET Applications(??APP_W3SVC_PROC??)\\Requests/Sec"
)
_PROCESS_CPU = (
    "azuremonitor.performancecounter.processtime",
    "\\Process(??APP_WIN32_PROC??)\\% Processor Time"
)
_PROCESS_CPU_NORMALIZED = (
    "azuremonitor.performancecounter.processtimenormalized",
    "\\Process(??APP_WIN32_PROC??)\\% Processor Time Normalized"
)
_PROCESS_IO_RATE = (
    "azuremonitor.performancecounter.processiobytessec",
    "\\Process(??APP_WIN32_PROC??)\\IO Data Bytes/sec"
)
_PROCESS_PRIVATE_BYTES = (
    "azuremonitor.performancecounter.processprivatebytes",
    "\\Process(??APP_WIN32_PROC??)\\Private Bytes"
)
_PROCESSOR_TIME = (
    "azuremonitor.performancecounter.processortotalprocessortime",
    "\\Processor(_Total)\\% Processor Time"
)

_PERFORMANCE_COUNTER_METRIC_NAME_MAPPINGS = dict(
    [
        _AVAILABLE_MEMORY,
        _EXCEPTION_RATE,
        _REQUEST_EXECUTION_TIME,
        _REQUEST_RATE,
        _PROCESS_CPU,
        _PROCESS_CPU_NORMALIZED,
        _PROCESS_IO_RATE,
        _PROCESS_PRIVATE_BYTES,
        _PROCESSOR_TIME,
    ]
)
