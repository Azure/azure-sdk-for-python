# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

"""
FILE: sample_stream.py

DESCRIPTION:
    This sample demonstrates how to consume a JSON Lines (JSONL) streaming
    response synchronously and asynchronously using the Stream/AsyncStream
    iterators and JSONLDecoder/AsyncJSONLDecoder.

USAGE:
    python sample_stream.py
"""

from typing import Any, MutableMapping
import asyncio


def sample_stream():
    # [START build_stream]
    from azure.core import PipelineClient
    from azure.core.rest import HttpRequest, HttpResponse
    from azure.core.streaming import Stream, JSONLDecoder

    client: PipelineClient[HttpRequest, HttpResponse] = PipelineClient("https://example.com")
    request = HttpRequest("GET", "https://example.com/stream")
    response = client.send_request(request, stream=True)

    def deserialize(response: HttpResponse, event: MutableMapping[str, Any]) -> MutableMapping[str, Any]:
        # Deserialize each decoded JSON object into a model. Here we just return it as-is.
        return event

    stream = Stream(
        response=response,
        decoder=JSONLDecoder(),
        deserialization_callback=deserialize,
    )
    with stream:
        for item in stream:
            print(item)
    # [END build_stream]


async def sample_stream_async():
    # [START build_stream_async]
    from azure.core import AsyncPipelineClient
    from azure.core.rest import HttpRequest, AsyncHttpResponse
    from azure.core.streaming import AsyncStream, AsyncJSONLDecoder

    client: AsyncPipelineClient[HttpRequest, AsyncHttpResponse] = AsyncPipelineClient("https://example.com")
    request = HttpRequest("GET", "https://example.com/stream")
    response = await client.send_request(request, stream=True)

    def deserialize(response: AsyncHttpResponse, event: MutableMapping[str, Any]) -> MutableMapping[str, Any]:
        # Deserialize each decoded JSON object into a model. Here we just return it as-is.
        return event

    stream = AsyncStream(
        response=response,
        decoder=AsyncJSONLDecoder(),
        deserialization_callback=deserialize,
    )
    async with stream:
        async for item in stream:
            print(item)
    # [END build_stream_async]


if __name__ == "__main__":
    sample_stream()
    asyncio.run(sample_stream_async())
