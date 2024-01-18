# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import uuid
import ast

from devtools_testutils.perfstress_tests import PerfStressTest, get_random_bytes

from azure.core import PipelineClient, AsyncPipelineClient
from azure.core.pipeline import (
    Pipeline,
    AsyncPipeline
)
from azure.core.pipeline.transport import (
    RequestsTransport,
    AioHttpTransport,
    AsyncioRequestsTransport,
)
from azure.core.pipeline.policies import (
    UserAgentPolicy,
    HeadersPolicy,
    ProxyPolicy,
    NetworkTraceLoggingPolicy,
    HttpLoggingPolicy,
    RetryPolicy,
    CustomHookPolicy,
    RedirectPolicy,
    RequestIdPolicy,
    ContentDecodePolicy,
    DistributedTracingPolicy,
    SensitiveHeaderCleanupPolicy,
    AsyncRetryPolicy,
    AsyncRedirectPolicy,
)
from azure.core.configuration import Configuration
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
        self.custom_policies = {
            "UserAgentPolicy": UserAgentPolicy,
            "HeadersPolicy": HeadersPolicy,
            "ProxyPolicy": ProxyPolicy,
            "NetworkTraceLoggingPolicy": NetworkTraceLoggingPolicy,
            "HttpLoggingPolicy": HttpLoggingPolicy,
            "RetryPolicy": RetryPolicy if self.args.sync else AsyncRetryPolicy,
            "CustomHookPolicy": CustomHookPolicy,
            "RedirectPolicy": RedirectPolicy if self.args.sync else AsyncRedirectPolicy,
            "ContentDecodePolicy": ContentDecodePolicy,
            "DistributedTracingPolicy": DistributedTracingPolicy,
        }
        self.async_default_policies = [
            UserAgentPolicy(),
            HeadersPolicy(),
            ProxyPolicy(),
            NetworkTraceLoggingPolicy(),
            HttpLoggingPolicy(),
            AsyncRetryPolicy(),
            CustomHookPolicy(),
            AsyncRedirectPolicy(),
            ContentDecodePolicy(),
            DistributedTracingPolicy(),
        ]

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
                    raise ValueError(f"Invalid sync transport:{self.args.transport}\n Valid options are:\n- requests\n")
            # if async, override async default
            else:
                try:
                    self.async_transport = async_transport_types[self.args.transport]
                except KeyError:
                    raise ValueError(f"Invalid async transport:{self.args.transport}\n Valid options are:\n- aiohttp\n- requests\n")

        self.error_map = {
            401: ClientAuthenticationError,
            404: ResourceNotFoundError,
            409: ResourceExistsError,
            304: ResourceNotModifiedError,
        }
    
    def _build_sync_pipeline_client(self, auth_policy):
        sync_core_policies = {
            "UserAgentPolicy": UserAgentPolicy,
            "HeadersPolicy": HeadersPolicy,
            "ProxyPolicy": ProxyPolicy,
            "NetworkTraceLoggingPolicy": NetworkTraceLoggingPolicy,
            "HttpLoggingPolicy": HttpLoggingPolicy,
            "RetryPolicy": RetryPolicy, 
            "CustomHookPolicy": CustomHookPolicy,
            "RedirectPolicy": RedirectPolicy,
            "ContentDecodePolicy": ContentDecodePolicy,
            "DistributedTracingPolicy": DistributedTracingPolicy,
            "RequestIdPolicy": RequestIdPolicy,
            "SensitiveHeaderCleanupPolicy": SensitiveHeaderCleanupPolicy,
        } # last 4 are not included in default generated policies
        default_policies = [
            UserAgentPolicy,
            HeadersPolicy,
            ProxyPolicy,
            NetworkTraceLoggingPolicy,
            HttpLoggingPolicy,
            RetryPolicy, 
            CustomHookPolicy,
            RedirectPolicy
        ]

        if self.args.policies is None:
            # if None, only auth policy is passed in
            sync_pipeline = Pipeline(
                transport=self.sync_transport(),
                policies=[auth_policy]
            )
        elif self.args.policies == "all":
            # if all, autorest default policies + auth policy
            sync_policies = [policy(sdk_moniker=self.sdk_moniker) for policy in default_policies]
            sync_policies.append(auth_policy)
            sync_pipeline = Pipeline(
                transport=self.sync_transport(),
                policies=sync_policies
            )
        else:
            # if custom list of policies, pass in custom list + auth policy
            try:
                custom_policies = ast.literal_eval(self.args.policies)
            except ValueError as exc:
                raise ValueError(f"""Invalid policies list: {self.args.policies}\n."""
                                 f"""Must be string list of string policies from the following list:\n"""
                                 f"""{list(sync_core_policies.keys())}""") from exc
            try:
                sync_policies = []
                for policy in custom_policies:
                    # if ContentDecodePolicy passed in, check for kwargs for that policy
                    if policy == "ContentDecodePolicy" and self.args.content_decode_policy_kwargs:
                        policy_kwargs = ast.literal_eval(self.args.content_decode_policy_kwargs)
                        print(policy_kwargs)
                        policy = sync_core_policies[policy](**policy_kwargs)
                        sync_policies.append(policy)
                    # else, just add policy to list
                    else:
                        policy = sync_core_policies[policy](sdk_moniker=self.sdk_moniker)
                        sync_policies.append(policy)
            except KeyError as exc:
                raise ValueError(f"Invalid policy in: {self.args.policies}\n Valid options are:\n- {list(sync_core_policies.keys())}") from exc
            sync_policies.append(auth_policy)
            sync_pipeline = Pipeline(
                transport=self.sync_transport(),
                policies=sync_policies
            )
        return PipelineClient(
            self.account_endpoint, pipeline=sync_pipeline
        )

    def _build_async_pipeline_client(self, auth_policy):
        async_core_policies = {
            "UserAgentPolicy": UserAgentPolicy,
            "HeadersPolicy": HeadersPolicy,
            "ProxyPolicy": ProxyPolicy,
            "NetworkTraceLoggingPolicy": NetworkTraceLoggingPolicy,
            "HttpLoggingPolicy": HttpLoggingPolicy,
            "RetryPolicy": AsyncRetryPolicy, 
            "CustomHookPolicy": CustomHookPolicy,
            "RedirectPolicy": AsyncRedirectPolicy,
            "ContentDecodePolicy": ContentDecodePolicy,
            "DistributedTracingPolicy": DistributedTracingPolicy,
            "RequestIdPolicy": RequestIdPolicy,
            "SensitiveHeaderCleanupPolicy": SensitiveHeaderCleanupPolicy,
        } # last 4 are not included in default generated policies
        default_policies = [
            UserAgentPolicy,
            HeadersPolicy,
            ProxyPolicy,
            NetworkTraceLoggingPolicy,
            HttpLoggingPolicy,
            AsyncRetryPolicy, 
            CustomHookPolicy,
            AsyncRedirectPolicy
        ]
        if self.args.policies is None:
            # if None, only auth policy is passed in
            async_pipeline = AsyncPipeline(
                transport=self.async_transport(),
                policies=[auth_policy]
            )
        elif self.args.policies == "all":
            # if all, autorest default policies + auth policy
            async_policies = [policy(sdk_moniker=self.sdk_moniker) for policy in default_policies]
            async_policies.append(auth_policy)
            async_pipeline = AsyncPipeline(
                transport=self.async_transport(),
                policies=async_policies
            )
        else:
            # if custom list of policies, pass in custom list + auth policy
            try:
                custom_policies = ast.literal_eval(self.args.policies)
            except ValueError as exc:
                raise ValueError(f"""Invalid policies list: {self.args.policies}\n."""
                                 f"""Must be string list of string policies from the following list:\n"""
                                 f"""{list(async_core_policies.keys())}""") from exc
            try:
                async_policies = []
                for policy in custom_policies:
                    # if ContentDecodePolicy passed in, check for kwargs for that policy
                    if policy == "ContentDecodePolicy" and self.args.content_decode_policy_kwargs:
                        policy_kwargs = ast.literal_eval(self.args.content_decode_policy_kwargs)
                        policy = async_core_policies[policy](**policy_kwargs)
                        async_policies.append(policy)
                    # else, just add policy to list
                    else:
                        policy = async_core_policies[policy](sdk_moniker=self.sdk_moniker)
                        async_policies.append(policy)
            except KeyError as exc:
                raise ValueError(f"Invalid policy in: {self.args.policies}\n Valid options are:\n- {list(async_core_policies.keys())}") from exc
            async_policies.append(auth_policy)
            async_pipeline = AsyncPipeline(
                transport=self.async_transport(),
                policies=async_policies
            )
        return AsyncPipelineClient(
            self.account_endpoint, pipeline=async_pipeline
        )

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
        parser.add_argument('--policies',
                            nargs='?',
                            type=str,
                            help="""List of policies to pass in to the pipeline. Options:"""
                            """\n- None: No extra policies passed in, except for authentication policy. This is the default."""
                            """\n- 'all': All policies added automatically by autorest."""
                            """\n- "['policy1','policy2',...]": String list of string policies, such as "['RetryPolicy', 'HttpLoggingPolicy'].""",
                            default=None)
        parser.add_argument('--content-decode-policy-kwargs',
                            nargs='?',
                            type=str,
                        help="""String dict of keyword args to pass to the ContentDecodePolicy if used, such as '{"response_encoding": <encoding_str>}'.""",
                            default=None)

class _BlobTest(_ServiceTest):
    container_name = "perfstress-" + str(uuid.uuid4())

    def __init__(self, arguments):
        super().__init__(arguments)
        self.account_endpoint = self.get_from_env("AZURE_STORAGE_BLOBS_ENDPOINT")
        self.container_name = self.get_from_env("AZURE_STORAGE_CONTAINER_NAME")
        self.api_version = "2021-12-02"
        self.sdk_moniker = f"storage-blob/{self.api_version}"
        self.pipeline_client = self._build_sync_pipeline_client(
            BlobSharedKeyCredentialPolicy(self.account_name, self.account_key)
        )
        self.async_pipeline_client = self._build_async_pipeline_client(
            BlobSharedKeyCredentialPolicy(self.account_name, self.account_key)
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
        self.sdk_moniker = f"tables/{self.api_version}"

        self.pipeline_client = self._build_sync_pipeline_client(
            TableSharedKeyCredentialPolicy(
                AzureNamedKeyCredential(self.account_name, self.account_key)
            )
        )
        self.async_pipeline_client = self._build_async_pipeline_client(
            TableSharedKeyCredentialPolicy(
                AzureNamedKeyCredential(self.account_name, self.account_key)
            )
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
