# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
import sys
import time

from azure.core.credentials import AccessToken
from azure.core.exceptions import ClientAuthenticationError
from azure.identity import AzureAuthorityHosts, CredentialUnavailableError, VisualStudioCodeCredential
from azure.core.pipeline.policies import SansIOHTTPPolicy
from azure.identity._constants import EnvironmentVariables
from azure.identity._internal.user_agent import USER_AGENT
import pytest
from urllib.parse import urlparse

from helpers import build_aad_response, mock_response, Request, validating_transport

try:
    from unittest import mock
except ImportError:  # python < 3.3
    import mock

GET_REFRESH_TOKEN = VisualStudioCodeCredential.__module__ + ".get_refresh_token"
GET_USER_SETTINGS = VisualStudioCodeCredential.__module__ + ".get_user_settings"


def get_credential(user_settings=None, **kwargs):
    # defaulting to empty user settings ensures tests work when real user settings are available
    with mock.patch(GET_USER_SETTINGS, lambda: user_settings or {}):
        return VisualStudioCodeCredential(**kwargs)


def test_tenant_id():
    def get_transport(expected_tenant):
        return validating_transport(
            requests=[
                Request(base_url="https://{}/{}".format(AzureAuthorityHosts.AZURE_PUBLIC_CLOUD, expected_tenant))
            ],
            responses=[mock_response(json_payload=build_aad_response(access_token="**"))],
        )

    # credential should default to "organizations" tenant
    transport = get_transport("organizations")
    credential = get_credential(transport=transport)
    with mock.patch(GET_REFRESH_TOKEN, lambda _: "**"):
        credential.get_token("scope")
    assert transport.send.call_count == 1

    # ... unless VS Code has a tenant configured
    user_settings = {"azure.tenant": "vs-code-setting"}
    transport = get_transport(user_settings["azure.tenant"])
    credential = get_credential(user_settings, transport=transport)
    with mock.patch(GET_REFRESH_TOKEN, lambda _: "**"):
        credential.get_token("scope")
    assert transport.send.call_count == 1

    # ... and a tenant specified by the application prevails over VS Code configuration
    transport = get_transport("from-application")
    credential = get_credential(user_settings, tenant_id="from-application", transport=transport)
    with mock.patch(GET_REFRESH_TOKEN, lambda _: "**"):
        credential.get_token("scope")
    assert transport.send.call_count == 1


def test_tenant_id_validation():
    """The credential should raise ValueError when given an invalid tenant_id"""

    valid_ids = {"c878a2ab-8ef4-413b-83a0-199afb84d7fb", "contoso.onmicrosoft.com", "organizations", "common"}
    for tenant in valid_ids:
        get_credential(tenant_id=tenant)

    invalid_ids = {"my tenant", "my_tenant", "/", "\\", '"my-tenant"', "'my-tenant'"}
    for tenant in invalid_ids:
        with pytest.raises(ValueError):
            get_credential(tenant_id=tenant)


def test_no_scopes():
    """The credential should raise ValueError when get_token is called with no scopes"""

    credential = get_credential()
    with pytest.raises(ValueError):
        credential.get_token()


def test_policies_configurable():
    policy = mock.Mock(spec_set=SansIOHTTPPolicy, on_request=mock.Mock())

    def send(*_, **kwargs):
        # ensure the `claims` and `tenant_id` keywords from credential's `get_token` method don't make it to transport
        assert "claims" not in kwargs
        assert "tenant_id" not in kwargs
        return mock_response(json_payload=build_aad_response(access_token="**"))

    credential = get_credential(policies=[policy], transport=mock.Mock(send=send))
    with mock.patch(GET_REFRESH_TOKEN, lambda _: "**"):
        credential.get_token("scope")

    assert policy.on_request.called


def test_user_agent():
    transport = validating_transport(
        requests=[Request(required_headers={"User-Agent": USER_AGENT})],
        responses=[mock_response(json_payload=build_aad_response(access_token="**"))],
    )
    credential = get_credential(transport=transport)
    with mock.patch(GET_REFRESH_TOKEN, lambda _: "**"):
        credential.get_token("scope")


@pytest.mark.parametrize("authority", ("localhost", "https://localhost"))
def test_request_url(authority):
    """the credential should accept an authority, with or without scheme, as an argument or environment variable"""

    tenant_id = "expected-tenant"
    access_token = "***"
    parsed_authority = urlparse(authority)
    expected_netloc = parsed_authority.netloc or authority  # "localhost" parses to netloc "", path "localhost"
    expected_refresh_token = "refresh-token"

    def mock_send(request, **kwargs):
        actual = urlparse(request.url)
        assert actual.scheme == "https"
        assert actual.netloc == expected_netloc
        assert actual.path.startswith("/" + tenant_id)
        assert request.body["refresh_token"] == expected_refresh_token
        return mock_response(json_payload={"token_type": "Bearer", "expires_in": 42, "access_token": access_token})

    credential = get_credential(tenant_id=tenant_id, transport=mock.Mock(send=mock_send), authority=authority)
    with mock.patch(GET_REFRESH_TOKEN, return_value=expected_refresh_token):
        token = credential.get_token("scope")
    assert token.token == access_token

    # authority can be configured via environment variable
    with mock.patch.dict("os.environ", {EnvironmentVariables.AZURE_AUTHORITY_HOST: authority}):
        credential = get_credential(tenant_id=tenant_id, transport=mock.Mock(send=mock_send))
        with mock.patch(GET_REFRESH_TOKEN, return_value=expected_refresh_token):
            credential.get_token("scope")
    assert token.token == access_token


def test_credential_unavailable_error():
    credential = get_credential()
    with mock.patch(GET_REFRESH_TOKEN, return_value=None):
        with pytest.raises(CredentialUnavailableError):
            credential.get_token("scope")


def test_redeem_token():
    expected_token = AccessToken("token", 42)
    expected_value = "value"

    mock_client = mock.Mock(spec=object)
    mock_client.obtain_token_by_refresh_token = mock.Mock(return_value=expected_token)
    mock_client.get_cached_access_token = mock.Mock(return_value=None)

    with mock.patch(GET_REFRESH_TOKEN, return_value=expected_value):
        credential = get_credential(_client=mock_client)
        token = credential.get_token("scope")
        assert token is expected_token
        mock_client.obtain_token_by_refresh_token.assert_called_with(
            ("scope",), expected_value, claims=None, tenant_id=None
        )
        assert mock_client.obtain_token_by_refresh_token.call_count == 1


def test_cache_refresh_token():
    expected_token = AccessToken("token", 42)

    mock_client = mock.Mock(spec=object)
    mock_client.obtain_token_by_refresh_token = mock.Mock(return_value=expected_token)
    mock_client.get_cached_access_token = mock.Mock(return_value=None)
    mock_get_credentials = mock.Mock(return_value="VALUE")

    with mock.patch(GET_REFRESH_TOKEN, mock_get_credentials):
        credential = get_credential(_client=mock_client)
        token = credential.get_token("scope")
        assert token is expected_token
        assert mock_get_credentials.call_count == 1
        token = credential.get_token("scope")
        assert token is expected_token
        assert mock_get_credentials.call_count == 1


def test_no_obtain_token_if_cached():
    expected_token = AccessToken("token", time.time() + 3600)

    mock_client = mock.Mock(
        obtain_token_by_refresh_token=mock.Mock(return_value=expected_token),
        get_cached_access_token=mock.Mock(return_value=expected_token),
    )

    credential = get_credential(_client=mock_client)
    with mock.patch(
        GET_REFRESH_TOKEN,
        mock.Mock(side_effect=Exception("credential should not acquire a new token")),
    ):
        token = credential.get_token("scope")

    assert mock_client.obtain_token_by_refresh_token.call_count == 0
    assert token.token == expected_token.token
    assert token.expires_on == expected_token.expires_on


def test_native_adapter():
    """Exercise the native adapter for the current OS"""

    if sys.platform.startswith("darwin"):
        from azure.identity._internal.macos_vscode_adapter import get_refresh_token
    elif sys.platform.startswith("linux"):
        from azure.identity._internal.linux_vscode_adapter import get_refresh_token
    elif sys.platform.startswith("win"):
        from azure.identity._internal.win_vscode_adapter import get_refresh_token
    else:
        pytest.skip('unsupported platform "{}"'.format(sys.platform))

    # the return value (None in CI, possibly something else on a dev machine) is irrelevant
    # because the goal is simply to expose a native interop problem like a segfault
    get_refresh_token("AzureCloud")


def test_adfs():
    """The credential should raise CredentialUnavailableError when configured for ADFS"""

    credential = get_credential(tenant_id="adfs")
    with pytest.raises(CredentialUnavailableError) as ex:
        credential.get_token("scope")
    assert "adfs" in ex.value.message.lower()


def test_custom_cloud_no_authority():
    """The credential is unavailable when VS Code is configured to use a custom cloud with no known authority"""

    cloud_name = "AzureCustomCloud"
    credential = get_credential({"azure.cloud": cloud_name})
    with pytest.raises(CredentialUnavailableError, match="authority.*" + cloud_name):
        credential.get_token("scope")


@pytest.mark.parametrize(
    "cloud,authority",
    (
        ("AzureCloud", AzureAuthorityHosts.AZURE_PUBLIC_CLOUD),
        ("AzureChinaCloud", AzureAuthorityHosts.AZURE_CHINA),
        ("AzureGermanCloud", AzureAuthorityHosts.AZURE_GERMANY),
        ("AzureUSGovernment", AzureAuthorityHosts.AZURE_GOVERNMENT),
    ),
)
def test_reads_cloud_settings(cloud, authority):
    """the credential should read authority and tenant from VS Code settings when an application doesn't specify them"""

    expected_tenant = "tenant-id"
    user_settings = {"azure.cloud": cloud, "azure.tenant": expected_tenant}

    transport = validating_transport(
        requests=[Request(base_url="https://{}/{}".format(authority, expected_tenant))],
        responses=[mock_response(json_payload=build_aad_response(access_token="**"))],
    )

    credential = get_credential(user_settings, transport=transport)

    with mock.patch(GET_REFRESH_TOKEN, lambda _: "**"):
        credential.get_token("scope")

    assert transport.send.call_count == 1


def test_no_user_settings():
    """the credential should default to Public Cloud and "organizations" tenant when it can't read VS Code settings"""

    transport = validating_transport(
        requests=[Request(base_url="https://{}/{}".format(AzureAuthorityHosts.AZURE_PUBLIC_CLOUD, "organizations"))],
        responses=[mock_response(json_payload=build_aad_response(access_token="**"))],
    )

    credential = get_credential(transport=transport)
    with mock.patch(GET_REFRESH_TOKEN, lambda _: "**"):
        credential.get_token("scope")

    assert transport.send.call_count == 1


def test_multitenant_authentication():
    first_tenant = "first-tenant"
    first_token = "***"
    second_tenant = "second-tenant"
    second_token = first_token * 2

    def send(request, **kwargs):
        # ensure the `claims` and `tenant_id` keywords from credential's `get_token` method don't make it to transport
        assert "claims" not in kwargs
        assert "tenant_id" not in kwargs
        parsed = urlparse(request.url)
        tenant = parsed.path.split("/")[1]
        assert tenant in (first_tenant, second_tenant), 'unexpected tenant "{}"'.format(tenant)
        token = first_token if tenant == first_tenant else second_token
        return mock_response(json_payload=build_aad_response(access_token=token))

    credential = get_credential(
        tenant_id=first_tenant, transport=mock.Mock(send=send), additionally_allowed_tenants=["*"]
    )
    with mock.patch(GET_REFRESH_TOKEN, lambda _: "**"):
        token = credential.get_token("scope")
    assert token.token == first_token

    token = credential.get_token("scope", tenant_id=first_tenant)
    assert token.token == first_token

    with mock.patch(GET_REFRESH_TOKEN, lambda _: "**"):
        token = credential.get_token("scope", tenant_id=second_tenant)
    assert token.token == second_token

    # should still default to the first tenant
    token = credential.get_token("scope")
    assert token.token == first_token


def test_multitenant_authentication_not_allowed():
    expected_tenant = "expected-tenant"
    expected_token = "***"

    def send(request, **kwargs):
        # ensure the `claims` and `tenant_id` keywords from credential's `get_token` method don't make it to transport
        assert "claims" not in kwargs
        assert "tenant_id" not in kwargs
        parsed = urlparse(request.url)
        tenant = parsed.path.split("/")[1]
        token = expected_token if tenant == expected_tenant else expected_token * 2
        return mock_response(json_payload=build_aad_response(access_token=token))

    credential = get_credential(
        tenant_id=expected_tenant, transport=mock.Mock(send=send), additionally_allowed_tenants=["*"]
    )

    with mock.patch(GET_REFRESH_TOKEN, lambda _: "**"):
        token = credential.get_token("scope")
    assert token.token == expected_token

    token = credential.get_token("scope", tenant_id=expected_tenant)
    assert token.token == expected_token

    token = credential.get_token("scope", tenant_id="un" + expected_tenant)
    assert token.token == expected_token * 2

    with mock.patch.dict("os.environ", {EnvironmentVariables.AZURE_IDENTITY_DISABLE_MULTITENANTAUTH: "true"}):
        token = credential.get_token("scope", tenant_id="un" + expected_tenant)
        assert token.token == expected_token
