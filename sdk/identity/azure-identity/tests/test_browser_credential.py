# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
from azure.core.exceptions import ClientAuthenticationError
from azure.core.pipeline.policies import SansIOHTTPPolicy
from azure.core.pipeline.transport import RequestsTransport
from azure.identity import InteractiveBrowserCredential
from azure.identity._internal.user_agent import USER_AGENT
import pytest
from unittest.mock import ANY, Mock, patch


WEBBROWSER_OPEN = InteractiveBrowserCredential.__module__ + ".webbrowser.open"


@pytest.mark.manual
def test_browser_credential():
    transport = Mock(wraps=RequestsTransport())
    credential = InteractiveBrowserCredential(transport=transport)
    scope = "https://management.azure.com/.default"  # N.B. this is valid only in Public Cloud

    record = credential.authenticate(scopes=(scope,))
    assert record.authority
    assert record.home_account_id
    assert record.tenant_id
    assert record.username

    # credential should have a cached access token for the scope used in authenticate
    with patch(WEBBROWSER_OPEN, Mock(side_effect=Exception("credential should authenticate silently"))):
        token = credential.get_token(scope)
    assert token.token

    credential = InteractiveBrowserCredential(transport=transport)
    token = credential.get_token(scope)
    assert token.token

    with patch(WEBBROWSER_OPEN, Mock(side_effect=Exception("credential should authenticate silently"))):
        second_token = credential.get_token(scope)
    assert second_token.token == token.token

    # every request should have the correct User-Agent
    for call in transport.send.call_args_list:
        args, _ = call
        request = args[0]
        assert request.headers["User-Agent"] == USER_AGENT


def test_tenant_id_validation():
    """The credential should raise ValueError when given an invalid tenant_id"""

    valid_ids = {"c878a2ab-8ef4-413b-83a0-199afb84d7fb", "contoso.onmicrosoft.com", "organizations", "common"}
    for tenant in valid_ids:
        InteractiveBrowserCredential(tenant_id=tenant)

    invalid_ids = {"my tenant", "my_tenant", "/", "\\", '"my-tenant"', "'my-tenant'"}
    for tenant in invalid_ids:
        with pytest.raises(ValueError):
            InteractiveBrowserCredential(tenant_id=tenant)


def test_no_scopes():
    """The credential should raise when get_token is called with no scopes"""

    with pytest.raises(ValueError):
        InteractiveBrowserCredential().get_token()


def test_policies_configurable():
    # the policy raises an exception so this test can run without authenticating i.e. opening a browser
    expected_message = "test_policies_configurable"
    policy = Mock(spec_set=SansIOHTTPPolicy, on_request=Mock(side_effect=Exception(expected_message)))

    credential = InteractiveBrowserCredential(policies=[policy])

    with pytest.raises(ClientAuthenticationError) as ex:
        credential.get_token("scope")

    assert expected_message in ex.value.message
    assert policy.on_request.called
