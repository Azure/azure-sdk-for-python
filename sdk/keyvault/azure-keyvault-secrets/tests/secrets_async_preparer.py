# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
import asyncio
from unittest.mock import Mock

from azure.core.credentials import AccessToken
from azure.identity.aio import EnvironmentCredential

from secrets_preparer import VaultClientPreparer

from secrets_vault_client_async import VaultClient


class AsyncVaultClientPreparer(VaultClientPreparer):
    def create_vault_client(self, vault_uri):
        if self.is_live:
            credential = EnvironmentCredential()
        else:
            credential = Mock(get_token=asyncio.coroutine(lambda _: AccessToken("fake-token", 0)))
        return VaultClient(vault_uri, credential)
