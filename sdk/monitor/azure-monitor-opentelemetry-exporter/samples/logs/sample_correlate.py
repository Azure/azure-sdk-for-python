# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.
"""
An example to show an application using Opentelemetry logging sdk. Logging calls to the standard Python
logging library are tracked and telemetry is exported to application insights with the AzureMonitorLogExporter.
"""
import os
import logging

from opentelemetry import trace
from opentelemetry.sdk._logs import (
    LogEmitterProvider,
    OTLPHandler,
    set_log_emitter_provider,
)
from opentelemetry.sdk._logs.export import BatchLogProcessor
from opentelemetry.sdk.trace import TracerProvider

from azure.monitor.opentelemetry.exporter import AzureMonitorLogExporter

trace.set_tracer_provider(TracerProvider())
tracer = trace.get_tracer(__name__)
log_emitter_provider = LogEmitterProvider()
set_log_emitter_provider(LogEmitterProvider())

exporter = AzureMonitorLogExporter.from_connection_string(
    os.environ["APPLICATIONINSIGHTS_CONNECTION_STRING"]
)

log_emitter_provider.add_log_processor(BatchLogProcessor(exporter))
handler = OTLPHandler()

# Attach OTel handler to root logger
logging.getLogger().addHandler(handler)
logging.getLogger().setLevel(logging.NOTSET)

logger = logging.getLogger(__name__)

logger.info("INFO: Outside of span")
with tracer.start_as_current_span("foo"):
    logger.warning("WARNING: Inside of span")
logger.error("ERROR: After span")
