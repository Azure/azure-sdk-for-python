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
from oep.oep._client import ApiDocumentation
import os


def sample_hello_world():

    # Tenant ID for your Azure Subscription
    TENANT_ID = "72f988bf-86f1-41af-91ab-2d7cd011db47"
    # Your Application Client ID of your Service Principal
    CLIENT_ID = "2f59abbc-7b40-4d0e-91b2-22ca3084bc84"
    # Your Service Principal secret key
    CLIENT_SECRET = "OKa8Q~Ng5h~3P_OH-OvVyLFUCnS5hhbtyblJJaKR"
    # Your Azure Subscription ID
    # SUBSCRIPTION_ID = "(update-this-value)"
    # # Your Resource Group name
    # RESOURCE_GROUP_NAME = "(update-this-value)"
    # # Your Azure Media Service account name
    # ACCOUNT_NAME = "(update-this-value)"
    os. environ['AZURE_CLIENT_ID'] = '2f59abbc-7b40-4d0e-91b2-22ca3084bc84'
    os. environ['AZURE_CLIENT_SECRET'] = 'OKa8Q~Ng5h~3P_OH-OvVyLFUCnS5hhbtyblJJaKR'
    os. environ['AZURE_TENANT_ID'] = '72f988bf-86f1-41af-91ab-2d7cd011db47'

    credentials = DefaultAzureCredential()
    # print(credentials.get_token('https://webpubsub.azure.com/.default'))

    # credential = DefaultAzureCredential()

    # print(credentials.get_token('https://management.core.windows.net/.default'))
    client = ApiDocumentation(
        credential=credentials
    )

    # print(client.health_message_using_get(data_partition_id='bvtstglf7zn1c-testdata', frame_of_reference='none'))
    # client.create_or_update_records_using_put(body=[
    #     {
    #         "acl": {
    #             "owners": [
    #                 "data.default.viewers@bvtstglf7zn1c-testdata.contoso.com"
    #             ],
    #             "viewers": [
    #                 "data.default.viewers@bvtstglf7zn1c-testdata.contoso.com"
    #             ]
    #         },
    #         "data": {
    #             "msg": "hello world from Data Lake"
    #         },
    #         "id": "bvtstglf7zn1c-testdata:999571446469:999571446469",
    #         "kind": "osdu:wks:master-data--Well:1.0.0",
    #         "legal": {
    #             "legaltags": [
    #                 "bvtstglf7zn1c-testdata-R3FullManifest-Legal-Tag-Test7116543"
    #             ],
    #             "otherRelevantDataCountries": [
    #                 "US"
    #             ],
    #             "status": "compliant"
    #         },
    #         "meta": [
    #             {}
    #         ],
    #         "version": 0
    #     }
    # ]
    #
    # , data_partition_id='bvtstglf7zn1c-testdata', frame_of_reference='none')

    client.get_record_versions_using_get(id='bvtstglf7zn1c-testdata:999571446469:999571446469', data_partition_id='bvtstglf7zn1c-testdata', frame_of_reference='none')


if __name__ == "__main__":


    sample_hello_world()


