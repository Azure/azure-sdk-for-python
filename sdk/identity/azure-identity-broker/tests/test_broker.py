# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
from azure.identity.broker import InteractiveBrowserCredential, UsernamePasswordCredential


def test_interactive_browser_cred_with_broker():
    cred = InteractiveBrowserCredential(allow_broker=True)
    assert cred._allow_broker


def test_interactive_browser_cred_without_broker():
    cred = InteractiveBrowserCredential()
    assert not cred._allow_broker

    cred = InteractiveBrowserCredential(allow_broker=False)
    assert not cred._allow_broker

def test_username_password_cred_with_broker():
    cred = UsernamePasswordCredential(allow_broker=True)
    assert cred._allow_broker


def test_username_password_cred_without_broker():
    cred = UsernamePasswordCredential("client-id", "username", "password")
    assert not cred._allow_broker

    cred = UsernamePasswordCredential("client-id", "username", "password", allow_broker=False)
    assert not cred._allow_broker
