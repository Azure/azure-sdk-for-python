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
        # Both markers required — byo_model alone must not activate BYO (prompty needs project_endpoint).
        assert not is_byo_model_config({"byo_model": "c/d"})
        assert not is_byo_model_config({"project_endpoint": "https://x"})
        # Markers must be non-empty strings; truthy-but-invalid values (e.g. ints) must not activate BYO.
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
        # max_retries=0 so AsyncPrompty's own retry loop is the only retry layer.
        _, gkwargs = mock_aipc.return_value.get_openai_client.call_args
        assert gkwargs["max_retries"] == 0
        _, rkwargs = oai.responses.create.call_args
        assert rkwargs["model"] == "my-conn/gpt-4o"
        assert rkwargs["input"] == [{"type": "message", "role": "user", "content": "rate coherence"}]
        assert rkwargs["temperature"] == 0.0
        assert rkwargs["max_output_tokens"] == 800
        # The per-request timeout set via with_options(timeout=30) reaches responses.create.
        assert rkwargs["timeout"] == 30

    def test_non_numeric_timeout_is_not_forwarded(self):
        # openai passes NotGiven() when no timeout is set; the shim forwards only a numeric timeout.
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
        # azure-ai-projects is optional (not in install_requires); the BYO path must surface a clear
        # MissingRequiredPackage error. A None entry in sys.modules makes the import raise ImportError.
        import sys

        from azure.ai.evaluation._legacy._adapters._errors import MissingRequiredPackage

        monkeypatch.setitem(sys.modules, "azure.ai.projects.aio", None)
        client = AsyncByoProjectResponsesClient("c/d", "https://acct.services.ai.azure.com/api/projects/p", MagicMock())
        with pytest.raises(MissingRequiredPackage):
            asyncio.run(client.chat.completions.create(messages=[{"role": "user", "content": "hi"}]))

    @patch("azure.ai.projects.aio.AIProjectClient")
    def test_extra_headers_forwarded_to_responses(self, mock_aipc):
        # ACA may supply extra headers for continuous evals; the shim must forward them to responses.create.
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
    def test_per_request_extra_headers_merged_and_forwarded(self, mock_aipc):
        # Headers passed per-request to chat.completions.create(extra_headers=...) must be forwarded
        # to responses.create, merged over client-level headers (per-request wins), as a copy.
        resp = MagicMock(output_text="ok", usage=None, id="r", model="m", status="completed")
        oai = MagicMock()
        oai.responses.create = AsyncMock(return_value=resp)
        mock_aipc.return_value.get_openai_client.return_value = oai

        client_headers = {"x-ms-client-request-id": "client-1", "x-shared": "from-client"}
        request_headers = {"Connection": "close", "x-shared": "from-request"}
        client = AsyncByoProjectResponsesClient(
            "c/d", "https://acct.services.ai.azure.com/api/projects/p", MagicMock(), extra_headers=client_headers
        )
        asyncio.run(
            client.chat.completions.create(messages=[{"role": "user", "content": "hi"}], extra_headers=request_headers)
        )

        _, rkwargs = oai.responses.create.call_args
        fwd = rkwargs["extra_headers"]
        assert fwd == {"x-ms-client-request-id": "client-1", "Connection": "close", "x-shared": "from-request"}
        # Per-request value wins on conflict.
        assert fwd["x-shared"] == "from-request"
        # Forwarded as a copy — neither source dict is the forwarded object (no mutation leak).
        assert fwd is not client_headers and fwd is not request_headers

    @patch("azure.ai.projects.aio.AIProjectClient")
    def test_preserves_server_created_timestamp(self, mock_aipc):
        # Responses exposes the server timestamp as created_at; the shim preserves it (not local time).
        cc = _ChatCompletion(SimpleNamespace(output_text="ok", usage=None, id="r", model="m", created_at=1752694800))
        assert cc.created == 1752694800

    def test_created_timestamp_falls_back_to_created_then_now(self):
        # Older/mocked shapes may only carry ``created``; that is honored as a fallback.
        assert _ChatCompletion(SimpleNamespace(output_text="ok", created=1700000000)).created == 1700000000
        # When neither is a real number, fall back to the local wall-clock time (a positive int).
        assert _ChatCompletion(SimpleNamespace(output_text="ok")).created > 0


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


class TestAsyncPromptyByoIntegration:
    """Exercise the BYO branch through AsyncPrompty end-to-end (not just the shim in isolation)."""

    _PROMPTY = (
        "---\n"
        "name: byo-judge\n"
        "model:\n"
        "  api: chat\n"
        "  parameters:\n"
        "    temperature: 0.0\n"
        "inputs:\n"
        "  question:\n"
        "    type: string\n"
        "---\n"
        "system:\n"
        "You are a judge.\n"
        "\n"
        "user:\n"
        "{{question}}\n"
    )

    @patch("azure.ai.projects.aio.AIProjectClient")
    def test_async_prompty_routes_byo_config_through_shim(self, mock_aipc, tmp_path):
        from azure.ai.evaluation._legacy.prompty._prompty import AsyncPrompty

        prompty_path = tmp_path / "byo_judge.prompty"
        prompty_path.write_text(self._PROMPTY, encoding="utf-8")

        resp = SimpleNamespace(output_text="score: 5", usage=None, id="r", model="conn/dep", created_at=1)
        oai = MagicMock()
        oai.responses.create = AsyncMock(return_value=resp)
        mock_aipc.return_value.get_openai_client.return_value = oai

        model = {
            "configuration": {
                "byo_model": "conn/dep",
                "project_endpoint": "https://acct.services.ai.azure.com/api/projects/p",
            },
            "parameters": {"temperature": 0.0},
        }
        flow = AsyncPrompty.load(source=str(prompty_path), model=model, token_credential=MagicMock())
        result = asyncio.run(flow(question="rate this"))

        # The BYO branch built the project client with the project endpoint and routed to responses.
        mock_aipc.assert_called_once()
        _, pkwargs = mock_aipc.call_args
        assert pkwargs["endpoint"] == "https://acct.services.ai.azure.com/api/projects/p"
        _, rkwargs = oai.responses.create.call_args
        assert rkwargs["model"] == "conn/dep"
        # The formatted judge output flows back through AsyncPrompty's response formatting.
        assert "score: 5" in str(result)
