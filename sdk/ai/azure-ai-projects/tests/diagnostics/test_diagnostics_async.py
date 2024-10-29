# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

from devtools_testutils.aio import recorded_by_proxy_async
from diagnostics_test_base import DiagnosticsTestBase, servicePreparerDiagnosticsTests


# The test class name needs to start with "Test" to get collected by pytest
class TestDiagnosticsAsync(DiagnosticsTestBase):

    @servicePreparerDiagnosticsTests()
    @recorded_by_proxy_async
    async def test_diagnostics_async(self, **kwargs):
        async with self.get_async_client(**kwargs) as project_client:
            assert project_client.diagnostics.connection_string == None
            assert await project_client.diagnostics.enable() == True
            assert project_client.diagnostics.connection_string is not None
            assert bool(
                DiagnosticsTestBase.REGEX_APPINSIGHTS_CONNECTION_STRING.match(
                    project_client.diagnostics.connection_string
                )
            )
            assert await project_client.diagnostics.enable() == True
