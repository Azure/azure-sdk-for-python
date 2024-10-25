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
        project_client = self.get_sync_client(**kwargs)
        print(project_client.diagnostics.enable())

