import pytest
import azure.mgmt.loganalytics
from devtools_testutils import AzureMgmtRecordedTestCase, recorded_by_proxy

class TestMgmtLogAnalytics(AzureMgmtRecordedTestCase):

    def setup_method(self, method):
        self.client = self.create_mgmt_client(
            azure.mgmt.loganalytics.LogAnalyticsManagementClient
        )

    @pytest.mark.skip('Hard to test')
    @recorded_by_proxy
    def test_loganalytics_operations(self):
        operations = self.client.operations.list()
        assert len(list(operations)) > 0
