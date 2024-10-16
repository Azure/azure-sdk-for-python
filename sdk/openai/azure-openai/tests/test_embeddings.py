# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

import pytest
import openai
from devtools_testutils import AzureRecordedTestCase
from conftest import configure, AZURE, OPENAI, PREVIEW, GA


@pytest.mark.live_test_only
class TestEmbeddings(AzureRecordedTestCase):

    @configure
    @pytest.mark.parametrize(
        "api_type, api_version",
        [(AZURE, GA), (AZURE, PREVIEW), (OPENAI, "v1")]
    )
    def test_embedding(self, client, api_type, api_version, **kwargs):

        embedding = client.embeddings.create(input="hello world", **kwargs)
        assert embedding.object == "list"
        assert embedding.model
        assert embedding.usage.prompt_tokens is not None
        assert embedding.usage.total_tokens is not None
        assert len(embedding.data) == 1
        assert embedding.data[0].object == "embedding"
        assert embedding.data[0].index is not None
        assert len(embedding.data[0].embedding) > 0

    @configure
    @pytest.mark.parametrize(
        "api_type, api_version",
        [(AZURE, GA), (AZURE, PREVIEW), (OPENAI, "v1")]
    )
    def test_embedding_batched(self, client, api_type, api_version, **kwargs):

        embedding = client.embeddings.create(input=["hello world", "second input"], **kwargs)
        assert embedding.object == "list"
        assert embedding.model
        assert embedding.usage.prompt_tokens is not None
        assert embedding.usage.total_tokens is not None
        assert len(embedding.data) == 2
        assert embedding.data[0].object == "embedding"
        assert embedding.data[0].index is not None
        assert len(embedding.data[0].embedding) > 0

    @configure
    @pytest.mark.parametrize(
        "api_type, api_version",
        [(AZURE, GA), (AZURE, PREVIEW), (OPENAI, "v1")]
    )
    def test_embedding_user(self, client, api_type, api_version, **kwargs):

        embedding = client.embeddings.create(input="hello world", user="krista", **kwargs)
        assert embedding.object == "list"
        assert embedding.model
        assert embedding.usage.prompt_tokens is not None
        assert embedding.usage.total_tokens is not None
        assert len(embedding.data) == 1
        assert embedding.data[0].object == "embedding"
        assert embedding.data[0].index is not None
        assert len(embedding.data[0].embedding) > 0

    @configure
    @pytest.mark.parametrize(
        "api_type, api_version",
        [(AZURE, PREVIEW), (AZURE, GA), (OPENAI, "v1")]
    )
    def test_embedding_dimensions(self, client, api_type, api_version, **kwargs):

        embedding = client.embeddings.create(input="hello world", dimensions=1, model="text-embedding-3-small")
        assert embedding.object == "list"
        assert embedding.model
        assert embedding.usage.prompt_tokens is not None
        assert embedding.usage.total_tokens is not None
        assert len(embedding.data) == 1
        assert embedding.data[0].object == "embedding"
        assert embedding.data[0].index is not None
        assert len(embedding.data[0].embedding) > 0

    @configure
    @pytest.mark.parametrize(
        "api_type, api_version",
        [(AZURE, PREVIEW), (AZURE, GA), (OPENAI, "v1")]
    )
    def test_embedding_encoding_format(self, client, api_type, api_version, **kwargs):

        embedding = client.embeddings.create(input="hello world", encoding_format="base64", model="text-embedding-3-small")
        assert embedding.object == "list"
        assert embedding.model
        assert embedding.usage.prompt_tokens is not None
        assert embedding.usage.total_tokens is not None
        assert len(embedding.data) > 0
