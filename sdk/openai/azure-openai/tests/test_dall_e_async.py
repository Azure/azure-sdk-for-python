# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

import pytest
import openai
from devtools_testutils import AzureRecordedTestCase
from conftest import configure_async, DALLE_AZURE, OPENAI, PREVIEW, GA


@pytest.mark.live_test_only
class TestDallEAsync(AzureRecordedTestCase):

    @configure_async
    @pytest.mark.asyncio
    @pytest.mark.parametrize(
        "api_type, api_version",
        [(DALLE_AZURE, GA), (DALLE_AZURE, PREVIEW), (OPENAI, "v1")]
    )
    async def test_image_create(self, client_async, api_type, api_version, **kwargs):
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
    @pytest.mark.parametrize("api_type, api_version", [(DALLE_AZURE, GA), (DALLE_AZURE, PREVIEW), (OPENAI, "v1")])
    async def test_image_create_n(self, client_async, api_type, api_version, **kwargs):
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
    @pytest.mark.parametrize("api_type, api_version", [(DALLE_AZURE, GA), (DALLE_AZURE, PREVIEW), (OPENAI, "v1")])
    async def test_image_create_size(self, client_async, api_type, api_version, **kwargs):
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
    @pytest.mark.parametrize("api_type, api_version", [(DALLE_AZURE, GA), (DALLE_AZURE, PREVIEW), (OPENAI, "v1")])
    async def test_image_create_response_format(self, client_async, api_type, api_version, **kwargs):
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
    @pytest.mark.parametrize("api_type, api_version", [(DALLE_AZURE, GA), (DALLE_AZURE, PREVIEW), (OPENAI, "v1")])
    async def test_image_create_user(self, client_async, api_type, api_version, **kwargs):
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
    @pytest.mark.parametrize("api_type, api_version", [(DALLE_AZURE, GA), (DALLE_AZURE, PREVIEW), (OPENAI, "v1")])
    async def test_image_create_quality(self, client_async, api_type, api_version, **kwargs):
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
    @pytest.mark.parametrize("api_type, api_version", [(DALLE_AZURE, GA), (DALLE_AZURE, PREVIEW), (OPENAI, "v1")])
    async def test_image_create_style(self, client_async, api_type, api_version, **kwargs):
        image = await client_async.images.generate(
            prompt="a cute baby seal",
            style="vivid",
            **kwargs,
        )
        assert image.created
        assert len(image.data) == 1
        assert image.data[0].url
        assert image.data[0].revised_prompt
