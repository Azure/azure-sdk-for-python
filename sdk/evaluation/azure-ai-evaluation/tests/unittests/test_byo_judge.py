# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Unit tests for admin-connected (BYO) judge-model support in the prompty judge path."""
import asyncio
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from azure.ai.evaluation._byo_judge import (
    AsyncByoProjectResponsesClient,
    is_byo_model_config,
    _to_responses_input,
    _map_params,
    _map_response_format,
    _Usage,
)


class TestByoJudgeHelpers:
    def test_is_byo_model_config(self):
        assert is_byo_model_config({"byo_model": "c/d", "project_endpoint": "https://x"})
        assert not is_byo_model_config({"azure_endpoint": "https://x"})
        assert not is_byo_model_config({})

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

    def test_with_options_returns_self(self):
        client = AsyncByoProjectResponsesClient("c/d", "https://acct.services.ai.azure.com/api/projects/p", MagicMock())
        assert client.with_options(timeout=5) is client


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
