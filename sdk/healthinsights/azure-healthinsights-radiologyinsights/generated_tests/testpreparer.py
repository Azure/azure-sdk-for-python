# coding=utf-8
from azure.healthinsights.radiologyinsights import RadiologyInsightsClient
from devtools_testutils import AzureRecordedTestCase, PowerShellPreparer
import functools


class RadiologyInsightsClientTestBase(AzureRecordedTestCase):

    def create_client(self, endpoint):
        credential = self.get_credential(RadiologyInsightsClient)
        return self.create_client_from_credential(
            RadiologyInsightsClient,
            credential=credential,
            endpoint=endpoint,
        )


RadiologyInsightsPreparer = functools.partial(
    PowerShellPreparer, "radiologyinsights", radiologyinsights_endpoint="https://fake_radiologyinsights_endpoint.com"
)
