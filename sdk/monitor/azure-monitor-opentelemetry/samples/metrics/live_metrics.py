# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License in the project root for
# license information.
# --------------------------------------------------------------------------

"""
This example sets up a minimal example of sending dependency through live metrics,
trace and exception telemetry to demonstrate the capabilities and collection set of live metrics.
Live metrics is enabled by default, it can be disabled by setting `enable_live_metrics` to `False`
"""
import logging
import time
import requests  # type: ignore[import-untyped] # pylint: disable=networking-import-outside-azure-core-transport

from opentelemetry import trace
from opentelemetry.sdk.resources import Resource
from azure.monitor.opentelemetry import configure_azure_monitor

configure_azure_monitor(
    resource=Resource.create(
        {
            "service.name": "live_metrics_service",
            "service.instance.id": "qp_instance_id",
        }
    ),
    logger_name=__name__,
    # enable_live_metrics=False,  # To disable live metrics configuration
)

tracer = trace.get_tracer(__name__)
logger = logging.getLogger(__name__)

# Continuously send metrics
while True:
    with tracer.start_as_current_span("parent"):
        logger.warning("sending request")
        response = requests.get("https://azure.microsoft.com/", timeout=5)
        try:
            val = 1 / 0
            print(val)
        except ZeroDivisionError:
            logger.error("Error: Division by zero", stack_info=True, exc_info=True)
    time.sleep(2)
