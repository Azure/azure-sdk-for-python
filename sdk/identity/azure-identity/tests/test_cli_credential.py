# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
from datetime import datetime
import json
import re

from azure.identity import AzureCliCredential, CredentialUnavailableError
from azure.identity._constants import EnvironmentVariables
from azure.identity._credentials.azure_cli import CLI_NOT_FOUND, NOT_LOGGED_IN
from azure.core.exceptions import ClientAuthenticationError

import subprocess
import pytest

from helpers import mock, INVALID_CHARACTERS

CHECK_OUTPUT = AzureCliCredential.__module__ + ".subprocess.check_output"

TEST_ERROR_OUTPUTS = (
    '{"accessToken": "secret value',
    '{"accessToken": "secret value"',
    '{"accessToken": "secret value and some other nonsense"',
    '{"accessToken": "secret value", some invalid json, "accessToken": "secret value"}',
    '{"accessToken": "secret value"}',
    '{"accessToken": "secret value", "subscription": "some-guid", "tenant": "some-guid", "tokenType": "Bearer"}',
    "no secrets or json here",
    "{}",
)


def raise_called_process_error(return_code, output="", cmd="...", stderr=""):
    error = subprocess.CalledProcessError(return_code, cmd=cmd, output=output, stderr=stderr)
    return mock.Mock(side_effect=error)


def test_no_scopes():
    """The credential should raise ValueError when get_token is called with no scopes"""

    with pytest.raises(ValueError):
        AzureCliCredential().get_token()


def test_multiple_scopes():
    """The credential should raise ValueError when get_token is called with more than one scope"""

    with pytest.raises(ValueError):
        AzureCliCredential().get_token("one scope", "and another")


def test_invalid_tenant_id():
    """Invalid tenant IDs should raise ValueErrors."""

    for c in INVALID_CHARACTERS:
        with pytest.raises(ValueError):
            AzureCliCredential(tenant_id="tenant" + c)

        with pytest.raises(ValueError):
            AzureCliCredential().get_token("scope", tenant_id="tenant" + c)


def test_invalid_scopes():
    """Scopes with invalid characters should raise ValueErrors."""

    for c in INVALID_CHARACTERS:
        with pytest.raises(ValueError):
            AzureCliCredential().get_token("scope" + c)


def test_get_token():
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
        with mock.patch(CHECK_OUTPUT, mock.Mock(return_value=successful_output)):
            token = AzureCliCredential().get_token("scope")

    assert token.token == access_token
    assert type(token.expires_on) == int
    assert token.expires_on == expected_expires_on


def test_cli_not_installed():
    """The credential should raise CredentialUnavailableError when the CLI isn't installed"""
    with mock.patch("shutil.which", return_value=None):
        with pytest.raises(CredentialUnavailableError, match=CLI_NOT_FOUND):
            AzureCliCredential().get_token("scope")


def test_cannot_execute_shell():
    """The credential should raise CredentialUnavailableError when the subprocess doesn't start"""

    with mock.patch("shutil.which", return_value="az"):
        with mock.patch(CHECK_OUTPUT, mock.Mock(side_effect=OSError())):
            with pytest.raises(CredentialUnavailableError):
                AzureCliCredential().get_token("scope")


def test_not_logged_in():
    """When the CLI isn't logged in, the credential should raise CredentialUnavailableError"""

    stderr = "ERROR: Please run 'az login' to setup account."
    with mock.patch("shutil.which", return_value="az"):
        with mock.patch(CHECK_OUTPUT, raise_called_process_error(1, stderr=stderr)):
            with pytest.raises(CredentialUnavailableError, match=NOT_LOGGED_IN):
                AzureCliCredential().get_token("scope")


def test_aadsts_error():
    """When the CLI isn't logged in, the credential should raise CredentialUnavailableError"""

    stderr = "ERROR: AADSTS70043: The refresh token has expired, Please run 'az login' to setup account."
    with mock.patch("shutil.which", return_value="az"):
        with mock.patch(CHECK_OUTPUT, raise_called_process_error(1, stderr=stderr)):
            with pytest.raises(ClientAuthenticationError, match=stderr):
                AzureCliCredential().get_token("scope")


def test_unexpected_error():
    """When the CLI returns an unexpected error, the credential should raise an error containing the CLI's output"""

    stderr = "something went wrong"
    with mock.patch("shutil.which", return_value="az"):
        with mock.patch(CHECK_OUTPUT, raise_called_process_error(42, stderr=stderr)):
            with pytest.raises(ClientAuthenticationError, match=stderr):
                AzureCliCredential().get_token("scope")


@pytest.mark.parametrize("output", TEST_ERROR_OUTPUTS)
def test_parsing_error_does_not_expose_token(output):
    """Errors during CLI output parsing shouldn't expose access tokens in that output"""

    with mock.patch("shutil.which", return_value="az"):
        with mock.patch(CHECK_OUTPUT, mock.Mock(return_value=output)):
            with pytest.raises(ClientAuthenticationError) as ex:
                AzureCliCredential().get_token("scope")

    assert "secret value" not in str(ex.value)
    assert "secret value" not in repr(ex.value)


@pytest.mark.parametrize("output", TEST_ERROR_OUTPUTS)
def test_subprocess_error_does_not_expose_token(output):
    """Errors from the subprocess shouldn't expose access tokens in CLI output"""

    with mock.patch("shutil.which", return_value="az"):
        with mock.patch(CHECK_OUTPUT, raise_called_process_error(1, output=output)):
            with pytest.raises(ClientAuthenticationError) as ex:
                AzureCliCredential().get_token("scope")

    assert "secret value" not in str(ex.value)
    assert "secret value" not in repr(ex.value)


def test_timeout():
    """The credential should raise CredentialUnavailableError when the subprocess times out"""

    from subprocess import TimeoutExpired

    with mock.patch("shutil.which", return_value="az"):
        with mock.patch(CHECK_OUTPUT, mock.Mock(side_effect=TimeoutExpired("", 42))) as check_output_mock:
            with pytest.raises(CredentialUnavailableError):
                AzureCliCredential(process_timeout=42).get_token("scope")

    # Ensure custom timeout is passed to subprocess
    _, kwargs = check_output_mock.call_args
    assert "timeout" in kwargs
    assert kwargs["timeout"] == 42


def test_multitenant_authentication_class():
    default_tenant = "first-tenant"
    first_token = "***"
    second_tenant = "second-tenant"
    second_token = first_token * 2

    def fake_check_output(command_line, **_):
        match = re.search("--tenant (.*)", command_line[-1])
        tenant = match.groups()[0] if match else default_tenant
        assert tenant in (default_tenant, second_tenant), 'unexpected tenant "{}"'.format(tenant)
        return json.dumps(
            {
                "expiresOn": datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f"),
                "accessToken": first_token if tenant == default_tenant else second_token,
                "subscription": "some-guid",
                "tenant": tenant,
                "tokenType": "Bearer",
            }
        )

    with mock.patch("shutil.which", return_value="az"):
        with mock.patch(CHECK_OUTPUT, fake_check_output):
            token = AzureCliCredential().get_token("scope")
            assert token.token == first_token

            token = AzureCliCredential(tenant_id=default_tenant).get_token("scope")
            assert token.token == first_token

            token = AzureCliCredential(tenant_id=second_tenant).get_token("scope")
            assert token.token == second_token


def test_multitenant_authentication():
    default_tenant = "first-tenant"
    first_token = "***"
    second_tenant = "second-tenant"
    second_token = first_token * 2

    def fake_check_output(command_line, **_):
        match = re.search("--tenant (.*)", command_line[-1])
        tenant = match.groups()[0] if match else default_tenant
        assert tenant in (default_tenant, second_tenant), 'unexpected tenant "{}"'.format(tenant)
        return json.dumps(
            {
                "expiresOn": datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f"),
                "accessToken": first_token if tenant == default_tenant else second_token,
                "subscription": "some-guid",
                "tenant": tenant,
                "tokenType": "Bearer",
            }
        )

    credential = AzureCliCredential()
    with mock.patch("shutil.which", return_value="az"):
        with mock.patch(CHECK_OUTPUT, fake_check_output):
            token = credential.get_token("scope")
            assert token.token == first_token

            token = credential.get_token("scope", tenant_id=default_tenant)
            assert token.token == first_token

            token = credential.get_token("scope", tenant_id=second_tenant)
            assert token.token == second_token

            # should still default to the first tenant
            token = credential.get_token("scope")
            assert token.token == first_token


def test_multitenant_authentication_not_allowed():
    expected_tenant = "expected-tenant"
    expected_token = "***"

    def fake_check_output(command_line, **_):
        match = re.search("--tenant (.*)", command_line[-1])
        assert match is None or match[1] == expected_tenant
        return json.dumps(
            {
                "expiresOn": datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f"),
                "accessToken": expected_token,
                "subscription": "some-guid",
                "tenant": expected_token,
                "tokenType": "Bearer",
            }
        )

    credential = AzureCliCredential()
    with mock.patch("shutil.which", return_value="az"):
        with mock.patch(CHECK_OUTPUT, fake_check_output):
            token = credential.get_token("scope")
            assert token.token == expected_token

            with mock.patch.dict("os.environ", {EnvironmentVariables.AZURE_IDENTITY_DISABLE_MULTITENANTAUTH: "true"}):
                token = credential.get_token("scope", tenant_id="un" + expected_tenant)
            assert token.token == expected_token
