import pytest
import azure.mgmt.loganalytics
from devtools_testutils import AzureMgmtRecordedTestCase, recorded_by_proxy, ResourceGroupPreparer


@pytest.mark.live_test_only
class TestMgmtLogAnalyticsWorkspace(AzureMgmtRecordedTestCase):

    def setup_method(self, method):
        self.client = self.create_mgmt_client(azure.mgmt.loganalytics.LogAnalyticsManagementClient)

    @ResourceGroupPreparer()
    @recorded_by_proxy
    def test_loganalytics_workspace(self, resource_group, location):
        workspace_name = "WorkspaceName"
        workspace_result = self.client.workspaces.begin_create_or_update(
            resource_group.name, workspace_name, {"location": location}
        ).result()

        workspace = self.client.workspaces.get(resource_group.name, workspace_name)
        assert workspace_result.name == workspace.name
