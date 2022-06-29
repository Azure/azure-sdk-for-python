import functools
import pytest

from devtools_testutils import AzureTestCase, PowerShellPreparer
import sys
import os
from azure.identity import DefaultAzureCredential
sys.path.append(os.path.abspath('../azure'))
from azure.oep.storage.aio._oep_storage_client import OepStorageClient

OepStoragePreparer = functools.partial(
    PowerShellPreparer, 'azure'
)

class TestHealthCheckOperaionAsync(AzureTestCase):

    @OepStoragePreparer()
    async def test_health_get(self):
        data_partition_id="dpId"
        base_url="https://fake-instance.oep.ppe.azure-int.net"
        credential = self.get_credential(OepStorageClient, is_async=True)
        client = self.create_client_from_credential(OepStorageClient, credential=credential, base_url=base_url)
        response = await client.health.get(data_partition_id=data_partition_id)
        assert response == 'Alive'
