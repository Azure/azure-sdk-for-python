# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Unit tests for admin-connected (BYO) judge-model support in the prompty judge path."""
import asyncio
from types import SimpleNamespace
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from azure.ai.evaluation._byo_judge import (
    AsyncByoProjectResponsesClient,
    is_byo_model_config,
    _to_responses_input,
    _map_params,
    _map_response_format,
    _ChatCompletion,
    _Usage,
)


class TestByoJudgeHelpers:
    def test_is_byo_model_config(self):
        assert is_byo_model_config({"byo_model": "c/d", "project_endpoint": "https://x"})
        assert not is_byo_model_config({"azure_endpoint": "https://x"})
        assert not is_byo_model_config({})
        # Both markers are required — byo_model alone must not activate the BYO path
        # (the prompty branch needs project_endpoint to route, else it would KeyError).
        assert not is_byo_model_config({"byo_model": "c/d"})
        assert not is_byo_model_config({"project_endpoint": "https://x"})
        # Markers must be non-empty strings — truthy-but-invalid values (e.g. ints) must not
        # activate BYO, else they bypass validate_model_config and fail deep inside the client.
        assert not is_byo_model_config({"byo_model": 1, "project_endpoint": 2})
        assert not is_byo_model_config({"byo_model": "", "project_endpoint": "https://x"})
        assert not is_byo_model_config({"byo_model": "c/d", "project_endpoint": ""})

    def test_to_responses_input(self):
        assert _to_responses_input([{"role": "user", "content": "hi"}]) == [
            {"type": "message", "role": "user", "content": "hi"}
        ]

    def test_map_params_curates_and_renames(self):
        assert _map_params({"temperature": 0.0, "max_tokens": 50, "top_p": 0.9, "stream": True}) == {
            "temperature": 0.0,
            "top_p": 0.9,
            "max_output_tokens": 50,
        }


class TestResponseFormatMapping:
    """chat.completions ``response_format`` -> Responses API ``text.format`` (JSON output parity)."""

    def test_json_object_passthrough(self):
        assert _map_response_format({"type": "json_object"}) == {"type": "json_object"}

    def test_text_passthrough(self):
        assert _map_response_format({"type": "text"}) == {"type": "text"}

    def test_json_schema_is_flattened(self):
        # chat.completions nests name/schema/strict under "json_schema"; Responses flattens them.
        rf = {
            "type": "json_schema",
            "json_schema": {
                "name": "coherence",
                "schema": {"type": "object", "properties": {"score": {"type": "integer"}}},
                "strict": True,
            },
        }
        assert _map_response_format(rf) == {
            "type": "json_schema",
            "name": "coherence",
            "schema": {"type": "object", "properties": {"score": {"type": "integer"}}},
            "strict": True,
        }

    def test_unknown_or_non_dict_returns_none(self):
        assert _map_response_format({"type": "weird"}) is None
        assert _map_response_format(None) is None
        assert _map_response_format("json_object") is None

    def test_map_params_wires_response_format_into_text(self):
        # The prompty runner passes response_format={"type": "json_object"}; it must reach text.format.
        mapped = _map_params({"temperature": 0.0, "response_format": {"type": "json_object"}})
        assert mapped["text"] == {"format": {"type": "json_object"}}
        assert mapped["temperature"] == 0.0

    def test_map_params_omits_text_for_unrecognized_response_format(self):
        assert "text" not in _map_params({"response_format": {"type": "weird"}})


class TestUsageAdapter:
    def test_responses_usage_mapped_to_chat_shape(self):
        usage = _Usage(MagicMock(input_tokens=5, output_tokens=7, total_tokens=12))
        assert (usage.prompt_tokens, usage.completion_tokens, usage.total_tokens) == (5, 7, 12)

    def test_missing_fields_default_to_zero(self):
        usage = _Usage(object())
        assert (usage.prompt_tokens, usage.completion_tokens, usage.total_tokens) == (0, 0, 0)

    def test_total_tokens_falls_back_to_prompt_plus_completion(self):
        # Responses usage without total_tokens -> compute it from prompt + completion.
        usage = _Usage(SimpleNamespace(input_tokens=5, output_tokens=7))
        assert usage.total_tokens == 12


class TestFinishReason:
    """A Responses result maps status -> chat.completions finish_reason (truncation detection)."""

    @staticmethod
    def _resp(**kwargs):
        kwargs.setdefault("output_text", "ok")
        kwargs.setdefault("usage", None)
        kwargs.setdefault("id", "r")
        kwargs.setdefault("model", "m")
        return SimpleNamespace(**kwargs)

    def test_completed_is_stop(self):
        assert _ChatCompletion(self._resp(status="completed")).choices[0].finish_reason == "stop"

    def test_missing_status_defaults_to_stop(self):
        assert _ChatCompletion(self._resp()).choices[0].finish_reason == "stop"

    def test_truncation_is_length(self):
        resp = self._resp(status="incomplete", incomplete_details=SimpleNamespace(reason="max_output_tokens"))
        assert _ChatCompletion(resp).choices[0].finish_reason == "length"

    def test_other_incomplete_reason_passes_through(self):
        resp = self._resp(status="incomplete", incomplete_details=SimpleNamespace(reason="content_filter"))
        assert _ChatCompletion(resp).choices[0].finish_reason == "content_filter"


class TestAsyncByoProjectResponsesClient:
    """The prompty judge path (coherence/relevance/fluency/... LLM-as-a-judge evaluators)."""

    @patch("azure.ai.projects.aio.AIProjectClient")
    def test_async_chat_completions_routes_to_responses(self, mock_aipc):
        resp = MagicMock()
        resp.output_text = "coherent: 5"
        resp.usage = MagicMock(input_tokens=12, output_tokens=3, total_tokens=15)
        resp.id = "resp_2"
        resp.model = "my-conn/gpt-4o"
        oai = MagicMock()
        oai.responses.create = AsyncMock(return_value=resp)
        mock_aipc.return_value.get_openai_client.return_value = oai

        client = AsyncByoProjectResponsesClient(
            byo_model="my-conn/gpt-4o",
            project_endpoint="https://acct.services.ai.azure.com/api/projects/p1",
            credential=MagicMock(),
        )
        # The prompty runner calls with_options(...).chat.completions.create(...).
        result = asyncio.run(
            client.with_options(timeout=30).chat.completions.create(
                model="ignored",
                messages=[{"role": "user", "content": "rate coherence"}],
                temperature=0.0,
                max_tokens=800,
            )
        )

        # chat.completions-shaped result the prompty response formatter expects.
        assert result.choices[0].message.content == "coherent: 5"
        assert result.choices[0].message.role == "assistant"
        assert result.choices[0].finish_reason == "stop"
        assert result.usage.prompt_tokens == 12
        assert result.usage.completion_tokens == 3
        assert result.usage.total_tokens == 15
        assert result.model == "my-conn/gpt-4o"

        # Underlying call is the project Responses API with the BYO model + mapped input/params.
        mock_aipc.assert_called_once()
        _, pkwargs = mock_aipc.call_args
        assert pkwargs["endpoint"] == "https://acct.services.ai.azure.com/api/projects/p1"
        _, rkwargs = oai.responses.create.call_args
        assert rkwargs["model"] == "my-conn/gpt-4o"
        assert rkwargs["input"] == [{"type": "message", "role": "user", "content": "rate coherence"}]
        assert rkwargs["temperature"] == 0.0
        assert rkwargs["max_output_tokens"] == 800
        # The per-request timeout set via with_options(timeout=30) reaches responses.create.
        assert rkwargs["timeout"] == 30

    def test_non_numeric_timeout_is_not_forwarded(self):
        # openai passes a NotGiven() sentinel when no timeout is configured; the shim must ignore it
        # (only a concrete numeric timeout is forwarded to responses.create).
        client = AsyncByoProjectResponsesClient("c/d", "https://acct.services.ai.azure.com/api/projects/p", MagicMock())
        client.with_options(timeout=object())
        assert client._timeout is None

    @patch("azure.ai.projects.aio.AIProjectClient")
    def test_awaits_coroutine_get_openai_client(self, mock_aipc):
        # In some azure-ai-projects versions get_openai_client() is a coroutine; the shim must await it.
        resp = MagicMock(output_text="ok", usage=None, id="r", model="m", status="completed")
        oai = MagicMock()
        oai.responses.create = AsyncMock(return_value=resp)

        async def _coro_get_openai_client(*args, **kwargs):
            return oai

        mock_aipc.return_value.get_openai_client = _coro_get_openai_client

        client = AsyncByoProjectResponsesClient("c/d", "https://acct.services.ai.azure.com/api/projects/p", MagicMock())
        result = asyncio.run(client.chat.completions.create(messages=[{"role": "user", "content": "hi"}]))
        assert result.choices[0].message.content == "ok"
        oai.responses.create.assert_awaited_once()

    def test_with_options_returns_self(self):
        client = AsyncByoProjectResponsesClient("c/d", "https://acct.services.ai.azure.com/api/projects/p", MagicMock())
        assert client.with_options(timeout=5) is client

    def test_missing_azure_ai_projects_raises_clear_error(self, monkeypatch):
        # azure-ai-projects is an optional dependency (not in install_requires). When the BYO path
        # is used without it installed, the shim must surface a clear MissingRequiredPackage error
        # instead of a raw ModuleNotFoundError. A None entry in sys.modules makes
        # ``from azure.ai.projects.aio import AIProjectClient`` raise ImportError.
        import sys

        from azure.ai.evaluation._legacy._adapters._errors import MissingRequiredPackage

        monkeypatch.setitem(sys.modules, "azure.ai.projects.aio", None)
        client = AsyncByoProjectResponsesClient("c/d", "https://acct.services.ai.azure.com/api/projects/p", MagicMock())
        with pytest.raises(MissingRequiredPackage):
            asyncio.run(client.chat.completions.create(messages=[{"role": "user", "content": "hi"}]))

    @patch("azure.ai.projects.aio.AIProjectClient")
    def test_extra_headers_forwarded_to_responses(self, mock_aipc):
        # ACA may supply additional headers (e.g. correlation/telemetry headers) when running
        # continuous evaluations; the shim must forward them to responses.create.
        resp = MagicMock(output_text="ok", usage=None, id="r", model="m", status="completed")
        oai = MagicMock()
        oai.responses.create = AsyncMock(return_value=resp)
        mock_aipc.return_value.get_openai_client.return_value = oai

        headers = {"x-ms-client-request-id": "abc-123", "x-correlation-id": "def-456"}
        client = AsyncByoProjectResponsesClient(
            byo_model="c/d",
            project_endpoint="https://acct.services.ai.azure.com/api/projects/p",
            credential=MagicMock(),
            extra_headers=headers,
        )
        asyncio.run(client.chat.completions.create(messages=[{"role": "user", "content": "hi"}]))

        _, rkwargs = oai.responses.create.call_args
        assert rkwargs["extra_headers"] == headers
        # The shim copies the headers so later caller mutations do not leak into the client.
        assert rkwargs["extra_headers"] is not headers

    @patch("azure.ai.projects.aio.AIProjectClient")
    def test_no_extra_headers_by_default(self, mock_aipc):
        # When no extra headers are supplied, none are forwarded to responses.create.
        resp = MagicMock(output_text="ok", usage=None, id="r", model="m", status="completed")
        oai = MagicMock()
        oai.responses.create = AsyncMock(return_value=resp)
        mock_aipc.return_value.get_openai_client.return_value = oai

        client = AsyncByoProjectResponsesClient("c/d", "https://acct.services.ai.azure.com/api/projects/p", MagicMock())
        asyncio.run(client.chat.completions.create(messages=[{"role": "user", "content": "hi"}]))

        _, rkwargs = oai.responses.create.call_args
        assert "extra_headers" not in rkwargs

    @patch("azure.ai.projects.aio.AIProjectClient")
    def test_preserves_server_created_timestamp(self, mock_aipc):
        # When the Responses result carries a server ``created`` timestamp, the shim preserves it
        # instead of overwriting with local wall-clock time.
        resp = MagicMock(output_text="ok", usage=None, id="r", model="m", status="completed", created=1752694800)
        oai = MagicMock()
        oai.responses.create = AsyncMock(return_value=resp)
        mock_aipc.return_value.get_openai_client.return_value = oai

        client = AsyncByoProjectResponsesClient("c/d", "https://acct.services.ai.azure.com/api/projects/p", MagicMock())
        result = asyncio.run(client.chat.completions.create(messages=[{"role": "user", "content": "hi"}]))
        assert result.created == 1752694800


class TestValidateModelConfigByo:
    def test_byo_config_passes_through_validation(self):
        from azure.ai.evaluation._common.utils import validate_model_config

        cfg = {
            "byo_model": "my-conn/gpt-4o",
            "project_endpoint": "https://acct.services.ai.azure.com/api/projects/p1",
        }
        # BYO configs intentionally omit azure_endpoint/azure_deployment and must not be rejected.
        assert validate_model_config(cfg) is cfg

    def test_non_byo_invalid_config_still_raises(self):
        from azure.ai.evaluation._common.utils import validate_model_config
        from azure.ai.evaluation._exceptions import EvaluationException

        with pytest.raises(EvaluationException):
            validate_model_config({"not": "a valid model config"})
