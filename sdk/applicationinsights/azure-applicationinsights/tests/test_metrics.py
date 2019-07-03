from azure.applicationinsights import ApplicationInsightsDataClient
from azure.applicationinsights.models import MetricsPostBodySchema, MetricsPostBodySchemaParameters
from devtools_testutils import AzureMgmtTestCase

class ApplicationInsightsMetricsTest(AzureMgmtTestCase):
    def setUp(self):
        super(ApplicationInsightsMetricsTest, self).setUp()
        self.client = self.create_basic_client(ApplicationInsightsDataClient) 
        self.application = 'DEMO_APP'

    def test_metrics_get(self):
        metricId = 'availabilityResults/count'
        result = self.client.metrics.get(self.application, metricId)
        self.assertIsNotNone(result.value)
        props = ['start', 'end']
        for prop in props:
            self.assertTrue(hasattr(result.value, prop))
        noneProps = ['interval', 'segments']
        self.assertIsNotNone(result.value.additional_properties['availabilityResults/count']['sum'])
    
    def test_metrics_get_multiple(self):
        metrics = [
            MetricsPostBodySchema(id='1', parameters=MetricsPostBodySchemaParameters(metric_id='availabilityResults/count', timespan='P2DT12H')),
            MetricsPostBodySchema(id='two', parameters=MetricsPostBodySchemaParameters(metric_id='availabilityResults/duration'))
        ]
        result = self.client.metrics.get_multiple(self.application, metrics)
        self.assertEqual(len(result), 2)
        props = ['start', 'end']
        for prop in props:
            for item in result:
                self.assertTrue(hasattr(item.body.value, prop))
        noneProps = ['interval', 'segments']
        self.assertIsNotNone(result[0].body.value.additional_properties['availabilityResults/count']['sum'])

    def test_metrics_get_metadata(self):
        result = self.client.metrics.get_metadata(self.application)
        props = ['metrics', 'dimensions']
        for prop in props:
            self.assertIsNotNone(result[prop])
        reqProps = ['requests/count', 'users/authenticated']
        for prop in reqProps:
            self.assertIsNotNone(result['metrics'][prop])
        self.assertIsNotNone(result['dimensions']['request/source']['displayName'])
