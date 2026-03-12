# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
import contextvars
import logging
import os
from logging import config
from typing import Any, Optional

from ._version import VERSION
from .constants import Constants

def _get_default_log_config() -> dict[str, Any]:
    """Build default log config with level from environment.

    :return: A dictionary containing logging configuration.
    :rtype: dict[str, Any]
    """
    log_level = _get_log_level()
    return {
        "version": 1,
        "disable_existing_loggers": False,
        "loggers": {
            "azure.ai.agentserver": {
                "handlers": ["console"],
                "level": log_level,
                "propagate": False,
            },
        },
        "handlers": {
            "console": {
                "formatter": "std_out", 
                "class": "logging.StreamHandler", 
                "stream": "ext://sys.stdout", 
                "level": log_level},
        },
        "formatters": {"std_out": {"format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s"}},
    }


def _get_log_level() -> str:
    """Read log level from the ``AGENT_LOG_LEVEL`` environment variable.

    Falls back to ``"INFO"`` if the variable is unset or contains an invalid value.

    :return: A valid Python logging level name.
    :rtype: str
    """
    log_level = os.getenv(Constants.AGENT_LOG_LEVEL, "INFO").upper()
    valid_levels = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
    if log_level not in valid_levels:
        print(f"Invalid log level '{log_level}' specified. Defaulting to 'INFO'.")
        log_level = "INFO"
    return log_level


request_context = contextvars.ContextVar("request_context", default=None)

APPINSIGHT_CONNSTR_ENV_NAME = "APPLICATIONINSIGHTS_CONNECTION_STRING"


def _get_dimensions() -> dict[str, str]:
    """Collect environment-based dimensions for structured logging.

    :return: A mapping of dimension keys to their runtime values.
    :rtype: dict[str, str]
    """
    env_values = {name: value for name, value in vars(Constants).items() if not name.startswith("_")}
    res = {"azure.ai.agentserver.version": VERSION}
    for name, env_name in env_values.items():
        if isinstance(env_name, str) and not env_name.startswith("_"):
            runtime_value = os.environ.get(env_name)
            if runtime_value:
                res[f"azure.ai.agentserver.{name.lower()}"] = runtime_value
    return res


def get_project_endpoint(logger: Optional[logging.Logger] = None) -> Optional[str]:
    """Resolve the project endpoint from environment variables.

    Checks ``AZURE_AI_PROJECT_ENDPOINT`` first, then falls back to deriving
    an endpoint from ``AGENT_PROJECT_NAME``.

    :param logger: Optional logger for diagnostic messages.
    :type logger: Optional[logging.Logger]
    :return: The resolved project endpoint URL, or ``None`` if unavailable.
    :rtype: Optional[str]
    """
    project_endpoint = os.environ.get(Constants.AZURE_AI_PROJECT_ENDPOINT)
    if project_endpoint:
        if logger:
            logger.info(
                "Using project endpoint from %s: %s",
                Constants.AZURE_AI_PROJECT_ENDPOINT,
                project_endpoint,
            )
        return project_endpoint
    project_resource_id = os.environ.get(Constants.AGENT_PROJECT_RESOURCE_ID)
    if project_resource_id:
        last_part = project_resource_id.split("/")[-1]

        parts = last_part.split("@")
        if len(parts) < 2:
            if logger:
                logger.warning("Invalid project resource id format: %s", project_resource_id)
            return None
        account = parts[0]
        project = parts[1]
        endpoint = f"https://{account}.services.ai.azure.com/api/projects/{project}"
        if logger:
            logger.info(
                "Using project endpoint derived from %s: %s",
                Constants.AGENT_PROJECT_RESOURCE_ID,
                endpoint,
            )
        return endpoint
    return None


def _get_application_insights_connstr(logger: Optional[logging.Logger] = None) -> Optional[str]:
    """Retrieve or derive the Application Insights connection string.

    Looks in the ``APPLICATIONINSIGHTS_CONNECTION_STRING`` environment variable first,
    then attempts to fetch it from the project endpoint.

    :param logger: Optional logger for diagnostic messages.
    :type logger: Optional[logging.Logger]
    :return: The connection string, or ``None`` if unavailable.
    :rtype: Optional[str]
    """
    try:
        conn_str = os.environ.get(APPINSIGHT_CONNSTR_ENV_NAME)
        if not conn_str:
            project_endpoint = get_project_endpoint(logger=logger)
            if project_endpoint:
                # try to get the project connected application insights
                from azure.ai.projects import AIProjectClient
                from azure.identity import DefaultAzureCredential
                project_client = AIProjectClient(credential=DefaultAzureCredential(), endpoint=project_endpoint)
                conn_str = project_client.telemetry.get_application_insights_connection_string()
                if not conn_str and logger:
                    logger.info(
                        "No Application Insights connection found for project: %s",
                        project_endpoint,
                    )
                elif conn_str:
                    os.environ[APPINSIGHT_CONNSTR_ENV_NAME] = conn_str
            elif logger:
                logger.info("Application Insights not configured, telemetry export disabled.")
        return conn_str
    except Exception as e:  # pylint: disable=broad-exception-caught  # bootstrap: many failure modes possible
        if logger:
            logger.warning(
                "Failed to get Application Insights connection string, telemetry export disabled: %s",
                e,
            )
        return None


class CustomDimensionsFilter(logging.Filter):
    """Logging filter that attaches environment dimensions and request context to log records."""

    def filter(self, record: logging.LogRecord) -> bool:
        """Inject custom dimensions into *record* and allow it through.

        :param record: The log record to enrich.
        :type record: logging.LogRecord
        :return: Always ``True`` so the record is never discarded.
        :rtype: bool
        """
        dimensions = _get_dimensions()
        for key, value in dimensions.items():
            setattr(record, key, value)
        cur_request_context = request_context.get()
        if cur_request_context:
            for key, value in cur_request_context.items():
                setattr(record, key, value)
        return True


def configure(log_config: Optional[dict[str, Any]] = None):
    """
    Configure logging based on the provided configuration dictionary.
    The dictionary should contain the logging configuration in a format compatible with `logging.config.dictConfig`.

    :param log_config: A dictionary containing logging configuration. If None, uses default config with AGENT_LOG_LEVEL.
    :type log_config: Optional[dict[str, Any]]
    """
    try:
        if log_config is None:
            log_config = _get_default_log_config()
        config.dictConfig(log_config)
        app_logger = logging.getLogger("azure.ai.agentserver")

        application_insights_connection_string = _get_application_insights_connstr(logger=app_logger)
        enable_application_insights_logger = (
            os.environ.get(Constants.ENABLE_APPLICATION_INSIGHTS_LOGGER, "true").lower() == "true"
        )
        if application_insights_connection_string and enable_application_insights_logger:
            from opentelemetry._logs import set_logger_provider
            from opentelemetry.sdk._logs import (
                LoggerProvider,
                LoggingHandler,
            )
            from opentelemetry.sdk._logs.export import BatchLogRecordProcessor
            from opentelemetry.sdk.resources import Resource

            from azure.monitor.opentelemetry.exporter import AzureMonitorLogExporter

            logger_provider = LoggerProvider(resource=Resource.create({"service.name": "azure.ai.agentserver"}))
            set_logger_provider(logger_provider)

            exporter = AzureMonitorLogExporter(connection_string=application_insights_connection_string)

            logger_provider.add_log_record_processor(BatchLogRecordProcessor(exporter))
            handler = LoggingHandler(logger_provider=logger_provider)
            handler.name = "appinsights_handler"

            # Add custom filter to inject dimensions
            custom_filter = CustomDimensionsFilter()
            handler.addFilter(custom_filter)

            # Only add to azure.ai.agentserver namespace to avoid infrastructure logs
            app_logger.setLevel(_get_log_level())
            app_logger.addHandler(handler)

    except Exception as e:  # pylint: disable=broad-exception-caught
        print(f"Failed to configure logging: {e}")


def get_logger() -> logging.Logger:
    """
    If the logger is not already configured, it will be initialized with default settings.

    :return: Configured logger instance.
    :rtype: logging.Logger
    """
    return logging.getLogger("azure.ai.agentserver")
