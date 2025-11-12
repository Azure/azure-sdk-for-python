# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License in the project root for
# license information.
# --------------------------------------------------------------------------

import logging
from logging import getLogger
from azure.monitor.opentelemetry import configure_azure_monitor
from opentelemetry import trace
from opentelemetry.sdk._logs import LogRecordProcessor, LogData
from azure.monitor.opentelemetry.exporter._generated.models import ContextTagKeys

logger = getLogger(__name__)
logger.setLevel(logging.INFO)



class LogRecordEnrichingProcessor(LogRecordProcessor):
    """
    A log record processor that enriches log records with operation name
    from the current span context.
    """
    
    def force_flush(self, timeout_millis: int = 30000) -> bool:
        """Force flush any pending log records."""
        return True
    
    def shutdown(self) -> None:
        """Shutdown the processor."""
        pass
    
    def on_emit(self, log_data: LogData) -> None:
        """
        Enrich the log record with operation name from the current span.
        
        Args:
            log_data: The log data containing log record and context information
        """
        # Get the current span from the current context (not from trace_context which might be None)
        current_span = trace.get_current_span()
        
        if current_span and hasattr(current_span, 'name') and current_span.name:
            # Add the operation name to log record attributes
            if log_data.log_record.attributes is None:
                log_data.log_record.attributes = {}
            log_data.log_record.attributes[ContextTagKeys.AI_OPERATION_NAME] = current_span.name


# Create the log record enriching processor
log_enriching_processor = LogRecordEnrichingProcessor()

# Configure Azure Monitor with the custom log record processor
configure_azure_monitor(
    log_record_processors=[log_enriching_processor]
)

# Your application code here
tracer = trace.get_tracer(__name__)

with tracer.start_as_current_span("span-name-here"):
    logger.info("This log will be enriched with operation name")

input()