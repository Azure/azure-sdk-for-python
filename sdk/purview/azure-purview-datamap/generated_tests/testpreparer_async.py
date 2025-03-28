# coding=utf-8
from azure.purview.datamap.aio import DataMapClient
from devtools_testutils import AzureRecordedTestCase


class DataMapClientTestBaseAsync(AzureRecordedTestCase):

    def create_async_client(self, endpoint):
        credential = self.get_credential(DataMapClient, is_async=True)
        return self.create_client_from_credential(
            DataMapClient,
            credential=credential,
            endpoint=endpoint,
        )
