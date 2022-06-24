import functools
import pytest

from devtools_testutils import AzureTestCase, PowerShellPreparer
import sys
import os
from azure.identity import DefaultAzureCredential
sys.path.append(os.path.abspath('../azure'))
from oep.storage._oep_storage_client import OepStorageClient

OepStoragePreparer = functools.partial(
    PowerShellPreparer, 'azure'
)

class TestOepregisry(AzureTestCase):

    # Start with any helper functions you might need, for example a client creation method:
    def create_oep_client(self):
        credential = DefaultAzureCredential()
        credential.get_token('https://management.azure.com/.default')
        client = self.create_client_from_credential(OepStorageClient, credential=credential, base_url='https://testInstance.oep.ppe.azure-int.net')
        client.health.get(data_partition_id='data-partition', frame_of_reference='none')
        return client

    ...

    # Write your tests
    @OepStoragePreparer()
    def test_client_creation(self):
        client = self.create_oep_client()
        assert client is not None