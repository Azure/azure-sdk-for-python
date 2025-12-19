# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.
"""
An example to show an application using Opentelemetry logging sdk. Logging calls to the standard Python
logging library are tracked and telemetry is exported to application insights with the AzureMonitorLogExporter.
"""
# mypy: disable-error-code="attr-defined"

from logging import getLogger

from azure.monitor.opentelemetry import configure_azure_monitor
from opentelemetry import trace

configure_azure_monitor(
    logger_name=__name__,
)

logger = getLogger(__name__)

# You can send `customEvent`` telemetry using a special `microsoft` attribute key through logging
# The name of the `customEvent` will correspond to the value of the attribute`
logger.info(
    "Hello World!",
    extra={
        "microsoft.custom_event.name": "test-event-name",
        "additional_attrs": "val1",
    },
)

# You can also populate fields like client_Ip with attribute `client.address`
logger.info(
    "This entry will have a custom client_Ip",
    extra={
        "microsoft.custom_event.name": "test_event",
        "client.address": "192.168.1.1",
    },
)

input()
