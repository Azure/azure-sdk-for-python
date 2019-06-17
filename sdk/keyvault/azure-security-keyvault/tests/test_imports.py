# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See LICENSE.txt in the project root for
# license information.
# -------------------------------------------------------------------------
try:
    from unittest.mock import Mock
except ImportError:  # python < 3.3
    from mock import Mock

from azure.security.keyvault import KeyClient
from azure.security.keyvault import SecretClient
from azure.security.keyvault import VaultClient


def test_imports():
    """instantiate each client and call purge, the easiest operaton to mock"""

    vault_url = "http://foo.bar"
    credential = Mock()

    def mock_run(*args, **kwargs):
        response = Mock()
        response.http_response.status_code = 204
        return response

    pipeline = Mock(run=mock_run)

    vault_client = VaultClient(vault_url, credential, pipeline=pipeline)

    KeyClient(vault_url, credential, pipeline=pipeline).purge_deleted_key("key name")
    vault_client.keys.purge_deleted_key("key name")

    SecretClient(vault_url, credential, pipeline=pipeline).purge_deleted_secret("secret name")
    vault_client.secrets.purge_deleted_secret("secret name")
