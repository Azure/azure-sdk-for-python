# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See LICENSE.txt in the project root for
# license information.
# -------------------------------------------------------------------------
import pytest
from corehttp.runtime import AsyncPipelineClient
from corehttp.exceptions import DecodeError

from utils import HTTP_REQUESTS


@pytest.mark.asyncio
@pytest.mark.parametrize("http_request", HTTP_REQUESTS)
async def test_decompress_plain_no_header(http_request):
    # expect plain text
    account_name = "coretests"
    account_url = "https://{}.blob.core.windows.net".format(account_name)
    url = "https://{}.blob.core.windows.net/tests/test.txt".format(account_name)
    client = AsyncPipelineClient(account_url)
    async with client:
        request = http_request("GET", url)
        pipeline_response = await client.pipeline.run(request, stream=True)
        response = pipeline_response.http_response
        data = response.iter_bytes()
        content = b""
        async for d in data:
            content += d
        decoded = content.decode("utf-8")
        assert decoded == "test"


@pytest.mark.asyncio
@pytest.mark.parametrize("http_request", HTTP_REQUESTS)
async def test_compress_plain_no_header(http_request):
    # expect plain text
    account_name = "coretests"
    account_url = "https://{}.blob.core.windows.net".format(account_name)
    url = "https://{}.blob.core.windows.net/tests/test.txt".format(account_name)
    client = AsyncPipelineClient(account_url)
    async with client:
        request = http_request("GET", url)
        pipeline_response = await client.pipeline.run(request, stream=True)
        response = pipeline_response.http_response
        data = response.iter_raw()
        content = b""
        async for d in data:
            content += d
        decoded = content.decode("utf-8")
        assert decoded == "test"


@pytest.mark.asyncio
@pytest.mark.parametrize("http_request", HTTP_REQUESTS)
async def test_decompress_compressed_no_header(http_request):
    # expect compressed text
    account_name = "coretests"
    account_url = "https://{}.blob.core.windows.net".format(account_name)
    url = "https://{}.blob.core.windows.net/tests/test.tar.gz".format(account_name)
    client = AsyncPipelineClient(account_url)
    async with client:
        request = http_request("GET", url)
        pipeline_response = await client.pipeline.run(request, stream=True)
        response = pipeline_response.http_response
        data = response.iter_bytes()
        content = b""
        async for d in data:
            content += d
        try:
            content.decode("utf-8")
            assert False
        except UnicodeDecodeError:
            pass


@pytest.mark.asyncio
@pytest.mark.parametrize("http_request", HTTP_REQUESTS)
async def test_compress_compressed_no_header(http_request):
    # expect compressed text
    account_name = "coretests"
    account_url = "https://{}.blob.core.windows.net".format(account_name)
    url = "https://{}.blob.core.windows.net/tests/test.tar.gz".format(account_name)
    client = AsyncPipelineClient(account_url)
    async with client:
        request = http_request("GET", url)
        pipeline_response = await client.pipeline.run(request, stream=True)
        response = pipeline_response.http_response
        data = response.iter_raw()
        content = b""
        async for d in data:
            content += d
        try:
            content.decode("utf-8")
            assert False
        except UnicodeDecodeError:
            pass


@pytest.mark.live_test_only
@pytest.mark.asyncio
@pytest.mark.parametrize("http_request", HTTP_REQUESTS)
async def test_decompress_plain_header(http_request):
    # expect error
    import zlib

    account_name = "coretests"
    account_url = "https://{}.blob.core.windows.net".format(account_name)
    url = "https://{}.blob.core.windows.net/tests/test_with_header.txt".format(account_name)
    client = AsyncPipelineClient(account_url)
    async with client:
        request = http_request("GET", url)
        pipeline_response = await client.pipeline.run(request, stream=True)
        response = pipeline_response.http_response
        data = response.iter_bytes()
        try:
            content = b""
            async for d in data:
                content += d
            assert False
        except (zlib.error, DecodeError):
            pass


@pytest.mark.asyncio
@pytest.mark.parametrize("http_request", HTTP_REQUESTS)
async def test_compress_plain_header(http_request):
    # expect plain text
    account_name = "coretests"
    account_url = "https://{}.blob.core.windows.net".format(account_name)
    url = "https://{}.blob.core.windows.net/tests/test_with_header.txt".format(account_name)
    client = AsyncPipelineClient(account_url)
    async with client:
        request = http_request("GET", url)
        pipeline_response = await client.pipeline.run(request, stream=True)
        response = pipeline_response.http_response
        data = response.iter_raw()
        content = b""
        async for d in data:
            content += d
        decoded = content.decode("utf-8")
        assert decoded == "test"


@pytest.mark.asyncio
@pytest.mark.parametrize("http_request", HTTP_REQUESTS)
async def test_decompress_compressed_header(http_request):
    # expect plain text
    account_name = "coretests"
    account_url = "https://{}.blob.core.windows.net".format(account_name)
    url = "https://{}.blob.core.windows.net/tests/test_with_header.tar.gz".format(account_name)
    client = AsyncPipelineClient(account_url)
    async with client:
        request = http_request("GET", url)
        pipeline_response = await client.pipeline.run(request, stream=True)
        response = pipeline_response.http_response
        data = response.iter_bytes()
        content = b""
        async for d in data:
            content += d
        decoded = content.decode("utf-8")
        assert decoded == "test"


@pytest.mark.live_test_only
@pytest.mark.asyncio
@pytest.mark.parametrize("http_request", HTTP_REQUESTS)
async def test_compress_compressed_header(http_request):
    # expect compressed text
    account_name = "coretests"
    account_url = "https://{}.blob.core.windows.net".format(account_name)
    url = "https://{}.blob.core.windows.net/tests/test_with_header.tar.gz".format(account_name)
    client = AsyncPipelineClient(account_url)
    async with client:
        request = http_request("GET", url)
        pipeline_response = await client.pipeline.run(request, stream=True)
        response = pipeline_response.http_response
        data = response.iter_raw()
        content = b""
        async for d in data:
            content += d
        try:
            content.decode("utf-8")
            assert False
        except UnicodeDecodeError:
            pass
