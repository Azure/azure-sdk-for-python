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

class TestQueryOperation(AzureTestCase):

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
                        "legaltag"
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

    # Write your tests
    @OepStoragePreparer()
    def test_query_operation(self):
        data_partition_id="dpid"
        client = self.create_oep_client()
        createAndUpdateRecordsResponse = self.create_and_update_record(client=client, data_partition_id=data_partition_id)
        record_ids_created = createAndUpdateRecordsResponse.record_ids
        kindsData = client.query.list_kinds(data_partition_id=data_partition_id)
        assert kindsData is not None
        kinds = kindsData.results
        data = client.query.list_records_by_kind(data_partition_id=data_partition_id, kind=kinds[0])
        assert data is not None
        client.record.purge_record_by_id(id=record_ids_created[0], data_partition_id=data_partition_id)

