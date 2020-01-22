# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
import os

from azure.identity import AuthFileCredential
from azure.core.exceptions import ClientAuthenticationError

import pytest
try:
    from unittest.mock import Mock, patch
except ImportError:
    from mock import Mock, patch


def test_auth_file_credential_parse():
    credential = AuthFileCredential('{}/authfile.json'.format(os.path.dirname(__file__)))
    credential._ensure_credential()
    
    inner = credential._credential

    assert inner is not None
    assert inner._form_data['client_id'] == 'mockclientid'
    assert inner._form_data['client_secret'] == 'mockclientsecret'
    assert 'mocktenantid' in inner._client._auth_url

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
