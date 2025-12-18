# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License in the project root for
# license information.
# --------------------------------------------------------------------------

import logging
from logging import getLogger
from azure.monitor.opentelemetry import configure_azure_monitor
from azure.monitor.opentelemetry.exporter._generated.models import ContextTagKeys
from opentelemetry import trace
from opentelemetry.sdk._logs import LogRecordProcessor, ReadableLogRecord

logger = getLogger(__name__)
logger.setLevel(logging.INFO)


class LogRecordEnrichingProcessor(LogRecordProcessor):
    """Enriches log records with operation name from the current span context."""

    def on_emit(self, readable_log_record: ReadableLogRecord) -> None:
        current_span = trace.get_current_span()
        if current_span and getattr(current_span, 'name', None):
            if readable_log_record.log_record.attributes is None:
                readable_log_record.log_record.attributes = {}
            readable_log_record.log_record.attributes[ContextTagKeys.AI_OPERATION_NAME] = current_span.name

    def shutdown(self) -> None:
        pass

    def force_flush(self, timeout_millis: int = 30000) -> bool:
        return True

# Create the log record enriching processor
log_enriching_processor = LogRecordEnrichingProcessor()

# Configure Azure Monitor with the custom log record processor
configure_azure_monitor(
    log_record_processors=[log_enriching_processor]
)

tracer = trace.get_tracer(__name__)

with tracer.start_as_current_span("span-name-here"):
    logger.info("This log will be enriched with operation name")

input()