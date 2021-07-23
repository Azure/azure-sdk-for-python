# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
from azure.core.pipeline.policies import ContentDecodePolicy, SansIOHTTPPolicy
from azure.identity import OnBehalfOfCredential, UserAssertion, UsernamePasswordCredential
from azure.identity._internal.user_agent import USER_AGENT
from six.moves.urllib_parse import urlparse

import os

try:
    from unittest.mock import MagicMock, Mock, patch
except ImportError:
    from mock import MagicMock, Mock, patch  # type: ignore


import pytest

from helpers import build_aad_response, get_discovery_response, mock_response
from recorded_test_case import RecordedTestCase


class RecordedTests(RecordedTestCase):
    def __init__(self, *args, **kwargs):

        from azure_devtools.scenario_tests import GeneralNameReplacer, RequestUrlNormalizer
        from recording_processors import IdTokenProcessor, RecordingRedactor

        scrubber = GeneralNameReplacer()
        super(RecordedTestCase, self).__init__(
            *args,
            recording_processors=[RecordingRedactor(record_unique_values=True), scrubber],
            replay_processors=[RequestUrlNormalizer(), IdTokenProcessor()],
            **kwargs
        )

    def test_obo(self):
        TENANT_ID = os.environ["OBO_TENANT_ID"]
        CLIENT_ID = os.environ["OBO_CLIENT_ID"]
        CLIENT_SECRET = os.environ["OBO_CLIENT_SECRET"]

        user_credential = UsernamePasswordCredential(CLIENT_ID, os.environ["OBO_USERNAME"], os.environ["OBO_PASSWORD"])
        user_token = user_credential.get_token(os.environ["OBO_SCOPE"])

        # avoid showing a specific client in the snippet
        class AzureClient(SubscriptionClient):
            def get_resource(self):
                return list(self.subscriptions.list())

        # [START obo]
        credential = OnBehalfOfCredential(TENANT_ID, CLIENT_ID, CLIENT_SECRET)
        client = AzureClient(credential)

        # typically the user token comes from an incoming HTTP request from the user
        with UserAssertion(user_token.token):
            # all token requests in this block will use the same assertion
            client.get_resource()
        # [END obo]



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


@pytest.mark.skip("depends on outstanding PR")
def test_close():
    transport = MagicMock()
    credential = OnBehalfOfCredential("tenant-id", "client-id", "client-secret", transport=transport)
    assert transport.__exit__.call_count == 0

    credential.close()
    assert transport.__exit__.call_count == 1


@pytest.mark.skip("depends on outstanding PR")
def test_context_manager():
    transport = MagicMock()
    credential = OnBehalfOfCredential("tenant-id", "client-id", "client-secret", transport=transport)

    with credential:
        assert transport.__enter__.call_count == 1

    assert transport.__enter__.call_count == 1
    assert transport.__exit__.call_count == 1


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


def test_user_agent():
    def send(request, **_):
        assert request.headers["User-Agent"] == USER_AGENT
        parsed = urlparse(request.url)
        tenant = parsed.path.split("/")[1]
        if "/oauth2/v2.0/token" not in parsed.path:
            return get_discovery_response("https://{}/{}".format(parsed.netloc, tenant))
        return mock_response(json_payload=build_aad_response(access_token="***"))

    credential = OnBehalfOfCredential("tenant-id", "client-id", "client-secret", transport=Mock(send=send))
    with UserAssertion("..."):
        credential.get_token("scope")
