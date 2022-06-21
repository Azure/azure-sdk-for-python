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
    # client.liveness_check_using_get(data_partition_id='bvtstglf7zn1c-testdata')

    client.add_member_using_post(data_partition_id='bvtstglf7zn1c-testdata',
                                 group_email='users@bvtstglf7zn1c-testdata.contoso.com',
                                 body={
                                     "email": "abcd@microsoft.com",
                                     "role": "MEMBER"
                                 })

if __name__ == "__main__":
    sample_hello_world()

