# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
import pytest
import sys
from azure.identity.broker import InteractiveBrowserBrokerCredential


@pytest.mark.skip("Not compatible with identity 1.15.0b1")
@pytest.mark.skipif(not sys.platform.startswith("win"), reason="tests Windows-specific behavior")
def test_interactive_browser_broker_cred():
    cred = InteractiveBrowserBrokerCredential()
    assert cred._get_app()._enable_broker
