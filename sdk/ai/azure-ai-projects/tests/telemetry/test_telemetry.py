# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
import sys
from devtools_testutils import recorded_by_proxy
from azure.ai.projects import AIProjectClient
from telemetry_test_base import TelemetryTestBase, servicePreparerTelemetryTests


# The test class name needs to start with "Test" to get collected by pytest
class TestTelemetry(TelemetryTestBase):

    @servicePreparerTelemetryTests()
    @recorded_by_proxy
    def test_telemetry_get_connection_string(self, **kwargs):
        with self.get_sync_client(**kwargs) as project_client:
            connection_string = project_client.telemetry.get_connection_string()
            print(connection_string)
            assert connection_string
            assert bool(TelemetryTestBase.REGEX_APPINSIGHTS_CONNECTION_STRING.match(connection_string))
            assert connection_string == project_client.telemetry.get_connection_string()

    @servicePreparerTelemetryTests()
    def test_telemetry_enable_console_tracing(self, **kwargs):
        with self.get_sync_client(**kwargs) as project_client:
            project_client.telemetry.enable()
            # TODO: Create inference client and do chat completions. How do I know if traces were emitted?

    @servicePreparerTelemetryTests()
    def test_telemetry_enable_console_tracing_to_stdout(self, **kwargs):
        with self.get_sync_client(**kwargs) as project_client:
            project_client.telemetry.enable(destination=sys.stdout)
            # TODO: Create inference client and do chat completions. How do I know if traces were emitted?
