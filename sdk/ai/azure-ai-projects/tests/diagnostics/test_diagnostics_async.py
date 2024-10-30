# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
import sys
from devtools_testutils.aio import recorded_by_proxy_async
from diagnostics_test_base import DiagnosticsTestBase, servicePreparerDiagnosticsTests


# The test class name needs to start with "Test" to get collected by pytest
class TestDiagnosticsAsync(DiagnosticsTestBase):

    @servicePreparerDiagnosticsTests()
    @recorded_by_proxy_async
    async def test_diagnostics_get_connection_string_async(self, **kwargs):
        async with self.get_async_client(**kwargs) as project_client:
            connection_string = await project_client.diagnostics.get_connection_string()
            print(connection_string)
            assert connection_string
            assert bool(DiagnosticsTestBase.REGEX_APPINSIGHTS_CONNECTION_STRING.match(connection_string))
            assert connection_string == await project_client.diagnostics.get_connection_string()

    @servicePreparerDiagnosticsTests()
    async def test_diagnostics_enable_console_tracing_async(self, **kwargs):
        async with self.get_async_client(**kwargs) as project_client:
            project_client.diagnostics.enable(destination=sys.stdout)
            #TODO: Create inference client and do chat completions. How do I know if traces were emitted?

    @servicePreparerDiagnosticsTests()
    async def test_diagnostics_enable_otlp_tracing(self, **kwargs):
        async with self.get_async_client(**kwargs) as project_client:
            project_client.diagnostics.enable(destination="https://some.otlp.collector.endpoint")
            #TODO: Create inference client and do chat completions. Test proxy will log attempt at telemetry call.