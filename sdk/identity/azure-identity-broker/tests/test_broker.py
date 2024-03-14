# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
import pytest
import sys
from unittest.mock import patch, Mock
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
                parent_window_handle="window_handle", use_operating_system_account=True
            )
            cred.get_token("scope")
        except Exception:  # msal raises TypeError which is expected. We are not testing msal here.
            pass
        assert mock_signin_silently.called
