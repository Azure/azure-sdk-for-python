# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License in the project root for
# license information.
# --------------------------------------------------------------------------
from azure.monitor.opentelemetry import configure_azure_monitor

# Enable or disable supported instrumentations with the instrumentation_options parameter
configure_azure_monitor(
    instrumentation_options = {
        "azure_sdk": {"enabled": False},
        "django": {"enabled": True},
        "fastapi": {"enabled": False},
        "flask": {"enabled": True},
        "psycopg2": {"enabled": False},
        "requests": {"enabled": True},
        "urllib": {"enabled": False},
        "urllib3": {"enabled": True},
    }
)
