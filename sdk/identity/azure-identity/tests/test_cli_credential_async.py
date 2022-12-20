# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
import asyncio
from datetime import datetime
import json
import re
import sys
from unittest import mock

from azure.identity import CredentialUnavailableError
from azure.identity.aio import AzureCliCredential
from azure.identity._constants import EnvironmentVariables
from azure.identity._credentials.azure_cli import CLI_NOT_FOUND, NOT_LOGGED_IN
from azure.core.exceptions import ClientAuthenticationError
import pytest

from helpers_async import get_completed_future
from test_cli_credential import TEST_ERROR_OUTPUTS

SUBPROCESS_EXEC = AzureCliCredential.__module__ + ".asyncio.create_subprocess_exec"

pytestmark = pytest.mark.asyncio


def mock_exec(stdout, stderr="", return_code=0):
    async def communicate():
        return (stdout.encode(), stderr.encode())

    process = mock.Mock(communicate=communicate, returncode=return_code)
    return mock.Mock(return_value=get_completed_future(process))


async def test_no_scopes():
    """The credential should raise ValueError when get_token is called with no scopes"""

    with pytest.raises(ValueError):
        await AzureCliCredential().get_token()


async def test_multiple_scopes():
    """The credential should raise ValueError when get_token is called with more than one scope"""

    with pytest.raises(ValueError):
        await AzureCliCredential().get_token("one scope", "and another")


async def test_close():
    """The credential must define close, although it's a no-op because the credential has no transport"""

    await AzureCliCredential().close()


async def test_context_manager():
    """The credential must be a context manager, although it does nothing as one because it has no transport"""

    async with AzureCliCredential():
        pass


@pytest.mark.skipif(not sys.platform.startswith("win"), reason="tests Windows-specific behavior")
async def test_windows_fallback():
    """The credential should fall back to the sync implementation when not using ProactorEventLoop on Windows"""

    sync_get_token = mock.Mock()
    with mock.patch("azure.identity.aio._credentials.azure_cli._SyncAzureCliCredential") as fallback:
        fallback.return_value = mock.Mock(get_token=sync_get_token)
        with mock.patch(AzureCliCredential.__module__ + ".asyncio.get_event_loop"):
            # asyncio.get_event_loop now returns Mock, i.e. never ProactorEventLoop
            credential = AzureCliCredential()
            await credential.get_token("scope")

    assert sync_get_token.call_count == 1


async def test_get_token():
    """The credential should parse the CLI's output to an AccessToken"""

    access_token = "access token"
    expected_expires_on = 1602015811
    successful_output = json.dumps(
        {
            "expiresOn": datetime.fromtimestamp(expected_expires_on).strftime("%Y-%m-%d %H:%M:%S.%f"),
            "accessToken": access_token,
            "subscription": "some-guid",
            "tenant": "some-guid",
            "tokenType": "Bearer",
        }
    )

    with mock.patch(SUBPROCESS_EXEC, mock_exec(successful_output)):
        credential = AzureCliCredential()
        token = await credential.get_token("scope")

    assert token.token == access_token
    assert type(token.expires_on) == int
    assert token.expires_on == expected_expires_on


async def test_cli_not_installed_linux():
    """The credential should raise CredentialUnavailableError when the CLI isn't installed"""

    stderr = "/bin/sh: 1: az: not found"
    with mock.patch(SUBPROCESS_EXEC, mock_exec("", stderr, return_code=127)):
        with pytest.raises(CredentialUnavailableError, match=CLI_NOT_FOUND):
            credential = AzureCliCredential()
            await credential.get_token("scope")


async def test_cli_not_installed_windows():
    """The credential should raise CredentialUnavailableError when the CLI isn't installed"""

    stderr = "'az' is not recognized as an internal or external command, operable program or batch file."
    with mock.patch(SUBPROCESS_EXEC, mock_exec("", stderr, return_code=1)):
        with pytest.raises(CredentialUnavailableError, match=CLI_NOT_FOUND):
            credential = AzureCliCredential()
            await credential.get_token("scope")


async def test_cannot_execute_shell():
    """The credential should raise CredentialUnavailableError when the subprocess doesn't start"""

    with mock.patch(SUBPROCESS_EXEC, mock.Mock(side_effect=OSError())):
        with pytest.raises(CredentialUnavailableError):
            credential = AzureCliCredential()
            await credential.get_token("scope")


async def test_not_logged_in():
    """When the CLI isn't logged in, the credential should raise CredentialUnavailableError"""

    stderr = "ERROR: Please run 'az login' to setup account."
    with mock.patch(SUBPROCESS_EXEC, mock_exec("", stderr, return_code=1)):
        with pytest.raises(CredentialUnavailableError, match=NOT_LOGGED_IN):
            credential = AzureCliCredential()
            await credential.get_token("scope")


async def test_unexpected_error():
    """When the CLI returns an unexpected error, the credential should raise an error containing the CLI's output"""

    stderr = "something went wrong"
    with mock.patch(SUBPROCESS_EXEC, mock_exec("", stderr, return_code=42)):
        with pytest.raises(ClientAuthenticationError, match=stderr):
            credential = AzureCliCredential()
            await credential.get_token("scope")


@pytest.mark.parametrize("output", TEST_ERROR_OUTPUTS)
async def test_parsing_error_does_not_expose_token(output):
    """Errors during CLI output parsing shouldn't expose access tokens in that output"""

    with mock.patch(SUBPROCESS_EXEC, mock_exec(output)):
        with pytest.raises(ClientAuthenticationError) as ex:
            credential = AzureCliCredential()
            await credential.get_token("scope")

    assert "secret value" not in str(ex.value)
    assert "secret value" not in repr(ex.value)


@pytest.mark.parametrize("output", TEST_ERROR_OUTPUTS)
async def test_subprocess_error_does_not_expose_token(output):
    """Errors from the subprocess shouldn't expose access tokens in CLI output"""

    with mock.patch(SUBPROCESS_EXEC, mock_exec(output, return_code=1)):
        with pytest.raises(ClientAuthenticationError) as ex:
            credential = AzureCliCredential()
            await credential.get_token("scope")

    assert "secret value" not in str(ex.value)
    assert "secret value" not in repr(ex.value)


async def test_timeout():
    """The credential should kill the subprocess after a timeout"""

    proc = mock.Mock(communicate=mock.Mock(side_effect=asyncio.TimeoutError), returncode=None)
    with mock.patch(SUBPROCESS_EXEC, mock.Mock(return_value=get_completed_future(proc))):
        with pytest.raises(CredentialUnavailableError):
            await AzureCliCredential().get_token("scope")

    assert proc.communicate.call_count == 1


async def test_multitenant_authentication():
    default_tenant = "first-tenant"
    first_token = "***"
    second_tenant = "second-tenant"
    second_token = first_token * 2

    async def fake_exec(*args, **_):
        match = re.search("--tenant (.*)", args[-1])
        tenant = match[1] if match else default_tenant
        assert tenant in (default_tenant, second_tenant), 'unexpected tenant "{}"'.format(tenant)
        output = json.dumps(
            {
                "expiresOn": datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f"),
                "accessToken": first_token if tenant == default_tenant else second_token,
                "subscription": "some-guid",
                "tenant": tenant,
                "tokenType": "Bearer",
            }
        ).encode()
        return mock.Mock(communicate=mock.Mock(return_value=get_completed_future((output, b""))), returncode=0)

    credential = AzureCliCredential()
    with mock.patch(SUBPROCESS_EXEC, fake_exec):
        token = await credential.get_token("scope")
        assert token.token == first_token

        token = await credential.get_token("scope", tenant_id=default_tenant)
        assert token.token == first_token

        token = await credential.get_token("scope", tenant_id=second_tenant)
        assert token.token == second_token

        # should still default to the first tenant
        token = await credential.get_token("scope")
        assert token.token == first_token

async def test_multitenant_authentication_not_allowed():
    expected_tenant = "expected-tenant"
    expected_token = "***"

    async def fake_exec(*args, **_):
        match = re.search("--tenant (.*)", args[-1])
        assert match is None or match[1] == expected_tenant
        output = json.dumps(
            {
                "expiresOn": datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f"),
                "accessToken": expected_token,
                "subscription": "some-guid",
                "tenant": expected_token,
                "tokenType": "Bearer",
            }
        ).encode()
        return mock.Mock(communicate=mock.Mock(return_value=get_completed_future((output, b""))), returncode=0)

    credential = AzureCliCredential()
    with mock.patch(SUBPROCESS_EXEC, fake_exec):
        token = await credential.get_token("scope")
        assert token.token == expected_token

        with mock.patch.dict("os.environ", {EnvironmentVariables.AZURE_IDENTITY_DISABLE_MULTITENANTAUTH: "true"}):
            token = await credential.get_token("scope", tenant_id="un" + expected_tenant)
        assert token.token == expected_token
