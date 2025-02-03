# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

"""Contains functionality for sending telemetry to Application Insights via OpenCensus Azure Monitor Exporter."""

import logging
import platform
from typing import Any

from azure.ai.ml._user_agent import USER_AGENT

# Disable internal azure monitor openTelemetry logs
AZURE_MONITOR_OPENTELEMETRY_LOGGER_NAMESPACE = "azure.monitor.opentelemetry"
logging.getLogger(AZURE_MONITOR_OPENTELEMETRY_LOGGER_NAMESPACE).addHandler(logging.NullHandler())

AML_INTERNAL_LOGGER_NAMESPACE = "azure.ai.ml._telemetry"
CONNECTION_STRING = (
    "InstrumentationKey=71b954a8-6b7d-43f5-986c-3d3a6605d803;"
    "IngestionEndpoint=https://westus2-0.in.applicationinsights.azure.com/;"
    "LiveEndpoint=https://westus2.livediagnostics.monitor.azure.com/;"
    "ApplicationId=82daf08e-6a78-455f-9ce1-9396a8b5128b"
)

test_subscriptions = [
    "b17253fa-f327-42d6-9686-f3e553e24763",
    "test_subscription",
    "6560575d-fa06-4e7d-95fb-f962e74efd7a",
    "b17253fa-f327-42d6-9686-f3e553e2452",
    "74eccef0-4b8d-4f83-b5f9-fa100d155b22",
    "4faaaf21-663f-4391-96fd-47197c630979",
    "00000000-0000-0000-0000-000000000",
]


class CustomDimensionsFilter(logging.Filter):
    """Add application-wide properties to log record"""

    def __init__(self, custom_dimensions=None):  # pylint: disable=super-init-not-called
        self.custom_dimensions = custom_dimensions or {}

    def filter(self, record: dict) -> bool:  # type: ignore[override]
        """Adds the default custom_dimensions into the current log record. Does not
        otherwise filter any records

        :param record: The record
        :type record: dict
        :return: True
        :rtype: bool
        """

        custom_dimensions = self.custom_dimensions.copy()
        if isinstance(custom_dimensions, dict):
            record.__dict__.update(custom_dimensions)
        return True


def in_jupyter_notebook() -> bool:
    """Checks if user is using a Jupyter Notebook. This is necessary because logging is not allowed in
    non-Jupyter contexts.

    Adapted from https://stackoverflow.com/a/22424821

    :return: Whether is running in a Jupyter Notebook
    :rtype: bool
    """
    try:  # cspell:ignore ipython
        from IPython import get_ipython

        if "IPKernelApp" not in get_ipython().config:
            return False
    except ImportError:
        return False
    except AttributeError:
        return False
    return True


def setup_azure_monitor(connection_string=None) -> None:
    """
    Set up Azure Monitor distro.

    This function sets up Azure Monitor using the provided connection string and specified logger name.

    :param connection_string: The Application Insights connection string.
    :type connection_string: str
    :return: None
    """
    # Dynamically import the azure.monitor.opentelemetry module to avoid dependency issues later on CLI
    from azure.monitor.opentelemetry import configure_azure_monitor

    configure_azure_monitor(
        connection_string=connection_string,
        logger_name=AML_INTERNAL_LOGGER_NAMESPACE,
    )


# cspell:ignore overriden
def configure_appinsights_logging(
    user_agent,
    connection_string=None,
    enable_telemetry=True,
    **kwargs: Any,
) -> None:
    """Set the Opentelemetry logging distro for specified logger and connection string to send info to AppInsights.

    :param user_agent: Information about the user's browser.
    :type user_agent: Dict[str, str]
    :param connection_string: The Application Insights connection string.
    :type connection_string: str
    :param enable_telemetry: Whether to enable telemetry. Will be overriden to False if not in a Jupyter Notebook.
    :type enable_telemetry: bool
    :return: None
    """
    try:
        if connection_string is None:
            connection_string = CONNECTION_STRING

        logger = logging.getLogger(AML_INTERNAL_LOGGER_NAMESPACE)
        logger.setLevel(logging.INFO)
        logger.propagate = False

        if (
            not in_jupyter_notebook()
            or not enable_telemetry
            or not user_agent
            or not user_agent.lower() == USER_AGENT.lower()
        ):
            # Disable logging for this logger, all the child loggers will inherit this setting
            logger.addHandler(logging.NullHandler())
            return

        if kwargs:
            if "properties" in kwargs and "subscription_id" in kwargs.get("properties"):  # type: ignore[operator]
                if kwargs.get("properties")["subscription_id"] in test_subscriptions:  # type: ignore[index]
                    logger.addHandler(logging.NullHandler())
                    return

        custom_properties = {"PythonVersion": platform.python_version()}
        custom_properties.update({"user_agent": user_agent})
        if "properties" in kwargs:
            custom_properties.update(kwargs.pop("properties"))

        logger.addFilter(CustomDimensionsFilter(custom_properties))

        setup_azure_monitor(connection_string)

    except Exception:  # pylint: disable=W0718
        # ignore any exceptions, telemetry collection errors shouldn't block an operation
        return
