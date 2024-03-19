# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
import pytest
import sys
from unittest.mock import patch, Mock

from azure.core.exceptions import ClientAuthenticationError
from azure.identity.broker import InteractiveBrowserBrokerCredential


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
