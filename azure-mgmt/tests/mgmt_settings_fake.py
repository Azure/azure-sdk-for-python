#-------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
#--------------------------------------------------------------------------

from azure.common.credentials import (
    BasicTokenAuthentication
)

SUBSCRIPTION_ID = "00000000-0000-0000-0000-000000000000"
# GraphRBAC tests
AD_DOMAIN = "myaddomain.onmicrosoft.com"

def get_credentials():
    return BasicTokenAuthentication(
        token = {
            'access_token':'faked_token'
        }
    )
