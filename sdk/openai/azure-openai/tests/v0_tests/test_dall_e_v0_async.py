# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

import pytest
import openai
from devtools_testutils import AzureRecordedTestCase
from conftest import configure_v0_async, AZURE, OPENAI, ALL


class TestDallEAsync(AzureRecordedTestCase):

    @pytest.mark.asyncio
    @pytest.mark.parametrize("api_type", ALL)
    @configure_v0_async
    async def test_image_create(self, set_vars, azure_openai_creds, api_type):
        image = await openai.Image.acreate(
            prompt="a cute baby seal"
        )
        assert image.created
        assert len(image.data) == 1
        assert image.data[0].url

    @pytest.mark.asyncio
    @pytest.mark.parametrize("api_type", [AZURE, OPENAI])
    @configure_v0_async
    async def test_image_create_n(self, set_vars, azure_openai_creds, api_type):
        image = await openai.Image.acreate(
            prompt="a cute baby seal",
            n=2
        )
        assert image.created
        assert len(image.data) == 2
        for img in image.data:
            assert img.url

    @pytest.mark.asyncio
    @pytest.mark.parametrize("api_type", [AZURE, OPENAI])
    @configure_v0_async
    async def test_image_create_size(self, set_vars, azure_openai_creds, api_type):
        image = await openai.Image.acreate(
            prompt="a cute baby seal",
            size="256x256"
        )
        assert image.created
        assert len(image.data) == 1
        assert image.data[0].url

    @pytest.mark.asyncio
    @pytest.mark.parametrize("api_type", [OPENAI])
    @configure_v0_async
    async def test_image_create_response_format(self, set_vars, azure_openai_creds, api_type):
        image = await openai.Image.acreate(
            prompt="a cute baby seal",
            response_format="b64_json"  # No Azure support yet
        )
        assert image.created
        assert len(image.data) == 1
        assert image.data[0].b64_json

    @pytest.mark.asyncio
    @pytest.mark.parametrize("api_type", [AZURE, OPENAI])
    @configure_v0_async
    async def test_image_create_user(self, set_vars, azure_openai_creds, api_type):
        image = await openai.Image.acreate(
            prompt="a cute baby seal",
            user="krista"
        )
        assert image.created
        assert len(image.data) == 1
        assert image.data[0].url
