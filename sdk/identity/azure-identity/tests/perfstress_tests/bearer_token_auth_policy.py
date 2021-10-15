# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See LICENSE.txt in the project root for
# license information.
# -------------------------------------------------------------------------
import asyncio
import time
from unittest.mock import Mock

from azure_devtools.perfstress_tests import PerfStressTest

from azure.core.credentials import AccessToken
from azure.core.pipeline import AsyncPipeline, Pipeline
from azure.core.pipeline.policies import AsyncBearerTokenCredentialPolicy, BearerTokenCredentialPolicy
from azure.core.pipeline.transport import HttpRequest


class BearerTokenPolicyTest(PerfStressTest):
    def __init__(self, arguments):
        super().__init__(arguments)

        token = AccessToken("**", int(time.time() + 3600))

        self.request = HttpRequest("GET", "https://localhost")

        credential = Mock(get_token=Mock(return_value=token))
        self.pipeline = Pipeline(transport=Mock(), policies=[BearerTokenCredentialPolicy(credential=credential)])

        get_token_future = asyncio.Future()
        get_token_future.set_result(token)
        async_credential = Mock(get_token=Mock(return_value=get_token_future))

        send_future = asyncio.Future()
        send_future.set_result(Mock())
        async_transport = Mock(send=Mock(return_value=send_future))
        self.async_pipeline = AsyncPipeline(
            async_transport, policies=[AsyncBearerTokenCredentialPolicy(credential=async_credential)]
        )

    def run_sync(self):
        self.pipeline.run(self.request)

    async def run_async(self):
        await self.async_pipeline.run(self.request)
