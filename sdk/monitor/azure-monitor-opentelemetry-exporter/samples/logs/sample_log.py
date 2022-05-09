# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.
"""
An example to show an application using Opentelemetry logging sdk. Logging calls to the standard Python
logging library are tracked and telemetry is exported to application insights with the AzureMonitorLogExporter.
"""
import os
import logging

from opentelemetry.sdk._logs import (
    LogEmitterProvider,
    OTLPHandler,
    get_log_emitter_provider,
    set_log_emitter_provider,
)
from opentelemetry.sdk._logs.export import BatchLogProcessor

from azure.monitor.opentelemetry.exporter import AzureMonitorLogExporter

set_log_emitter_provider(LogEmitterProvider())
exporter = AzureMonitorLogExporter.from_connection_string(
    os.environ["APPLICATIONINSIGHTS_CONNECTION_STRING"]
)
get_log_emitter_provider().add_log_processor(BatchLogProcessor(exporter))

# Attach OTel handler to namespaced logger
handler = OTLPHandler()
logger = logging.getLogger(__name__)
logger.addHandler(handler)
logger.setLevel(logging.NOTSET)

logger.warning("Hello World!")
