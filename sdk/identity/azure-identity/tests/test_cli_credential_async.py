# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
import asyncio
from datetime import datetime
from itertools import product
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

from helpers import INVALID_CHARACTERS, INVALID_SUBSCRIPTION_CHARACTERS, GET_TOKEN_METHODS
from helpers_async import get_completed_future
from test_cli_credential import TEST_ERROR_OUTPUTS

SUBPROCESS_EXEC = AzureCliCredential.__module__ + ".asyncio.create_subprocess_exec"

pytestmark = pytest.mark.asyncio


def mock_exec(stdout, stderr="", return_code=0):
    async def communicate():
        return (stdout.encode(), stderr.encode())

    process = mock.Mock(communicate=communicate, returncode=return_code)
    return mock.Mock(return_value=get_completed_future(process))


@pytest.mark.parametrize("get_token_method", GET_TOKEN_METHODS)
async def test_no_scopes(get_token_method):
    """The credential should raise ValueError when get_token is called with no scopes"""

    with pytest.raises(ValueError):
        await getattr(AzureCliCredential(), get_token_method)()


@pytest.mark.parametrize("get_token_method", GET_TOKEN_METHODS)
async def test_multiple_scopes(get_token_method):
    """The credential should raise ValueError when get_token is called with more than one scope"""

    with pytest.raises(ValueError):
        await getattr(AzureCliCredential(), get_token_method)("one scope", "and another")


@pytest.mark.parametrize("get_token_method", GET_TOKEN_METHODS)
async def test_invalid_tenant_id(get_token_method):
    """Invalid tenant IDs should raise ValueErrors."""

    for c in INVALID_CHARACTERS:
        with pytest.raises(ValueError):
            AzureCliCredential(tenant_id="tenant" + c)

        with pytest.raises(ValueError):
            kwargs = {"tenant_id": "tenant" + c}
            if get_token_method == "get_token_info":
                kwargs = {"options": kwargs}
            await getattr(AzureCliCredential(), get_token_method)("scope", **kwargs)


@pytest.mark.parametrize("get_token_method", GET_TOKEN_METHODS)
async def test_invalid_scopes(get_token_method):
    """Scopes with invalid characters should raise ValueErrors."""

    for c in INVALID_CHARACTERS:
        with pytest.raises(ValueError):
            await getattr(AzureCliCredential(), get_token_method)("https://scope" + c)


@pytest.mark.parametrize("get_token_method", GET_TOKEN_METHODS)
async def test_subscription(get_token_method):
    """The credential should accept a subscription ID"""

    subscription = "foo subscription"
    credential = AzureCliCredential(subscription=subscription)
    assert credential.subscription == subscription

    async def fake_exec(*args, **_):
        assert f'--subscription "{subscription}"' in args[-1]
        output = json.dumps(
            {
                "expiresOn": datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f"),
                "accessToken": "access-token",
                "subscription": subscription,
                "tenant": "tenant",
                "tokenType": "Bearer",
            }
        ).encode()
        return mock.Mock(communicate=mock.Mock(return_value=get_completed_future((output, b""))), returncode=0)

    with mock.patch("shutil.which", return_value="az"):
        with mock.patch(SUBPROCESS_EXEC, fake_exec):
            token = await getattr(credential, get_token_method)("scope")
            assert token.token == "access-token"


def test_invalid_subscriptons():
    """Subscriptions with invalid characters should raise ValueErrors."""

    for c in INVALID_SUBSCRIPTION_CHARACTERS:
        with pytest.raises(ValueError):
            AzureCliCredential(subscription="subscription" + c)


async def test_close():
    """The credential must define close, although it's a no-op because the credential has no transport"""

    await AzureCliCredential().close()


async def test_context_manager():
    """The credential must be a context manager, although it does nothing as one because it has no transport"""

    async with AzureCliCredential():
        pass


@pytest.mark.skipif(not sys.platform.startswith("win"), reason="tests Windows-specific behavior")
@pytest.mark.parametrize("get_token_method", GET_TOKEN_METHODS)
async def test_windows_fallback(get_token_method):
    """The credential should fall back to the sync implementation when not using ProactorEventLoop on Windows"""

    sync_get_token = mock.Mock()
    with mock.patch("azure.identity.aio._credentials.azure_cli._SyncAzureCliCredential") as fallback:
        fallback.return_value = mock.Mock(
            spec_set=["get_token", "get_token_info"], get_token=sync_get_token, get_token_info=sync_get_token
        )
        with mock.patch(AzureCliCredential.__module__ + ".asyncio.get_event_loop"):
            # asyncio.get_event_loop now returns Mock, i.e. never ProactorEventLoop
            credential = AzureCliCredential()
            await getattr(credential, get_token_method)("scope")

    assert sync_get_token.call_count == 1


@pytest.mark.parametrize("get_token_method", GET_TOKEN_METHODS)
async def test_get_token(get_token_method):
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

    with mock.patch("shutil.which", return_value="az"):
        with mock.patch(SUBPROCESS_EXEC, mock_exec(successful_output)):
            credential = AzureCliCredential()
            token = await getattr(credential, get_token_method)("scope")

    assert token.token == access_token
    assert type(token.expires_on) == int
    assert token.expires_on == expected_expires_on


@pytest.mark.parametrize("get_token_method", GET_TOKEN_METHODS)
async def test_expires_on_used(get_token_method):
    """Test that 'expires_on' is preferred over 'expiresOn'."""
    expires_on = 1602015811
    successful_output = json.dumps(
        {
            "expiresOn": datetime.fromtimestamp(1555555555).strftime("%Y-%m-%d %H:%M:%S.%f"),
            "expires_on": expires_on,
            "accessToken": "access token",
            "subscription": "some-guid",
            "tenant": "some-guid",
            "tokenType": "Bearer",
        }
    )

    with mock.patch("shutil.which", return_value="az"):
        with mock.patch(SUBPROCESS_EXEC, mock_exec(successful_output)):
            credential = AzureCliCredential()
            token = await getattr(credential, get_token_method)("scope")

    assert token.expires_on == expires_on


@pytest.mark.parametrize("get_token_method", GET_TOKEN_METHODS)
async def test_expires_on_string(get_token_method):
    """Test that 'expires_on' still works if it's a string."""
    expires_on = 1602015811
    successful_output = json.dumps(
        {
            "expires_on": f"{expires_on}",
            "accessToken": "access token",
            "subscription": "some-guid",
            "tenant": "some-guid",
            "tokenType": "Bearer",
        }
    )

    with mock.patch("shutil.which", return_value="az"):
        with mock.patch(SUBPROCESS_EXEC, mock_exec(successful_output)):
            credential = AzureCliCredential()
            token = await getattr(credential, get_token_method)("scope")

    assert type(token.expires_on) == int
    assert token.expires_on == expires_on


@pytest.mark.parametrize("get_token_method", GET_TOKEN_METHODS)
async def test_cli_not_installed(get_token_method):
    """The credential should raise CredentialUnavailableError when the CLI isn't installed"""

    with mock.patch("shutil.which", return_value=None):
        with pytest.raises(CredentialUnavailableError, match=CLI_NOT_FOUND):
            credential = AzureCliCredential()
            await getattr(credential, get_token_method)("scope")


@pytest.mark.parametrize("get_token_method", GET_TOKEN_METHODS)
async def test_cannot_execute_shell(get_token_method):
    """The credential should raise CredentialUnavailableError when the subprocess doesn't start"""

    with mock.patch("shutil.which", return_value="az"):
        with mock.patch(SUBPROCESS_EXEC, mock.Mock(side_effect=OSError())):
            with pytest.raises(CredentialUnavailableError):
                credential = AzureCliCredential()
                await getattr(credential, get_token_method)("scope")


@pytest.mark.parametrize("get_token_method", GET_TOKEN_METHODS)
async def test_not_logged_in(get_token_method):
    """When the CLI isn't logged in, the credential should raise CredentialUnavailableError"""

    stderr = "ERROR: Please run 'az login' to setup account."
    with mock.patch("shutil.which", return_value="az"):
        with mock.patch(SUBPROCESS_EXEC, mock_exec("", stderr, return_code=1)):
            with pytest.raises(CredentialUnavailableError, match=NOT_LOGGED_IN):
                credential = AzureCliCredential()
                await getattr(credential, get_token_method)("scope")


@pytest.mark.parametrize("get_token_method", GET_TOKEN_METHODS)
async def test_aadsts_error(get_token_method):
    """When the CLI isn't logged in, the credential should raise CredentialUnavailableError"""

    stderr = "ERROR: AADSTS70043: The refresh token has expired, Please run 'az login' to setup account."
    with mock.patch("shutil.which", return_value="az"):
        with mock.patch(SUBPROCESS_EXEC, mock_exec("", stderr, return_code=1)):
            with pytest.raises(ClientAuthenticationError, match=stderr):
                credential = AzureCliCredential()
                await getattr(credential, get_token_method)("scope")


@pytest.mark.parametrize("get_token_method", GET_TOKEN_METHODS)
async def test_unexpected_error(get_token_method):
    """When the CLI returns an unexpected error, the credential should raise an error containing the CLI's output"""

    stderr = "something went wrong"
    with mock.patch("shutil.which", return_value="az"):
        with mock.patch(SUBPROCESS_EXEC, mock_exec("", stderr, return_code=42)):
            with pytest.raises(ClientAuthenticationError, match=stderr):
                credential = AzureCliCredential()
                await getattr(credential, get_token_method)("scope")


@pytest.mark.parametrize("output,get_token_method", product(TEST_ERROR_OUTPUTS, GET_TOKEN_METHODS))
async def test_parsing_error_does_not_expose_token(output, get_token_method):
    """Errors during CLI output parsing shouldn't expose access tokens in that output"""

    with mock.patch("shutil.which", return_value="az"):
        with mock.patch(SUBPROCESS_EXEC, mock_exec(output)):
            with pytest.raises(ClientAuthenticationError) as ex:
                credential = AzureCliCredential()
                await getattr(credential, get_token_method)("scope")

    assert "secret value" not in str(ex.value)
    assert "secret value" not in repr(ex.value)


@pytest.mark.parametrize("output,get_token_method", product(TEST_ERROR_OUTPUTS, GET_TOKEN_METHODS))
async def test_subprocess_error_does_not_expose_token(output, get_token_method):
    """Errors from the subprocess shouldn't expose access tokens in CLI output"""

    with mock.patch("shutil.which", return_value="az"):
        with mock.patch(SUBPROCESS_EXEC, mock_exec(output, return_code=1)):
            with pytest.raises(ClientAuthenticationError) as ex:
                credential = AzureCliCredential()
                await getattr(credential, get_token_method)("scope")

    assert "secret value" not in str(ex.value)
    assert "secret value" not in repr(ex.value)


@pytest.mark.parametrize("get_token_method", GET_TOKEN_METHODS)
async def test_timeout(get_token_method):
    """The credential should kill the subprocess after a timeout"""

    proc = mock.Mock(communicate=mock.Mock(side_effect=asyncio.TimeoutError), returncode=None)
    with mock.patch("shutil.which", return_value="az"):
        with mock.patch(SUBPROCESS_EXEC, mock.Mock(return_value=get_completed_future(proc))):
            with pytest.raises(CredentialUnavailableError):
                await getattr(AzureCliCredential(), get_token_method)("scope")

    assert proc.communicate.call_count == 1


@pytest.mark.parametrize("get_token_method", GET_TOKEN_METHODS)
async def test_multitenant_authentication(get_token_method):
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
    with mock.patch("shutil.which", return_value="az"):
        with mock.patch(SUBPROCESS_EXEC, fake_exec):
            token = await getattr(credential, get_token_method)("scope")
            assert token.token == first_token

            kwargs = {"tenant_id": default_tenant}
            if get_token_method == "get_token_info":
                kwargs = {"options": kwargs}
            token = await getattr(credential, get_token_method)("scope", **kwargs)
            assert token.token == first_token

            kwargs = {"tenant_id": second_tenant}
            if get_token_method == "get_token_info":
                kwargs = {"options": kwargs}
            token = await getattr(credential, get_token_method)("scope", **kwargs)
            assert token.token == second_token

            # should still default to the first tenant
            token = await getattr(credential, get_token_method)("scope")
            assert token.token == first_token


@pytest.mark.parametrize("get_token_method", GET_TOKEN_METHODS)
async def test_multitenant_authentication_not_allowed(get_token_method):
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
    with mock.patch("shutil.which", return_value="az"):
        with mock.patch(SUBPROCESS_EXEC, fake_exec):
            token = await getattr(credential, get_token_method)("scope")
            assert token.token == expected_token

            with mock.patch.dict("os.environ", {EnvironmentVariables.AZURE_IDENTITY_DISABLE_MULTITENANTAUTH: "true"}):
                kwargs = {"tenant_id": "un" + expected_tenant}
                if get_token_method == "get_token_info":
                    kwargs = {"options": kwargs}
                token = await getattr(credential, get_token_method)("scope", **kwargs)
            assert token.token == expected_token
