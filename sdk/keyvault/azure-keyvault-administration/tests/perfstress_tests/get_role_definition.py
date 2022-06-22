# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

import uuid
from azure_devtools.perfstress_tests import PerfStressTest
from azure.identity import DefaultAzureCredential
from azure.identity.aio import DefaultAzureCredential as AsyncDefaultAzureCredential
from azure.keyvault.administration import (
    KeyVaultAccessControlClient, 
    KeyVaultDataAction,
    KeyVaultPermission,
     KeyVaultRoleScope,
)
from azure.keyvault.administration.aio import KeyVaultAccessControlClient as AsyncKeyVaultAccessControlClient


class GetRoleDefinitionTest(PerfStressTest):

    def __init__(self, arguments):
        super().__init__(arguments)

        # Auth configuration
        self.credential = DefaultAzureCredential()
        self.async_credential = AsyncDefaultAzureCredential()

        # Create clients
        vault_url = self.get_from_env("AZURE_MANAGEDHSM_URL")
        self.client = KeyVaultAccessControlClient(vault_url, self.credential, **self._client_kwargs)
        self.async_client = AsyncKeyVaultAccessControlClient(vault_url, self.async_credential, **self._client_kwargs)
        self.role_name = uuid.uuid4()
        self.scope = KeyVaultRoleScope.GLOBAL
        self.permissions = [KeyVaultPermission(data_actions=[KeyVaultDataAction.CREATE_HSM_KEY])]
    
    async def global_setup(self):
        """The global setup is run only once."""
        await super().global_setup()
        await self.async_client.set_role_definition(scope=self.scope, name=self.role_name, permissions=self.permissions)

    async def global_cleanup(self):
        """The global cleanup is run only once."""
        await self.async_client.delete_role_definition(scope=self.scope, name=self.role_name)
        await super().global_cleanup()
    
    async def close(self):
        """This is run after cleanup."""
        await self.async_client.close()
        await self.async_credential.close()
        await super().close()

    def run_sync(self):
        """The synchronous perf test."""
        self.client.get_role_definition(self.scope, self.role_name)

    async def run_async(self):
        """The asynchronous perf test."""
        await self.async_client.get_role_definition(self.scope, self.role_name)
