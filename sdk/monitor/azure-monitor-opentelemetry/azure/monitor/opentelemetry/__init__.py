# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License in the project root for
# license information.
# -------------------------------------------------------------------------

from azure.monitor.opentelemetry._configure import configure_azure_monitor

from ._version import VERSION

__all__ = [
    "configure_azure_monitor",
]
__version__ = VERSION
