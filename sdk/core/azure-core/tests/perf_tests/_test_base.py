# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import uuid

from devtools_testutils.perfstress_tests import PerfStressTest, get_random_bytes

from azure.core import PipelineClient, AsyncPipelineClient
from azure.core.pipeline.transport import (
    RequestsTransport,
    AioHttpTransport,
    AsyncioRequestsTransport,
)
from azure.core.credentials import AzureNamedKeyCredential
from azure.core.exceptions import (
    ClientAuthenticationError,
    ResourceExistsError,
    ResourceNotFoundError,
    ResourceNotModifiedError,
)

from azure.storage.blob._shared.authentication import SharedKeyCredentialPolicy as BlobSharedKeyCredentialPolicy
from azure.data.tables._authentication import SharedKeyCredentialPolicy as TableSharedKeyCredentialPolicy


class _ServiceTest(PerfStressTest):
    transport = None
    async_transport = None

    def __init__(self, arguments):
        super().__init__(arguments)
        self.account_name = self.get_from_env("AZURE_STORAGE_ACCOUNT_NAME")
        self.account_key = self.get_from_env("AZURE_STORAGE_ACCOUNT_KEY")
        async_transport_types = {"aiohttp": AioHttpTransport, "requests": AsyncioRequestsTransport}
        sync_transport_types = {"requests": RequestsTransport}

        # defaults transports
        self.sync_transport = RequestsTransport
        self.async_transport = AioHttpTransport

        # if transport is specified, use that
        if self.args.transport:
            # if sync, override sync default
            if self.args.sync:
                try:
                    self.sync_transport = sync_transport_types[self.args.transport]
                except:
                    raise ValueError(f"Invalid sync transport:{self.args.transport}\n Valid options are:\n- requests\n")
            # if async, override async default
            else:
                try:
                    self.async_transport = async_transport_types[self.args.transport]
                except:
                    raise ValueError(f"Invalid async transport:{self.args.transport}\n Valid options are:\n- aiohttp\n- requests\n")

        self.error_map = {
            401: ClientAuthenticationError,
            404: ResourceNotFoundError,
            409: ResourceExistsError,
            304: ResourceNotModifiedError,
        }

    @staticmethod
    def add_arguments(parser):
        super(_ServiceTest, _ServiceTest).add_arguments(parser)
        parser.add_argument(
            '--transport',
            nargs='?',
            type=str,
            help="""Underlying HttpTransport type. Defaults to `aiohttp` if async, `requests` if sync. Other possible values for async:\n"""
                 """ - `requests`\n""",
            default=None
        )
        parser.add_argument('-s', '--size', nargs='?', type=int, help='Size of data to transfer.  Default is 10240.', default=10240)

class _BlobTest(_ServiceTest):
    container_name = "perfstress-" + str(uuid.uuid4())

    def __init__(self, arguments):
        super().__init__(arguments)
        self.account_endpoint = self.get_from_env("AZURE_STORAGE_BLOBS_ENDPOINT")
        self.container_name = self.get_from_env("AZURE_STORAGE_CONTAINER_NAME")
        self.api_version = "2021-12-02"

        self.pipeline_client = PipelineClient(
            self.account_endpoint, transport=self.sync_transport(), policies=[
                BlobSharedKeyCredentialPolicy(self.account_name, self.account_key)
            ]
        )
        self.async_pipeline_client = AsyncPipelineClient(self.account_endpoint, transport=self.async_transport(), policies=[
                BlobSharedKeyCredentialPolicy(self.account_name, self.account_key)
            ]
        )

    async def close(self):
        self.pipeline_client.close()
        await self.async_pipeline_client.close()
        await super().close()

class _TableTest(_ServiceTest):
    container_name = "perfstress-" + str(uuid.uuid4())

    def __init__(self, arguments):
        super().__init__(arguments)
        self.account_endpoint = self.get_from_env("AZURE_STORAGE_TABLES_ENDPOINT")
        self.api_version = '2019-02-02'
        self.data_service_version = '3.0'

        self.pipeline_client = PipelineClient(
            self.account_endpoint, transport=self.sync_transport(), policies=[
                TableSharedKeyCredentialPolicy(
                    AzureNamedKeyCredential(self.account_name, self.account_key)
                )
            ]
        )
        self.async_pipeline_client = AsyncPipelineClient(self.account_endpoint, transport=self.async_transport(), policies=[
                TableSharedKeyCredentialPolicy(
                    AzureNamedKeyCredential(self.account_name, self.account_key)
                )
            ]
        )
    
    def get_base_entity(self, pk, rk, size):
        # 227 is the length of the entity with Data of length 0
        base_entity_length = 227
        data_length = max(size - base_entity_length, 0)
        # size = 227 + data_length
        return {
            "PartitionKey": pk,
            "RowKey": rk,
            "Data": 'a' * data_length,
        }
    
    def get_entity(self, rk=0):
        return {
            "PartitionKey": 'pk',
            "RowKey": str(rk),
            "Property1": f'a{rk}',
            "Property2": f'b{rk}'
        }

    async def close(self):
        self.pipeline_client.close()
        await self.async_pipeline_client.close()
        await super().close()
