# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

import pytest
import openai
from devtools_testutils import AzureRecordedTestCase
from conftest import configure_async, AZURE, OPENAI, ALL


class TestEmbeddingsAsync(AzureRecordedTestCase):

    @configure_async
    @pytest.mark.asyncio
    @pytest.mark.parametrize("api_type", ALL)
    async def test_embedding(self, client_async, azure_openai_creds, api_type, **kwargs):

        embedding = await client_async.embeddings.create(input="hello world", **kwargs)
        assert embedding.object == "list"
        assert embedding.model
        assert embedding.usage.prompt_tokens is not None
        assert embedding.usage.total_tokens is not None
        assert len(embedding.data) == 1
        assert embedding.data[0].object == "embedding"
        assert embedding.data[0].index is not None
        assert len(embedding.data[0].embedding) > 0

    @configure_async
    @pytest.mark.asyncio
    @pytest.mark.parametrize("api_type", [AZURE, OPENAI])
    async def test_embedding_batched(self, client_async, azure_openai_creds, api_type, **kwargs):

        embedding = await client_async.embeddings.create(input=["hello world", "second input"], **kwargs)
        assert embedding.object == "list"
        assert embedding.model
        assert embedding.usage.prompt_tokens is not None
        assert embedding.usage.total_tokens is not None
        assert len(embedding.data) == 2
        assert embedding.data[0].object == "embedding"
        assert embedding.data[0].index is not None
        assert len(embedding.data[0].embedding) > 0

    @configure_async
    @pytest.mark.asyncio
    @pytest.mark.parametrize("api_type", [AZURE, OPENAI])
    async def test_embedding_user(self, client_async, azure_openai_creds, api_type, **kwargs):

        embedding = await client_async.embeddings.create(input="hello world", user="krista", **kwargs)
        assert embedding.object == "list"
        assert embedding.model
        assert embedding.usage.prompt_tokens is not None
        assert embedding.usage.total_tokens is not None
        assert len(embedding.data) == 1
        assert embedding.data[0].object == "embedding"
        assert embedding.data[0].index is not None
        assert len(embedding.data[0].embedding) > 0
