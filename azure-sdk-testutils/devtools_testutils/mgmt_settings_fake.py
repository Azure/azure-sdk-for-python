#-------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
#--------------------------------------------------------------------------

from azure.common.credentials import (
    BasicTokenAuthentication,
    UserPassCredentials
)

SUBSCRIPTION_ID = "00000000-0000-0000-0000-000000000000"

# this is used explicitly for ADLA job id replacement in recordings.
ADLA_JOB_ID = "00000000-0000-0000-0000-000000000000"
# GraphRBAC tests
AD_DOMAIN = "myaddomain.onmicrosoft.com"
# Keyvault tests
TENANT_ID = '00000000-0000-0000-0000-000000000000'
CLIENT_OID = '00000000-0000-0000-0000-000000000000'
# Cognitive Services tests
CS_SUBSCRIPTION_KEY = '0000000000000000000000000000'
# Event Grid key
EVENT_GRID_KEY = '0000000000000000000000000000'

# Read for details of this file:
# https://github.com/Azure/azure-sdk-for-python/wiki/Contributing-to-the-tests

def get_credentials(**kwargs):
    # Put your credentials here in the "real" file
    #return UserPassCredentials(
    #    'user@myaddomain.onmicrosoft.com',
    #    'Password'
    #)
    # Needed to play recorded tests
    return BasicTokenAuthentication(
        token = {
            'access_token':'faked_token'
        }
    )