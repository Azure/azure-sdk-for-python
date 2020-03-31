# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
from datetime import datetime
import json

from azure.identity import CredentialUnavailableError
from azure.identity._credentials.azure_cli import AzureCliCredential, CLI_NOT_FOUND
from azure.core.exceptions import ClientAuthenticationError

import subprocess
import pytest

from helpers import mock

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


def raise_called_process_error(return_code, output, cmd="..."):
    error = subprocess.CalledProcessError(return_code, cmd=cmd, output=output)
    return mock.Mock(side_effect=error)


def test_no_scopes():
    """The credential should raise ValueError when get_token is called with no scopes"""

    with pytest.raises(ValueError):
        AzureCliCredential().get_token()


def test_multiple_scopes():
    """The credential should raise ValueError when get_token is called with more than one scope"""

    with pytest.raises(ValueError):
        AzureCliCredential().get_token("one scope", "and another")


def test_get_token():
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
        token = AzureCliCredential().get_token("scope")

    assert token.token == access_token
    assert type(token.expires_on) == int
    assert token.expires_on == valid_seconds


def test_cli_not_installed_linux():
    """The credential should raise CredentialUnavailableError when the CLI isn't installed"""

    output = "/bin/sh: 1: az: not found"
    with mock.patch(CHECK_OUTPUT, raise_called_process_error(127, output)):
        with pytest.raises(CredentialUnavailableError, match=CLI_NOT_FOUND):
            AzureCliCredential().get_token("scope")


def test_cli_not_installed_windows():
    """The credential should raise CredentialUnavailableError when the CLI isn't installed"""

    output = "'az' is not recognized as an internal or external command, operable program or batch file."
    with mock.patch(CHECK_OUTPUT, raise_called_process_error(1, output)):
        with pytest.raises(CredentialUnavailableError, match=CLI_NOT_FOUND):
            AzureCliCredential().get_token("scope")


def test_cannot_execute_shell():
    """The credential should raise CredentialUnavailableError when the subprocess doesn't start"""

    with mock.patch(CHECK_OUTPUT, mock.Mock(side_effect=OSError())):
        with pytest.raises(CredentialUnavailableError):
            AzureCliCredential().get_token("scope")


def test_not_logged_in():
    """When the CLI isn't logged in, the credential should raise an error containing the CLI's output"""

    output = "ERROR: Please run 'az login' to setup account."
    with mock.patch(CHECK_OUTPUT, raise_called_process_error(1, output)):
        with pytest.raises(ClientAuthenticationError, match=output):
            AzureCliCredential().get_token("scope")


@pytest.mark.parametrize("output", TEST_ERROR_OUTPUTS)
def test_parsing_error_does_not_expose_token(output):
    """Errors during CLI output parsing shouldn't expose access tokens in that output"""

    with mock.patch(CHECK_OUTPUT, mock.Mock(return_value=output)):
        with pytest.raises(ClientAuthenticationError) as ex:
            AzureCliCredential().get_token("scope")

    assert "secret value" not in str(ex.value)
    assert "secret value" not in repr(ex.value)


@pytest.mark.parametrize("output", TEST_ERROR_OUTPUTS)
def test_subprocess_error_does_not_expose_token(output):
    """Errors from the subprocess shouldn't expose access tokens in CLI output"""

    with mock.patch(CHECK_OUTPUT, raise_called_process_error(1, output=output)):
        with pytest.raises(ClientAuthenticationError) as ex:
            AzureCliCredential().get_token("scope")

    assert "secret value" not in str(ex.value)
    assert "secret value" not in repr(ex.value)
