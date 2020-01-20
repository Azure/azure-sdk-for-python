# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
import os

from azure.identity import AuthFileCredential
from azure.core.exceptions import ClientAuthenticationError

def test_auth_file_credential_parse():
    credential = AuthFileCredential('{}/authfile.json'.format(os.path.dirname(__file__)))
    credential._ensure_credential()
    
    inner = credential._credential

    assert inner is not None
    assert inner._form_data['client_id'] == 'mockclientid'
    assert inner._form_data['client_secret'] == 'mockclientsecret'
    assert 'mocktenantid' in inner._client._auth_url

def test_bad_auth_file():
    credential = AuthFileCredential('Bad*Path')
    try:
        credential.get_token("https://mock.scope/.default/")
    except ClientAuthenticationError as e:
        assert 'Error parsing SDK Auth File' in e.message