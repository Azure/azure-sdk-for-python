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

class TestRecordOperationAsync(AzureTestCase):

    @OepStoragePreparer()
    async def test_record_operation_async(self):
        credential = self.get_credential(OepStorageClient, is_async=True)
        client = self.create_client_from_credential(OepStorageClient, credential=credential, base_url='https://instance.oep.ppe.azure-int.net')
        data_partition_id="dpid"
        createAndUpdateRecordsResponse = await client.record.create_or_update_record(body=[
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
        ], data_partition_id=data_partition_id)
        assert createAndUpdateRecordsResponse is not None
        record_ids_created = createAndUpdateRecordsResponse.record_ids
        assert record_ids_created is not None
        record_id_version_created = createAndUpdateRecordsResponse.record_id_versions
        assert record_id_version_created is not None
        record_versions_by_id = await client.record.list_record_versions_by_id(id=record_ids_created[0], data_partition_id = data_partition_id)
        assert record_versions_by_id is not None
        latest_record = await client.record.get_latest_record_version_by_id(id=record_ids_created[0], data_partition_id = data_partition_id)
        assert latest_record is not None
        specific_record = await client.record.get_specific_record_version(id=record_ids_created[0], data_partition_id = data_partition_id, version= record_versions_by_id.versions[0])
        assert specific_record is not None
        await client.record.purge_record_by_id(id=record_ids_created[0], data_partition_id = data_partition_id)
