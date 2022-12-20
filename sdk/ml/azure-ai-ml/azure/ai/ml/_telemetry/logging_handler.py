# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

# pylint: disable=protected-access

"""Contains functionality for sending telemetry to Application Insights via OpenCensus Azure Monitor Exporter."""

import logging

# import platform
from os import getenv

# from opencensus.ext.azure.log_exporter import AzureLogHandler

# from azure.ai.ml._user_agent import USER_AGENT


AML_INTERNAL_LOGGER_NAMESPACE = "azure.ai.ml._telemetry"

# vienna-sdk-unitedstates
INSTRUMENTATION_KEY = "71b954a8-6b7d-43f5-986c-3d3a6605d803"

AZUREML_SDKV2_TELEMETRY_OPTOUT_ENV_VAR = "AZUREML_SDKV2_TELEMETRY_OPTOUT"

# application insight logger name
LOGGER_NAME = "ApplicationInsightLogger"

SUCCESS = True
FAILURE = False

TRACEBACK_LOOKUP_STR = "Traceback (most recent call last)"

# extract traceback path from message
reformat_traceback = True

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
    """Add application-wide properties to AzureLogHandler records"""

    def __init__(self, custom_dimensions=None):  # pylint: disable=super-init-not-called
        self.custom_dimensions = custom_dimensions or {}

    def filter(self, record):
        """Adds the default custom_dimensions into the current log record"""
        custom_dimensions = self.custom_dimensions.copy()
        custom_dimensions.update(getattr(record, "custom_dimensions", {}))
        record.custom_dimensions = custom_dimensions

        return True


def in_jupyter_notebook() -> bool:
    """
    Checks if user is using a Jupyter Notebook. This is necessary because logging is not allowed in
    non-Jupyter contexts.

    Adapted from https://stackoverflow.com/a/22424821
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


def is_telemetry_collection_disabled():
    telemetry_disabled = getenv(AZUREML_SDKV2_TELEMETRY_OPTOUT_ENV_VAR)
    if telemetry_disabled and (telemetry_disabled.lower() == "true" or telemetry_disabled == "1"):
        return True
    if not in_jupyter_notebook:
        return True
    return False


# def get_appinsights_log_handler(
#      user_agent,
#      *args, # pylint: disable=unused-argument
#      instrumentation_key=None,
#      component_name=None,
#      **kwargs
#  ):
#     """Enable the OpenCensus logging handler for specified logger and instrumentation key to send info to AppInsights.

#     :param user_agent: Information about the user's browser.
#     :type user_agent: Dict[str, str]
#     :param instrumentation_key: The Application Insights instrumentation key.
#     :type instrumentation_key: str
#     :param component_name: The component name.
#     :type component_name: str
#     :param args: Optional arguments for formatting messages.
#     :type args: list
#     :param kwargs: Optional keyword arguments for adding additional information to messages.
#     :type kwargs: dict
#     :return: The logging handler.
#     :rtype: opencensus.ext.azure.log_exporter.AzureLogHandler
#     """
#     try:
#         if instrumentation_key is None:
#             instrumentation_key = INSTRUMENTATION_KEY

#     if is_telemetry_collection_disabled():
#         return logging.NullHandler()

#     if not user_agent or not user_agent.lower() == USER_AGENT.lower():
#         return logging.NullHandler()

#     if "properties" in kwargs and "subscription_id" in kwargs.get("properties"):
#         if kwargs.get("properties")["subscription_id"] in test_subscriptions:
#             return logging.NullHandler()

#     child_namespace = component_name or __name__
#     current_logger = logging.getLogger(AML_INTERNAL_LOGGER_NAMESPACE).getChild(child_namespace)
#     current_logger.propagate = False
#     current_logger.setLevel(logging.CRITICAL)

#     custom_properties = {"PythonVersion": platform.python_version()}
#     custom_properties.update({"user_agent": user_agent})
#     if "properties" in kwargs:
#         custom_properties.update(kwargs.pop("properties"))
#     handler = AzureLogHandler(connection_string=f'InstrumentationKey={instrumentation_key}')
#     current_logger.addHandler(handler)
#     handler.addFilter(CustomDimensionsFilter(custom_properties))

#     return handler
# except Exception: # pylint: disable=broad-except
#     # ignore exceptions, telemetry should not block
#     return logging.NullHandler()
