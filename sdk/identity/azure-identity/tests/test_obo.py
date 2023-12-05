# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
import os

try:
    from unittest.mock import Mock, patch
except ImportError:
    from mock import Mock, patch  # type: ignore

from azure.core.pipeline.policies import ContentDecodePolicy, SansIOHTTPPolicy
from azure.identity import OnBehalfOfCredential, UsernamePasswordCredential
from azure.identity._constants import EnvironmentVariables
from azure.identity._internal.user_agent import USER_AGENT
import pytest
from urllib.parse import urlparse

from helpers import build_aad_response, FAKE_CLIENT_ID, get_discovery_response, mock_response
from recorded_test_case import RecordedTestCase
from test_certificate_credential import PEM_CERT_PATH
from devtools_testutils import is_live, recorded_by_proxy

missing_variables = [
    var
    for var in (
        "OBO_CERT_BYTES",
        "OBO_CLIENT_ID",
        "OBO_CLIENT_SECRET",
        "OBO_PASSWORD",
        "OBO_SCOPE",
        "OBO_TENANT_ID",
        "OBO_USERNAME",
    )
    if var not in os.environ
]


class TestObo(RecordedTestCase):
    def load_settings(self):
        if is_live():
            self.obo_settings = {
                "cert_bytes": os.environ["OBO_CERT_BYTES"],
                "client_id": os.environ["OBO_CLIENT_ID"],
                "client_secret": os.environ["OBO_CLIENT_SECRET"],
                "password": os.environ["OBO_PASSWORD"],
                "scope": os.environ["OBO_SCOPE"],
                "tenant_id": os.environ["OBO_TENANT_ID"],
                "username": os.environ["OBO_USERNAME"],
            }
        else:
            self.obo_settings = {
                "cert_bytes": open(PEM_CERT_PATH, "rb").read(),
                "client_id": FAKE_CLIENT_ID,
                "client_secret": "secret",
                "password": "fake-password",
                "scope": "api://scope",
                "tenant_id": "tenant",
                "username": "username",
            }

    @pytest.mark.manual
    @pytest.mark.skipif(any(missing_variables), reason="No value for environment variables")
    @recorded_by_proxy
    def test_obo(self):
        self.load_settings()
        client_id = self.obo_settings["client_id"]
        tenant_id = self.obo_settings["tenant_id"]

        user_credential = UsernamePasswordCredential(
            client_id, self.obo_settings["username"], self.obo_settings["password"], tenant_id=tenant_id
        )
        assertion = user_credential.get_token(self.obo_settings["scope"]).token
        credential = OnBehalfOfCredential(
            tenant_id, client_id, client_secret=self.obo_settings["client_secret"], user_assertion=assertion
        )
        credential.get_token(self.obo_settings["scope"])

    @pytest.mark.manual
    @pytest.mark.skipif(any(missing_variables), reason="No value for environment variables")
    @recorded_by_proxy
    def test_obo_cert(self):
        self.load_settings()
        client_id = self.obo_settings["client_id"]
        tenant_id = self.obo_settings["tenant_id"]

        user_credential = UsernamePasswordCredential(
            client_id, self.obo_settings["username"], self.obo_settings["password"], tenant_id=tenant_id
        )
        assertion = user_credential.get_token(self.obo_settings["scope"]).token
        credential = OnBehalfOfCredential(
            tenant_id, client_id, client_certificate=self.obo_settings["cert_bytes"], user_assertion=assertion
        )
        credential.get_token(self.obo_settings["scope"])


def test_multitenant_authentication():
    first_tenant = "first-tenant"
    first_token = "***"
    second_tenant = "second-tenant"
    second_token = first_token * 2

    def send(request, **kwargs):
        # ensure the `claims` and `tenant_id` keywords from credential's `get_token` method don't make it to transport
        assert "claims" not in kwargs
        assert "tenant_id" not in kwargs
        assert request.headers["User-Agent"].startswith(USER_AGENT)
        parsed = urlparse(request.url)
        tenant = parsed.path.split("/")[1]
        assert tenant in (first_tenant, second_tenant), 'unexpected tenant "{}"'.format(tenant)
        if "/oauth2/v2.0/token" not in parsed.path:
            return get_discovery_response("https://{}/{}".format(parsed.netloc, tenant))

        token = first_token if tenant == first_tenant else second_token
        return mock_response(json_payload=build_aad_response(access_token=token))

    transport = Mock(send=Mock(wraps=send))
    credential = OnBehalfOfCredential(
        first_tenant,
        "client-id",
        client_secret="secret",
        user_assertion="assertion",
        transport=transport,
        additionally_allowed_tenants=["*"],
    )
    token = credential.get_token("scope")
    assert token.token == first_token

    token = credential.get_token("scope", tenant_id=first_tenant)
    assert token.token == first_token

    token = credential.get_token("scope", tenant_id=second_tenant)
    assert token.token == second_token

    # should still default to the first tenant
    token = credential.get_token("scope")
    assert token.token == first_token


@pytest.mark.parametrize("authority", ("localhost", "https://localhost"))
def test_authority(authority):
    """the credential should accept an authority, with or without scheme, as an argument or environment variable"""

    tenant_id = "expected-tenant"
    parsed_authority = urlparse(authority)
    expected_netloc = parsed_authority.netloc or authority
    expected_authority = "https://{}/{}".format(expected_netloc, tenant_id)

    mock_ctor = Mock(
        return_value=Mock(acquire_token_on_behalf_of=lambda *_, **__: {"access_token": "**", "expires_in": 42})
    )

    credential = OnBehalfOfCredential(
        tenant_id, "client-id", client_secret="secret", user_assertion="assertion", authority=authority
    )
    with patch("msal.ConfidentialClientApplication", mock_ctor):
        # must call get_token because the credential constructs the MSAL application lazily
        credential.get_token("scope")

    assert mock_ctor.call_count == 1
    _, kwargs = mock_ctor.call_args
    assert kwargs["authority"] == expected_authority
    mock_ctor.reset_mock()

    # authority can be configured via environment variable
    with patch.dict("os.environ", {EnvironmentVariables.AZURE_AUTHORITY_HOST: authority}, clear=True):
        credential = OnBehalfOfCredential(tenant_id, "client-id", client_secret="secret", user_assertion="assertion")
    with patch("msal.ConfidentialClientApplication", mock_ctor):
        credential.get_token("scope")

    assert mock_ctor.call_count == 1
    _, kwargs = mock_ctor.call_args
    assert kwargs["authority"] == expected_authority


def test_tenant_id_validation():
    """The credential should raise ValueError when given an invalid tenant_id"""
    valid_ids = {"c878a2ab-8ef4-413b-83a0-199afb84d7fb", "contoso.onmicrosoft.com", "organizations", "common"}
    for tenant in valid_ids:
        OnBehalfOfCredential(tenant, "client-id", client_secret="secret", user_assertion="assertion")
    invalid_ids = {"my tenant", "my_tenant", "/", "\\", '"my-tenant"', "'my-tenant'"}
    for tenant in invalid_ids:
        with pytest.raises(ValueError):
            OnBehalfOfCredential(tenant, "client-id", client_secret="secret", user_assertion="assertion")


def test_no_scopes():
    """The credential should raise ValueError when get_token is called with no scopes"""
    credential = OnBehalfOfCredential(
        "tenant-id", "client-id", client_secret="client-secret", user_assertion="assertion"
    )
    with pytest.raises(ValueError):
        credential.get_token()


def test_policies_configurable():
    policy = Mock(spec_set=SansIOHTTPPolicy, on_request=Mock(), on_exception=lambda _: False)

    def send(request, **kwargs):
        # ensure the `claims` and `tenant_id` keywords from credential's `get_token` method don't make it to transport
        assert "claims" not in kwargs
        assert "tenant_id" not in kwargs
        parsed = urlparse(request.url)
        tenant = parsed.path.split("/")[1]
        if "/oauth2/v2.0/token" not in parsed.path:
            return get_discovery_response("https://{}/{}".format(parsed.netloc, tenant))
        return mock_response(json_payload=build_aad_response(access_token="***"))

    credential = OnBehalfOfCredential(
        "tenant-id",
        "client-id",
        client_secret="client-secret",
        user_assertion="assertion",
        policies=[ContentDecodePolicy(), policy],
        transport=Mock(send=send),
    )
    credential.get_token("scope")
    assert policy.on_request.called


def test_no_user_assertion():
    """The credential should raise ValueError when ctoring with no user_assertion"""
    with pytest.raises(TypeError):
        credential = OnBehalfOfCredential("tenant-id", "client-id", client_secret="client-secret")


def test_no_client_credential():
    """The credential should raise ValueError when ctoring with no client_secret or client_certificate"""
    with pytest.raises(TypeError):
        credential = OnBehalfOfCredential("tenant-id", "client-id", user_assertion="assertion")
