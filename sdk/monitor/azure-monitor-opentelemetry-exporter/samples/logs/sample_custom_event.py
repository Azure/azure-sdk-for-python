# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.
"""
An example to show an application using Opentelemetry logging sdk. Logging calls to the standard Python
logging library are tracked and telemetry is exported to application insights with the AzureMonitorLogExporter.
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

logger_provider = LoggerProvider()
set_logger_provider(logger_provider)
exporter = AzureMonitorLogExporter.from_connection_string(
    os.environ["APPLICATIONINSIGHTS_CONNECTION_STRING"]
)
get_logger_provider().add_log_record_processor(
    BatchLogRecordProcessor(exporter, schedule_delay_millis=5000)
)

# Attach LoggingHandler to namespaced logger
handler = LoggingHandler()
logger = logging.getLogger(__name__)
logger.addHandler(handler)
logger.setLevel(logging.INFO)

# You can send `customEvent`` telemetry using a special `microsoft` attribute key through logging
# The name of the `customEvent` will correspond to the value of the attribute`
logger.info(
    "Hello World!",
    extra={
        "microsoft.custom_event.name": "test-event-name",
        "additional_attrs": "val1",
    },
)

# You can also populate fields like client_Ip with attribute `client.address`
logger.info(
    "This entry will have a custom client_Ip",
    extra={
        "microsoft.custom_event.name": "test_event",
        "client.address": "192.168.1.1",
    },
)

input()
