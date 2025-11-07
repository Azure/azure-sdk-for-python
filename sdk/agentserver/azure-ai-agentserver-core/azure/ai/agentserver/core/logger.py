# pylint: disable=broad-exception-caught,dangerous-default-value
# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
import contextvars
import logging
import os
from logging import config

from ._version import VERSION
from .constants import Constants

default_log_config = {
    "version": 1,
    "disable_existing_loggers": False,
    "loggers": {
        "azure.ai.agentserver": {
            "handlers": ["console"],
            "level": "INFO",
            "propagate": False,
        },
    },
    "handlers": {
        "console": {"formatter": "std_out", "class": "logging.StreamHandler", "level": "INFO"},
    },
    "formatters": {"std_out": {"format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s"}},
}

request_context = contextvars.ContextVar("request_context", default=None)

_APPLICATIONINSIGHTS_CONNECTION_STRING = "APPLICATIONINSIGHTS_CONNECTION_STRING"


def get_dimensions():
    env_values = {name: value for name, value in vars(Constants).items() if not name.startswith("_")}
    res = {"azure.ai.agentserver.version": VERSION}
    for name, env_name in env_values.items():
        if isinstance(env_name, str) and not env_name.startswith("_"):
            runtime_value = os.environ.get(env_name)
            if runtime_value:
                res[f"azure.ai.agentserver.{name.lower()}"] = runtime_value
    return res


def get_project_endpoint():
    project_resource_id = os.environ.get(Constants.AGENT_PROJECT_RESOURCE_ID)
    if project_resource_id:
        last_part = project_resource_id.split("/")[-1]

        parts = last_part.split("@")
        if len(parts) < 2:
            print(f"invalid project resource id: {project_resource_id}")
            return None
        account = parts[0]
        project = parts[1]
        return f"https://{account}.services.ai.azure.com/api/projects/{project}"
    print("environment variable AGENT_PROJECT_RESOURCE_ID not set.")
    return None


def get_application_insights_connstr():
    try:
        conn_str = os.environ.get(_APPLICATIONINSIGHTS_CONNECTION_STRING)
        if not conn_str:
            print("environment variable APPLICATIONINSIGHTS_CONNECTION_STRING not set.")
            project_endpoint = get_project_endpoint()
            if project_endpoint:
                # try to get the project connected application insights
                from azure.ai.projects import AIProjectClient
                from azure.identity import DefaultAzureCredential

                project_client = AIProjectClient(credential=DefaultAzureCredential(), endpoint=project_endpoint)
                conn_str = project_client.telemetry.get_application_insights_connection_string()
                if not conn_str:
                    print(f"no connected application insights found for project:{project_endpoint}")
                else:
                    os.environ[_APPLICATIONINSIGHTS_CONNECTION_STRING] = conn_str
        return conn_str
    except Exception as e:
        print(f"failed to get application insights with error: {e}")
        return None


class CustomDimensionsFilter(logging.Filter):
    def filter(self, record):
        # Add custom dimensions to every log record
        dimensions = get_dimensions()
        for key, value in dimensions.items():
            setattr(record, key, value)
        cur_request_context = request_context.get()
        if cur_request_context:
            for key, value in cur_request_context.items():
                setattr(record, key, value)
        return True


def configure(log_config: dict = default_log_config):
    """
    Configure logging based on the provided configuration dictionary.
    The dictionary should contain the logging configuration in a format compatible with `logging.config.dictConfig`.

    :param log_config: A dictionary containing logging configuration.
    :type log_config: dict
    """
    try:
        config.dictConfig(log_config)

        application_insights_connection_string = get_application_insights_connstr()
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
            app_logger = logging.getLogger("azure.ai.agentserver")
            app_logger.setLevel(get_log_level())
            app_logger.addHandler(handler)

    except Exception as e:
        print(f"Failed to configure logging: {e}")


def get_log_level():
    log_level = os.getenv(Constants.AGENT_LOG_LEVEL, "INFO").upper()
    valid_levels = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
    if log_level not in valid_levels:
        print(f"Invalid log level '{log_level}' specified. Defaulting to 'INFO'.")
        log_level = "INFO"
    return log_level


def get_logger() -> logging.Logger:
    """
    If the logger is not already configured, it will be initialized with default settings.

    :return: Configured logger instance.
    :rtype: logging.Logger
    """
    return logging.getLogger("azure.ai.agentserver")
