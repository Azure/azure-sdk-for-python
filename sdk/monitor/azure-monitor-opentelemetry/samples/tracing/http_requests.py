# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License in the project root for
# license information.
# --------------------------------------------------------------------------
import logging

import requests
from azure.monitor.opentelemetry import configure_azure_monitor
from opentelemetry import trace

logger = logging.getLogger(__name__)

# Configure Azure monitor collection telemetry pipeline
configure_azure_monitor()

tracer = trace.get_tracer(__name__)
with tracer.start_as_current_span("Request parent span") as span:
    try:
        # Requests made using the requests library will be automatically captured
        response = requests.get("https://azure.microsoft.com/", timeout=5)
        # Set the OTEL_PYTHON_EXCLUDE_URLS environment variable to "http://example.com"
        # This request will not be tracked due to the excluded_urls configuration
        response = requests.get("http://example.com", timeout=5)
        logger.warning("Request sent")
    except Exception as ex:
        # If an exception occurs, this can be manually recorded on the parent span
        span.set_attribute("status", "exception")
        span.record_exception(ex)

input()
