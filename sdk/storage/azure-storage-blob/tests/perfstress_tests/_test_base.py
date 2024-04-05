# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import uuid

from devtools_testutils.perfstress_tests import PerfStressTest
from azure.storage.blob import BlobServiceClient as SyncBlobServiceClient
from azure.storage.blob.aio import BlobServiceClient as AsyncBlobServiceClient
from azure.identity import ClientSecretCredential as SyncClientSecretCredential
from azure.identity.aio import ClientSecretCredential as AsyncClientSecretCredential

from .key_wrapper import KeyWrapper


class _ServiceTest(PerfStressTest):
    service_client = None
    async_service_client = None

    def __init__(self, arguments):
        super().__init__(arguments)
        if self.args.test_proxies:
            self._client_kwargs['_additional_pipeline_policies'] = self._client_kwargs['per_retry_policies']
        self._client_kwargs['max_single_put_size'] = self.args.max_put_size
        self._client_kwargs['max_block_size'] = self.args.max_block_size
        self._client_kwargs['min_large_block_upload_threshold'] = self.args.buffer_threshold
        if self.args.client_encryption:
            self.key_encryption_key = KeyWrapper()
            self._client_kwargs['require_encryption'] = True
            self._client_kwargs['key_encryption_key'] = self.key_encryption_key
            self._client_kwargs['encryption_version'] = self.args.client_encryption
        # self._client_kwargs['api_version'] = '2019-02-02'  # Used only for comparison with T1 legacy tests

        if not _ServiceTest.service_client or self.args.no_client_share:
            if self.args.use_entra_id:
                tenant_id = self.get_from_env("AZURE-STORAGE-BLOB_TENANT_ID")
                client_id = self.get_from_env("AZURE-STORAGE-BLOB_CLIENT_ID")
                client_secret = self.get_from_env("AZURE-STORAGE-BLOB_CLIENT_SECRET")
                sync_token_credential = SyncClientSecretCredential(
                    tenant_id,
                    client_id,
                    client_secret
                )
                async_token_credential = AsyncClientSecretCredential(
                    tenant_id,
                    client_id,
                    client_secret
                )
                account_name = self.get_from_env("AZURE_STORAGE_ACCOUNT_NAME")
                # We assume these tests will only be run on the Azure public cloud for now.
                url = f"https://{account_name}.blob.core.windows.net"
                _ServiceTest.service_client = SyncBlobServiceClient(account_url=url, credential=sync_token_credential, **self._client_kwargs)
                _ServiceTest.async_service_client = AsyncBlobServiceClient(account_url=url, credential=async_token_credential, **self._client_kwargs)
            else:
                connection_string = self.get_from_env("AZURE_STORAGE_CONNECTION_STRING")
                _ServiceTest.service_client = SyncBlobServiceClient.from_connection_string(conn_str=connection_string, **self._client_kwargs)
                _ServiceTest.async_service_client = AsyncBlobServiceClient.from_connection_string(conn_str=connection_string, **self._client_kwargs)
        self.service_client = _ServiceTest.service_client
        self.async_service_client = _ServiceTest.async_service_client

    async def close(self):
        await self.async_service_client.close()
        await super().close()

    @staticmethod
    def add_arguments(parser):
        super(_ServiceTest, _ServiceTest).add_arguments(parser)
        parser.add_argument('--max-put-size', nargs='?', type=int, help='Maximum size of data uploading in single HTTP PUT. Defaults to 64*1024*1024', default=64*1024*1024)
        parser.add_argument('--max-block-size', nargs='?', type=int, help='Maximum size of data in a block within a blob. Defaults to 4*1024*1024', default=4*1024*1024)
        parser.add_argument('--buffer-threshold', nargs='?', type=int, help='Minimum block size to prevent full block buffering. Defaults to 4*1024*1024+1', default=4*1024*1024+1)
        parser.add_argument('--client-encryption', nargs='?', type=str, help='The version of client-side encryption to use. Leave out for no encryption.', default=None)
        parser.add_argument('--max-concurrency', nargs='?', type=int, help='Maximum number of concurrent threads used for data transfer. Defaults to 1', default=1)
        parser.add_argument('-s', '--size', nargs='?', type=int, help='Size of data to transfer.  Default is 10240.', default=10240)
        parser.add_argument('--no-client-share', action='store_true', help='Create one ServiceClient per test instance.  Default is to share a single ServiceClient.', default=False)
        parser.add_argument(
            "--use-entra-id", action="store_true", help="Use Microsoft Entra ID authentication instead of connection string."
        )


class _ContainerTest(_ServiceTest):
    container_name = "perfstress-" + str(uuid.uuid4())

    def __init__(self, arguments):
        super().__init__(arguments)
        self.container_client = self.service_client.get_container_client(self.container_name)
        self.async_container_client = self.async_service_client.get_container_client(self.container_name)

    async def global_setup(self):
        await super().global_setup()
        await self.async_container_client.create_container()

    async def global_cleanup(self):
        await self.async_container_client.delete_container()
        await super().global_cleanup()

    async def close(self):
        await self.async_container_client.close()
        await super().close()


class _BlobTest(_ContainerTest):
    def __init__(self, arguments):
        super().__init__(arguments)
        blob_name = "blobtest-" + str(uuid.uuid4())
        self.blob_client = self.container_client.get_blob_client(blob_name)
        self.async_blob_client = self.async_container_client.get_blob_client(blob_name)

    async def close(self):
        await self.async_blob_client.close()
        await super().close()
