import azure.mgmt.loganalytics
from devtools_testutils import AzureMgmtTestCase


class MgmtLoganalyticsTest(AzureMgmtTestCase):

    def setUp(self):
        super(MgmtLoganalyticsTest, self).setUp()
        self.client = self.create_mgmt_client(
            azure.mgmt.loganalytics.LogAnalyticsManagementClient
        )

    def test_loganalytics_operations(self):
        operations = self.client.operations.list()
        self.assertTrue(len(list(operations)) > 0)
