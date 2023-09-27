# Copyright The OpenTelemetry Authors
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import unittest

from azure.monitor.opentelemetry.exporter import (
    AzureMonitorLogExporter,
    AzureMonitorMetricExporter,
    AzureMonitorTraceExporter,
)


class TestAzureMonitorExporters(unittest.TestCase):
    def test_constructors(self):
        cs_string = "InstrumentationKey=1234abcd-5678-4efa-8abc-1234567890ab"
        for exporter in [
            AzureMonitorLogExporter,
            AzureMonitorMetricExporter,
            AzureMonitorTraceExporter,
        ]:
            try:
                exporter(connection_string=cs_string)
            except Exception as ex:  # pylint: disable=broad-except
                print(ex)
                self.fail(
                    f"Unexpected exception raised when instantiating {exporter.__name__}"
                )
