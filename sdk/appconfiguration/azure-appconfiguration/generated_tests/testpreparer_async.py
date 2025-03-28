# coding=utf-8
from azure.appconfiguration.aio import AzureAppConfigurationClient
from devtools_testutils import AzureRecordedTestCase


class AzureAppConfigurationClientTestBaseAsync(AzureRecordedTestCase):

    def create_async_client(self, endpoint):
        credential = self.get_credential(AzureAppConfigurationClient, is_async=True)
        return self.create_client_from_credential(
            AzureAppConfigurationClient,
            credential=credential,
            endpoint=endpoint,
        )
