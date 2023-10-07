# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
from azure.identity.broker import InteractiveBrowserBrokerCredential, UsernamePasswordBrokerCredential


def test_interactive_browser_cred_with_broker():
    cred = InteractiveBrowserBrokerCredential(allow_broker=True)
    assert cred._allow_broker


def test_interactive_browser_cred_without_broker():
    cred = InteractiveBrowserBrokerCredential()
    assert not cred._allow_broker

    cred = InteractiveBrowserBrokerCredential(allow_broker=False)
    assert not cred._allow_broker


def test_username_password_cred_with_broker():
    cred = UsernamePasswordBrokerCredential("client-id", "username", "password", allow_broker=True)
    assert cred._allow_broker


def test_username_password_cred_without_broker():
    cred = UsernamePasswordBrokerCredential("client-id", "username", "password")
    assert not cred._allow_broker

    cred = UsernamePasswordBrokerCredential("client-id", "username", "password", allow_broker=False)
    assert not cred._allow_broker
