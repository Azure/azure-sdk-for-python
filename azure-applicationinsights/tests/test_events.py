from azure.applicationinsights import ApplicationInsightsDataClient
from azure.applicationinsights.models import MetricsPostBodySchema, MetricsPostBodySchemaParameters
from devtools_testutils import AzureMgmtTestCase

class ApplicationInsightsEventsTest(AzureMgmtTestCase):
    def setUp(self):
        super(ApplicationInsightsEventsTest, self).setUp()
        self.client = self.create_basic_client(ApplicationInsightsDataClient) 
        self.application = 'DEMO_APP'
        self.props = [
            'id', 
            'timestamp', 
            'count', 
            'custom_dimensions', 
            'operation', 
            'session', 
            'user', 
            'cloud', 
            'ai', 
            'application', 
            'client', 
            'type'
        ]
        self.noneProps = ['interval', 'segments']

    def test_events_get_by_type(self):
        eventType = 'requests'
        result = self.client.events.get_by_type(self.application, eventType)
        self.assertIsNotNone(result.value)
        self.assertGreaterEqual(len(result.value), 1)
        self.assertTrue(hasattr(result, 'value'))
        self.check_props(result)
        
    def test_events_get(self):
        eventType = 'requests'
        eventId = '923e9660-7385-11e8-80fe-b756f505275f'
        result = self.client.events.get(self.application, eventType, eventId)
        self.assertIsNotNone(result.value)
        self.assertEqual(len(result.value), 1)
        self.assertEqual(result.value[0].id, eventId)
        self.check_props(result)

    def test_events_get_odata_metadata(self):
        result = self.client.events.get_odata_metadata(self.application, raw = True)
        self.assertIsNotNone(result)
        self.assertEqual(result.response.status_code, 200)
        self.assertIsNotNone(result.output)
        
    def check_props(self, result):
        self.assertTrue(hasattr(result, 'value'))
        for item in result.value:
            for prop in self.props:
                self.assertTrue(hasattr(item, prop))
            for prop in self.noneProps:
                self.assertFalse(hasattr(item, prop))