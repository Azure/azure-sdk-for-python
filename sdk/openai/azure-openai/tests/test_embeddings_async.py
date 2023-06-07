# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

import pytest
import openai
from devtools_testutils import AzureRecordedTestCase


class TestEmbeddingsAsync(AzureRecordedTestCase):

    @pytest.mark.asyncio
    async def test_embedding_bad_deployment_name(self, azure_openai_creds):
        with pytest.raises(openai.error.InvalidRequestError) as e:
            await openai.Embedding.acreate(input="hello world", deployment_id="deployment")
        assert e.value.http_status == 404
        assert "The API deployment for this resource does not exist" in str(e.value)

    @pytest.mark.asyncio
    async def test_embedding_kw_input(self, azure_openai_creds):
        deployment = azure_openai_creds["embeddings_name"]

        embedding = await openai.Embedding.acreate(input="hello world", deployment_id=deployment)
        assert embedding
        embedding = await openai.Embedding.acreate(input="hello world", engine=deployment)
        assert embedding
        with pytest.raises(openai.error.InvalidRequestError) as e:
            await openai.Embedding.acreate(input="hello world", model=deployment)
        assert "Must provide an 'engine' or 'deployment_id' parameter" in str(e.value)

    @pytest.mark.asyncio
    async def test_embedding(self, azure_openai_creds):
        deployment = azure_openai_creds["embeddings_name"]

        embedding = await openai.Embedding.acreate(input="hello world", deployment_id=deployment)
        assert embedding.object == "list"
        assert embedding.model
        assert embedding.usage.prompt_tokens is not None
        assert embedding.usage.total_tokens is not None
        assert len(embedding.data) == 1
        assert embedding.data[0].object == "embedding"
        assert embedding.data[0].index is not None
        assert len(embedding.data[0].embedding) > 0

    @pytest.mark.skip("openai.error.InvalidRequestError: Too many inputs. The max number of inputs is 1. "
                      "We hope to increase the number of inputs per request soon. Please contact us through "
                      "an Azure support request at: https://go.microsoft.com/fwlink/?linkid=2213926 for further questions")
    @pytest.mark.asyncio
    async def test_embedding_batched(self, azure_openai_creds):
        deployment = azure_openai_creds["embeddings_name"]
        embedding = await openai.Embedding.acreate(input=["hello world", "second input"], deployment_id=deployment)

    @pytest.mark.asyncio
    async def test_embedding_user(self, azure_openai_creds):
        deployment = azure_openai_creds["embeddings_name"]

        embedding = await openai.Embedding.acreate(input="hello world", deployment_id=deployment, user="krista")
        assert embedding.object == "list"
        assert embedding.model
        assert embedding.usage.prompt_tokens is not None
        assert embedding.usage.total_tokens is not None
        assert len(embedding.data) == 1
        assert embedding.data[0].object == "embedding"
        assert embedding.data[0].index is not None
        assert len(embedding.data[0].embedding) > 0
