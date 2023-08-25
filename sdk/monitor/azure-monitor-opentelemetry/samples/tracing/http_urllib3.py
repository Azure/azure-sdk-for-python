# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License in the project root for
# license information.
# --------------------------------------------------------------------------
import logging

import urllib3
from azure.monitor.opentelemetry import configure_azure_monitor
from opentelemetry import trace

logger = logging.getLogger(__name__)

# Configure Azure monitor collection telemetry pipeline
configure_azure_monitor()

http = urllib3.PoolManager()

tracer = trace.get_tracer(__name__)
with tracer.start_as_current_span("Request parent span") as span:
    try:
        # Requests made using the urllib3 library will be automatically captured
        response = http.request("GET", "https://www.example.org/")
        logger.warning("Request sent")
    except Exception as ex:
        # If an exception occurs, this can be manually recorded on the parent span
        span.set_attribute("status", "exception")
        span.record_exception(ex)

input()
