from azure.applicationinsights import ApplicationInsightsDataClient
from azure.applicationinsights.models import QueryBody
from devtools_testutils import AzureMgmtTestCase

class ApplicationInsightsQueryTest(AzureMgmtTestCase):
    def setUp(self):
        super(ApplicationInsightsQueryTest, self).setUp()
        self.client = self.create_basic_client(ApplicationInsightsDataClient) 

    def test_query(self):
        query = 'requests | take 10'
        application = 'DEMO_APP'
        result = self.client.query.execute(application, QueryBody(query = query))
        # All queries should return at least a table.
        self.assertGreaterEqual(len(result.tables), 1)

        # Request table schema has 37 columns.
        self.assertEqual(len(result.tables[0].columns), 37)

        # The application should contain enough data to retrieve 10 rows, as asked
        self.assertEqual(len(result.tables[0].rows), 10)
        self.assertIs(type(result.tables[0].rows[0][7]), float)
