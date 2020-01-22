# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
import json

from azure.identity import AzureCliCredential
from azure.core.exceptions import ClientAuthenticationError

from subprocess import CompletedProcess
import pytest
try:
    from unittest.mock import Mock, patch
except ImportError:
    from mock import Mock, patch


def test_cli_credential():
    access_token = '***'
    expires_on = '9999-1-1 00:00:00.1' 
    mock_token = json.dumps({"accessToken" : access_token, "expiresOn" : expires_on})
    mock_proc = CompletedProcess(args=None, stdout=mock_token, returncode=0, stderr='')

    with patch('azure.identity._credentials.cli_credential.run', return_value=mock_proc):
        cred = AzureCliCredential()
        token = cred.get_token()

        assert token.token == access_token

def test_cli_installation():
    mock_proc = CompletedProcess(args=None, stdout='', returncode=127, stderr='')

    with pytest.raises(ClientAuthenticationError) as excinfo:
        with patch('azure.identity._credentials.cli_credential.run', return_value=mock_proc):
            cred = AzureCliCredential()
            token = cred.get_token()

    assert ClientAuthenticationError == excinfo.type
    assert AzureCliCredential._CLI_NOT_INSTALLED_ERR in str(excinfo.value)

def test_cli_login():
    mock_proc = CompletedProcess(args=None, stdout='', returncode=1, stderr='')

    with pytest.raises(ClientAuthenticationError) as excinfo:
        with patch('azure.identity._credentials.cli_credential.run', return_value=mock_proc):
            cred = AzureCliCredential()
            token = cred.get_token()

    assert ClientAuthenticationError == excinfo.type
    assert AzureCliCredential._CLI_LOGIN_ERR in str(excinfo.value)

def test_stdout_error():
    def test_no_json():
        mock_token = 'not a json'
        mock_proc = CompletedProcess(args=None, stdout=mock_token, returncode=0, stderr='')

        with pytest.raises(ClientAuthenticationError) as excinfo:
            with patch('azure.identity._credentials.cli_credential.run', return_value=mock_proc):
                cred = AzureCliCredential()
                token = cred.get_token()

        assert ClientAuthenticationError == excinfo.type
        assert 'JSONDecodeError' in str(excinfo.value)

    def test_bad_token():
        mock_token = json.dumps({"foo" : "bar"})
        mock_proc = CompletedProcess(args=None, stdout=mock_token, returncode=0, stderr='')

        with pytest.raises(ClientAuthenticationError) as excinfo:
            with patch('azure.identity._credentials.cli_credential.run', return_value=mock_proc):
                cred = AzureCliCredential()
                token = cred.get_token()

        assert ClientAuthenticationError == excinfo.type
        assert 'KeyError' in str(excinfo.value)

    test_no_json()
    test_bad_token()
