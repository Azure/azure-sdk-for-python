# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

import pytest
import openai
from devtools_testutils import AzureRecordedTestCase
from conftest import configure, AZURE, OPENAI, ALL


class TestDallE(AzureRecordedTestCase):

    @configure
    # @pytest.mark.parametrize("api_type", ALL)  # re-enable when supported
    @pytest.mark.parametrize("api_type", [OPENAI])
    def test_image_create(self, client, azure_openai_creds, api_type, **kwargs):
        image = client.images.generate(
            prompt="a cute baby seal"
        )
        assert image.created
        assert len(image.data) == 1
        assert image.data[0].url

    @configure
    # @pytest.mark.parametrize("api_type", [AZURE, OPENAI])  # re-enable when supported
    @pytest.mark.parametrize("api_type", [OPENAI])
    def test_image_create_n(self, client, azure_openai_creds, api_type, **kwargs):
        image = client.images.generate(
            prompt="a cute baby seal",
            n=2
        )
        assert image.created
        assert len(image.data) == 2
        for img in image.data:
            assert img.url

    @configure
    # @pytest.mark.parametrize("api_type", [AZURE, OPENAI])  # re-enable when supported
    @pytest.mark.parametrize("api_type", [OPENAI])
    def test_image_create_size(self, client, azure_openai_creds, api_type, **kwargs):
        image = client.images.generate(
            prompt="a cute baby seal",
            size="256x256"
        )
        assert image.created
        assert len(image.data) == 1
        assert image.data[0].url

    @configure
    @pytest.mark.parametrize("api_type", [OPENAI])
    def test_image_create_response_format(self, client, azure_openai_creds, api_type, **kwargs):
        image = client.images.generate(
            prompt="a cute baby seal",
            response_format="b64_json"  # No Azure support yet
        )
        assert image.created
        assert len(image.data) == 1
        assert image.data[0].b64_json

    @configure
    # @pytest.mark.parametrize("api_type", [AZURE, OPENAI])  # re-enable when supported
    @pytest.mark.parametrize("api_type", [OPENAI])
    def test_image_create_user(self, client, azure_openai_creds, api_type, **kwargs):
        image = client.images.generate(
            prompt="a cute baby seal",
            user="krista"
        )
        assert image.created
        assert len(image.data) == 1
        assert image.data[0].url
