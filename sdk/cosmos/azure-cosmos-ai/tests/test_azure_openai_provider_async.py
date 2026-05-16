# The MIT License (MIT)
# Copyright (c) 2023 Microsoft Corporation

# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:

# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.

# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

"""Unit tests for AzureOpenAIEmbeddingProvider (async)."""

from types import SimpleNamespace
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from azure.core.credentials import AccessToken, AzureKeyCredential

from azure.cosmos.ai.aio import AzureOpenAIEmbeddingProvider


ENDPOINT = "https://example.com/"
ENDPOINT_KEY = "https://example.com"
DEPLOYMENT = "text-embedding-3-small"
DIMENSIONS = 1536


class _FakeAsyncTokenCredential:
    def __init__(self):
        self.calls = []

    async def get_token(self, *scopes, **kwargs):  # pylint: disable=unused-argument
        self.calls.append(scopes)
        return AccessToken("fake-token", 9999999999)

    async def close(self):
        pass


def _fake_response(vectors, total_tokens=42):
    return SimpleNamespace(
        data=[SimpleNamespace(embedding=v) for v in vectors],
        usage=SimpleNamespace(total_tokens=total_tokens) if total_tokens is not None else None,
    )


@pytest.fixture
def mock_aoai():
    """Patches AsyncAzureOpenAI inside the async provider module."""
    with patch("azure.cosmos.ai.aio._azure_openai_provider.AsyncAzureOpenAI") as cls:
        instance = MagicMock(name="AsyncAzureOpenAIInstance")
        instance.embeddings.create = AsyncMock(return_value=_fake_response([[0.1, 0.2]]))
        instance.close = AsyncMock()
        cls.return_value = instance
        yield cls, instance


# ----- constructor / credential dispatch -----


def test_init_accepts_str(mock_aoai):  # pylint: disable=unused-argument
    AzureOpenAIEmbeddingProvider(credential="my-key")


def test_init_accepts_azure_key_credential(mock_aoai):  # pylint: disable=unused-argument
    AzureOpenAIEmbeddingProvider(credential=AzureKeyCredential("my-key"))


def test_init_accepts_async_token_credential(mock_aoai):  # pylint: disable=unused-argument
    AzureOpenAIEmbeddingProvider(credential=_FakeAsyncTokenCredential())


def test_init_rejects_unknown_credential():
    with pytest.raises(TypeError):
        AzureOpenAIEmbeddingProvider(credential=12345)  # type: ignore[arg-type]


# ----- generate_embeddings -----


@pytest.mark.asyncio
async def test_generate_embeddings_forwards_params_and_returns_result(mock_aoai):
    cls, instance = mock_aoai
    instance.embeddings.create.return_value = _fake_response(
        [[1.0, 2.0], [3.0, 4.0], [5.0, 6.0]], total_tokens=99
    )

    provider = AzureOpenAIEmbeddingProvider(credential="key")
    result = await provider.generate_embeddings(
        ["a", "b", "c"],
        endpoint=ENDPOINT,
        deployment_name=DEPLOYMENT,
        dimensions=DIMENSIONS,
    )

    cls.assert_called_once()
    _, ctor_kwargs = cls.call_args
    assert ctor_kwargs["azure_endpoint"] == ENDPOINT_KEY
    assert ctor_kwargs["api_key"] == "key"
    assert ctor_kwargs["api_version"] == "2024-10-21"

    instance.embeddings.create.assert_awaited_once_with(
        input=["a", "b", "c"],
        model=DEPLOYMENT,
        dimensions=DIMENSIONS,
    )

    assert result.vectors == [[1.0, 2.0], [3.0, 4.0], [5.0, 6.0]]
    assert result.total_tokens == 99


@pytest.mark.asyncio
async def test_generate_embeddings_missing_usage_returns_none(mock_aoai):
    _, instance = mock_aoai
    instance.embeddings.create.return_value = _fake_response([[1.0]], total_tokens=None)

    provider = AzureOpenAIEmbeddingProvider(credential="key")
    result = await provider.generate_embeddings(
        ["a"], endpoint=ENDPOINT, deployment_name=DEPLOYMENT, dimensions=DIMENSIONS
    )
    assert result.total_tokens is None


@pytest.mark.asyncio
async def test_empty_texts_short_circuits(mock_aoai):
    cls, instance = mock_aoai
    provider = AzureOpenAIEmbeddingProvider(credential="key")
    result = await provider.generate_embeddings(
        [], endpoint=ENDPOINT, deployment_name=DEPLOYMENT, dimensions=DIMENSIONS
    )
    assert result.vectors == []
    assert result.total_tokens == 0
    cls.assert_not_called()
    instance.embeddings.create.assert_not_called()


@pytest.mark.asyncio
async def test_exceptions_propagate(mock_aoai):
    _, instance = mock_aoai
    instance.embeddings.create.side_effect = RuntimeError("boom")

    provider = AzureOpenAIEmbeddingProvider(credential="key")
    with pytest.raises(RuntimeError, match="boom"):
        await provider.generate_embeddings(
            ["a"], endpoint=ENDPOINT, deployment_name=DEPLOYMENT, dimensions=DIMENSIONS
        )


# ----- credential plumbing -----


@pytest.mark.asyncio
async def test_azure_key_credential_passed_as_api_key(mock_aoai):
    cls, _ = mock_aoai
    provider = AzureOpenAIEmbeddingProvider(credential=AzureKeyCredential("aaa"))
    await provider.generate_embeddings(
        ["x"], endpoint=ENDPOINT, deployment_name=DEPLOYMENT, dimensions=DIMENSIONS
    )
    _, ctor_kwargs = cls.call_args
    assert ctor_kwargs["api_key"] == "aaa"


@pytest.mark.asyncio
async def test_async_token_credential_uses_bearer_token_provider(mock_aoai):
    cls, _ = mock_aoai
    cred = _FakeAsyncTokenCredential()
    provider = AzureOpenAIEmbeddingProvider(credential=cred)
    await provider.generate_embeddings(
        ["x"], endpoint=ENDPOINT, deployment_name=DEPLOYMENT, dimensions=DIMENSIONS
    )
    _, ctor_kwargs = cls.call_args
    assert "api_key" not in ctor_kwargs
    token_provider = ctor_kwargs["azure_ad_token_provider"]
    token = await token_provider()
    assert token == "fake-token"
    assert cred.calls and cred.calls[0][0] == "https://cognitiveservices.azure.com/.default"


# ----- close / async context manager -----


@pytest.mark.asyncio
async def test_close_clears_cache(mock_aoai):
    cls, instance = mock_aoai
    provider = AzureOpenAIEmbeddingProvider(credential="key")
    await provider.generate_embeddings(
        ["x"], endpoint=ENDPOINT, deployment_name=DEPLOYMENT, dimensions=DIMENSIONS
    )
    await provider.close()
    instance.close.assert_awaited_once()
    await provider.generate_embeddings(
        ["x"], endpoint=ENDPOINT, deployment_name=DEPLOYMENT, dimensions=DIMENSIONS
    )
    assert cls.call_count == 2


@pytest.mark.asyncio
async def test_async_context_manager_closes(mock_aoai):
    _, instance = mock_aoai
    async with AzureOpenAIEmbeddingProvider(credential="key") as provider:
        await provider.generate_embeddings(
            ["x"], endpoint=ENDPOINT, deployment_name=DEPLOYMENT, dimensions=DIMENSIONS
        )
    instance.close.assert_awaited_once()
