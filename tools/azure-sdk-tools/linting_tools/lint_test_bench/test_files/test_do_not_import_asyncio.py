# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
from asyncio import sleep
from azure.core.pipeline import AsyncPipeline
from azure.core.pipeline.transport import HttpRequest as PipelineTransportHttpRequest
from azure.core.pipeline.policies import (
    UserAgentPolicy,
    AsyncRedirectPolicy,
)
from azure.core.pipeline.transport import (
    HttpTransport,
    HttpResponse,
)
# This code violates do-not-import-asyncio, no-legacy-azure-core-http-response-import

async def main():
    port = 8080
    request = PipelineTransportHttpRequest("GET", "http://localhost:{}/basic/string".format(port))
    policies = [UserAgentPolicy("myusergant"), AsyncRedirectPolicy()]
    async with AsyncPipeline(HttpTransport, policies=policies) as pipeline:
        response: HttpResponse = await pipeline.run(request)
        await sleep(0.1)
        print(response.http_response.status_code)
