# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
from azure.core.pipeline import AsyncPipeline
from azure.core.pipeline.transport import HttpRequest as PipelineTransportHttpRequest
from azure.core.pipeline.policies import (
    UserAgentPolicy,
    AsyncRedirectPolicy,
)
from azure.core.pipeline.transport import (
    AioHttpTransport,
)
# This code violates do-not-import-asyncio

async def main():
    port = 8080
    request = PipelineTransportHttpRequest("GET", "http://localhost:{}/basic/string".format(port))
    policies = [UserAgentPolicy("myusergant"), AsyncRedirectPolicy()]
    async with AsyncPipeline(AioHttpTransport(), policies=policies) as pipeline:
        response = await pipeline.run(request)
        print(response.http_response.status_code)
