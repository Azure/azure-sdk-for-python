# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

# pylint: disable=protected-access

"""Contains functionality for sending telemetry to Application Insights via OpenCensus Azure Monitor Exporter."""

import logging
import platform
import traceback

from opencensus.ext.azure.log_exporter import AzureLogHandler
from opencensus.ext.azure.common import utils
from opencensus.ext.azure.common.protocol import (
    Data,
    ExceptionData,
    Message,
    Envelope,
)
from azure.ai.ml._user_agent import USER_AGENT


AML_INTERNAL_LOGGER_NAMESPACE = "azure.ai.ml._telemetry"

# vienna-sdk-unitedstates
INSTRUMENTATION_KEY = "71b954a8-6b7d-43f5-986c-3d3a6605d803"

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


# cspell:ignore overriden
def get_appinsights_log_handler(
    user_agent,
    *args,  # pylint: disable=unused-argument
    instrumentation_key=None,
    component_name=None,
    enable_telemetry=True,
    **kwargs,
):
    """Enable the OpenCensus logging handler for specified logger and instrumentation key to send info to AppInsights.

    :param user_agent: Information about the user's browser.
    :type user_agent: Dict[str, str]
    :param instrumentation_key: The Application Insights instrumentation key.
    :type instrumentation_key: str
    :param component_name: The component name.
    :type component_name: str
    :param enable_telemetry: Whether to enable telemetry. Will be overriden to False if not in a Jupyter Notebook.
    :type enable_telemetry: bool
    :param args: Optional arguments for formatting messages.
    :type args: list
    :param kwargs: Optional keyword arguments for adding additional information to messages.
    :type kwargs: dict
    :return: The logging handler.
    :rtype: AzureMLSDKLogHandler
    """
    try:
        if instrumentation_key is None:
            instrumentation_key = INSTRUMENTATION_KEY

        if not in_jupyter_notebook() or not enable_telemetry:
            return logging.NullHandler()

        if not user_agent or not user_agent.lower() == USER_AGENT.lower():
            return logging.NullHandler()

        if "properties" in kwargs and "subscription_id" in kwargs.get("properties"):
            if kwargs.get("properties")["subscription_id"] in test_subscriptions:
                return logging.NullHandler()

        child_namespace = component_name or __name__
        current_logger = logging.getLogger(AML_INTERNAL_LOGGER_NAMESPACE).getChild(child_namespace)
        current_logger.propagate = False
        current_logger.setLevel(logging.CRITICAL)

        custom_properties = {"PythonVersion": platform.python_version()}
        custom_properties.update({"user_agent": user_agent})
        if "properties" in kwargs:
            custom_properties.update(kwargs.pop("properties"))
        handler = AzureMLSDKLogHandler(
            connection_string=f"InstrumentationKey={instrumentation_key}",
            custom_properties=custom_properties,
            enable_telemetry=enable_telemetry,
        )
        current_logger.addHandler(handler)

        return handler
    except Exception:  # pylint: disable=broad-except
        # ignore any exceptions, telemetry collection errors shouldn't block an operation
        return logging.NullHandler()


# cspell:ignore AzureMLSDKLogHandler
class AzureMLSDKLogHandler(AzureLogHandler):
    """Customized AzureLogHandler for AzureML SDK"""

    def __init__(self, custom_properties, enable_telemetry, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self._is_telemetry_collection_disabled = not enable_telemetry
        self._custom_properties = custom_properties
        self.addFilter(CustomDimensionsFilter(self._custom_properties))

    def emit(self, record):
        if self._is_telemetry_collection_disabled:
            return

        try:
            self._queue.put(record, block=False)

            # log the record immediately if it is an error
            if record.exc_info and not all(item is None for item in record.exc_info):
                self._queue.flush()
        except Exception:  # pylint: disable=broad-except
            # ignore any exceptions, telemetry collection errors shouldn't block an operation
            return

    # The code below is vendored from opencensus-ext-azure's AzureLogHandler base class, but the telemetry disabling
    # logic has been added to the beginning. Without this, the base class would still send telemetry even if
    # enable_telemetry had been set to true.
    def log_record_to_envelope(self, record):
        if self._is_telemetry_collection_disabled:
            return

        envelope = create_envelope(self.options.instrumentation_key, record)

        properties = {
            "process": record.processName,
            "module": record.module,
            "level": record.levelname,
        }
        if hasattr(record, "custom_dimensions") and isinstance(record.custom_dimensions, dict):
            properties.update(record.custom_dimensions)

        if record.exc_info:
            exctype, _value, tb = record.exc_info
            callstack = []
            level = 0
            has_full_stack = False
            exc_type = "N/A"
            message = self.format(record)
            if tb is not None:
                has_full_stack = True
                for _, line, method, _text in traceback.extract_tb(tb):
                    callstack.append(
                        {
                            "level": level,
                            "method": method,
                            "line": line,
                        }
                    )
                    level += 1
                callstack.reverse()
            elif record.message:
                message = record.message

            if exctype is not None:
                exc_type = exctype.__name__

            envelope.name = "Microsoft.ApplicationInsights.Exception"

            data = ExceptionData(
                exceptions=[
                    {
                        "id": 1,
                        "outerId": 0,
                        "typeName": exc_type,
                        "message": message,
                        "hasFullStack": has_full_stack,
                        "parsedStack": callstack,
                    }
                ],
                severityLevel=max(0, record.levelno - 1) // 10,
                properties=properties,
            )
            envelope.data = Data(baseData=data, baseType="ExceptionData")
        else:
            envelope.name = "Microsoft.ApplicationInsights.Message"
            data = Message(
                message=self.format(record),
                severityLevel=max(0, record.levelno - 1) // 10,
                properties=properties,
            )
            envelope.data = Data(baseData=data, baseType="MessageData")
        return envelope


def create_envelope(instrumentation_key, record):
    envelope = Envelope(
        iKey=instrumentation_key,
        tags=dict(utils.azure_monitor_context),
        time=utils.timestamp_to_iso_str(record.created),
    )
    envelope.tags["ai.operation.id"] = getattr(
        record,
        "traceId",
        "00000000000000000000000000000000",
    )
    envelope.tags["ai.operation.parentId"] = "|{}.{}.".format(
        envelope.tags["ai.operation.id"],
        getattr(record, "spanId", "0000000000000000"),
    )

    return envelope
