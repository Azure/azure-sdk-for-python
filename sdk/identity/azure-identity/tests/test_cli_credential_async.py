# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
from datetime import datetime
import json
from unittest import mock

from azure.identity import CredentialUnavailableError, AzureCliCredential as _SyncCredential
from azure.identity.aio import AzureCliCredential
from azure.identity._credentials.azure_cli import CLI_NOT_FOUND
from azure.core.exceptions import ClientAuthenticationError
import pytest

from test_cli_credential import raise_called_process_error, TEST_ERROR_OUTPUTS

CHECK_OUTPUT = _SyncCredential.__module__ + ".subprocess.check_output"


@pytest.mark.asyncio
async def test_close():
    """the credential must define close, although it's a no-op because the credential has no transport"""

    await AzureCliCredential().close()


@pytest.mark.asyncio
async def test_context_manager():
    """the credential must be a context manager, although it does nothing as one because it has no transport"""

    async with AzureCliCredential():
        pass


@pytest.mark.asyncio
async def test_get_token():
    """The credential should parse the CLI's output to an AccessToken"""

    access_token = "access token"
    valid_seconds = 42
    successful_output = json.dumps(
        {
            # expiresOn is a naive datetime representing valid_seconds from the epoch
            "expiresOn": datetime.fromtimestamp(valid_seconds).strftime("%Y-%m-%d %H:%M:%S.%f"),
            "accessToken": access_token,
            "subscription": "some-guid",
            "tenant": "some-guid",
            "tokenType": "Bearer",
        }
    )

    with mock.patch(CHECK_OUTPUT, mock.Mock(return_value=successful_output)):
        credential = AzureCliCredential()
        token = await credential.get_token("scope")

    assert token.token == access_token
    assert type(token.expires_on) == int
    assert token.expires_on == valid_seconds


@pytest.mark.asyncio
async def test_cli_not_installed_linux():
    """The credential should raise CredentialUnavailableError when the CLI isn't installed"""

    output = "/bin/sh: 1: az: not found"
    with mock.patch(CHECK_OUTPUT, raise_called_process_error(127, output)):
        with pytest.raises(CredentialUnavailableError, match=CLI_NOT_FOUND):
            credential = AzureCliCredential()
            await credential.get_token("scope")


@pytest.mark.asyncio
async def test_cli_not_installed_windows():
    """The credential should raise CredentialUnavailableError when the CLI isn't installed"""

    output = "'az' is not recognized as an internal or external command, operable program or batch file."
    with mock.patch(CHECK_OUTPUT, raise_called_process_error(1, output)):
        with pytest.raises(CredentialUnavailableError, match=CLI_NOT_FOUND):
            credential = AzureCliCredential()
            await credential.get_token("scope")


@pytest.mark.parametrize("platform", ("darwin", "linux2", "win32"))
@pytest.mark.asyncio
async def test_cannot_execute_shell(platform):
    """The credential should raise CredentialUnavailableError when the subprocess doesn't start"""

    with mock.patch(_SyncCredential.__module__ + ".sys.platform", platform):
        with mock.patch(CHECK_OUTPUT, mock.Mock(side_effect=OSError())):
            with pytest.raises(CredentialUnavailableError):
                credential = AzureCliCredential()
                await credential.get_token("scope")


@pytest.mark.asyncio
async def test_not_logged_in():
    """When the CLI isn't logged in, the credential should raise an error containing the CLI's output"""

    output = "ERROR: Please run 'az login' to setup account."
    with mock.patch(CHECK_OUTPUT, raise_called_process_error(1, output)):
        with pytest.raises(ClientAuthenticationError, match=output):
            credential = AzureCliCredential()
            await credential.get_token("scope")


@pytest.mark.parametrize("output", TEST_ERROR_OUTPUTS)
@pytest.mark.asyncio
async def test_parsing_error_does_not_expose_token(output):
    """Errors during CLI output parsing shouldn't expose access tokens in that output"""

    with mock.patch(CHECK_OUTPUT, mock.Mock(return_value=output)):
        with pytest.raises(ClientAuthenticationError) as ex:
            credential = AzureCliCredential()
            await credential.get_token("scope")

    assert "secret value" not in str(ex.value)
    assert "secret value" not in repr(ex.value)


@pytest.mark.parametrize("output", TEST_ERROR_OUTPUTS)
@pytest.mark.asyncio
async def test_subprocess_error_does_not_expose_token(output):
    """Errors from the subprocess shouldn't expose access tokens in CLI output"""

    with mock.patch(CHECK_OUTPUT, raise_called_process_error(1, output=output)):
        with pytest.raises(ClientAuthenticationError) as ex:
            credential = AzureCliCredential()
            await credential.get_token("scope")

    assert "secret value" not in str(ex.value)
    assert "secret value" not in repr(ex.value)
