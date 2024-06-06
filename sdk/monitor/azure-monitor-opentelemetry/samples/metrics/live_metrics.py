# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.
"""
This example shows how configure live metrics to be enabled. It sets up a minimal example of sending dependency,
trace and exception telemetry to demonstrate the capabilities and collection set of live metrics.
"""
import logging
import requests
import time

from azure.monitor.opentelemetry import configure_azure_monitor
from opentelemetry import trace

from opentelemetry.sdk.resources import Resource

configure_azure_monitor(
    resource=Resource.create({
        "service.name": "live_metrics_service",
        "service.instance.id": "qp_instance_id",
    }),
    logger_name=__name__,
    enable_live_metrics=True,  # Enable live metrics configuration
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
