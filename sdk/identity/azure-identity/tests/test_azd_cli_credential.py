# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
from datetime import datetime
import json
import re

from azure.identity import AzureDeveloperCliCredential, CredentialUnavailableError
from azure.identity._constants import EnvironmentVariables
from azure.identity._credentials.azd_cli import CLI_NOT_FOUND, NOT_LOGGED_IN, COMMAND_LINE, extract_cli_error_message
from azure.core.exceptions import ClientAuthenticationError

import subprocess
import pytest

from helpers import mock, INVALID_CHARACTERS, GET_TOKEN_METHODS

CHECK_OUTPUT = AzureDeveloperCliCredential.__module__ + ".subprocess.check_output"

TEST_ERROR_OUTPUTS = (
    '{"token": "secret value',
    '{"token": "secret value"',
    '{"token": "secret value and some other nonsense"',
    '{"token": "secret value", some invalid json, "token": "secret value"}',
    '{"token": "secret value"}',
    '{"token": "secret value", "subscription": "some-guid", "tenant": "some-guid", "tokenType": "Bearer"}',
    "no secrets or json here",
    "{}",
)


def raise_called_process_error(return_code, output="", cmd="...", stderr=""):
    error = subprocess.CalledProcessError(return_code, cmd=cmd, output=output, stderr=stderr)
    return mock.Mock(side_effect=error)


@pytest.mark.parametrize("get_token_method", GET_TOKEN_METHODS)
def test_no_scopes(get_token_method):
    """The credential should raise ValueError when get_token is called with no scopes"""

    with pytest.raises(ValueError):
        getattr(AzureDeveloperCliCredential(), get_token_method)()


@pytest.mark.parametrize("get_token_method", GET_TOKEN_METHODS)
def test_invalid_tenant_id(get_token_method):
    """Invalid tenant IDs should raise ValueErrors."""

    for c in INVALID_CHARACTERS:
        with pytest.raises(ValueError):
            AzureDeveloperCliCredential(tenant_id="tenant" + c)

        with pytest.raises(ValueError):
            kwargs = {"tenant_id": "tenant" + c}
            if get_token_method == "get_token_info":
                kwargs = {"options": kwargs}
            getattr(AzureDeveloperCliCredential(), get_token_method)("scope", **kwargs)


@pytest.mark.parametrize("get_token_method", GET_TOKEN_METHODS)
def test_invalid_scopes(get_token_method):
    """Scopes with invalid characters should raise ValueErrors."""

    for c in INVALID_CHARACTERS:
        with pytest.raises(ValueError):
            getattr(AzureDeveloperCliCredential(), get_token_method)("scope" + c)

        with pytest.raises(ValueError):
            getattr(AzureDeveloperCliCredential(), get_token_method)("scope", "scope2", "scope" + c)


@pytest.mark.parametrize("get_token_method", GET_TOKEN_METHODS)
def test_get_token(get_token_method):
    """The credential should parse the CLI's output to an token"""

    access_token = "access token"
    expected_expires_on = 1602015811
    successful_output = json.dumps(
        {
            "expiresOn": datetime.fromtimestamp(expected_expires_on).strftime("%Y-%m-%dT%H:%M:%SZ"),
            "token": access_token,
            "subscription": "some-guid",
            "tenant": "some-guid",
            "tokenType": "Bearer",
        }
    )

    with mock.patch("shutil.which", return_value="azd"):
        with mock.patch(CHECK_OUTPUT, mock.Mock(return_value=successful_output)):
            token = getattr(AzureDeveloperCliCredential(), get_token_method)("scope")

    assert token.token == access_token
    assert type(token.expires_on) == int
    assert token.expires_on == expected_expires_on


@pytest.mark.parametrize("get_token_method", GET_TOKEN_METHODS)
def test_command_list(get_token_method):
    """The credential should formulate the command arg list correctly"""
    access_token = "access token"
    expected_expires_on = 1602015811
    successful_output = json.dumps(
        {
            "expiresOn": datetime.fromtimestamp(expected_expires_on).strftime("%Y-%m-%dT%H:%M:%SZ"),
            "token": access_token,
            "subscription": "some-guid",
            "tenant": "some-guid",
            "tokenType": "Bearer",
        }
    )

    def fake_check_output(command_line, **_):
        assert command_line == ["azd"] + COMMAND_LINE + ["--scope", "scope"]
        return successful_output

    with mock.patch("shutil.which", return_value="azd"):
        with mock.patch(CHECK_OUTPUT, fake_check_output):
            token = getattr(AzureDeveloperCliCredential(), get_token_method)("scope")

    assert token.token == access_token
    assert token.expires_on == expected_expires_on


@pytest.mark.parametrize("get_token_method", GET_TOKEN_METHODS)
def test_cli_not_installed(get_token_method):
    """The credential should raise CredentialUnavailableError when the CLI isn't installed"""
    with mock.patch("shutil.which", return_value=None):
        with pytest.raises(CredentialUnavailableError, match=CLI_NOT_FOUND):
            getattr(AzureDeveloperCliCredential(), get_token_method)("scope")


@pytest.mark.parametrize("get_token_method", GET_TOKEN_METHODS)
def test_cannot_execute_shell(get_token_method):
    """The credential should raise CredentialUnavailableError when the subprocess doesn't start"""

    with mock.patch("shutil.which", return_value="azd"):
        with mock.patch(CHECK_OUTPUT, mock.Mock(side_effect=OSError())):
            with pytest.raises(CredentialUnavailableError):
                getattr(AzureDeveloperCliCredential(), get_token_method)("scope")


@pytest.mark.parametrize("get_token_method", GET_TOKEN_METHODS)
def test_not_logged_in(get_token_method):
    """When the CLI isn't logged in, the credential should raise CredentialUnavailableError"""

    stderr = "ERROR: not logged in, run `azd auth login` to login"
    with mock.patch("shutil.which", return_value="azd"):
        with mock.patch(CHECK_OUTPUT, raise_called_process_error(1, stderr=stderr)):
            with pytest.raises(CredentialUnavailableError, match=NOT_LOGGED_IN):
                getattr(AzureDeveloperCliCredential(), get_token_method)("scope")


@pytest.mark.parametrize("get_token_method", GET_TOKEN_METHODS)
def test_aadsts_error(get_token_method):
    """When there is an AADSTS error, the credential should raise an error containing the CLI's output even if the
    error also contains the 'not logged in' string."""

    stderr = "ERROR: AADSTS70043: The refresh token has expired, not logged in, run `azd auth login` to login"
    with mock.patch("shutil.which", return_value="azd"):
        with mock.patch(CHECK_OUTPUT, raise_called_process_error(1, stderr=stderr)):
            with pytest.raises(ClientAuthenticationError, match=stderr):
                getattr(AzureDeveloperCliCredential(), get_token_method)("scope")


@pytest.mark.parametrize("get_token_method", GET_TOKEN_METHODS)
def test_unexpected_error(get_token_method):
    """When the CLI returns an unexpected error, the credential should raise an error containing the CLI's output"""

    stderr = "something went wrong"
    with mock.patch("shutil.which", return_value="azd"):
        with mock.patch(CHECK_OUTPUT, raise_called_process_error(42, stderr=stderr)):
            with pytest.raises(ClientAuthenticationError, match=stderr):
                getattr(AzureDeveloperCliCredential(), get_token_method)("scope")


@pytest.mark.parametrize("get_token_method", GET_TOKEN_METHODS)
def test_unexpected_error_no_stderr(get_token_method):
    """When the CLI returns an unexpected error with no stderr captured, the credential should raise an error with a str output"""
    stderr = ""
    default_message = "Failed to invoke Azure Developer CLI"
    with mock.patch("shutil.which", return_value="azd"):
        with mock.patch(CHECK_OUTPUT, raise_called_process_error(42, stderr=stderr)):
            with pytest.raises(ClientAuthenticationError, match=default_message):
                getattr(AzureDeveloperCliCredential(), get_token_method)("scope")


@pytest.mark.parametrize("output", TEST_ERROR_OUTPUTS)
@pytest.mark.parametrize("get_token_method", GET_TOKEN_METHODS)
def test_parsing_error_does_not_expose_token(output, get_token_method):
    """Errors during CLI output parsing shouldn't expose access tokens in that output"""

    with mock.patch("shutil.which", return_value="azd"):
        with mock.patch(CHECK_OUTPUT, mock.Mock(return_value=output)):
            with pytest.raises(ClientAuthenticationError) as ex:
                getattr(AzureDeveloperCliCredential(), get_token_method)("scope")

    assert "secret value" not in str(ex.value)
    assert "secret value" not in repr(ex.value)


@pytest.mark.parametrize("output", TEST_ERROR_OUTPUTS)
@pytest.mark.parametrize("get_token_method", GET_TOKEN_METHODS)
def test_subprocess_error_does_not_expose_token(output, get_token_method):
    """Errors from the subprocess shouldn't expose access tokens in CLI output"""

    with mock.patch("shutil.which", return_value="azd"):
        with mock.patch(CHECK_OUTPUT, raise_called_process_error(1, output=output)):
            with pytest.raises(ClientAuthenticationError) as ex:
                getattr(AzureDeveloperCliCredential(), get_token_method)("scope")

    assert "secret value" not in str(ex.value)
    assert "secret value" not in repr(ex.value)


@pytest.mark.parametrize("get_token_method", GET_TOKEN_METHODS)
def test_timeout(get_token_method):
    """The credential should raise CredentialUnavailableError when the subprocess times out"""

    from subprocess import TimeoutExpired

    with mock.patch("shutil.which", return_value="azd"):
        with mock.patch(CHECK_OUTPUT, mock.Mock(side_effect=TimeoutExpired("", 42))) as check_output_mock:
            with pytest.raises(CredentialUnavailableError):
                getattr(AzureDeveloperCliCredential(process_timeout=42), get_token_method)("scope")

    # Ensure custom timeout is passed to subprocess
    _, kwargs = check_output_mock.call_args
    assert "timeout" in kwargs
    assert kwargs["timeout"] == 42


@pytest.mark.parametrize("get_token_method", GET_TOKEN_METHODS)
def test_multitenant_authentication_class(get_token_method):
    default_tenant = "first-tenant"
    first_token = "***"
    second_tenant = "second-tenant"
    second_token = first_token * 2

    def fake_check_output(command_line, **_):
        tenant_id_index = command_line.index("--tenant-id") if "--tenant-id" in command_line else None
        tenant = command_line[tenant_id_index + 1] if tenant_id_index is not None else default_tenant
        assert tenant in (default_tenant, second_tenant), 'unexpected tenant "{}"'.format(tenant)
        return json.dumps(
            {
                "expiresOn": datetime.now().strftime("%Y-%m-%dT%H:%M:%SZ"),
                "token": first_token if tenant == default_tenant else second_token,
                "subscription": "some-guid",
                "tenant": tenant,
                "tokenType": "Bearer",
            }
        )

    with mock.patch("shutil.which", return_value="azd"):
        with mock.patch(CHECK_OUTPUT, fake_check_output):
            token = getattr(AzureDeveloperCliCredential(), get_token_method)("scope")
            assert token.token == first_token

            token = getattr(AzureDeveloperCliCredential(tenant_id=default_tenant), get_token_method)("scope")
            assert token.token == first_token

            token = getattr(AzureDeveloperCliCredential(tenant_id=second_tenant), get_token_method)("scope")
            assert token.token == second_token


@pytest.mark.parametrize("get_token_method", GET_TOKEN_METHODS)
def test_multitenant_authentication(get_token_method):
    default_tenant = "first-tenant"
    first_token = "***"
    second_tenant = "second-tenant"
    second_token = first_token * 2

    def fake_check_output(command_line, **_):
        tenant_id_index = command_line.index("--tenant-id") if "--tenant-id" in command_line else None
        tenant = command_line[tenant_id_index + 1] if tenant_id_index is not None else default_tenant
        assert tenant in (default_tenant, second_tenant), 'unexpected tenant "{}"'.format(tenant)
        return json.dumps(
            {
                "expiresOn": datetime.now().strftime("%Y-%m-%dT%H:%M:%SZ"),
                "token": first_token if tenant == default_tenant else second_token,
                "subscription": "some-guid",
                "tenant": tenant,
                "tokenType": "Bearer",
            }
        )

    credential = AzureDeveloperCliCredential()
    with mock.patch("shutil.which", return_value="azd"):
        with mock.patch(CHECK_OUTPUT, fake_check_output):
            token = getattr(credential, get_token_method)("scope")
            assert token.token == first_token

            kwargs = {"tenant_id": default_tenant}
            if get_token_method == "get_token_info":
                kwargs = {"options": kwargs}
            token = getattr(credential, get_token_method)("scope", **kwargs)
            assert token.token == first_token

            kwargs = {"tenant_id": second_tenant}
            if get_token_method == "get_token_info":
                kwargs = {"options": kwargs}
            token = getattr(credential, get_token_method)("scope", **kwargs)
            assert token.token == second_token

            # should still default to the first tenant
            token = getattr(credential, get_token_method)("scope")
            assert token.token == first_token


@pytest.mark.parametrize("get_token_method", GET_TOKEN_METHODS)
def test_multitenant_authentication_not_allowed(get_token_method):
    expected_tenant = "expected-tenant"
    expected_token = "***"

    def fake_check_output(command_line, **_):
        match = re.search("--tenant-id (.*)", command_line[-1])
        assert match is None or match[1] == expected_tenant
        return json.dumps(
            {
                "expiresOn": datetime.now().strftime("%Y-%m-%dT%H:%M:%SZ"),
                "token": expected_token,
                "subscription": "some-guid",
                "tenant": expected_token,
                "tokenType": "Bearer",
            }
        )

    credential = AzureDeveloperCliCredential()
    with mock.patch("shutil.which", return_value="azd"):
        with mock.patch(CHECK_OUTPUT, fake_check_output):
            token = getattr(credential, get_token_method)("scope")
            assert token.token == expected_token

            with mock.patch.dict("os.environ", {EnvironmentVariables.AZURE_IDENTITY_DISABLE_MULTITENANTAUTH: "true"}):
                kwargs = {"tenant_id": "un" + expected_tenant}
                if get_token_method == "get_token_info":
                    kwargs = {"options": kwargs}
                token = getattr(credential, get_token_method)("scope", **kwargs)
            assert token.token == expected_token


@pytest.mark.parametrize("get_token_method", GET_TOKEN_METHODS)
def test_claims_challenge_raises_error(get_token_method):
    """The credential should raise CredentialUnavailableError when claims challenge is provided"""

    claims = '{"access_token":{"acrs":{"essential":true,"values":["p1"]}}}'
    credential = AzureDeveloperCliCredential()

    expected_message = "Suggestion: re-authentication required, run `azd auth login` to acquire a new token."
    error_output = """\
{"data":{"message":"\\nERROR: fetching token: AADSTS50076: Due to a configuration change made by your administrator, or because you moved to a new location, you must use multi-factor authentication to access 'tenant-id'. Trace ID: trace-id Correlation ID: correlation-id Timestamp: 2025-08-18 22:08:14Z\\n"}}
{"data":{"message":"Suggestion: re-authentication required, run `azd auth login` to acquire a new token.\\n"}}"""

    with mock.patch("shutil.which", return_value="azd"):
        with mock.patch(CHECK_OUTPUT, raise_called_process_error(1, stderr=error_output)):
            with pytest.raises(ClientAuthenticationError) as exc:
                kwargs = {"claims": claims}
                if get_token_method == "get_token_info":
                    kwargs = {"options": kwargs}
                getattr(credential, get_token_method)("scope", **kwargs)
            assert exc.value.message == expected_message


@pytest.mark.parametrize("get_token_method", GET_TOKEN_METHODS)
def test_empty_claims_does_not_raise_error(get_token_method):
    """The credential should not raise error when claims parameter is empty or None"""

    access_token = "access token"
    expected_expires_on = 1602015811
    successful_output = json.dumps(
        {
            "expiresOn": datetime.fromtimestamp(expected_expires_on).strftime("%Y-%m-%dT%H:%M:%SZ"),
            "token": access_token,
            "subscription": "some-guid",
            "tenant": "some-guid",
            "tokenType": "Bearer",
        }
    )

    # Mock the CLI to avoid actual invocation
    with mock.patch("shutil.which", return_value="azd"):
        with mock.patch(CHECK_OUTPUT, mock.Mock(return_value=successful_output)):
            credential = AzureDeveloperCliCredential()

            # Test with None (default)
            token = getattr(credential, get_token_method)("scope")
            assert token.token == access_token

            # Test with empty string claims
            kwargs = {"claims": ""}
            if get_token_method == "get_token_info":
                kwargs = {"options": kwargs}
            token = getattr(credential, get_token_method)("scope", **kwargs)
            assert token.token == access_token

            # Test with None claims explicitly
            kwargs = {"claims": None}
            if get_token_method == "get_token_info":
                kwargs = {"options": kwargs}
            token = getattr(credential, get_token_method)("scope", **kwargs)
            assert token.token == access_token


@pytest.mark.parametrize("get_token_method", GET_TOKEN_METHODS)
def test_claims_command_line_argument(get_token_method):
    """The credential should pass claims as --claims argument to azd command"""

    claims = '{"access_token":{"acrs":{"essential":true,"values":["p1"]}}}'
    expected_encoded_claims = "eyJhY2Nlc3NfdG9rZW4iOnsiYWNycyI6eyJlc3NlbnRpYWwiOnRydWUsInZhbHVlcyI6WyJwMSJdfX19"
    access_token = "access token"
    expected_expires_on = 1602015811

    def fake_check_output(command_line, **kwargs):
        # Verify that claims are passed as --claims argument
        assert "--claims" in command_line
        claims_index = command_line.index("--claims")
        assert command_line[claims_index + 1] == expected_encoded_claims

        return json.dumps(
            {
                "expiresOn": datetime.fromtimestamp(expected_expires_on).strftime("%Y-%m-%dT%H:%M:%SZ"),
                "token": access_token,
                "subscription": "some-guid",
                "tenant": "some-guid",
                "tokenType": "Bearer",
            }
        )

    credential = AzureDeveloperCliCredential()
    with mock.patch("shutil.which", return_value="azd"):
        with mock.patch(CHECK_OUTPUT, fake_check_output):
            kwargs = {"claims": claims}
            if get_token_method == "get_token_info":
                kwargs = {"options": kwargs}
            token = getattr(credential, get_token_method)("scope", **kwargs)
            assert token.token == access_token


class TestExtractCliErrorMessage:
    """Tests for the error message extraction function."""

    def test_extract_suggestion_message_preferred(self):
        """Should prefer messages containing 'Suggestion' (case-insensitive)"""
        output = """\
{"type":"consoleMessage","timestamp":"2025-08-18T15:08:14.4849845-07:00","data":{"message":"\\nERROR: fetching token: AADSTS50076: Due to a configuration change made by your administrator, or because you moved to a new location, you must use multi-factor authentication to access 'tenant-id'. Trace ID: trace-id Correlation ID: correlation-id Timestamp: 2025-08-18 22:08:14Z\\n"}}
{"type":"consoleMessage","timestamp":"2025-08-18T15:08:14.4849845-07:00","data":{"message":"Suggestion: re-authentication required, run `azd auth login` to acquire a new token.\\n"}}"""

        result = extract_cli_error_message(output)
        assert result == "Suggestion: re-authentication required, run `azd auth login` to acquire a new token."

    def test_extract_suggestion_case_insensitive(self):
        """Should find 'suggestion' in any case"""
        output = """\
{"type":"consoleMessage","data":{"message":"First message"}}
{"type":"consoleMessage","data":{"message":"SUGGESTION: Try running azd auth login"}}"""

        result = extract_cli_error_message(output)
        assert result == "SUGGESTION: Try running azd auth login"

    def test_extract_last_message_when_no_suggestion(self):
        """Should return last message when multiple messages but no suggestion"""
        output = """\
{"type":"consoleMessage","data":{"message":"First error message"}}
{"type":"consoleMessage","data":{"message":"Second error message"}}
{"type":"consoleMessage","data":{"message":"Third error message"}}"""

        result = extract_cli_error_message(output)
        assert result == "Third error message"

    def test_extract_first_message_when_only_one(self):
        """Should return first message when only one exists"""
        output = '{"type":"consoleMessage","data":{"message":"Only error message"}}'

        result = extract_cli_error_message(output)
        assert result == "Only error message"

    def test_extract_message_from_nested_data(self):
        """Should extract message from nested data structure"""
        output = '{"type":"consoleMessage","data":{"message":"Error in nested data"}}'

        result = extract_cli_error_message(output)
        assert result == "Error in nested data"

    def test_extract_message_from_root_level(self):
        """Should extract message from root level of JSON"""
        output = '{"message":"Root level error message"}'

        result = extract_cli_error_message(output)
        assert result == "Root level error message"

    def test_extract_mixed_message_locations(self):
        """Should handle messages at different JSON levels"""
        output = """\
{"message":"Root level message"}
{"data":{"message":"Nested message"}}
{"data":{"message":"suggestion: Use this suggestion"}}"""

        result = extract_cli_error_message(output)
        assert result == "suggestion: Use this suggestion"

    def test_ignore_empty_messages(self):
        """Should ignore empty or whitespace-only messages"""
        output = """\
{"data":{"message":"   "}}
{"data":{"message":""}}
{"data":{"message":"Valid message"}}"""

        result = extract_cli_error_message(output)
        assert result == "Valid message"

    def test_ignore_non_json_lines(self):
        """Should ignore lines that are not valid JSON"""
        output = """\
This is not JSON
{"data":{"message":"Valid JSON message"}}
Another non-JSON line
{"data":{"message":"Suggestion: Another valid message"}}"""

        result = extract_cli_error_message(output)
        assert result == "Suggestion: Another valid message"

    def test_ignore_non_string_messages(self):
        """Should ignore messages that are not strings"""
        output = """\
{"data":{"message":123}}
{"data":{"message":{"nested":"object"}}}
{"data":{"message":"Valid string message"}}"""

        result = extract_cli_error_message(output)
        assert result == "Valid string message"

    def test_ignore_empty_lines(self):
        """Should ignore empty lines and whitespace-only lines"""
        output = """\

{"data":{"message":"First message"}}

{"data":{"message":"Second message"}}

"""

        result = extract_cli_error_message(output)
        assert result == "Second message"

    def test_sanitize_token_in_output(self):
        """Should sanitize tokens in the extracted message"""
        output = '{"data":{"message":"Error with \\"token\\": \\"abc123token\\" in message"}}'

        result = extract_cli_error_message(output)
        assert result is not None
        assert "abc123token" not in result
        assert "****" in result

    def test_return_none_for_no_valid_messages(self):
        """Should return None when no valid messages found"""
        output = """\
{"data":{"notamessage":"Not a message"}}
{"nomessage":"Also not a message"}
This is not JSON"""

        result = extract_cli_error_message(output)
        assert result is None

    def test_return_none_for_empty_output(self):
        """Should return None for empty output"""
        result = extract_cli_error_message("")
        assert result is None

    def test_return_none_for_whitespace_only_output(self):
        """Should return None for whitespace-only output"""
        result = extract_cli_error_message("   \n\n   \t  ")
        assert result is None

    def test_complex_real_world_example(self):
        """Should handle complex real-world azd output"""
        output = """\
{"type":"consoleMessage","timestamp":"2025-08-18T15:08:14.4849845-07:00","data":{"message":"\\nERROR: fetching token: AADSTS50076: Due to a configuration change made by your administrator, or because you moved to a new location, you must use multi-factor authentication to access 'tenant-id'. Trace ID: trace-id Correlation ID: correlation-id Timestamp: 2025-08-18 22:08:14Z\\n"}}
{"type":"consoleMessage","timestamp":"2025-08-18T15:08:14.4849845-07:00","data":{"message":"Suggestion: re-authentication required, run `azd auth login` to acquire a new token.\\n"}}
{"type":"progress","data":{"activity":"Cleaning up"}}"""

        result = extract_cli_error_message(output)
        assert result == "Suggestion: re-authentication required, run `azd auth login` to acquire a new token."

    def test_strip_whitespace_from_messages(self):
        """Should strip leading and trailing whitespace from messages"""
        output = '{"data":{"message":"  \\n  Error message with whitespace  \\n  "}}'

        result = extract_cli_error_message(output)
        assert result == "Error message with whitespace"

    def test_handle_malformed_json_gracefully(self):
        """Should handle malformed JSON lines gracefully"""
        output = """\
{"data":{"message":"First valid message"}
{"malformed":"json"without"closing"brace"
{"data":{"message":"suggestion: This should be found"}}"""

        result = extract_cli_error_message(output)
        assert result == "suggestion: This should be found"
