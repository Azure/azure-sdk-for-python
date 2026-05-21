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

"""Tests for AzureOpenAIEmbeddingProvider (sync).

This module exposes two test classes:

* ``TestAzureOpenAIProvider`` runs fully mocked unit tests and is always
  collected.
* ``TestAzureOpenAIProviderLive`` runs opt-in live tests against a real
  Azure OpenAI resource. Set ``COSMOS_AI_LIVE_TESTS=1`` and provide
  connection settings via environment variables to enable it:

    * ``AZURE_OPENAI_ENDPOINT``             required (e.g. ``https://<resource>.openai.azure.com/``)
    * ``AZURE_OPENAI_EMBEDDING_DEPLOYMENT`` required
    * ``AZURE_OPENAI_EMBEDDING_DIMENSIONS`` required (int)
    * ``AZURE_OPENAI_API_KEY``              required for the API key tests
"""

import os
from types import SimpleNamespace
from unittest.mock import MagicMock, patch

import pytest
from azure.core.credentials import AccessToken, AzureKeyCredential
from azure.identity import DefaultAzureCredential

from azure.cosmos.ai import AzureOpenAIEmbeddingProvider


ENDPOINT = "https://example.com/"
ENDPOINT_KEY = "https://example.com"
DEPLOYMENT = "text-embedding-3-small"
DIMENSIONS = 1536


# Apply the shared cosmos CI test marker at module scope. The cosmos-sdk-client
# pipeline template filters via ``-m cosmosEmulator``; without this declaration
# every test in this module would be silently deselected in CI.
pytestmark = pytest.mark.cosmosEmulator


class _FakeTokenCredential:
    def __init__(self):
        self.calls = []

    def get_token(self, *scopes, **kwargs):  # pylint: disable=unused-argument
        self.calls.append(scopes)
        return AccessToken("fake-token", 9999999999)


class _FakeAsyncTokenCredential:
    """Stand-in for an azure.identity.aio credential without the import cost."""

    def __init__(self):
        self.calls = []

    async def get_token(self, *scopes, **kwargs):  # pylint: disable=unused-argument
        self.calls.append(scopes)
        return AccessToken("fake-token", 9999999999)


def _fake_response(vectors, total_tokens=42):
    return SimpleNamespace(
        data=[SimpleNamespace(embedding=v) for v in vectors],
        usage=SimpleNamespace(total_tokens=total_tokens) if total_tokens is not None else None,
    )


@pytest.fixture
def mock_aoai():
    """Patches AzureOpenAI inside the provider module."""
    with patch("azure.cosmos.ai._azure_openai_provider.AzureOpenAI") as cls:
        instance = MagicMock(name="AzureOpenAIInstance")
        cls.return_value = instance
        instance.embeddings.create.return_value = _fake_response([[0.1, 0.2], [0.3, 0.4]])
        yield cls, instance


class TestAzureOpenAIProvider:
    """Unit tests with a mocked underlying ``AzureOpenAI`` client."""

    # ----- constructor / credential dispatch -----

    def test_init_accepts_str(self, mock_aoai):  # pylint: disable=unused-argument
        AzureOpenAIEmbeddingProvider(credential="my-key")

    def test_init_accepts_azure_key_credential(self, mock_aoai):  # pylint: disable=unused-argument
        AzureOpenAIEmbeddingProvider(credential=AzureKeyCredential("my-key"))

    def test_init_accepts_token_credential(self, mock_aoai):  # pylint: disable=unused-argument
        AzureOpenAIEmbeddingProvider(credential=_FakeTokenCredential())

    def test_init_rejects_unknown_credential(self):
        with pytest.raises(TypeError):
            AzureOpenAIEmbeddingProvider(credential=12345)  # type: ignore[arg-type]

    def test_init_rejects_async_credential_with_actionable_message(self):
        with pytest.raises(TypeError, match=r"(?i)async"):
            AzureOpenAIEmbeddingProvider(credential=_FakeAsyncTokenCredential())  # type: ignore[arg-type]

    def test_init_accepts_api_version_override(self, mock_aoai):
        cls, _ = mock_aoai
        provider = AzureOpenAIEmbeddingProvider(credential="key", api_version="2024-12-01-preview")
        provider.generate_embeddings(
            ["x"], endpoint=ENDPOINT, deployment_name=DEPLOYMENT, dimensions=DIMENSIONS
        )
        _, ctor_kwargs = cls.call_args
        assert ctor_kwargs["api_version"] == "2024-12-01-preview"

    def test_init_accepts_openai_client_kwargs(self, mock_aoai):
        cls, _ = mock_aoai
        provider = AzureOpenAIEmbeddingProvider(
            credential="key",
            openai_client_kwargs={"timeout": 30.0, "default_headers": {"x-test": "1"}},
        )
        provider.generate_embeddings(
            ["x"], endpoint=ENDPOINT, deployment_name=DEPLOYMENT, dimensions=DIMENSIONS
        )
        _, ctor_kwargs = cls.call_args
        assert ctor_kwargs["timeout"] == 30.0
        assert ctor_kwargs["default_headers"] == {"x-test": "1"}
        # Explicit provider-controlled kwargs still win.
        assert ctor_kwargs["azure_endpoint"] == ENDPOINT_KEY
        assert ctor_kwargs["api_version"] == "2024-10-21"

    # ----- generate_embeddings -----

    def test_generate_embeddings_forwards_params_and_returns_result(self, mock_aoai):
        cls, instance = mock_aoai
        instance.embeddings.create.return_value = _fake_response(
            [[1.0, 2.0], [3.0, 4.0], [5.0, 6.0]], total_tokens=99
        )

        provider = AzureOpenAIEmbeddingProvider(credential="key")
        result = provider.generate_embeddings(
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

        instance.embeddings.create.assert_called_once_with(
            input=["a", "b", "c"],
            model=DEPLOYMENT,
            dimensions=DIMENSIONS,
        )

        assert result.vectors == [[1.0, 2.0], [3.0, 4.0], [5.0, 6.0]]
        assert result.total_tokens == 99
        assert isinstance(result.latency, float)
        assert result.latency >= 0.0

    def test_generate_embeddings_missing_usage_returns_none(self, mock_aoai):
        _, instance = mock_aoai
        instance.embeddings.create.return_value = _fake_response([[1.0]], total_tokens=None)

        provider = AzureOpenAIEmbeddingProvider(credential="key")
        result = provider.generate_embeddings(
            ["a"], endpoint=ENDPOINT, deployment_name=DEPLOYMENT, dimensions=DIMENSIONS
        )
        assert result.total_tokens is None

    def test_empty_texts_short_circuits(self, mock_aoai):
        cls, instance = mock_aoai
        provider = AzureOpenAIEmbeddingProvider(credential="key")
        result = provider.generate_embeddings(
            [], endpoint=ENDPOINT, deployment_name=DEPLOYMENT, dimensions=DIMENSIONS
        )
        assert result.vectors == []
        assert result.total_tokens == 0
        assert result.latency is None
        cls.assert_not_called()
        instance.embeddings.create.assert_not_called()

    def test_exceptions_propagate(self, mock_aoai):
        _, instance = mock_aoai
        instance.embeddings.create.side_effect = RuntimeError("boom")

        provider = AzureOpenAIEmbeddingProvider(credential="key")
        with pytest.raises(RuntimeError, match="boom"):
            provider.generate_embeddings(
                ["a"], endpoint=ENDPOINT, deployment_name=DEPLOYMENT, dimensions=DIMENSIONS
            )

    # ----- credential plumbing into AzureOpenAI -----

    def test_azure_key_credential_passed_as_api_key(self, mock_aoai):
        cls, _ = mock_aoai
        provider = AzureOpenAIEmbeddingProvider(credential=AzureKeyCredential("aaa"))
        provider.generate_embeddings(
            ["x"], endpoint=ENDPOINT, deployment_name=DEPLOYMENT, dimensions=DIMENSIONS
        )
        _, ctor_kwargs = cls.call_args
        assert ctor_kwargs["api_key"] == "aaa"

    def test_token_credential_uses_bearer_token_provider(self, mock_aoai):
        cls, _ = mock_aoai
        cred = _FakeTokenCredential()
        provider = AzureOpenAIEmbeddingProvider(credential=cred)
        provider.generate_embeddings(
            ["x"], endpoint=ENDPOINT, deployment_name=DEPLOYMENT, dimensions=DIMENSIONS
        )
        _, ctor_kwargs = cls.call_args
        assert "api_key" not in ctor_kwargs
        token_provider = ctor_kwargs["azure_ad_token_provider"]
        token = token_provider()
        assert token == "fake-token"
        assert cred.calls and cred.calls[0][0] == "https://cognitiveservices.azure.com/.default"

    # ----- close / context manager -----

    def test_close_clears_cache(self, mock_aoai):
        cls, instance = mock_aoai
        provider = AzureOpenAIEmbeddingProvider(credential="key")
        provider.generate_embeddings(
            ["x"], endpoint=ENDPOINT, deployment_name=DEPLOYMENT, dimensions=DIMENSIONS
        )
        provider.close()
        instance.close.assert_called_once()
        provider.generate_embeddings(
            ["x"], endpoint=ENDPOINT, deployment_name=DEPLOYMENT, dimensions=DIMENSIONS
        )
        assert cls.call_count == 2

    def test_context_manager_closes(self, mock_aoai):
        _, instance = mock_aoai
        with AzureOpenAIEmbeddingProvider(credential="key") as provider:
            provider.generate_embeddings(
                ["x"], endpoint=ENDPOINT, deployment_name=DEPLOYMENT, dimensions=DIMENSIONS
            )
        instance.close.assert_called_once()


# ----- live test config -----

_LIVE_ENABLED = os.getenv("COSMOS_AI_LIVE_TESTS") == "1"
_LIVE_ENDPOINT = os.getenv("AZURE_OPENAI_ENDPOINT", "")
_LIVE_DEPLOYMENT = os.getenv("AZURE_OPENAI_EMBEDDING_DEPLOYMENT", "")
_LIVE_DIMENSIONS = int(os.getenv("AZURE_OPENAI_EMBEDDING_DIMENSIONS") or "0")
_LIVE_API_KEY = os.getenv("AZURE_OPENAI_API_KEY", "")

_LIVE_SKIP_REASON = (
    "Set COSMOS_AI_LIVE_TESTS=1, AZURE_OPENAI_ENDPOINT, "
    "AZURE_OPENAI_EMBEDDING_DEPLOYMENT and AZURE_OPENAI_EMBEDDING_DIMENSIONS "
    "to run live tests."
)

_LIVE_TEXTS = ["healthcare research papers", "azure cosmos vector search"]


def _assert_valid_live_result(result, expected_count):
    assert len(result.vectors) == expected_count
    for vec in result.vectors:
        assert isinstance(vec, list)
        assert len(vec) == _LIVE_DIMENSIONS
        assert all(isinstance(v, float) for v in vec)
    assert result.total_tokens is None or result.total_tokens > 0
    assert isinstance(result.latency, float)
    assert result.latency > 0.0


@pytest.mark.skipif(
    not (_LIVE_ENABLED and _LIVE_ENDPOINT and _LIVE_DEPLOYMENT and _LIVE_DIMENSIONS),
    reason=_LIVE_SKIP_REASON,
)
class TestAzureOpenAIProviderLive:
    """Live tests against a real Azure OpenAI resource. Opt-in."""

    @pytest.mark.skipif(not _LIVE_API_KEY, reason="AZURE_OPENAI_API_KEY not set.")
    def test_live_generate_embeddings_with_string_key(self):
        with AzureOpenAIEmbeddingProvider(credential=_LIVE_API_KEY) as provider:
            result = provider.generate_embeddings(
                _LIVE_TEXTS,
                endpoint=_LIVE_ENDPOINT,
                deployment_name=_LIVE_DEPLOYMENT,
                dimensions=_LIVE_DIMENSIONS,
            )
        _assert_valid_live_result(result, len(_LIVE_TEXTS))

    @pytest.mark.skipif(not _LIVE_API_KEY, reason="AZURE_OPENAI_API_KEY not set.")
    def test_live_generate_embeddings_with_azure_key_credential(self):
        with AzureOpenAIEmbeddingProvider(credential=AzureKeyCredential(_LIVE_API_KEY)) as provider:
            result = provider.generate_embeddings(
                _LIVE_TEXTS,
                endpoint=_LIVE_ENDPOINT,
                deployment_name=_LIVE_DEPLOYMENT,
                dimensions=_LIVE_DIMENSIONS,
            )
        _assert_valid_live_result(result, len(_LIVE_TEXTS))

    def test_live_generate_embeddings_with_default_azure_credential(self):
        try:
            credential = DefaultAzureCredential()
        except Exception as exc:  # pylint: disable=broad-except
            pytest.skip(f"DefaultAzureCredential unavailable: {exc}")
        with AzureOpenAIEmbeddingProvider(credential=credential) as provider:
            try:
                result = provider.generate_embeddings(
                    _LIVE_TEXTS,
                    endpoint=_LIVE_ENDPOINT,
                    deployment_name=_LIVE_DEPLOYMENT,
                    dimensions=_LIVE_DIMENSIONS,
                )
            except Exception as exc:  # pylint: disable=broad-except
                pytest.skip(f"Entra auth to Azure OpenAI failed (RBAC not granted?): {exc}")
        _assert_valid_live_result(result, len(_LIVE_TEXTS))

    def test_live_empty_texts_short_circuits_no_network(self):
        with AzureOpenAIEmbeddingProvider(credential=_LIVE_API_KEY or "unused") as provider:
            result = provider.generate_embeddings(
                [],
                endpoint=_LIVE_ENDPOINT,
                deployment_name=_LIVE_DEPLOYMENT,
                dimensions=_LIVE_DIMENSIONS,
            )
        assert result.vectors == []
        assert result.total_tokens == 0
        assert result.latency is None

    @pytest.mark.skipif(not _LIVE_API_KEY, reason="AZURE_OPENAI_API_KEY not set.")
    def test_live_underlying_client_is_cached_across_calls(self):
        with AzureOpenAIEmbeddingProvider(credential=_LIVE_API_KEY) as provider:
            provider.generate_embeddings(
                _LIVE_TEXTS[:1],
                endpoint=_LIVE_ENDPOINT,
                deployment_name=_LIVE_DEPLOYMENT,
                dimensions=_LIVE_DIMENSIONS,
            )
            first_clients = dict(provider._clients)  # pylint: disable=protected-access
            assert len(first_clients) == 1
            provider.generate_embeddings(
                _LIVE_TEXTS[:1],
                endpoint=_LIVE_ENDPOINT,
                deployment_name=_LIVE_DEPLOYMENT,
                dimensions=_LIVE_DIMENSIONS,
            )
            second_clients = dict(provider._clients)  # pylint: disable=protected-access
            assert first_clients.keys() == second_clients.keys()
            for key in first_clients:
                assert first_clients[key] is second_clients[key]
