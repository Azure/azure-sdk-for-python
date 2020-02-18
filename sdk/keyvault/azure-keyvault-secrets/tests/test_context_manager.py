# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
from azure.keyvault.secrets import SecretClient

from _shared.helpers import mock


def test_close():
    transport = mock.MagicMock()
    client = SecretClient(vault_url="https://localhost", credential=object(), transport=transport)
    client.close()
    assert transport.__enter__.call_count == 0
    assert transport.__exit__.call_count == 1


def test_context_manager():
    transport = mock.MagicMock()
    client = SecretClient(vault_url="https://localhost", credential=object(), transport=transport)

    with client:
        assert transport.__enter__.call_count == 1
    assert transport.__enter__.call_count == 1
    assert transport.__exit__.call_count == 1
