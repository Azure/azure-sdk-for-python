# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License in the project root for
# license information.
# --------------------------------------------------------------------------

from logging import WARNING, getLogger

from azure.monitor.opentelemetry import configure_azure_monitor
from opentelemetry.sdk.resources import Resource, ResourceAttributes

configure_azure_monitor()

logger = getLogger(__name__)

logger.info("info log")
logger.warning("warning log")
logger.error("error log")
