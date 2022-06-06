# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.
"""
An example showing how to include context correlation information in logging telemetry.
"""
import os
import logging

from opentelemetry import trace
from opentelemetry.sdk._logs import (
    LogEmitterProvider,
    LoggingHandler,
    get_log_emitter_provider,
    set_log_emitter_provider,
)
from opentelemetry.sdk._logs.export import BatchLogProcessor
from opentelemetry.sdk.trace import TracerProvider

from azure.monitor.opentelemetry.exporter import AzureMonitorLogExporter

trace.set_tracer_provider(TracerProvider())
tracer = trace.get_tracer(__name__)
set_log_emitter_provider(LogEmitterProvider())

exporter = AzureMonitorLogExporter.from_connection_string(
    os.environ["APPLICATIONINSIGHTS_CONNECTION_STRING"]
)
get_log_emitter_provider().add_log_processor(BatchLogProcessor(exporter))

# Attach LoggingHandler to namespaced logger
handler = LoggingHandler()
logger = logging.getLogger(__name__)
logger.addHandler(handler)
logger.setLevel(logging.NOTSET)

logger.info("INFO: Outside of span")
with tracer.start_as_current_span("foo"):
    logger.warning("WARNING: Inside of span")
logger.error("ERROR: After span")
