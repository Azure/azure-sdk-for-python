from azure.loganalytics import LogAnalyticsDataClient
from azure.loganalytics.models import QueryBody
from devtools_testutils import AzureMgmtTestCase

class LogAnalyticsQueryTest(AzureMgmtTestCase):
    def setUp(self):
        super(LogAnalyticsQueryTest, self).setUp()
        self.client = self.create_basic_client(LogAnalyticsDataClient) 

    def test_query(self):
        query = 'AzureActivity | take 10'
        workspace = 'DEMO_WORKSPACE'
        result = self.client.query(workspace, QueryBody(query))
        
        # All queries should return at least a table.
        self.assertGreaterEqual(len(result.tables), 1)

        # AzureActivity table schema has 23 columns.
        self.assertEqual(len(result.tables[0].columns), 23)

        # The workspace should contain enough data to retrieve 10 rows, as asked
        self.assertEqual(len(result.tables[0].rows), 10)