# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

import pytest
import openai
from devtools_testutils import AzureRecordedTestCase
from conftest import DALLE_AZURE, OPENAI, DALLE_ALL, configure_async


class TestDallEAsync(AzureRecordedTestCase):

    @configure_async
    @pytest.mark.asyncio
    @pytest.mark.parametrize("api_type", DALLE_ALL)
    async def test_image_create(self, client_async, azure_openai_creds, api_type, **kwargs):
        image = await client_async.images.generate(
            prompt="a cute baby seal",
            **kwargs,
        )
        assert image.created
        assert len(image.data) == 1
        assert image.data[0].url
        assert image.data[0].revised_prompt

    @configure_async
    @pytest.mark.asyncio
    @pytest.mark.parametrize("api_type", [OPENAI, DALLE_AZURE])
    async def test_image_create_n(self, client_async, azure_openai_creds, api_type, **kwargs):
        image = await client_async.images.generate(
            prompt="a cute baby seal",
            n=1,
            **kwargs,
        )
        assert image.created
        assert len(image.data) == 1
        for img in image.data:
            assert img.url
            assert img.revised_prompt

    @configure_async
    @pytest.mark.asyncio
    @pytest.mark.parametrize("api_type", [OPENAI, DALLE_AZURE])
    async def test_image_create_size(self, client_async, azure_openai_creds, api_type, **kwargs):
        image = await client_async.images.generate(
            prompt="a cute baby seal",
            size="1024x1024",
            **kwargs,
        )
        assert image.created
        assert len(image.data) == 1
        assert image.data[0].url
        assert image.data[0].revised_prompt

    @configure_async
    @pytest.mark.asyncio
    @pytest.mark.parametrize("api_type", [OPENAI, DALLE_AZURE])
    async def test_image_create_response_format(self, client_async, azure_openai_creds, api_type, **kwargs):
        image = await client_async.images.generate(
            prompt="a cute baby seal",
            response_format="b64_json",
            **kwargs,
        )
        assert image.created
        assert len(image.data) == 1
        assert image.data[0].b64_json
        assert image.data[0].revised_prompt

    @configure_async
    @pytest.mark.asyncio
    @pytest.mark.parametrize("api_type", [OPENAI, DALLE_AZURE])
    async def test_image_create_user(self, client_async, azure_openai_creds, api_type, **kwargs):
        image = await client_async.images.generate(
            prompt="a cute baby seal",
            user="krista",
            **kwargs,
        )
        assert image.created
        assert len(image.data) == 1
        assert image.data[0].url
        assert image.data[0].revised_prompt

    @configure_async
    @pytest.mark.asyncio
    @pytest.mark.parametrize("api_type", [OPENAI, DALLE_AZURE])
    async def test_image_create_quality(self, client_async, azure_openai_creds, api_type, **kwargs):
        image = await client_async.images.generate(
            prompt="a cute baby seal",
            quality="standard",
            **kwargs,
        )
        assert image.created
        assert len(image.data) == 1
        assert image.data[0].url
        assert image.data[0].revised_prompt

    @configure_async
    @pytest.mark.asyncio
    @pytest.mark.parametrize("api_type", [OPENAI, DALLE_AZURE])
    async def test_image_create_style(self, client_async, azure_openai_creds, api_type, **kwargs):
        image = await client_async.images.generate(
            prompt="a cute baby seal",
            style="vivid",
            **kwargs,
        )
        assert image.created
        assert len(image.data) == 1
        assert image.data[0].url
        assert image.data[0].revised_prompt
