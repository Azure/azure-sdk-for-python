# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See LICENSE.txt in the project root for
# license information.
# -------------------------------------------------------------------------
from unittest.mock import Mock

from azure.security.keyvault.aio import KeyClient
from azure.security.keyvault.aio import SecretClient
from azure.security.keyvault.aio import VaultClient
import pytest


@pytest.mark.asyncio
async def test_imports():
    """instantiate each client and call purge, the easiest operaton to mock"""

    vault_url = "http://foo.bar"
    credential = Mock()

    async def mock_run(*args, **kwargs):
        response = Mock()
        response.http_response.status_code = 204
        return response

    pipeline = Mock(run=mock_run)

    vault_client = VaultClient(vault_url, credential, pipeline=pipeline)

    await KeyClient(vault_url, credential, pipeline=pipeline).purge_deleted_key("key name")
    await vault_client.keys.purge_deleted_key("key name")

    await SecretClient(vault_url, credential, pipeline=pipeline).purge_deleted_secret("secret name")
    await vault_client.secrets.purge_deleted_secret("secret name")
