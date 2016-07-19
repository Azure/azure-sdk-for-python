#-------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
#--------------------------------------------------------------------------
import json
import os.path

from msrestazure.azure_active_directory import UserPassCredentials
from msrestazure.azure_active_directory import ServicePrincipalCredentials

_XPLAT_CLIENT_ID = '04b07795-8ddb-461a-bbee-02f9e1bf7b46'

def get_credentials_from_username_password(tenant, username, password):
    """ Get credentials from tenant, username and password.

    The tenant is the uuid in your OAuth 2 endpoint:
    https://login.microsoftonline.com/00000000-0000-0000-0000-000000000000/
    """
    return UserPassCredentials(
        client_id=_XPLAT_CLIENT_ID,
        username=username,
        password=password,
        tenant=tenant,
    )

def get_credentials_from_client_credentials(authority, client_id, secret):
    import adal
    token_response = adal.acquire_token_with_client_credentials(
        authority,
        client_id,
        secret,
    )
    return token_response.get('accessToken')


def get_credentials_from_json_file(working_folder):
    '''
    Read the token from a json file 'credentials_real.json' in this directory
    where the file looks like this:
    {
      "authorization_header": "Bearer eyJ0...8f5w"
    }
    '''
    with open(os.path.join(working_folder, 'credentials_real.json')) as credential_file:
        credential = json.load(credential_file)
        token = credential['authorization_header'].split()[1]
        return token
