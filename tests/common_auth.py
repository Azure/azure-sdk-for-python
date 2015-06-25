#-------------------------------------------------------------------------
# Copyright (c) Microsoft.  All rights reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#   http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#--------------------------------------------------------------------------
import json
import os.path

from .util import (
    get_test_file_path,
)


def get_token_from_username_password(authority_url, username, password):
    import adal
    token_response = adal.acquire_token_with_username_password(
        authority_url,
        username,
        password,
    )
    return token_response.get('accessToken')


def get_token_from_client_credentials(authority, client_id, secret):
    import adal
    token_response = adal.acquire_token_with_client_credentials(
        authority,
        client_id,
        secret,
    )
    return token_response.get('accessToken')


def get_token_from_json_file():
    '''
    Read the token from a json file 'credentials_real.json' in this directory
    where the file looks like this:
    {
      "authorization_header": "Bearer eyJ0...8f5w"
    }
    '''
    with open(get_test_file_path(os.path.join('credentials_real.json'))) as credential_file:
        credential = json.load(credential_file)
        token = credential['authorization_header'].split()[1]
        return token
