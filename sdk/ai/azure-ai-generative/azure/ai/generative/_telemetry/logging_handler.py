# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

# pylint: disable=protected-access

"""Contains functionality for sending telemetry to Application Insights via OpenCensus Azure Monitor Exporter."""

import logging
import platform
import traceback
from typing import Union, Dict
import os

from opencensus.ext.azure.log_exporter import AzureLogHandler
from opencensus.ext.azure.common import utils
from opencensus.ext.azure.common.protocol import (
    Data,
    ExceptionData,
    Message,
    Envelope,
)
from opencensus.trace import config_integration

from azure.ai.ml._telemetry.logging_handler import in_jupyter_notebook, CustomDimensionsFilter, INSTRUMENTATION_KEY

from azure.ai.generative._user_agent import USER_AGENT

GEN_AI_INTERNAL_LOGGER_NAMESPACE = "azure.ai.generative._telemetry"

test_subscriptions = [
    "b17253fa-f327-42d6-9686-f3e553e24763",
    "test_subscription",
    "6560575d-fa06-4e7d-95fb-f962e74efd7a",
    "74eccef0-4b8d-4f83-b5f9-fa100d155b22",
    "4faaaf21-663f-4391-96fd-47197c630979",
    "00000000-0000-0000-0000-000000000",
]

# activate operation id tracking
config_integration.trace_integrations(["logging"])


class ActivityLogger:
    def __init__(self, name: str):
        self.package_logger: logging.Logger = logging.getLogger(GEN_AI_INTERNAL_LOGGER_NAMESPACE + name)
        self.package_logger.propagate = False
        self.module_logger = logging.getLogger(name)
        self.custom_dimensions: Dict[str, Union[str, Dict]] = {}

    def update_info(self) -> None:
        self.package_logger.addHandler(get_appinsights_log_handler(USER_AGENT))


# cspell:ignore overriden
def get_appinsights_log_handler(
    user_agent,
    *args,  # pylint: disable=unused-argument
    instrumentation_key=None,
    component_name=None,
    **kwargs,
):
    """Enable the OpenCensus logging handler for specified logger and instrumentation key to send info to AppInsights.

    :param user_agent: Information about the user's browser.
    :type user_agent: Dict[str, str]
    :param args: Optional arguments for formatting messages.
    :type args: list
    :keyword instrumentation_key: The Application Insights instrumentation key.
    :paramtype instrumentation_key: str
    :keyword component_name: The component name.
    :paramtype component_name: str
    :keyword kwargs: Optional keyword arguments for adding additional information to messages.
    :paramtype kwargs: dict
    :return: The logging handler.
    :rtype: AzureGenAILogHandler
    """
    try:
        if instrumentation_key is None:
            instrumentation_key = INSTRUMENTATION_KEY

        enable_telemetry = os.getenv("AZURE_AI_GENERATIVE_ENABLE_LOGGING", "True")
        if enable_telemetry == "True":
            os.environ["AZURE_AI_RESOURCES_ENABLE_LOGGING"] = "True"
        if not in_jupyter_notebook() or enable_telemetry == "False":
            return logging.NullHandler()

        if not user_agent or not any(
            name in user_agent.lower() for name in ["azure-ai-generative", "azure-ai-resources"]
        ):
            return logging.NullHandler()

        if "properties" in kwargs and "subscription_id" in kwargs.get("properties"):
            if kwargs.get("properties")["subscription_id"] in test_subscriptions:
                return logging.NullHandler()

        child_namespace = component_name or __name__
        current_logger = logging.getLogger(GEN_AI_INTERNAL_LOGGER_NAMESPACE).getChild(child_namespace)
        current_logger.propagate = False
        current_logger.setLevel(logging.CRITICAL)

        custom_properties = {"PythonVersion": platform.python_version()}
        custom_properties.update({"user_agent": user_agent})
        if "properties" in kwargs:
            custom_properties.update(kwargs.pop("properties"))
        handler = AzureGenAILogHandler(
            connection_string=f"InstrumentationKey={instrumentation_key}",
            custom_properties=custom_properties,
            enable_telemetry=enable_telemetry,
        )
        current_logger.addHandler(handler)
        return handler
    except Exception:  # pylint: disable=broad-except
        # swallow any exceptions, telemetry collection errors shouldn't block an operation
        return logging.NullHandler()


# cspell:ignore AzureMLSDKLogHandler
class AzureGenAILogHandler(AzureLogHandler):
    """Customized AzureLogHandler for Azure Gen AI SDK"""

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
            return None

        envelope = create_envelope(self.options.instrumentation_key, record)

        properties = {
            "process": record.processName,
            "module": record.module,
            "level": record.levelname,
            "operation_id": envelope.tags.get("ai.generative.operation.id"),
            "operation_parent_id": envelope.tags.get("ai.generative.operation.parentId"),
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
    envelope.tags["ai.generative.operation.id"] = getattr(
        record,
        "traceId",
        "00000000000000000000000000000000",
    )
    envelope.tags[
        "ai.generative.operation.parentId"
    ] = f"|{envelope.tags.get('ai.generative.operation.id')}.{getattr(record, 'spanId', '0000000000000000')}"

    return envelope
