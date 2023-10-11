# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License in the project root for
# license information.
# --------------------------------------------------------------------------

from logging import getLogger

from azure.monitor.opentelemetry import configure_azure_monitor
from opentelemetry import trace

configure_azure_monitor()

logger = getLogger(__name__)
tracer = trace.get_tracer(__name__)

logger.info("Uncorrelated info log")
logger.warning("Uncorrelated warning log")
logger.error("Uncorrelated error log")

with tracer.start_as_current_span("Span for correlated logs"):
    logger.info("Correlated info log")
    logger.warning("Correlated warning log")
    logger.error("Correlated error log")

input()
