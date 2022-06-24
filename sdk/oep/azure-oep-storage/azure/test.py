# Copyright (c) Microsoft Corporation.
# Licensed under the MIT license.

"""
FILE: sample_hello_world.py
DESCRIPTION:
    This sample demonstrates the most basic operation that can be
    performed - creation of a Farmer. Use this to understand how to
    create the client object, how to authenticate it, and make sure
    your client is set up correctly to call into your FarmBeats endpoint.
USAGE:
    ```python sample_hello_world.py```
    Set the environment variables with your own values before running the sample:
    - `AZURE_TENANT_ID`: The tenant ID of your active directory application.
    - `AZURE_CLIENT_ID`: The client ID of your active directory application.
    - `AZURE_CLIENT_SECRET`: The client secret of your active directory application.
    - `FARMBEATS_ENDPOINT`: The FarmBeats endpoint that you want to run these samples on.
"""
from azure.identity import DefaultAzureCredential
import os
import sys
sys.path.append(os.path.abspath('../azure'))
from oep.storage._oep_storage_client import OepStorageClient

def health_check():

    os. environ['AZURE_CLIENT_ID'] = '2f59abbc-7b40-4d0e-91b2-22ca3084bc84'
    os. environ['AZURE_CLIENT_SECRET'] = 'OKa8Q~Ng5h~3P_OH-OvVyLFUCnS5hhbtyblJJaKR'
    os. environ['AZURE_TENANT_ID'] = '72f988bf-86f1-41af-91ab-2d7cd011db47'

    credentials = DefaultAzureCredential()
    client = OepStorageClient(
        credential=credentials,
        base_url='https://bvtstglf7zn1c.oep.ppe.azure-int.net'
    )
    client.health.get(data_partition_id='bvtstglf7zn1c-testdata', frame_of_reference='none')
    x = client.record.list_record_versions_by_id(id='bvtstglf7zn1c-testdata:999571446469:999571446469', data_partition_id='bvtstglf7zn1c-testdata', frame_of_reference='none')
    print(x)

if __name__ == "__main__":
    health_check()