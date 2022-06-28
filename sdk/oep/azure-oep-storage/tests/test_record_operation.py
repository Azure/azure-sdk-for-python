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

class TestRecordOperation(AzureTestCase):

    # Start with any helper functions you might need, for example a client creation method:
    def create_oep_client(self):
        credential = DefaultAzureCredential()
        client = self.create_client_from_credential(OepStorageClient, credential=credential, base_url='https://instance.oep.ppe.azure-int.net')
        return client

    def create_and_update_record(self, client, data_partition_id):
        return client.record.create_or_update_record(body=[
            {
                "acl": {
                    "owners": [
                        "viewer@dpid.contoso.com"
                    ],
                    "viewers": [
                        "viewer@dpid.contoso.com"
                    ]
                },
                "data": {
                    "msg": "hello world from Data Lake"
                },
                "id": "dpid:id:id",
                "kind": "kind",
                "legal": {
                    "legaltags": [
                        "dpid-Test-Legal-Tag-6446736"
                    ],
                    "otherRelevantDataCountries": [
                        "US"
                    ],
                    "status": "compliant"
                },
                "meta": [
                    {}
                ],
                "version": 0
            }
        ]  , data_partition_id=data_partition_id)

    def list_record_versions_by_id(self, client, id, data_partition_id):
        return client.record.list_record_versions_by_id(id=id, data_partition_id = data_partition_id)

    def list_latest_record_version_by_id(self, client, id, data_partition_id):
        return client.record.get_latest_record_version_by_id(id=id, data_partition_id = data_partition_id)

    def get_specific_record_version(self, client, id, version, data_partition_id):
        return client.record.get_specific_record_version(id=id, data_partition_id = data_partition_id, version= version)

    def purge_record_by_id(self, client, id, data_partition_id):
        return client.record.purge_record_by_id(id=id, data_partition_id=data_partition_id)

    # Write your tests
    @OepStoragePreparer()
    def test_record_operations(self):
        client = self.create_oep_client()
        data_partition_id="dpid"
        createAndUpdateRecordsResponse = self.create_and_update_record(client=client, data_partition_id=data_partition_id)
        assert createAndUpdateRecordsResponse is not None
        record_ids_created = createAndUpdateRecordsResponse.record_ids
        assert record_ids_created is not None
        record_id_version_created = createAndUpdateRecordsResponse.record_id_versions
        assert record_id_version_created is not None
        record_versions_by_id = self.list_record_versions_by_id(id=record_ids_created[0], client=client, data_partition_id=data_partition_id)
        assert record_versions_by_id is not None
        latest_record = self.list_latest_record_version_by_id(id=record_ids_created[0], client=client, data_partition_id=data_partition_id)
        assert latest_record is not None
        specific_record = self.get_specific_record_version(id=record_ids_created[0], client=client, version=record_versions_by_id.versions[0], data_partition_id=data_partition_id)
        assert specific_record is not None
        self.purge_record_by_id(id=record_ids_created[0], client=client, data_partition_id=data_partition_id)

