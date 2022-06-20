# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.

import unittest
from azure.monitor.opentelemetry.exporter import (
    AzureMonitorMetricExporter,
    AzureMonitorLogExporter,
    AzureMonitorTraceExporter,
)

class TestAzureMonitorExporters(unittest.TestCase):
    def test_constructors(self):
        for exporter in [
            AzureMonitorMetricExporter,
            AzureMonitorLogExporter,
            AzureMonitorTraceExporter,
        ]:
            try:
                exporter()
            except Exception:  # pylint: disable=broad-except
                self.fail(
                    f"Unexpected exception raised when instantiating {exporter.__name__}"
                )
