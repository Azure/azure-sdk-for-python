# pylint: disable=broad-exception-caught,dangerous-default-value
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
    """
    Build default log config with level from environment.
    
    :return: A dictionary containing logging configuration.
    :rtype: dict
    """
    log_level = get_log_level()
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


def get_log_level():
    log_level = os.getenv(Constants.AGENT_LOG_LEVEL, "INFO").upper()
    valid_levels = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
    if log_level not in valid_levels:
        print(f"Invalid log level '{log_level}' specified. Defaulting to 'INFO'.")
        log_level = "INFO"
    return log_level


request_context = contextvars.ContextVar("request_context", default=None)

APPINSIGHT_CONNSTR_ENV_NAME = "APPLICATIONINSIGHTS_CONNECTION_STRING"


def get_dimensions():
    env_values = {name: value for name, value in vars(Constants).items() if not name.startswith("_")}
    res = {"azure.ai.agentserver.version": VERSION}
    for name, env_name in env_values.items():
        if isinstance(env_name, str) and not env_name.startswith("_"):
            runtime_value = os.environ.get(env_name)
            if runtime_value:
                res[f"azure.ai.agentserver.{name.lower()}"] = runtime_value
    return res


def get_project_endpoint(logger=None):
    project_endpoint = os.environ.get(Constants.AZURE_AI_PROJECT_ENDPOINT)
    if project_endpoint:
        if logger:
            logger.info(f"Using project endpoint from {Constants.AZURE_AI_PROJECT_ENDPOINT}: {project_endpoint}")
        return project_endpoint
    project_resource_id = os.environ.get(Constants.AGENT_PROJECT_RESOURCE_ID)
    if project_resource_id:
        last_part = project_resource_id.split("/")[-1]

        parts = last_part.split("@")
        if len(parts) < 2:
            if logger:
                logger.warning(f"Invalid project resource id format: {project_resource_id}")
            return None
        account = parts[0]
        project = parts[1]
        endpoint = f"https://{account}.services.ai.azure.com/api/projects/{project}"
        if logger:
            logger.info(f"Using project endpoint derived from {Constants.AGENT_PROJECT_RESOURCE_ID}: {endpoint}")
        return endpoint
    return None


def get_application_insights_connstr(logger=None):
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
                    logger.info(f"No Application Insights connection found for project: {project_endpoint}")
                elif conn_str:
                    os.environ[APPINSIGHT_CONNSTR_ENV_NAME] = conn_str
            elif logger:
                logger.info("Application Insights not configured, telemetry export disabled.")
        return conn_str
    except Exception as e:
        if logger:
            logger.warning(f"Failed to get Application Insights connection string, telemetry export disabled: {e}")
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

        application_insights_connection_string = get_application_insights_connstr(logger=app_logger)
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
            app_logger.setLevel(get_log_level())
            app_logger.addHandler(handler)

    except Exception as e:
        print(f"Failed to configure logging: {e}")


def get_logger() -> logging.Logger:
    """
    If the logger is not already configured, it will be initialized with default settings.

    :return: Configured logger instance.
    :rtype: logging.Logger
    """
    return logging.getLogger("azure.ai.agentserver")
