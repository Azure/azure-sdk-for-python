# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.
"""
An example showing how to export exception telemetry using the AzureMonitorLogExporter.
"""
import os
import logging

from opentelemetry.sdk._logs import (
    LogEmitterProvider,
    OTLPHandler,
    set_log_emitter_provider,
)
from opentelemetry.sdk._logs.export import BatchLogProcessor

from azure.monitor.opentelemetry.exporter import AzureMonitorLogExporter

log_emitter_provider = LogEmitterProvider()
set_log_emitter_provider(log_emitter_provider)

exporter = AzureMonitorLogExporter.from_connection_string(
    os.environ["APPLICATIONINSIGHTS_CONNECTION_STRING"]
)

log_emitter_provider.add_log_processor(BatchLogProcessor(exporter))
handler = OTLPHandler()

# Attach OTel handler to namespaced logger
logger = logging.getLogger(__name__)
logger.addHandler(handler)
logger.setLevel(logging.NOTSET)

try:
    val = 1 / 0
    print(val)
except ZeroDivisionError:
    logger.exception("Error: Division by zero")
