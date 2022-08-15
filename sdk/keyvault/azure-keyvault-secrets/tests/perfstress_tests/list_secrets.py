# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
import asyncio

from azure_devtools.perfstress_tests import PerfStressTest
from azure.identity import DefaultAzureCredential
from azure.identity.aio import DefaultAzureCredential as AsyncDefaultAzureCredential
from azure.keyvault.secrets import SecretClient
from azure.keyvault.secrets.aio import SecretClient as AsyncSecretClient


class ListSecretsTest(PerfStressTest):
    def __init__(self, arguments):
        super().__init__(arguments)

        # Auth configuration
        self.credential = DefaultAzureCredential()
        self.async_credential = AsyncDefaultAzureCredential()

        # Create clients
        vault_url = self.get_from_env("AZURE_KEYVAULT_URL")
        self.client = SecretClient(vault_url, self.credential, **self._client_kwargs)
        self.async_client = AsyncSecretClient(vault_url, self.async_credential, **self._client_kwargs)
        self.secret_names = ["livekvtestlistperfsecret{}".format(i) for i in range(self.args.count)]

    async def global_setup(self):
        """The global setup is run only once."""
        # Validate that vault contains 0 secrets (including soft-deleted secrets), since additional secrets
        # (including soft-deleted) impact performance.
        async for secret in self.async_client.list_properties_of_secrets():
            raise Exception(
                "KeyVault %s must contain 0 secrets (including soft-deleted) before starting perf test"
                % self.async_client.vault_url
            )
        async for secret in self.async_client.list_deleted_secrets():
            raise Exception(
                "KeyVault %s must contain 0 secrets (including soft-deleted) before starting perf test"
                % self.async_client.vault_url
            )

        await super().global_setup()
        create = [self.async_client.set_secret(name, "secret-value") for name in self.secret_names]
        await asyncio.wait(create)

    async def global_cleanup(self):
        """The global cleanup is run only once."""
        delete = [self.async_client.delete_secret(name) for name in self.secret_names]
        await asyncio.wait(delete)
        purge = [self.async_client.purge_deleted_secret(name) for name in self.secret_names]
        await asyncio.wait(purge)
        await super().global_cleanup()

    async def close(self):
        """This is run after cleanup."""
        await self.async_client.close()
        await self.async_credential.close()
        await super().close()

    def run_sync(self):
        """The synchronous perf test."""
        secret_properties = self.client.list_properties_of_secrets()
        # enumerate secrets to exercise paging code
        list(secret_properties)

    async def run_async(self):
        """The asynchronous perf test."""
        secret_properties = self.async_client.list_properties_of_secrets()
        # enumerate secrets to exercise paging code
        async for _ in secret_properties:
            pass

    @staticmethod
    def add_arguments(parser):
        super(ListSecretsTest, ListSecretsTest).add_arguments(parser)
        parser.add_argument(
            "--count", nargs="?", type=int, help="Number of secrets to list. Defaults to 10", default=10
        )
