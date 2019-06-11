# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See LICENSE.txt in the project root for
# license information.
# -------------------------------------------------------------------------
import asyncio
from unittest.mock import Mock

from azure.identity.aio import AsyncEnvironmentCredential
from azure.security.keyvault.aio import VaultClient

from preparer import VaultClientPreparer


class AsyncVaultClientPreparer(VaultClientPreparer):
    def create_vault_client(self, vault_uri):
        if self.is_live:
            credential = AsyncEnvironmentCredential()
        else:
            credential = Mock(get_token=asyncio.coroutine(lambda _: "fake-token"))
        return VaultClient(vault_uri, credential)
