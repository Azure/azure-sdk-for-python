# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
import json

from azure.identity.aio import AzureCliCredential
from azure.core.exceptions import ClientAuthenticationError

from subprocess import CompletedProcess
import pytest
from unittest.mock import Mock, patch

from helpers_async import get_completed_future


@pytest.mark.asyncio
async def test_cli_credential():
    access_token = '***'
    expires_on = '9999-1-1 00:00:00.1' 
    mock_token = json.dumps({"accessToken" : access_token, "expiresOn" : expires_on})

    mock_proc = Mock()
    attrs = {
        'returncode': 0,
        'communicate.return_value': get_completed_future((mock_token, ''))}
    mock_proc.configure_mock(**attrs)

    with patch('asyncio.create_subprocess_shell', return_value=get_completed_future(mock_proc)):
        cred = AzureCliCredential()
        token = await cred.get_token()

        assert token.token == access_token

@pytest.mark.asyncio
async def test_cli_installation():
    mock_proc = Mock()
    attrs = {
        'returncode': 127,
        'communicate.return_value': get_completed_future(('', ''))}
    mock_proc.configure_mock(**attrs)

    with pytest.raises(ClientAuthenticationError) as excinfo:
        with patch('asyncio.create_subprocess_shell', return_value=get_completed_future(mock_proc)):
            cred = AzureCliCredential()
            token = await cred.get_token()

    assert ClientAuthenticationError == excinfo.type
    assert AzureCliCredential._CLI_NOT_INSTALLED_ERR in str(excinfo.value)

@pytest.mark.asyncio
async def test_cli_login():
    mock_proc = Mock()
    attrs = {
        'returncode': 1,
        'communicate.return_value': get_completed_future(('', ''))}
    mock_proc.configure_mock(**attrs)

    with pytest.raises(ClientAuthenticationError) as excinfo:
        with patch('asyncio.create_subprocess_shell', return_value=get_completed_future(mock_proc)):
            cred = AzureCliCredential()
            token = await cred.get_token()

    assert ClientAuthenticationError == excinfo.type
    assert AzureCliCredential._CLI_LOGIN_ERR in str(excinfo.value)

@pytest.mark.asyncio
async def test_no_json():
    mock_proc = Mock()
    attrs = {
        'returncode': 0,
        'communicate.return_value': get_completed_future(('Bad*Token',''))}
    mock_proc.configure_mock(**attrs)

    with pytest.raises(ClientAuthenticationError) as excinfo:
        with patch('asyncio.create_subprocess_shell', return_value=get_completed_future(mock_proc)):
            cred = AzureCliCredential()
            token = await cred.get_token()

    assert ClientAuthenticationError == excinfo.type
    assert "Azure CLI didn't provide an access token" in str(excinfo.value)

@pytest.mark.asyncio
async def test_bad_token():
    bad_token = json.dumps({'foo': 'bar'})
    mock_proc = Mock()
    attrs = {
        'returncode': 0,
        'communicate.return_value': get_completed_future((bad_token, ''))}
    mock_proc.configure_mock(**attrs)

    with pytest.raises(ClientAuthenticationError) as excinfo:
        with patch('asyncio.create_subprocess_shell', return_value=get_completed_future(mock_proc)):
            cred = AzureCliCredential()
            token = await cred.get_token()

    assert ClientAuthenticationError == excinfo.type
    assert "Azure CLI didn't provide an access token" in str(excinfo.value)
