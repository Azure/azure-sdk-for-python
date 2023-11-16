# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

import pytest
import openai
from devtools_testutils import AzureRecordedTestCase
from conftest import configure_v0_async, AZURE, OPENAI, ALL


class TestEmbeddingsAsync(AzureRecordedTestCase):

    @pytest.mark.asyncio
    @pytest.mark.parametrize("api_type", [AZURE])
    @configure_v0_async
    async def test_embedding_bad_deployment_name(self, set_vars, azure_openai_creds, api_type):
        with pytest.raises(openai.error.InvalidRequestError) as e:
            await openai.Embedding.acreate(input="hello world", deployment_id="deployment")
        assert e.value.http_status == 404
        assert "The API deployment for this resource does not exist" in str(e.value)

    @pytest.mark.asyncio
    @pytest.mark.parametrize("api_type", [AZURE])
    @configure_v0_async
    async def test_embedding_kw_input(self, set_vars, azure_openai_creds, api_type):
        deployment = azure_openai_creds["embeddings_name"]

        embedding = await openai.Embedding.acreate(input="hello world", deployment_id=deployment)
        assert embedding
        embedding = await openai.Embedding.acreate(input="hello world", engine=deployment)
        assert embedding
        with pytest.raises(openai.error.InvalidRequestError) as e:
            await openai.Embedding.acreate(input="hello world", model=deployment)
        assert "Must provide an 'engine' or 'deployment_id' parameter" in str(e.value)

    @pytest.mark.asyncio
    @pytest.mark.parametrize("api_type", ALL)
    @configure_v0_async
    async def test_embedding(self, set_vars, azure_openai_creds, api_type):
        kwargs = {"model": azure_openai_creds["embeddings_model"]} if api_type == "openai" \
          else {"deployment_id": azure_openai_creds["embeddings_name"]}

        embedding = await openai.Embedding.acreate(input="hello world", **kwargs)
        assert embedding.object == "list"
        assert embedding.model
        assert embedding.usage.prompt_tokens is not None
        assert embedding.usage.total_tokens is not None
        assert len(embedding.data) == 1
        assert embedding.data[0].object == "embedding"
        assert embedding.data[0].index is not None
        assert len(embedding.data[0].embedding) > 0

    @pytest.mark.asyncio
    @pytest.mark.parametrize("api_type", [AZURE, OPENAI])
    @configure_v0_async
    async def test_embedding_batched(self, set_vars, azure_openai_creds, api_type):
        kwargs = {"model": azure_openai_creds["embeddings_model"]} if api_type == "openai" \
          else {"deployment_id": azure_openai_creds["embeddings_name"]}
        embedding = await openai.Embedding.acreate(input=["hello world", "second input"], **kwargs)
        assert embedding.object == "list"
        assert embedding.model
        assert embedding.usage.prompt_tokens is not None
        assert embedding.usage.total_tokens is not None
        assert len(embedding.data) == 2
        assert embedding.data[0].object == "embedding"
        assert embedding.data[0].index is not None
        assert len(embedding.data[0].embedding) > 0

    @pytest.mark.asyncio
    @pytest.mark.parametrize("api_type", [AZURE, OPENAI])
    @configure_v0_async
    async def test_embedding_user(self, set_vars, azure_openai_creds, api_type):
        kwargs = {"model": azure_openai_creds["embeddings_model"]} if api_type == "openai" \
          else {"deployment_id": azure_openai_creds["embeddings_name"]}

        embedding = await openai.Embedding.acreate(input="hello world", user="krista", **kwargs)
        assert embedding.object == "list"
        assert embedding.model
        assert embedding.usage.prompt_tokens is not None
        assert embedding.usage.total_tokens is not None
        assert len(embedding.data) == 1
        assert embedding.data[0].object == "embedding"
        assert embedding.data[0].index is not None
        assert len(embedding.data[0].embedding) > 0
