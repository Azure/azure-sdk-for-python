# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
import pytest
import re
import sys
from unittest.mock import patch, Mock

from azure.core import PipelineClient
from azure.core.exceptions import ClientAuthenticationError
from azure.core.rest import HttpRequest, HttpResponse
from azure.identity.broker import InteractiveBrowserBrokerCredential, PopTokenRequestOptions
import msal


@pytest.mark.skipif(not sys.platform.startswith("win"), reason="tests Windows-specific behavior")
def test_interactive_browser_broker_cred():
    cred = InteractiveBrowserBrokerCredential()
    assert cred._get_app()._enable_broker


@pytest.mark.skipif(not sys.platform.startswith("win"), reason="tests Windows-specific behavior")
def test_interactive_browser_broker_cred_signed_in_account():
    with patch("msal.broker._signin_silently", Mock(return_value="token")) as mock_signin_silently:
        try:
            cred = InteractiveBrowserBrokerCredential(
                parent_window_handle="window_handle", use_default_broker_account=True
            )
            cred.get_token("scope")
        except Exception:  # msal raises TypeError which is expected. We are not testing msal here.
            pass
        assert mock_signin_silently.called


def test_enable_support_logging_default():
    """The keyword argument for enabling PII in MSAL should be disabled by default."""

    cred = InteractiveBrowserBrokerCredential(parent_window_handle="window_handle")
    with patch("msal.PublicClientApplication") as mock_client_application:
        with patch("msal.PublicClientApplication.acquire_token_interactive"):
            with pytest.raises(ClientAuthenticationError):
                cred.get_token("scope")

        assert mock_client_application.call_count == 1, "credential didn't create an msal application"
        _, kwargs = mock_client_application.call_args
        assert not kwargs["enable_pii_log"]


def test_enable_support_logging_enabled():
    """The keyword argument for enabling PII in MSAL should be propagated correctly."""

    cred = InteractiveBrowserBrokerCredential(parent_window_handle="window_handle", enable_support_logging=True)
    with patch("msal.PublicClientApplication") as mock_client_application:
        with patch("msal.PublicClientApplication.acquire_token_interactive"):
            with pytest.raises(ClientAuthenticationError):
                cred.get_token("scope")

        assert mock_client_application.call_count == 1, "credential didn't create an msal application"
        _, kwargs = mock_client_application.call_args
        assert kwargs["enable_pii_log"]


@pytest.mark.manual
@pytest.mark.skipif(not sys.platform.startswith("win"), reason="tests Windows-specific behavior")
def test_broker_pop_authentication_flow():
    """The credential should be be able to access a resource with a PoP token."""

    endpoint = "https://graph.microsoft.com/beta/me"
    client = PipelineClient(base_url=endpoint)

    request = HttpRequest("GET", endpoint)
    response: HttpResponse = client.send_request(request)

    assert response.status_code == 401

    www_authenticate = response.headers["WWW-Authenticate"]
    found = re.search(r'nonce="(.+?)"', www_authenticate)

    assert found, "server didn't return a nonce"
    nonce = found.group(1)

    request_options = PopTokenRequestOptions(
        {
            "pop": {
                "nonce": nonce,
                "resource_request_url": endpoint,
                "resource_request_method": "GET",
            }
        }
    )

    cred = InteractiveBrowserBrokerCredential(parent_window_handle=msal.PublicClientApplication.CONSOLE_WINDOW_HANDLE)
    pop_token = cred.get_token_info("https://graph.microsoft.com/.default", options=request_options)
    assert pop_token.token_type == "pop"

    request = HttpRequest("GET", endpoint, headers={"Authorization": f"{pop_token.token_type} {pop_token.token}"})
    response = client.send_request(request)

    assert response.status_code == 200
