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

from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor

from azure.monitor.opentelemetry.exporter import AzureMonitorTraceExporter

class CustomFilter(logging.Filter):

    def filter(self, record):
        if hasattr(record, "ignore"):
            return False
        return True


class LogHandler:
    def __init__(
        self,
        app_name: str,
        app_version: str,
        **kwargs,
    ):
        """_summary_

        Args:
            app_name: app name
            app_version: app version
            kwargs Additional logging parameters
        """
        self.app_name = app_name
        self.app_version = app_version
        self.kwargs = kwargs

        # Create the logging provider
        self.logger_provider = LoggerProvider()
        set_logger_provider(self.logger_provider)
        exporter = AzureMonitorLogExporter(
            connection_string=os.environ["APPLICATIONINSIGHTS_CONNECTION_STRING"],
        )
        self.logger_provider.add_log_record_processor(BatchLogRecordProcessor(exporter))

        # Create the logging handler
        self.handler = LoggingHandler()

        # Attach LoggingHandler to root logger
        self._logger = logging.getLogger(self.app_name)
        self._logger.addHandler(self.handler)
        self._logger.addFilter(CustomFilter())
        self._logger.setLevel(logging.INFO)

log_handler = LogHandler(app_name='app-name', app_version=1.0)
logger = log_handler._logger


exporter = AzureMonitorTraceExporter.from_connection_string(
    os.environ["APPLICATIONINSIGHTS_CONNECTION_STRING"]
)

tracer_provider = TracerProvider()
trace.set_tracer_provider(tracer_provider)
tracer = trace.get_tracer(__name__)
span_processor = BatchSpanProcessor(exporter, schedule_delay_millis=60000)
trace.get_tracer_provider().add_span_processor(span_processor)

with tracer.start_as_current_span(name="my-application") as application_span:
    logger.info("test logs message")
    logger.info("test ignore message", extra={"ignore": "true"})
    logger.exception("test exception message")

input()