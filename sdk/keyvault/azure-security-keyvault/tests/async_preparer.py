# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See LICENSE.txt in the project root for
# license information.
# -------------------------------------------------------------------------
import asyncio
from unittest.mock import Mock

from azure.core.credentials import AccessToken
from azure.identity.aio import EnvironmentCredential
from azure.security.keyvault.aio import VaultClient

from preparer import VaultClientPreparer


class AsyncVaultClientPreparer(VaultClientPreparer):
    def create_vault_client(self, vault_uri):
        if self.is_live:
            credential = EnvironmentCredential()
        else:
            credential = Mock(get_token=asyncio.coroutine(lambda _: AccessToken("fake-token", 0)))
        return VaultClient(vault_uri, credential)
