# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import os
import uuid
import string
import random

from devtools_testutils.perfstress_tests import PerfStressTest

from corehttp.runtime import PipelineClient, AsyncPipelineClient
from corehttp.runtime.pipeline import Pipeline, AsyncPipeline
from corehttp.transport.aiohttp import AioHttpTransport
from corehttp.transport.requests import RequestsTransport
from corehttp.transport.httpx import HttpXTransport, AsyncHttpXTransport
from corehttp.runtime.policies import (
    UserAgentPolicy,
    HeadersPolicy,
    ProxyPolicy,
    NetworkTraceLoggingPolicy,
    RetryPolicy,
    AsyncRetryPolicy,
    BearerTokenCredentialPolicy,
    AsyncBearerTokenCredentialPolicy,
)
import corehttp.runtime.policies as policies
from corehttp.credentials import ServiceNamedKeyCredential
from corehttp.exceptions import (
    ClientAuthenticationError,
    ResourceExistsError,
    ResourceNotFoundError,
    ResourceNotModifiedError,
)
from azure.identity import ClientSecretCredential
from azure.identity.aio import ClientSecretCredential as AsyncClientSecretCredential
from azure.data.tables.aio import TableClient

from azure.storage.blob._shared.authentication import SharedKeyCredentialPolicy as BlobSharedKeyCredentialPolicy
from azure.data.tables._authentication import SharedKeyCredentialPolicy as TableSharedKeyCredentialPolicy

_LETTERS = string.ascii_letters


class _ServiceTest(PerfStressTest):
    transport = None
    async_transport = None

    def __init__(self, arguments):
        super().__init__(arguments)
        self.account_name = self.get_from_env("AZURE_STORAGE_ACCOUNT_NAME")
        self.account_key = self.get_from_env("AZURE_STORAGE_ACCOUNT_KEY")
        async_transport_types = {"aiohttp": AioHttpTransport, "httpx": AsyncHttpXTransport}
        sync_transport_types = {"requests": RequestsTransport, "httpx": HttpXTransport}
        self.tenant_id = os.environ["COREHTTP_TENANT_ID"]
        self.client_id = os.environ["COREHTTP_CLIENT_ID"]
        self.client_secret = os.environ["COREHTTP_CLIENT_SECRET"]
        self.storage_scope = "https://storage.azure.com/.default"

        # defaults transports
        self.sync_transport = RequestsTransport
        self.async_transport = AioHttpTransport

        # if transport is specified, use that
        if self.args.transport:
            # if sync, override sync default
            if self.args.sync:
                try:
                    self.sync_transport = sync_transport_types[self.args.transport]
                except KeyError:
                    raise ValueError(
                        f"Invalid sync transport:{self.args.transport}\n Valid options are:\n- requests\n- httpx\n"
                    )
            # if async, override async default
            else:
                try:
                    self.async_transport = async_transport_types[self.args.transport]
                except KeyError:
                    raise ValueError(
                        f"Invalid async transport:{self.args.transport}\n Valid options are:\n- aiohttp\n- httpx\n"
                    )

        self.error_map = {
            401: ClientAuthenticationError,
            404: ResourceNotFoundError,
            409: ResourceExistsError,
            304: ResourceNotModifiedError,
        }

    def _build_sync_pipeline_client(self, auth_policy):
        default_policies = [
            UserAgentPolicy,
            HeadersPolicy,
            ProxyPolicy,
            NetworkTraceLoggingPolicy,
            RetryPolicy,
        ]

        if self.args.policies is None:
            # if None, only auth policy is passed in
            sync_pipeline = Pipeline(transport=self.sync_transport(), policies=[auth_policy])
        elif self.args.policies == "all":
            # if all, autorest default policies + auth policy
            sync_policies = [auth_policy]
            sync_policies.extend([policy(sdk_moniker=self.sdk_moniker) for policy in default_policies])
            sync_pipeline = Pipeline(transport=self.sync_transport(), policies=sync_policies)
        else:
            sync_policies = [auth_policy]
            for p in self.args.policies.split(","):
                try:
                    policy = getattr(policies, p)
                except AttributeError as exc:
                    raise ValueError(
                        f"Corehttp has no policy named {exc.name}. Please use policies from the following list: {policies.__all__}"
                    ) from exc
                sync_policies.append(policy(sdk_moniker=self.sdk_moniker))
            sync_pipeline = Pipeline(transport=self.sync_transport(), policies=sync_policies)
        return PipelineClient(self.account_endpoint, pipeline=sync_pipeline)

    def _build_async_pipeline_client(self, auth_policy):
        default_policies = [
            UserAgentPolicy,
            HeadersPolicy,
            ProxyPolicy,
            NetworkTraceLoggingPolicy,
            AsyncRetryPolicy,
        ]
        if self.args.policies is None:
            # if None, only auth policy is passed in
            async_pipeline = AsyncPipeline(transport=self.async_transport(), policies=[auth_policy])
        elif self.args.policies == "all":
            # if all, autorest default policies + auth policy
            async_policies = [auth_policy]
            async_policies.extend([policy(sdk_moniker=self.sdk_moniker) for policy in default_policies])
            async_pipeline = AsyncPipeline(transport=self.async_transport(), policies=async_policies)
        else:
            async_policies = [auth_policy]
            # if custom list of policies, pass in custom list + auth policy
            for p in self.args.policies.split(","):
                try:
                    policy = getattr(policies, p)
                except AttributeError as exc:
                    raise ValueError(
                        f"Corehttp has no policy named {exc.name}. Please use policies from the following list: {policies.__all__}"
                    ) from exc
                async_policies.append(policy(sdk_moniker=self.sdk_moniker))
            async_pipeline = AsyncPipeline(transport=self.async_transport(), policies=async_policies)
        return AsyncPipelineClient(self.account_endpoint, pipeline=async_pipeline)

    def _set_auth_policies(self):
        if not self.args.use_entra_id:
            # if tables, create table credential policy, else blob policy
            if "tables" in self.sdk_moniker:
                self.sync_auth_policy = TableSharedKeyCredentialPolicy(
                    ServiceNamedKeyCredential(self.account_name, self.account_key)
                )
                self.async_auth_policy = self.sync_auth_policy
            else:
                self.sync_auth_policy = BlobSharedKeyCredentialPolicy(self.account_name, self.account_key)
                self.async_auth_policy = self.sync_auth_policy
        else:
            sync_credential = ClientSecretCredential(self.tenant_id, self.client_id, self.client_secret)
            self.sync_auth_policy = BearerTokenCredentialPolicy(sync_credential, self.storage_scope)
            async_credential = AsyncClientSecretCredential(self.tenant_id, self.client_id, self.client_secret)
            self.async_auth_policy = AsyncBearerTokenCredentialPolicy(async_credential, self.storage_scope)

    @staticmethod
    def add_arguments(parser):
        super(_ServiceTest, _ServiceTest).add_arguments(parser)
        parser.add_argument(
            "--transport",
            nargs="?",
            type=str,
            help="""Underlying HttpTransport type. Defaults to `aiohttp` if async, `requests` if sync. Other possible values for sync/async:\n"""
            """ - `httpx`\n""",
            default=None,
        )
        parser.add_argument(
            "-s", "--size", nargs="?", type=int, help="Size of data to transfer.  Default is 10240.", default=10240
        )
        parser.add_argument(
            "--policies",
            nargs="?",
            type=str,
            help="""List of policies to pass in to the pipeline. Options:"""
            """\n- None: No extra policies passed in, except for authentication policy. This is the default."""
            """\n- 'all': All policies added automatically by autorest."""
            """\n- 'policy1,policy2': Comma-separated list of policies, such as 'RetryPolicy,UserAgentPolicy'""",
            default=None,
        )
        parser.add_argument(
            "--use-entra-id", action="store_true", help="Use Microsoft Entra ID authentication instead of shared key."
        )


class _BlobTest(_ServiceTest):
    container_name = "perfstress-" + str(uuid.uuid4())

    def __init__(self, arguments):
        super().__init__(arguments)
        self.account_endpoint = self.get_from_env("AZURE_STORAGE_BLOBS_ENDPOINT")
        self.container_name = self.get_from_env("AZURE_STORAGE_CONTAINER_NAME")
        self.api_version = "2021-12-02"
        self.sdk_moniker = f"storage-blob/{self.api_version}"

        self._set_auth_policies()
        self.pipeline_client = self._build_sync_pipeline_client(self.sync_auth_policy)
        self.async_pipeline_client = self._build_async_pipeline_client(self.async_auth_policy)

    async def close(self):
        self.pipeline_client.close()
        await self.async_pipeline_client.close()
        await super().close()


class _TableTest(_ServiceTest):
    table_name = "".join(random.choice(_LETTERS) for i in range(30))

    def __init__(self, arguments):
        super().__init__(arguments)
        self.account_endpoint = self.get_from_env("AZURE_STORAGE_TABLES_ENDPOINT")
        self.api_version = "2019-02-02"
        self.data_service_version = "3.0"
        self.sdk_moniker = f"tables/{self.api_version}"
        self._set_auth_policies()

        self.pipeline_client = self._build_sync_pipeline_client(self.sync_auth_policy)
        self.async_pipeline_client = self._build_async_pipeline_client(self.async_auth_policy)

        self.connection_string = self.get_from_env("AZURE_STORAGE_CONN_STR")
        self.async_table_client = TableClient.from_connection_string(self.connection_string, self.table_name)

    async def global_setup(self):
        await super().global_setup()
        await self.async_table_client.create_table()

    async def global_cleanup(self):
        await self.async_table_client.delete_table()

    def get_base_entity(self, pk, rk, size):
        # 227 is the length of the entity with Data of length 0
        base_entity_length = 227
        data_length = max(size - base_entity_length, 0)
        # size = 227 + data_length
        return {
            "PartitionKey": pk,
            "RowKey": rk,
            "Data": "a" * data_length,
        }

    def get_entity(self, rk=0):
        return {"PartitionKey": "pk", "RowKey": str(rk), "Property1": f"a{rk}", "Property2": f"b{rk}"}

    async def close(self):
        self.pipeline_client.close()
        await self.async_pipeline_client.close()
        await super().close()
