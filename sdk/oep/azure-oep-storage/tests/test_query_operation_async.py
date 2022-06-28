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

class TestQueryOperationAsync(AzureTestCase):

    @OepStoragePreparer()
    async def test_query_operation_async(self):
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
        kindsData = await client.query.list_kinds(data_partition_id=data_partition_id)
        assert kindsData is not None
        kinds = kindsData.results
        data = await client.query.list_records_by_kind(data_partition_id=data_partition_id, kind=kinds[0])
        assert data is not None
        await client.record.purge_record_by_id(id=record_ids_created[0], data_partition_id = data_partition_id)