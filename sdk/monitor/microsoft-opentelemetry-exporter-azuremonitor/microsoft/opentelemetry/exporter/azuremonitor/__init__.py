# coding=utf-8
# --------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------

from microsoft.opentelemetry.exporter.azuremonitor.export.trace import AzureMonitorSpanExporter
from ._version import VERSION

__all__ = ["AzureMonitorSpanExporter"]
__version__ = VERSION
