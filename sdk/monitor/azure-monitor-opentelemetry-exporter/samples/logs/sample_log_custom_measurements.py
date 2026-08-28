# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.
"""
An example showing how to add custom measurements to logging telemetry. Entries of the
`microsoft.custom_measurements` attribute populate the `measurements` field of the exported
telemetry. OpenTelemetry attribute values cannot hold maps, so the value is a JSON object
encoded as a string.
"""
# mypy: disable-error-code="attr-defined"
import json
import os
import logging

from opentelemetry._logs import (
    get_logger_provider,
    set_logger_provider,
)
from opentelemetry.sdk._logs import LoggerProvider
from opentelemetry.instrumentation.logging.handler import LoggingHandler
from opentelemetry.sdk._logs.export import BatchLogRecordProcessor

from azure.monitor.opentelemetry.exporter import AzureMonitorLogExporter

set_logger_provider(LoggerProvider())
exporter = AzureMonitorLogExporter.from_connection_string(os.environ["APPLICATIONINSIGHTS_CONNECTION_STRING"])
get_logger_provider().add_log_record_processor(BatchLogRecordProcessor(exporter))

# Attach LoggingHandler to namespaced logger
handler = LoggingHandler()
logger = logging.getLogger(__name__)
logger.addHandler(handler)
logger.setLevel(logging.INFO)

custom_measurements = json.dumps({"itemsProcessed": 42.0, "queueDepth": 7})

logger.info(
    "INFO: Custom event with measurements",
    extra={
        #"microsoft.custom_event.name": "custom-measurements-event", ## Enable to see the custom measurements attribute for custom events.
        "microsoft.custom_measurements": custom_measurements,
    },
)

