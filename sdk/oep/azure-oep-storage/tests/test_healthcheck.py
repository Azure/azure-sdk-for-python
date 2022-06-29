import functools
import pytest

from devtools_testutils import AzureTestCase, PowerShellPreparer
import sys
import os
from azure.identity import DefaultAzureCredential
sys.path.append(os.path.abspath('../azure'))
from azure.oep.storage._oep_storage_client import OepStorageClient

OepStoragePreparer = functools.partial(
    PowerShellPreparer, 'azure'
)

class TestHealthCheckOperaion(AzureTestCase):

    # Start with any helper functions you might need, for example a client creation method:
    def create_oep_client(self, base_url):
        credential = DefaultAzureCredential()
        client = self.create_client_from_credential(OepStorageClient, credential=credential, base_url=base_url)
        return client

    def get_health_response(self, client, data_partition_id):
        return client.health.get(data_partition_id=data_partition_id)

    # Write your tests
    @OepStoragePreparer()
    def test_health_get(self):
        data_partition_id="dpId"
        base_url="https://fake-instance.oep.ppe.azure-int.net"
        client = self.create_oep_client(base_url=base_url)
        response = self.get_health_response(client=client, data_partition_id=data_partition_id)
        assert response == "Alive"
