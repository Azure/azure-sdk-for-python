# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
import json

from azure.identity.aio import AzureCliCredential
from azure.core.exceptions import ClientAuthenticationError

from subprocess import CompletedProcess
import pytest
try:
    from unittest.mock import Mock, patch
except ImportError:
    from mock import Mock, patch


@pytest.mark.asyncio
async def test_cli_credential():
    access_token = '***'
    expires_on = '9999-1-1 00:00:00.1' 
    mock_token = json.dumps({"accessToken" : access_token, "expiresOn" : expires_on})

    mock_proc = Mock()
    attrs = {
        'wait.return_value': 0,
        'stdout.read.return_value': mock_token,
        'stderr.read.return_value': ''}
    mock_proc.configure_mock(**attrs)

    with patch('azure.identity.aio._credentials.cli_credential.Popen', return_value=mock_proc):
        cred = AzureCliCredential()
        token = await cred.get_token()

        assert token.token == access_token

@pytest.mark.asyncio
async def test_cli_installation():
    mock_proc = Mock()
    attrs = {
        'wait.return_value': 127,
        'stdout.read.return_value': '',
        'stderr.read.return_value': ''}
    mock_proc.configure_mock(**attrs)

    with pytest.raises(ClientAuthenticationError) as excinfo:
        with patch('azure.identity.aio._credentials.cli_credential.Popen', return_value=mock_proc):
            cred = AzureCliCredential()
            token = await cred.get_token()

    assert ClientAuthenticationError == excinfo.type
    assert AzureCliCredential._CLI_NOT_INSTALLED_ERR in str(excinfo.value)

@pytest.mark.asyncio
async def test_cli_login():
    mock_proc = Mock()
    attrs = {
        'wait.return_value': 1,
        'stdout.read.return_value': '',
        'stderr.read.return_value': ''}
    mock_proc.configure_mock(**attrs)

    with pytest.raises(ClientAuthenticationError) as excinfo:
        with patch('azure.identity.aio._credentials.cli_credential.Popen', return_value=mock_proc):
            cred = AzureCliCredential()
            token = await cred.get_token()

    assert ClientAuthenticationError == excinfo.type
    assert AzureCliCredential._CLI_LOGIN_ERR in str(excinfo.value)

@pytest.mark.asyncio
async def test_stdout_error():
    async def test_no_json():
        mock_proc = Mock()
        attrs = {
            'wait.return_value': 0,
            'stdout.read.return_value': 'Bad*Token',
            'stderr.read.return_value': ''}
        mock_proc.configure_mock(**attrs)

        with pytest.raises(ClientAuthenticationError) as excinfo:
            with patch('azure.identity.aio._credentials.cli_credential.Popen', return_value=mock_proc):
                cred = AzureCliCredential()
                token = await cred.get_token()

        assert ClientAuthenticationError == excinfo.type
        assert 'JSONDecodeError' in str(excinfo.value)

    async def test_bad_token():
        bad_token = json.dumps({'foo': 'bar'})
        mock_proc = Mock()
        attrs = {
            'wait.return_value': 0,
            'stdout.read.return_value': bad_token,
            'stderr.read.return_value': ''}
        mock_proc.configure_mock(**attrs)

        with pytest.raises(ClientAuthenticationError) as excinfo:
            with patch('azure.identity.aio._credentials.cli_credential.Popen', return_value=mock_proc):
                cred = AzureCliCredential()
                token = await cred.get_token()

        assert ClientAuthenticationError == excinfo.type
        assert 'KeyError' in str(excinfo.value)

    await test_no_json()
    await test_bad_token()
