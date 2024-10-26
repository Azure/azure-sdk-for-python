# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

from devtools_testutils import recorded_by_proxy
from connection_test_base import ConnectionsTestBase, servicePreparerConnectionsTests


# The test class name needs to start with "Test" to get collected by pytest
class TestConnections(ConnectionsTestBase):

    @servicePreparerConnectionsTests()
    @recorded_by_proxy
    def test_connections_get(self, **kwargs):
        project_client = self.get_sync_client(**kwargs)

    @servicePreparerConnectionsTests()
    @recorded_by_proxy
    def test_connections_get_default(self, **kwargs):
        project_client = self.get_sync_client(**kwargs)

    @servicePreparerConnectionsTests()
    @recorded_by_proxy
    def test_connections_list(self, **kwargs):
        project_client = self.get_sync_client(**kwargs)
