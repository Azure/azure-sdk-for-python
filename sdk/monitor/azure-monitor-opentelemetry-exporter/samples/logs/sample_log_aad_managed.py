# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.
"""
An example to show an application using Opentelemetry logging sdk. Logging calls to the standard Python
logging library are tracked and telemetry is exported to application insights with the AzureMonitorLogExporter.
"""
import os
import logging

from azure.identity import ManagedIdentityCredential
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
credential = ManagedIdentityCredential(client_id="<client_id>")
exporter = AzureMonitorLogExporter.from_connection_string(
    os.environ["APPLICATIONINSIGHTS_CONNECTION_STRING"],
    credential=credential
)
get_logger_provider().add_log_record_processor(BatchLogRecordProcessor(exporter))

# Attach LoggingHandler to namespaced logger
handler = LoggingHandler()
logger = logging.getLogger(__name__)
logger.addHandler(handler)
logger.setLevel(logging.NOTSET)

logger.warning("Hello World with AAD Managed Identity!")
