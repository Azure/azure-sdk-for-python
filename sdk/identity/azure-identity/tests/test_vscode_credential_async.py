# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
import time
from unittest import mock
from urllib.parse import urlparse

from azure.core.credentials import AccessToken
from azure.identity import AzureAuthorityHosts, CredentialUnavailableError
from azure.identity._constants import EnvironmentVariables
from azure.identity._internal.user_agent import USER_AGENT
from azure.identity.aio import VisualStudioCodeCredential
from azure.core.pipeline.policies import SansIOHTTPPolicy
import pytest

from helpers import build_aad_response, mock_response, Request
from helpers_async import async_validating_transport, wrap_in_future
from test_vscode_credential import GET_REFRESH_TOKEN, GET_USER_SETTINGS


def get_credential(user_settings=None, **kwargs):
    # defaulting to empty user settings ensures tests work when real user settings are available
    with mock.patch(GET_USER_SETTINGS, lambda: user_settings or {}):
        return VisualStudioCodeCredential(**kwargs)


@pytest.mark.asyncio
async def test_tenant_id():
    def get_transport(expected_tenant):
        return async_validating_transport(
            requests=[
                Request(base_url="https://{}/{}".format(AzureAuthorityHosts.AZURE_PUBLIC_CLOUD, expected_tenant))
            ],
            responses=[mock_response(json_payload=build_aad_response(access_token="**"))],
        )

    # credential should default to "organizations" tenant
    transport = get_transport("organizations")
    credential = get_credential(transport=transport)
    with mock.patch(GET_REFRESH_TOKEN, lambda _: "**"):
        await credential.get_token("scope")
    assert transport.send.call_count == 1

    # ... unless VS Code has a tenant configured
    user_settings = {"azure.tenant": "vs-code-setting"}
    transport = get_transport(user_settings["azure.tenant"])
    credential = get_credential(user_settings, transport=transport)
    with mock.patch(GET_REFRESH_TOKEN, lambda _: "**"):
        await credential.get_token("scope")
    assert transport.send.call_count == 1

    # ... and a tenant specified by the application prevails over VS Code configuration
    transport = get_transport("from-application")
    credential = get_credential(user_settings, tenant_id="from-application", transport=transport)
    with mock.patch(GET_REFRESH_TOKEN, lambda _: "**"):
        await credential.get_token("scope")
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


@pytest.mark.asyncio
async def test_no_scopes():
    """The credential should raise ValueError when get_token is called with no scopes"""

    credential = get_credential()
    with pytest.raises(ValueError):
        await credential.get_token()


@pytest.mark.asyncio
async def test_policies_configurable():
    policy = mock.Mock(spec_set=SansIOHTTPPolicy, on_request=mock.Mock())

    async def send(*_, **__):
        return mock_response(json_payload=build_aad_response(access_token="**"))

    credential = get_credential(policies=[policy], transport=mock.Mock(send=send))
    with mock.patch(GET_REFRESH_TOKEN, lambda _: "**"):
        await credential.get_token("scope")

    assert policy.on_request.called


@pytest.mark.asyncio
async def test_user_agent():
    transport = async_validating_transport(
        requests=[Request(required_headers={"User-Agent": USER_AGENT})],
        responses=[mock_response(json_payload=build_aad_response(access_token="**"))],
    )
    credential = get_credential(transport=transport)
    with mock.patch(GET_REFRESH_TOKEN, lambda _: "**"):
        await credential.get_token("scope")


@pytest.mark.asyncio
@pytest.mark.parametrize("authority", ("localhost", "https://localhost"))
async def test_request_url(authority):
    """the credential should accept an authority, with or without scheme, as an argument or environment variable"""

    tenant_id = "expected-tenant"
    access_token = "***"
    parsed_authority = urlparse(authority)
    expected_netloc = parsed_authority.netloc or authority  # "localhost" parses to netloc "", path "localhost"
    expected_refresh_token = "refresh-token"

    async def mock_send(request, **kwargs):
        actual = urlparse(request.url)
        assert actual.scheme == "https"
        assert actual.netloc == expected_netloc
        assert actual.path.startswith("/" + tenant_id)
        assert request.body["refresh_token"] == expected_refresh_token
        return mock_response(json_payload={"token_type": "Bearer", "expires_in": 42, "access_token": access_token})

    credential = get_credential(
        tenant_id=tenant_id, transport=mock.Mock(send=mock_send), authority=authority
    )
    with mock.patch(GET_REFRESH_TOKEN, return_value=expected_refresh_token):
        token = await credential.get_token("scope")
    assert token.token == access_token

    # authority can be configured via environment variable
    with mock.patch.dict("os.environ", {EnvironmentVariables.AZURE_AUTHORITY_HOST: authority}, clear=True):
        credential = get_credential(tenant_id=tenant_id, transport=mock.Mock(send=mock_send))
        with mock.patch(
            GET_REFRESH_TOKEN, return_value=expected_refresh_token
        ):
            await credential.get_token("scope")
    assert token.token == access_token


@pytest.mark.asyncio
async def test_credential_unavailable_error():
    credential = get_credential()
    with mock.patch(GET_REFRESH_TOKEN, return_value=None):
        with pytest.raises(CredentialUnavailableError):
            await credential.get_token("scope")


@pytest.mark.asyncio
async def test_redeem_token():
    expected_token = AccessToken("token", 42)
    expected_value = "value"

    mock_client = mock.Mock(spec=object)
    token_by_refresh_token = mock.Mock(return_value=expected_token)
    mock_client.obtain_token_by_refresh_token = wrap_in_future(token_by_refresh_token)
    mock_client.get_cached_access_token = mock.Mock(return_value=None)

    with mock.patch(GET_REFRESH_TOKEN, return_value=expected_value):
        credential = get_credential(_client=mock_client)
        token = await credential.get_token("scope")
        assert token is expected_token
        token_by_refresh_token.assert_called_with(("scope",), expected_value)


@pytest.mark.asyncio
async def test_cache_refresh_token():
    expected_token = AccessToken("token", 42)

    mock_client = mock.Mock(spec=object)
    token_by_refresh_token = mock.Mock(return_value=expected_token)
    mock_client.obtain_token_by_refresh_token = wrap_in_future(token_by_refresh_token)
    mock_client.get_cached_access_token = mock.Mock(return_value=None)
    mock_get_credentials = mock.Mock(return_value="VALUE")

    credential = get_credential(_client=mock_client)
    with mock.patch(GET_REFRESH_TOKEN, mock_get_credentials):
        await credential.get_token("scope")
        assert mock_get_credentials.call_count == 1
        await credential.get_token("scope")
        assert mock_get_credentials.call_count == 1


@pytest.mark.asyncio
async def test_no_obtain_token_if_cached():
    expected_token = AccessToken("token", time.time() + 3600)

    token_by_refresh_token = mock.Mock(return_value=expected_token)
    mock_client = mock.Mock(
        get_cached_access_token=mock.Mock(return_value=expected_token),
        obtain_token_by_refresh_token=wrap_in_future(token_by_refresh_token)
    )

    credential = get_credential(_client=mock_client)
    with mock.patch(
        GET_REFRESH_TOKEN,
        mock.Mock(side_effect=Exception("credential should not acquire a new token")),
    ):
        token = await credential.get_token("scope")

    assert token_by_refresh_token.call_count == 0
    assert token.token == expected_token.token
    assert token.expires_on == expected_token.expires_on


@pytest.mark.asyncio
async def test_adfs():
    """The credential should raise CredentialUnavailableError when configured for ADFS"""

    credential = get_credential(tenant_id="adfs")
    with pytest.raises(CredentialUnavailableError) as ex:
        await credential.get_token("scope")
    assert "adfs" in ex.value.message.lower()


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "cloud,authority",
    (
        ("AzureCloud", AzureAuthorityHosts.AZURE_PUBLIC_CLOUD),
        ("AzureChinaCloud", AzureAuthorityHosts.AZURE_CHINA),
        ("AzureGermanCloud", AzureAuthorityHosts.AZURE_GERMANY),
        ("AzureUSGovernment", AzureAuthorityHosts.AZURE_GOVERNMENT),
    ),
)
async def test_reads_cloud_settings(cloud, authority):
    """the credential should read authority and tenant from VS Code settings when an application doesn't specify them"""

    expected_tenant = "tenant-id"
    user_settings = {"azure.cloud": cloud, "azure.tenant": expected_tenant}

    transport = async_validating_transport(
        requests=[Request(base_url="https://{}/{}".format(authority, expected_tenant))],
        responses=[mock_response(json_payload=build_aad_response(access_token="**"))],
    )

    credential = get_credential(user_settings, transport=transport)
    with mock.patch(GET_REFRESH_TOKEN, lambda _: "**"):
        await credential.get_token("scope")

    assert transport.send.call_count == 1


@pytest.mark.asyncio
async def test_no_user_settings():
    """the credential should default to Public Cloud and "organizations" tenant when it can't read VS Code settings"""

    transport = async_validating_transport(
        requests=[Request(base_url="https://{}/{}".format(AzureAuthorityHosts.AZURE_PUBLIC_CLOUD, "organizations"))],
        responses=[mock_response(json_payload=build_aad_response(access_token="**"))],
    )

    credential = get_credential(transport=transport)
    with mock.patch(GET_REFRESH_TOKEN, lambda _: "**"):
        await credential.get_token("scope")

    assert transport.send.call_count == 1
