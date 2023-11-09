# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.
"""
An example showing how to export exception telemetry using the AzureMonitorLogExporter.
"""
# mypy: disable-error-code="attr-defined"
import os
import logging

from opentelemetry._logs import (
    get_logger_provider,
    set_logger_provider,
)
from opentelemetry.sdk._logs import (
    LoggerProvider,
    LoggingHandler,
)
from opentelemetry.sdk._logs.export import BatchLogRecordProcessor

from azure.monitor.opentelemetry.exporter import AzureMonitorLogExporter

set_logger_provider(LoggerProvider())
exporter = AzureMonitorLogExporter.from_connection_string(
    os.environ["APPLICATIONINSIGHTS_CONNECTION_STRING"]
)
get_logger_provider().add_log_record_processor(BatchLogRecordProcessor(exporter))

# Attach LoggingHandler to namespaced logger
handler = LoggingHandler()
logger = logging.getLogger(__name__)
logger.addHandler(handler)
logger.setLevel(logging.ERROR)

# The following code will generate two pieces of exception telemetry
# that are identical in nature
try:
    val = 1 / 0
    print(val)
except ZeroDivisionError:
    logger.exception("Error: Division by zero")

try:
    val = 1 / 0
    print(val)
except ZeroDivisionError:
    logger.error("Error: Division by zero", stack_info=True, exc_info=True)

input()
