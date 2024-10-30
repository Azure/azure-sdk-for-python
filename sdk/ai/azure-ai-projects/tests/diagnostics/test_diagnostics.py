# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
import sys
from devtools_testutils import recorded_by_proxy
from azure.ai.projects import AIProjectClient
from diagnostics_test_base import DiagnosticsTestBase, servicePreparerDiagnosticsTests


# The test class name needs to start with "Test" to get collected by pytest
class TestDiagnostics(DiagnosticsTestBase):

    @servicePreparerDiagnosticsTests()
    @recorded_by_proxy
    def test_diagnostics_get_connection_string(self, **kwargs):
        with self.get_sync_client(**kwargs) as project_client:
            connection_string = project_client.diagnostics.get_connection_string()
            print(connection_string)
            assert connection_string
            assert bool(DiagnosticsTestBase.REGEX_APPINSIGHTS_CONNECTION_STRING.match(connection_string))
            assert connection_string == project_client.diagnostics.get_connection_string()

    @servicePreparerDiagnosticsTests()
    def test_diagnostics_enable_console_tracing(self, **kwargs):
        with self.get_sync_client(**kwargs) as project_client:
            project_client.diagnostics.enable(destination=sys.stdout)
            #TODO: Create inference client and do chat completions. How do I know if traces were emitted?

    @servicePreparerDiagnosticsTests()
    def test_diagnostics_enable_otlp_tracing(self, **kwargs):
        with self.get_sync_client(**kwargs) as project_client:
            project_client.diagnostics.enable(destination="https://some.otlp.collector.endpoint")
            #TODO: Create inference client and do chat completions. Test proxy will log attempt at telemetry call.
