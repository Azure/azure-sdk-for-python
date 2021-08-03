# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
import os

try:
    from unittest.mock import Mock
except ImportError:
    from mock import Mock  # type: ignore

from azure_devtools.scenario_tests import RecordingProcessor
from azure.core.pipeline.policies import ContentDecodePolicy, SansIOHTTPPolicy
from azure.identity import CredentialUnavailableError, OnBehalfOfCredential, UserAssertion, UsernamePasswordCredential
from azure.identity._internal.user_agent import USER_AGENT
from azure.mgmt.resource import SubscriptionClient
import pytest
from six.moves.urllib_parse import urlparse

from helpers import build_aad_response, build_id_token, FAKE_CLIENT_ID, get_discovery_response, mock_response
from recorded_test_case import RecordedTestCase


class SubscriptionListRemover(RecordingProcessor):
    def process_response(self, response):
        if "/subscriptions/" in response["body"]["string"]:
            response["body"]["string"] = '{"value":[]}'
        return response


class RecordedTests(RecordedTestCase):
    def __init__(self, *args, **kwargs):
        super(RecordedTests, self).__init__(*args, **kwargs)

        if self.is_live:
            missing_variables = [
                var
                for var in (
                    "OBO_CLIENT_ID",
                    "OBO_CLIENT_SECRET",
                    "OBO_PASSWORD",
                    "OBO_SCOPE",
                    "OBO_TENANT_ID",
                    "OBO_USERNAME",
                )
                if var not in os.environ
            ]
            if any(missing_variables):
                pytest.skip("No value for environment variables: " + ", ".join(missing_variables))

            self.recording_processors.append(SubscriptionListRemover())
            self.obo_settings = {
                "client_id": os.environ["OBO_CLIENT_ID"],
                "client_secret": os.environ["OBO_CLIENT_SECRET"],
                "password": os.environ["OBO_PASSWORD"],
                "scope": os.environ["OBO_SCOPE"],
                "tenant_id": os.environ["OBO_TENANT_ID"],
                "username": os.environ["OBO_USERNAME"],
            }
            self.scrubber.register_name_pair(self.obo_settings["tenant_id"], "tenant")
            self.scrubber.register_name_pair(self.obo_settings["username"], "username")

        else:
            self.obo_settings = {
                "client_id": FAKE_CLIENT_ID,
                "client_secret": "secret",
                "password": "fake-password",
                "scope": "api://scope",
                "tenant_id": "tenant",
                "username": "username",
            }

    def test_obo(self):
        client_id = self.obo_settings["client_id"]
        client_secret = self.obo_settings["client_secret"]
        tenant_id = self.obo_settings["tenant_id"]

        user_credential = UsernamePasswordCredential(
            client_id, self.obo_settings["username"], self.obo_settings["password"], tenant_id=tenant_id
        )
        user_token = user_credential.get_token(self.obo_settings["scope"]).token

        # wrap a real client to avoid showing a specific one in the snippet and thus implying the client type matters
        class AzureClient(SubscriptionClient):
            def get_resource(self):
                list(self.subscriptions.list())

        # [START snippet]
        credential = OnBehalfOfCredential(tenant_id, client_id, client_secret)
        client = AzureClient(credential)

        # typically the assertion is an access token from an incoming HTTP request from the user
        with UserAssertion(user_token):
            # all client calls in this block are authenticated on behalf of the same user
            client.get_resource()
        # [END snippet]


def test_caching():
    client_id = "client-id"
    scope = "scope"
    tenant = "tenant-id"

    def send(request, **_):
        assert request.headers["User-Agent"].startswith(USER_AGENT)
        parsed = urlparse(request.url)
        authority = "https://{}/{}".format(parsed.netloc, tenant)
        if "/oauth2/v2.0/token" not in parsed.path:
            return get_discovery_response(authority)
        return mock_response(
            json_payload=build_aad_response(
                access_token=request.body["assertion"],
                refresh_token="***",
                id_token=build_id_token(aud=client_id, iss=authority),
            )
        )

    transport = Mock(send=Mock(wraps=send))
    credential = OnBehalfOfCredential(tenant, client_id, "secret", transport=transport)

    with UserAssertion("A"):
        token = credential.get_token(scope)
        assert token.token == "A"
        requests_sent = transport.send.call_count  # exact request count is up to msal
        assert requests_sent > 0

        # credential should return a cached token
        token = credential.get_token(scope)
        assert token.token == "A"
        assert transport.send.call_count == requests_sent

    with UserAssertion("B"):
        token = credential.get_token(scope)
    assert token.token == "B"
    assert transport.send.call_count > requests_sent


def test_nested_assertion():
    with UserAssertion("A"):
        for assertion in ("A", "B"):
            with pytest.raises(ValueError):
                with UserAssertion(assertion):
                    pass


def test_requires_assertion():
    """The credential should raise CredentialUnavailableError when no user assertion is set"""
    with pytest.raises(CredentialUnavailableError):
        OnBehalfOfCredential("tenant-id", "client-id", "secret").get_token("scope")


def test_tenant_id_validation():
    """The credential should raise ValueError when given an invalid tenant_id"""
    valid_ids = {"c878a2ab-8ef4-413b-83a0-199afb84d7fb", "contoso.onmicrosoft.com", "organizations", "common"}
    for tenant in valid_ids:
        OnBehalfOfCredential(tenant, "client-id", "secret")
    invalid_ids = {"", "my tenant", "my_tenant", "/", "\\", '"my-tenant"', "'my-tenant'"}
    for tenant in invalid_ids:
        with pytest.raises(ValueError):
            OnBehalfOfCredential(tenant, "client-id", "secret")


def test_no_scopes():
    """The credential should raise ValueError when get_token is called with no scopes"""
    credential = OnBehalfOfCredential("tenant-id", "client-id", "client-secret")
    with pytest.raises(ValueError):
        with UserAssertion("..."):
            credential.get_token()


def test_policies_configurable():
    policy = Mock(spec_set=SansIOHTTPPolicy, on_request=Mock(), on_exception=lambda _: False)

    def send(request, **_):
        parsed = urlparse(request.url)
        tenant = parsed.path.split("/")[1]
        if "/oauth2/v2.0/token" not in parsed.path:
            return get_discovery_response("https://{}/{}".format(parsed.netloc, tenant))
        return mock_response(json_payload=build_aad_response(access_token="***"))

    credential = OnBehalfOfCredential(
        "tenant-id", "client-id", "client-secret", policies=[ContentDecodePolicy(), policy], transport=Mock(send=send)
    )
    with UserAssertion("..."):
        credential.get_token("scope")
    assert policy.on_request.called
