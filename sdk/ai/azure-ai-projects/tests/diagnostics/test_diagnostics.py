# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

from devtools_testutils import recorded_by_proxy
from diagnostics_test_base import DiagnosticsTestBase, servicePreparerDiagnosticsTests


# The test class name needs to start with "Test" to get collected by pytest
class TestDiagnostics(DiagnosticsTestBase):

    @servicePreparerDiagnosticsTests()
    @recorded_by_proxy
    def test_diagnostics(self, **kwargs):
        with self.get_sync_client(**kwargs) as project_client:
            assert project_client.diagnostics.connection_string == None
            assert project_client.diagnostics.enable() == True
            assert project_client.diagnostics.connection_string is not None
            assert bool(
                DiagnosticsTestBase.REGEX_APPINSIGHTS_CONNECTION_STRING.match(
                    project_client.diagnostics.connection_string
                )
            )
            assert project_client.diagnostics.enable() == True
