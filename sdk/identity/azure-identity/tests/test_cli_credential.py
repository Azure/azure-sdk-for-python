# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
import json

from azure.identity import CliCredential
from azure.core.exceptions import ClientAuthenticationError

try:
    from unittest.mock import Mock
except ImportError:
    from mock import Mock


def test_cli_credential():
    access_token = '***'
    expires_on = '9999-1-1 00:00:00.1' 

    cred = CliCredential()
    cred._get_proc_stdout = Mock(return_value=json.dumps({"accessToken" : access_token, "expiresOn" : expires_on}))
    token = cred.get_token()
    assert token.token == access_token

def test_cli_installation():
    cred = CliCredential()
    
    def mock_proc(command):
        raise ClientAuthenticationError(cred._CLI_NOT_INSTALLED_ERR)
    cred._get_proc_stdout = mock_proc

    try:
        token = cred.get_token()
    except ClientAuthenticationError as e:
        assert 'Azure CLI not installed' in e.message

def test_cli_login():
    cred = CliCredential()

    def mock_proc(command):
        raise ClientAuthenticationError('Please run \'az login\' to setup account.')
    cred._get_proc_stdout = mock_proc
    
    try:
        token = cred.get_token()
    except ClientAuthenticationError as e:
        assert 'az login' in e.message
