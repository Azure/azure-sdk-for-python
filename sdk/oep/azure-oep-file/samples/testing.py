from azure.identity import DefaultAzureCredential
from oep._client import ApiDocumentation
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
    client = ApiDocumentation(
        credential=credentials
    )
    # client.liveness_check_using_get(data_partition_id='bvtstglf7zn1c-testdata',frame_of_reference='fajba')
    # client.get_location_file_using_get(data_partition_id='bvtstglf7zn1c-testdata',frame_of_reference='fajba')
    # client.post_files_metadata_using_post(data_partition_id='bvtstglf7zn1c-testdata',
    #                                       frame_of_reference='fajba',
    #                                       body={
    #                                           "kind": "osdu:wks:dataset--File.Generic:1.0.0",
    #                                           "acl": {
    #                                               "viewers": [
    #                                                   "data.default.viewers@bvtstglf7zn1c-testdata.contoso.com"
    #                                               ],
    #                                               "owners": [
    #                                                   "data.default.viewers@bvtstglf7zn1c-testdata.contoso.com"
    #                                               ]
    #                                           },
    #                                           "legal": {
    #                                               "legaltags": [
    #                                                   "bvtstglf7zn1c-testdata-R3FullManifest-Legal-Tag-Test3706517"
    #                                               ],
    #                                               "otherRelevantDataCountries": [
    #                                                   "US"
    #                                               ],
    #                                               "status": "compliant"
    #                                           },
    #                                           "data": {
    #                                               "Endian": "BIG",
    #                                               "DatasetProperties": {
    #                                                   "FileSourceInfo": {
    #                                                       "FileSource": "/osdu-user/1655884402137-2022-06-22-07-53-22-137/8651127327c64b42a7fa0f8afb13d64d"
    #                                                   }
    #                                               }
    #                                           }
    #                                       })
    # client.get_file_metadata_by_id_using_get(data_partition_id='bvtstglf7zn1c-testdata',frame_of_reference='fajba',id='bvtstglf7zn1c-testdata:dataset--File.Generic:8ff6e7f0-deb1-4ac3-b499-c82658ed2353')
    client.download_url_using_get(data_partition_id='bvtstglf7zn1c-testdata',frame_of_reference='fajba',id='bvtstglf7zn1c-testdata:dataset--File.Generic:8ff6e7f0-deb1-4ac3-b499-c82658ed2353')
if __name__ == "__main__":
    sample_hello_world()