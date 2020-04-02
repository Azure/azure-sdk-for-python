# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
from azure.keyvault.keys import KeyClient
from azure.keyvault.keys.crypto import CryptographyClient

from _shared.helpers import mock


def test_key_client_close():
    transport = mock.MagicMock()
    client = KeyClient(vault_url="https://localhost", credential=object(), transport=transport)
    client.close()
    assert transport.__enter__.call_count == 0
    assert transport.__exit__.call_count == 1


def test_key_client_context_manager():
    transport = mock.MagicMock()
    client = KeyClient(vault_url="https://localhost", credential=object(), transport=transport)

    with client:
        assert transport.__enter__.call_count == 1
    assert transport.__enter__.call_count == 1
    assert transport.__exit__.call_count == 1


def test_crypto_client_close():
    transport = mock.MagicMock()
    client = CryptographyClient(key="https://localhost/a/b/c", credential=object(), transport=transport)
    client.close()
    assert transport.__enter__.call_count == 0
    assert transport.__exit__.call_count == 1


def test_crypto_client_context_manager():
    transport = mock.MagicMock()
    client = CryptographyClient(key="https://localhost/a/b/c", credential=object(), transport=transport)

    with client:
        assert transport.__enter__.call_count == 1
    assert transport.__enter__.call_count == 1
    assert transport.__exit__.call_count == 1
