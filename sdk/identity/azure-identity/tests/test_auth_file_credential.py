# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
import os

from azure.identity import AuthFileCredential
from azure.core.exceptions import ClientAuthenticationError

from helpers import validating_transport, Request, mock_response, build_aad_response

import pytest
try:
    from unittest.mock import patch
except ImportError:
    from mock import patch


def test_auth_file_credential_parse():
    client_id = 'mockclientid'   # same value with that in authfile.json
    secret = 'mockclientsecret'  # same value with that in authfile.json
    tenant_id =  'mocktenantid'  # same value with that in authfile.json
    access_token = '***'

    transport = validating_transport(
        requests=[Request(url_substring=tenant_id, required_data={"client_id": client_id, "client_secret": secret})],
        responses=[
            mock_response(
                json_payload={
                    "token_type": "Bearer",
                    "expires_in": 42,
                    "ext_expires_in": 42,
                    "access_token": access_token
                }
            )
        ]
    )

    token = AuthFileCredential('{}/authfile.json'.format(os.path.dirname(__file__)), transport=transport).get_token('scope')

    assert token.token == access_token

def test_bad_auth_file():
    def test_file_not_found():
        with pytest.raises(ClientAuthenticationError) as e:
            credential = AuthFileCredential('Bad*Path')
            token = credential.get_token("https://mock.scope/.default/")

        assert 'No file found on the given path' == str(e.value)
    
    def test_file_no_json():
        with pytest.raises(ClientAuthenticationError) as nojson_e:
            credential = AuthFileCredential('{}/authfile_nojson.json'.format(os.path.dirname(__file__)))
            token = credential.get_token("https://mock.scope/.default")

        assert 'Error parsing SDK Auth File' == str(nojson_e.value)

    def test_file_bad_value():
        with pytest.raises(ClientAuthenticationError) as nojson_e:
            credential = AuthFileCredential('{}/authfile_badvalue.json'.format(os.path.dirname(__file__)))
            token = credential.get_token("https://mock.scope/.default")

        assert 'Error parsing SDK Auth File' == str(nojson_e.value)

    test_file_not_found()
    test_file_no_json()
    test_file_bad_value()
