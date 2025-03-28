# coding=utf-8
from azure.healthinsights.radiologyinsights.aio import RadiologyInsightsClient
from devtools_testutils import AzureRecordedTestCase


class RadiologyInsightsClientTestBaseAsync(AzureRecordedTestCase):

    def create_async_client(self, endpoint):
        credential = self.get_credential(RadiologyInsightsClient, is_async=True)
        return self.create_client_from_credential(
            RadiologyInsightsClient,
            credential=credential,
            endpoint=endpoint,
        )
