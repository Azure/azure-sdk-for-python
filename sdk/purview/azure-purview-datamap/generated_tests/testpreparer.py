# coding=utf-8
from azure.purview.datamap import DataMapClient
from devtools_testutils import AzureRecordedTestCase, PowerShellPreparer
import functools


class DataMapClientTestBase(AzureRecordedTestCase):

    def create_client(self, endpoint):
        credential = self.get_credential(DataMapClient)
        return self.create_client_from_credential(
            DataMapClient,
            credential=credential,
            endpoint=endpoint,
        )


DataMapPreparer = functools.partial(PowerShellPreparer, "datamap", datamap_endpoint="https://fake_datamap_endpoint.com")
