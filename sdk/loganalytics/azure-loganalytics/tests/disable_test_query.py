from azure.loganalytics import LogAnalyticsDataClient
from azure.loganalytics.models import QueryBody
from devtools_testutils import AzureMgmtTestCase

class LogAnalyticsQueryTest(AzureMgmtTestCase):
    def setUp(self):
        super(LogAnalyticsQueryTest, self).setUp()
        self.client = self.create_basic_client(LogAnalyticsDataClient) 

    def test_query(self):
        query = 'Heartbeat | take 10'
        workspace = 'DEMO_WORKSPACE'
        result = self.client.query(workspace, QueryBody(**{'query': query}))
        print(result.tables[0].columns)
        print(result.tables[0].rows[0])
        # All queries should return at least a table.
        self.assertGreaterEqual(len(result.tables), 1)

        # Heartbeat table schema has 29 columns.
        self.assertEqual(len(result.tables[0].columns), 29)

        # The workspace should contain enough data to retrieve 10 rows, as asked
        self.assertEqual(len(result.tables[0].rows), 10)

        # Validate deserialization
        self.assertIs(type(result.tables[0].rows[0][16]), float)
        self.assertIs(type(result.tables[0].rows[0][15]), bool)