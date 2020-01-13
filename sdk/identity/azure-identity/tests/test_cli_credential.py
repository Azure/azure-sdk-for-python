# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
import json

from azure.identity import CliCredential
from azure.core.exceptions import ClientAuthenticationError

from subprocess import CalledProcessError
try:
    from unittest.mock import Mock, patch
except ImportError:
    from mock import Mock, patch


def test_cli_credential():
    access_token = '***'
    expires_on = '9999-1-1 00:00:00.1' 
    mock_token = json.dumps({"accessToken" : access_token, "expiresOn" : expires_on})

    with patch('azure.identity._credentials.cli_credential.check_output', return_value=mock_token):
        cred = CliCredential()
        token = cred.get_token()
        assert token.token == access_token

def test_cli_installation():
    cmd = ['az', 'account', 'get-access-token']
    with patch('azure.identity._credentials.cli_credential.check_output',
        side_effect=[CalledProcessError(1, cmd, "'az' is not recognized as ..."),
            FileNotFoundError("No such file or directory: 'az'"),
            CalledProcessError(1, cmd, "command not found")]):

        creds = (
            CliCredential(), # cred on windows
            CliCredential(), # cred on mac
            CliCredential()  # cred on linux
        )
        for cred in creds:
            try:
                token = cred.get_token()
            except ClientAuthenticationError as e:
                assert CliCredential._CLI_NOT_INSTALLED_ERR in e.message

def test_cli_login():
    cmd = ['az', 'account', 'get-access-token']
    with patch('azure.identity._credentials.cli_credential.check_output',
        side_effect=[CalledProcessError(1, cmd, "Please run 'az login'"),
            CalledProcessError(1, cmd, "No subscription found"),
            CalledProcessError(1, cmd, "Please run 'az login'")]):

        creds = (
            CliCredential(), # cred on windows
            CliCredential(), # cred on mac
            CliCredential()  # cred on linux
        )
        for cred in creds:
            try:
                token = cred.get_token()
            except ClientAuthenticationError as e:
                assert CliCredential._CLI_LOGIN_ERR in e.message
