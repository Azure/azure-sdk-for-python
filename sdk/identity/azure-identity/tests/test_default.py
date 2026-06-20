# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
import os
import sys

from azure.core.credentials import AccessToken, AccessTokenInfo
from azure.core.exceptions import ClientAuthenticationError
from azure.identity import (
    AzureCliCredential,
    AzureDeveloperCliCredential,
    AzurePowerShellCredential,
    CredentialUnavailableError,
    DefaultAzureCredential,
    InteractiveBrowserCredential,
    SharedTokenCacheCredential,
    VisualStudioCodeCredential,
)
from azure.identity._constants import EnvironmentVariables
from azure.identity._credentials.azure_cli import AzureCliCredential
from azure.identity._credentials.azd_cli import AzureDeveloperCliCredential
from azure.identity._credentials.managed_identity import ManagedIdentityCredential
from azure.identity._internal.utils import is_wsl
import pytest
from urllib.parse import urlparse

from helpers import mock_response, Request, validating_transport, GET_TOKEN_METHODS
from test_shared_cache_credential import build_aad_response, get_account_event, populated_cache
from unittest.mock import MagicMock, Mock, patch


def test_close():
    transport = MagicMock()
    credential = DefaultAzureCredential(transport=transport)
    assert not transport.__enter__.called
    assert not transport.__exit__.called

    credential.close()
    assert not transport.__enter__.called
    assert transport.__exit__.called  # call count depends on the chain's composition


def test_context_manager():
    transport = MagicMock()
    credential = DefaultAzureCredential(transport=transport)

    with credential:
        assert transport.__enter__.called  # call count depends on the chain's composition
        assert not transport.__exit__.called

    assert transport.__enter__.called
    assert transport.__exit__.called


@pytest.mark.parametrize("get_token_method", GET_TOKEN_METHODS)
def test_iterates_only_once(get_token_method):
    """When a credential succeeds, DefaultAzureCredential should use that credential thereafter, ignoring the others"""

    unavailable_credential = Mock(
        spec_set=["get_token", "get_token_info"],
        get_token=Mock(side_effect=CredentialUnavailableError(message="...")),
        get_token_info=Mock(side_effect=CredentialUnavailableError(message="...")),
    )
    successful_credential = Mock(
        spec_set=["get_token", "get_token_info"],
        get_token=Mock(return_value=AccessToken("***", 42)),
        get_token_info=Mock(return_value=AccessTokenInfo("***", 42)),
    )

    credential = DefaultAzureCredential()
    credential.credentials = (
        unavailable_credential,
        successful_credential,
        Mock(
            spec_set=["get_token", "get_token_info"],
            get_token=Mock(side_effect=Exception("iteration didn't stop after a credential provided a token")),
            get_token_info=Mock(side_effect=Exception("iteration didn't stop after a credential provided a token")),
        ),
    )

    for n in range(3):
        getattr(credential, get_token_method)("scope")
        assert getattr(unavailable_credential, get_token_method).call_count == 1
        assert getattr(successful_credential, get_token_method).call_count == n + 1


@pytest.mark.parametrize("authority", ("localhost", "https://localhost"))
def test_authority(authority):
    """the credential should accept authority configuration by keyword argument or environment"""

    parsed_authority = urlparse(authority)
    expected_netloc = parsed_authority.netloc or authority  # "localhost" parses to netloc "", path "localhost"

    def test_initialization(mock_credential, expect_argument):
        DefaultAzureCredential(authority=authority)
        assert mock_credential.call_count == 1

        # N.B. if os.environ has been patched somewhere in the stack, that patch is in place here
        environment = dict(os.environ, **{EnvironmentVariables.AZURE_AUTHORITY_HOST: authority})
        with patch.dict(DefaultAzureCredential.__module__ + ".os.environ", environment, clear=True):
            DefaultAzureCredential()
        assert mock_credential.call_count == 2

        for _, kwargs in mock_credential.call_args_list:
            if expect_argument:
                actual = urlparse(kwargs["authority"])
                assert actual.scheme == "https"
                assert actual.netloc == expected_netloc
            else:
                assert "authority" not in kwargs

    # authority should be passed to EnvironmentCredential as a keyword argument
    environment = {var: "foo" for var in EnvironmentVariables.CLIENT_SECRET_VARS}
    with patch(DefaultAzureCredential.__module__ + ".EnvironmentCredential") as mock_credential:
        with patch.dict("os.environ", environment, clear=True):
            test_initialization(mock_credential, expect_argument=True)

    # authority should be passed to SharedTokenCacheCredential as a keyword argument
    with patch(DefaultAzureCredential.__module__ + ".SharedTokenCacheCredential") as mock_credential:
        mock_credential.supported = lambda: True
        test_initialization(mock_credential, expect_argument=True)

    # authority should not be passed to ManagedIdentityCredential
    with patch(DefaultAzureCredential.__module__ + ".ManagedIdentityCredential") as mock_credential:
        with patch.dict("os.environ", {EnvironmentVariables.MSI_ENDPOINT: "localhost"}, clear=True):
            test_initialization(mock_credential, expect_argument=False)

    # authority should not be passed to AzureCliCredential
    with patch(DefaultAzureCredential.__module__ + ".AzureCliCredential") as mock_credential:
        with patch(DefaultAzureCredential.__module__ + ".SharedTokenCacheCredential") as shared_cache:
            shared_cache.supported = lambda: False
            with patch.dict("os.environ", {}, clear=True):
                test_initialization(mock_credential, expect_argument=False)

    # authority should not be passed to AzureDeveloperCliCredential
    with patch(DefaultAzureCredential.__module__ + ".AzureDeveloperCliCredential") as mock_credential:
        with patch(DefaultAzureCredential.__module__ + ".SharedTokenCacheCredential") as shared_cache:
            shared_cache.supported = lambda: False
            with patch.dict("os.environ", {}, clear=True):
                test_initialization(mock_credential, expect_argument=False)


def test_exclude_options():
    def assert_credentials_not_present(chain, *excluded_credential_classes):
        actual = {c.__class__ for c in chain.credentials}
        assert len(actual)

        # no unexpected credential is in the chain
        excluded = set(excluded_credential_classes)
        assert len(actual & excluded) == 0

        # only excluded credentials have been excluded from the default
        default = {c.__class__ for c in DefaultAzureCredential().credentials}
        assert actual <= default  # n.b. we know actual is non-empty
        assert default - actual <= excluded

    # when exclude_managed_identity_credential is set to True, check if ManagedIdentityCredential instance is not present
    credential = DefaultAzureCredential(exclude_managed_identity_credential=True)
    assert_credentials_not_present(credential, ManagedIdentityCredential)

    if SharedTokenCacheCredential.supported():
        credential = DefaultAzureCredential(exclude_shared_token_cache_credential=True)
        assert_credentials_not_present(credential, SharedTokenCacheCredential)

    credential = DefaultAzureCredential(exclude_cli_credential=True)
    assert_credentials_not_present(credential, AzureCliCredential)

    credential = DefaultAzureCredential(exclude_visual_studio_code_credential=True)
    assert_credentials_not_present(credential, VisualStudioCodeCredential)

    credential = DefaultAzureCredential(exclude_cli_credential=True)
    assert_credentials_not_present(credential, AzureCliCredential)

    credential = DefaultAzureCredential(exclude_powershell_credential=True)
    assert_credentials_not_present(credential, AzurePowerShellCredential)

    credential = DefaultAzureCredential(exclude_developer_cli_credential=True)
    assert_credentials_not_present(credential, AzureDeveloperCliCredential)

    # test excluding broker credential
    credential = DefaultAzureCredential(exclude_broker_credential=True)
    from azure.identity._credentials.broker import BrokerCredential

    assert_credentials_not_present(credential, BrokerCredential)

    # interactive auth is excluded by default
    credential = DefaultAzureCredential(exclude_interactive_browser_credential=False)
    actual = {c.__class__ for c in credential.credentials}
    default = {c.__class__ for c in DefaultAzureCredential().credentials}
    assert actual - default == {InteractiveBrowserCredential}

    # broker credential is included by default
    credential = DefaultAzureCredential()
    from azure.identity._credentials.broker import BrokerCredential

    actual = {c.__class__ for c in credential.credentials}
    assert BrokerCredential in actual, "BrokerCredential should be included in DefaultAzureCredential by default"


@pytest.mark.parametrize("get_token_method", GET_TOKEN_METHODS)
def test_shared_cache_tenant_id(get_token_method):
    expected_access_token = "expected-access-token"
    refresh_token_a = "refresh-token-a"
    refresh_token_b = "refresh-token-b"

    # The value of the UPN is arbitrary because this test verifies the credential's behavior given a specified
    # tenant ID. During a complete live test run, $AZURE_USERNAME will have a value which DefaultAzureCredential
    # should pass to SharedTokenCacheCredential. This test will fail if the mock accounts don't match that value.
    upn = os.environ.get(EnvironmentVariables.AZURE_USERNAME, "spam@eggs")

    tenant_a = "tenant-a"
    tenant_b = "tenant-b"

    # two cached accounts, same username, different tenants -> shared_cache_tenant_id should prevail
    account_a = get_account_event(username=upn, uid="another-guid", utid=tenant_a, refresh_token=refresh_token_a)
    account_b = get_account_event(username=upn, uid="more-guid", utid=tenant_b, refresh_token=refresh_token_b)
    cache = populated_cache(account_a, account_b)

    credential = get_credential_for_shared_cache_test(
        refresh_token_b, expected_access_token, cache, shared_cache_tenant_id=tenant_b
    )
    token = getattr(credential, get_token_method)("scope")
    assert token.token == expected_access_token

    # redundantly specifying shared_cache_username makes no difference
    credential = get_credential_for_shared_cache_test(
        refresh_token_b, expected_access_token, cache, shared_cache_tenant_id=tenant_b, shared_cache_username=upn
    )
    token = getattr(credential, get_token_method)("scope")
    assert token.token == expected_access_token

    # shared_cache_tenant_id should prevail over AZURE_TENANT_ID
    with patch("os.environ", {EnvironmentVariables.AZURE_TENANT_ID: tenant_a}):
        credential = get_credential_for_shared_cache_test(
            refresh_token_b, expected_access_token, cache, shared_cache_tenant_id=tenant_b
        )
    token = getattr(credential, get_token_method)("scope")
    assert token.token == expected_access_token

    # AZURE_TENANT_ID should be used when shared_cache_tenant_id isn't specified
    with patch("os.environ", {EnvironmentVariables.AZURE_TENANT_ID: tenant_b}):
        credential = get_credential_for_shared_cache_test(refresh_token_b, expected_access_token, cache)
    token = getattr(credential, get_token_method)("scope")
    assert token.token == expected_access_token


@pytest.mark.parametrize("get_token_method", GET_TOKEN_METHODS)
def test_shared_cache_username(get_token_method):
    expected_access_token = "expected-access-token"
    refresh_token_a = "refresh-token-a"
    refresh_token_b = "refresh-token-b"
    upn_a = "spam@eggs"
    upn_b = "eggs@spam"

    # The value of the tenant ID is arbitrary because this test verifies the credential's behavior given a specified
    # username. During a complete live test run, $AZURE_TENANT_ID will have a value which DefaultAzureCredential should
    # pass to SharedTokenCacheCredential. This test will fail if the mock accounts don't match that value.
    tenant_id = os.environ.get(EnvironmentVariables.AZURE_TENANT_ID, "the-tenant")

    # two cached accounts, same tenant, different usernames -> shared_cache_username should prevail
    account_a = get_account_event(username=upn_a, uid="another-guid", utid=tenant_id, refresh_token=refresh_token_a)
    account_b = get_account_event(username=upn_b, uid="more-guid", utid=tenant_id, refresh_token=refresh_token_b)
    cache = populated_cache(account_a, account_b)

    credential = get_credential_for_shared_cache_test(
        refresh_token_a, expected_access_token, cache, shared_cache_username=upn_a
    )
    token = getattr(credential, get_token_method)("scope")
    assert token.token == expected_access_token

    # redundantly specifying shared_cache_tenant_id makes no difference
    credential = get_credential_for_shared_cache_test(
        refresh_token_a, expected_access_token, cache, shared_cache_tenant_id=tenant_id, shared_cache_username=upn_a
    )
    token = getattr(credential, get_token_method)("scope")
    assert token.token == expected_access_token

    # shared_cache_username should prevail over AZURE_USERNAME
    with patch("os.environ", {EnvironmentVariables.AZURE_USERNAME: upn_b}):
        credential = get_credential_for_shared_cache_test(
            refresh_token_a, expected_access_token, cache, shared_cache_username=upn_a
        )
    token = getattr(credential, get_token_method)("scope")
    assert token.token == expected_access_token

    # AZURE_USERNAME should be used when shared_cache_username isn't specified
    with patch("os.environ", {EnvironmentVariables.AZURE_USERNAME: upn_b}):
        credential = get_credential_for_shared_cache_test(refresh_token_b, expected_access_token, cache)
    token = getattr(credential, get_token_method)("scope")
    assert token.token == expected_access_token


@patch(DefaultAzureCredential.__module__ + ".SharedTokenCacheCredential")
def test_default_credential_shared_cache_use(mock_credential):
    mock_credential.supported = Mock(return_value=False)

    # unsupported platform -> default credential shouldn't use shared cache
    credential = DefaultAzureCredential()
    assert mock_credential.call_count == 0
    assert mock_credential.supported.call_count == 1
    mock_credential.supported.reset_mock()

    mock_credential.supported = Mock(return_value=True)

    # supported platform -> default credential should use shared cache
    credential = DefaultAzureCredential()
    assert mock_credential.call_count == 1
    assert mock_credential.supported.call_count == 1
    mock_credential.supported.reset_mock()


def test_managed_identity_client_id():
    """the credential should accept a user-assigned managed identity's client ID by kwarg or environment variable"""

    expected_args = {
        "client_id": "the-client",
        "_exclude_workload_identity_credential": False,
        "_enable_imds_probe": True,
    }

    with patch(DefaultAzureCredential.__module__ + ".ManagedIdentityCredential") as mock_credential:
        DefaultAzureCredential(managed_identity_client_id=expected_args["client_id"])
    mock_credential.assert_called_once_with(**expected_args)

    # client id can also be specified in $AZURE_CLIENT_ID
    with patch.dict(os.environ, {EnvironmentVariables.AZURE_CLIENT_ID: expected_args["client_id"]}, clear=True):
        with patch(DefaultAzureCredential.__module__ + ".ManagedIdentityCredential") as mock_credential:
            DefaultAzureCredential()
    mock_credential.assert_called_once_with(**expected_args)

    # keyword argument should override environment variable
    with patch.dict(
        os.environ, {EnvironmentVariables.AZURE_CLIENT_ID: "not-" + expected_args["client_id"]}, clear=True
    ):
        with patch(DefaultAzureCredential.__module__ + ".ManagedIdentityCredential") as mock_credential:
            DefaultAzureCredential(managed_identity_client_id=expected_args["client_id"])
    mock_credential.assert_called_once_with(**expected_args)


def get_credential_for_shared_cache_test(expected_refresh_token, expected_access_token, cache, **kwargs):
    exclude_other_credentials = {
        option: True
        for option in (
            "exclude_cli_credential",
            "exclude_developer_cli_credential",
            "exclude_environment_credential",
            "exclude_managed_identity_credential",
            "exclude_powershell_credential",
        )
    }
    options = dict(exclude_other_credentials, **kwargs)

    # validating transport will raise if the shared cache credential isn't used, or selects the wrong refresh token
    transport = validating_transport(
        requests=[Request(required_data={"refresh_token": expected_refresh_token})],
        responses=[mock_response(json_payload=build_aad_response(access_token=expected_access_token))],
    )

    # this credential uses a mock shared cache, so it works on all platforms
    with patch.object(SharedTokenCacheCredential, "supported"):
        return DefaultAzureCredential(_cache=cache, transport=transport, **options)


def test_interactive_browser_tenant_id():
    """the credential should allow configuring a tenant ID for InteractiveBrowserCredential by kwarg or environment"""

    tenant_id = "tenant-id"

    def validate_tenant_id(credential):
        assert len(credential.call_args_list) == 1, "InteractiveBrowserCredential should be instantiated once"
        _, kwargs = credential.call_args
        assert "tenant_id" in kwargs

    with patch(DefaultAzureCredential.__module__ + ".InteractiveBrowserCredential") as mock_credential:
        DefaultAzureCredential(exclude_interactive_browser_credential=False, interactive_browser_tenant_id=tenant_id)
    validate_tenant_id(mock_credential)

    # tenant id can also be specified in $AZURE_TENANT_ID
    with patch.dict(os.environ, {EnvironmentVariables.AZURE_TENANT_ID: tenant_id}, clear=True):
        with patch(DefaultAzureCredential.__module__ + ".InteractiveBrowserCredential") as mock_credential:
            DefaultAzureCredential(exclude_interactive_browser_credential=False)
    validate_tenant_id(mock_credential)

    # keyword argument should override environment variable
    with patch.dict(os.environ, {EnvironmentVariables.AZURE_TENANT_ID: "not-" + tenant_id}, clear=True):
        with patch(DefaultAzureCredential.__module__ + ".InteractiveBrowserCredential") as mock_credential:
            DefaultAzureCredential(
                exclude_interactive_browser_credential=False, interactive_browser_tenant_id=tenant_id
            )
    validate_tenant_id(mock_credential)


def test_interactive_browser_client_id():
    """the credential should allow configuring a client ID for InteractiveBrowserCredential by kwarg"""

    client_id = "client-id"

    def validate_client_id(credential):
        assert len(credential.call_args_list) == 1, "InteractiveBrowserCredential should be instantiated once"
        _, kwargs = credential.call_args
        assert kwargs["client_id"] == client_id

    with patch(DefaultAzureCredential.__module__ + ".InteractiveBrowserCredential") as mock_credential:
        DefaultAzureCredential(exclude_interactive_browser_credential=False, interactive_browser_client_id=client_id)
    validate_client_id(mock_credential)


def test_process_timeout():
    """the credential should allow configuring a process timeout for Azure CLI and PowerShell by kwarg"""

    timeout = 42

    with patch(DefaultAzureCredential.__module__ + ".AzureCliCredential") as mock_cli_credential:
        with patch(DefaultAzureCredential.__module__ + ".AzurePowerShellCredential") as mock_pwsh_credential:
            DefaultAzureCredential(process_timeout=timeout)

    for credential in (mock_cli_credential, mock_pwsh_credential):
        _, kwargs = credential.call_args
        assert "process_timeout" in kwargs
        assert kwargs["process_timeout"] == timeout


def test_process_timeout_default():
    """the credential should allow configuring a process timeout for Azure CLI and PowerShell by kwarg"""

    with patch(DefaultAzureCredential.__module__ + ".AzureCliCredential") as mock_cli_credential:
        with patch(DefaultAzureCredential.__module__ + ".AzurePowerShellCredential") as mock_pwsh_credential:
            DefaultAzureCredential()

    for credential in (mock_cli_credential, mock_pwsh_credential):
        _, kwargs = credential.call_args
        assert "process_timeout" in kwargs
        assert kwargs["process_timeout"] == 10


def test_unexpected_kwarg():
    """the credential shouldn't raise when given an unexpected keyword argument"""
    DefaultAzureCredential(foo=42)


def test_error_tenant_id():
    with pytest.raises(TypeError):
        DefaultAzureCredential(tenant_id="foo")


def test_validate_cloud_shell_credential_in_dac():
    MANAGED_IDENTITY_ENVIRON = "azure.identity._credentials.managed_identity.os.environ"
    with patch.dict(MANAGED_IDENTITY_ENVIRON, {EnvironmentVariables.MSI_ENDPOINT: "https://localhost"}, clear=True):
        DefaultAzureCredential()
        DefaultAzureCredential(managed_identity_client_id="foo")
        DefaultAzureCredential(identity_config={"client_id": "foo"})
        DefaultAzureCredential(identity_config={"object_id": "foo"})
        DefaultAzureCredential(identity_config={"resource_id": "foo"})


@pytest.mark.skipif(not sys.platform.startswith("win") and not is_wsl(), reason="tests Windows-specific behavior")
def test_broker_credential():
    """Test that DefaultAzureCredential uses the broker credential when available"""
    with patch("azure.identity.broker.InteractiveBrowserBrokerCredential") as mock_credential:
        credential = DefaultAzureCredential()
        # The broker credential should be in the chain
        broker_credentials = [c for c in credential.credentials if c.__class__.__name__ == "BrokerCredential"]
        assert len(broker_credentials) == 1, "BrokerCredential should be in the chain"
    # InteractiveBrowserBrokerCredential should be instantiated by BrokerCredential
    assert mock_credential.call_count >= 1, "InteractiveBrowserBrokerCredential should be instantiated"


def test_broker_credential_client_id():
    """Test that DefaultAzureCredential allows configuring a client ID for BrokerCredential"""

    client_id = "broker-client-id"
    credential = DefaultAzureCredential(broker_client_id=client_id)
    broker_credentials = [c for c in credential.credentials if c.__class__.__name__ == "BrokerCredential"]
    assert (
        len(broker_credentials) == 1
    ), "BrokerCredential should be in the chain even when broker package is not installed"
    broker_credential = broker_credentials[0]
    assert broker_credential._client_id == client_id, "Credential should be instantiated with the specified client ID"


def test_broker_credential_tenant_id():
    """Test that DefaultAzureCredential allows configuring a tenant ID for BrokerCredential"""

    tenant_id = "broker-tenant-id"

    credential = DefaultAzureCredential(broker_tenant_id=tenant_id)
    broker_credentials = [c for c in credential.credentials if c.__class__.__name__ == "BrokerCredential"]
    assert (
        len(broker_credentials) == 1
    ), "BrokerCredential should be in the chain even when broker package is not installed"
    broker_credential = broker_credentials[0]
    assert broker_credential._tenant_id == tenant_id, "Credential should be instantiated with the specified tenant ID"


def test_broker_credential_requirements_not_installed():
    """Test that DefaultAzureCredential includes BrokerCredential even when broker package is not installed"""

    # Mock the get_broker_credential function to return None (simulating package not installed)
    with patch.dict("sys.modules", {"azure.identity.broker": None}):
        credential = DefaultAzureCredential()
        # The broker credential should still be in the chain
        broker_credentials = [c for c in credential.credentials if c.__class__.__name__ == "BrokerCredential"]
        assert (
            len(broker_credentials) == 1
        ), "BrokerCredential should be in the chain even when broker package is not installed"

        # Test that the broker credential raises CredentialUnavailableError
        broker_cred = broker_credentials[0]
        with pytest.raises(CredentialUnavailableError) as exc_info:
            broker_cred.get_token_info("https://management.azure.com/.default")


def test_failed_dac_credential_error_reporting():
    """Test that FailedDACCredential properly reports initialization errors"""
    from azure.identity._credentials.default import FailedDACCredential

    credential_name = "WorkloadIdentityCredential"
    error_message = "Failed to initialize: missing required environment variable AZURE_FEDERATED_TOKEN_FILE"

    failed_credential = FailedDACCredential(credential_name, error_message)

    # Test get_token raises CredentialUnavailableError with the original error
    with pytest.raises(CredentialUnavailableError) as exc_info:
        failed_credential.get_token("https://management.azure.com/.default")

    assert str(exc_info.value) == error_message

    # Test get_token_info raises CredentialUnavailableError with the original error
    with pytest.raises(CredentialUnavailableError) as exc_info:
        failed_credential.get_token_info("https://management.azure.com/.default")

    assert str(exc_info.value) == error_message

    # Test context manager support
    with failed_credential:
        pass  # Should not raise during context entry/exit

    # Test close method
    failed_credential.close()  # Should not raise


def test_failed_dac_credential_in_chain():
    """Test that FailedDACCredential errors are properly reported when DefaultAzureCredential fails"""
    from azure.identity._credentials.default import FailedDACCredential

    # Create a mock successful credential to ensure the chain doesn't fail immediately
    successful_credential = Mock(
        spec_set=["get_token", "get_token_info"],
        get_token=Mock(return_value=AccessToken("***", 42)),
        get_token_info=Mock(return_value=AccessTokenInfo("***", 42)),
    )

    # Create a DefaultAzureCredential and replace its credentials with a failed credential and successful one
    credential = DefaultAzureCredential()
    failed_cred = FailedDACCredential("WorkloadIdentityCredential", "initialization error")
    credential.credentials = (failed_cred, successful_credential)

    # The chain should succeed using the successful credential
    token = credential.get_token("https://management.azure.com/.default")
    assert token.token == "***"
    assert token.expires_on == 42

    # Test with only failed credentials to ensure error propagation
    credential_all_failed = DefaultAzureCredential()
    failed_cred1 = FailedDACCredential("WorkloadIdentityCredential", "workload identity error")
    failed_cred2 = FailedDACCredential("TestCredential", "test credential error")
    credential_all_failed.credentials = (failed_cred1, failed_cred2)

    # Should raise an error that includes both credential errors
    with pytest.raises(ClientAuthenticationError) as exc_info:
        credential_all_failed.get_token("https://management.azure.com/.default")

    # The error should mention the failed credentials
    error_str = str(exc_info.value)
    assert "workload identity error" in error_str or "test credential error" in error_str


def test_require_envvar_raises_error_when_envvar_missing():
    with patch.dict("os.environ", {}, clear=True):
        with pytest.raises(ValueError) as exc_info:
            DefaultAzureCredential(require_envvar=True)
        assert "AZURE_TOKEN_CREDENTIALS" in str(exc_info.value)
