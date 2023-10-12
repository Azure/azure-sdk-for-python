# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
import pytest
from azure.identity.broker import (
    InteractiveBrowserBrokerCredential,
    UsernamePasswordBrokerCredential,
)


@pytest.mark.skip("Not compatible with identity 1.15.0b1")
def test_interactive_browser_cred_with_broker():
    cred = InteractiveBrowserBrokerCredential(allow_broker=True)
    assert cred._allow_broker
    assert cred._get_app()._enable_broker

    cred = InteractiveBrowserBrokerCredential()
    assert cred._allow_broker
    assert cred._get_app()._enable_broker


def test_interactive_browser_cred_without_broker():
    cred = InteractiveBrowserBrokerCredential(allow_broker=False)
    assert not cred._allow_broker


@pytest.mark.skip("Not compatible with identity 1.15.0b1")
def test_username_password_cred_with_broker():
    cred = UsernamePasswordBrokerCredential("client-id", "username", "password", allow_broker=True)
    assert cred._allow_broker
    assert cred._get_app()._enable_broker

    cred = UsernamePasswordBrokerCredential("client-id", "username", "password")
    assert cred._allow_broker
    assert cred._get_app()._enable_broker


def test_username_password_cred_without_broker():
    cred = UsernamePasswordBrokerCredential("client-id", "username", "password", allow_broker=False)
    assert not cred._allow_broker
