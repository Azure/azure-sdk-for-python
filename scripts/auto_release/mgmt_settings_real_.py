# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

# Keyvault tests
# Note: Keyvault tests require EnvironmentCredential variables to be populated as well. (AZURE_CLIENT_ID etc)
TENANT_ID = "72f988bf-86f1-41af-91ab-2d7cd011db47"
# Note: Not the OID from the azure portal.  Use 'az ad sp show --id <id> | grep objectId'
CLIENT_OID = "21e28ac6-e003-427c-bd8f-9045112102f9"
# Cognitive Services tests
CS_SUBSCRIPTION_KEY = "0000000000000000000000000000"
# Event Grid key
EVENT_GRID_KEY = "0000000000000000000000000000"
# HDInsight tests
HDI_ADLS_ACCOUNT_NAME = "fakehdiadlsaccount"
HDI_ADLS_CLIENT_ID = "00000000-0000-0000-0000-000000000000"

# Ubuntu image
LINUX_OS_VHD = "https://mystorageaccount.blob.core.windows.net/inputtestdatadonotdelete/ubuntu.vhd"

# Storage tests related
ACTIVE_DIRECTORY_APPLICATION_ID = "00000000-0000-0000-0000-00000000000"
ACTIVE_DIRECTORY_APPLICATION_SECRET = "000000000ft5g5g5g5g5g5g5g5000000?"
ACTIVE_DIRECTORY_TENANT_ID = "00000000-0000-0000-0000-000000000000"
IS_SERVER_SIDE_FILE_ENCRYPTION_ENABLED = True
ENABLE_LOGGING = True
AZURE_STORAGE_CONNECTION_STRING = "DefaultEndpointsProtocol=https;AccountName=storagename;AccountKey=NzhL3hKZbJBuJ2484dPTR+xF30kYaWSSCbs2BzLgVVI1woqeST/1IgqaLm6QAOTxtGvxctSNbIR/1hW8yH+bJg==;EndpointSuffix=core.windows.net"

# Read for details of this file:
# https://github.com/Azure/azure-sdk-for-python/wiki/Contributing-to-the-tests

SUBSCRIPTION_ID = "Replace"
BATCH_CLIENT_ID = "Replace"
BATCH_SECRET = "Replace"
BATCH_TENANT = "Replace"

from azure.identity import ClientSecretCredential
def get_azure_core_credentials():
     
     return ClientSecretCredential(
         client_id = BATCH_CLIENT_ID,
         client_secret = BATCH_SECRET,
         tenant_id = BATCH_TENANT
     )


from azure.common.credentials import ServicePrincipalCredentials

def get_credentials(**kwargs):
    return ServicePrincipalCredentials(
        client_id=BATCH_CLIENT_ID,
        secret=BATCH_SECRET,
        tenant=BATCH_TENANT,
        **kwargs
        )
    
