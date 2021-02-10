# coding=utf-8
# --------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------

from azure.monitor.opentelemetry.exporter.export.trace._exporter import AzureMonitorTraceExporter
from ._version import VERSION

__all__ = ["AzureMonitorTraceExporter"]
__version__ = VERSION
