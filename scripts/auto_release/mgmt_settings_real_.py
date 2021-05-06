#-------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
#--------------------------------------------------------------------------

from azure.common.credentials import (
    BasicTokenAuthentication,
    UserPassCredentials,
    ServicePrincipalCredentials,
)

SUBSCRIPTION_ID = "ENV_SUBSCRIPTION_ID"
CLIENT_ID = 'ENV_CLIENT_ID'
CLIENT_SECRET = 'ENV_CLIENT_SECRET'

# Keyvault tests
TENANT_ID = 'ENV_TENANT_ID'
# Cognitive Services tests
CS_SUBSCRIPTION_KEY = '0000000000000000000000000000'
# Event Grid key
EVENT_GRID_KEY = '0000000000000000000000000000'
# HDInsight tests
HDI_ADLS_ACCOUNT_NAME = 'fakehdiadlsaccount'
HDI_ADLS_CLIENT_ID = '00000000-0000-0000-0000-000000000000'

# Ubuntu image
LINUX_OS_VHD = "https://mystorageaccount.blob.core.windows.net/inputtestdatadonotdelete/ubuntu.vhd"

# Storage tests related
ACTIVE_DIRECTORY_APPLICATION_ID  = '00000000-0000-0000-0000-00000000000'
ACTIVE_DIRECTORY_APPLICATION_SECRET = '000000000ft5g5g5g5g5g5g5g5000000?'
ACTIVE_DIRECTORY_TENANT_ID = '00000000-0000-0000-0000-000000000000'
IS_SERVER_SIDE_FILE_ENCRYPTION_ENABLED = True
ENABLE_LOGGING = True

# Read for details of this file:
# https://github.com/Azure/azure-sdk-for-python/wiki/Contributing-to-the-tests

def get_azure_core_credentials(**kwargs):
    from azure.identity import ClientSecretCredential
    return ClientSecretCredential(
        client_id = 'ENV_CLIENT_ID',
        client_secret = 'ENV_CLIENT_SECRET',
        tenant_id = 'ENV_TENANT_ID'
    )
    # # Needed to play recorded tests
    # from azure.core.credentials import AccessToken
    # class FakeCredential(object):
        # def get_token(self, *scopes, **kwargs):
            # return AccessToken('fake_token', 2527537086)
    # return FakeCredential()

def get_credentials(**kwargs):
    # Put your credentials here in the "real" file
    #return UserPassCredentials(
    #    'user@myaddomain.onmicrosoft.com',
    #    'Password'
    #)
    # note that UserCredential does not work any longer. Must use a ServicePrincipal.
    # for deprecated APIs I believe will still work.
    return ServicePrincipalCredentials(
        client_id = 'ENV_CLIENT_ID',
        secret = 'ENV_CLIENT_SECRET',
        tenant = 'ENV_TENANT_ID'
    )
    # Needed to play recorded tests
    # return BasicTokenAuthentication(
        # token = {
            # 'access_token':'faked_token'
        # }
    # )