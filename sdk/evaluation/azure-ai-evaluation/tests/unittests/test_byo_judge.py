# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Unit tests for the admin-connected (BYO) judge-model prototype."""
from unittest.mock import MagicMock, patch

import pytest

from azure.ai.evaluation._byo_judge import (
    ByoProjectResponsesClient,
    build_byo_judge_client,
    is_byo_model_config,
    _to_responses_input,
    _map_params,
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


class TestByoJudgeClient:
    @patch("azure.ai.projects.AIProjectClient")
    def test_chat_completions_routes_to_responses(self, mock_aipc):
        resp = MagicMock()
        resp.output_text = "judge says 5"
        resp.usage = MagicMock()
        resp.id = "resp_1"
        resp.model = "my-conn/gpt-4o"
        oai = MagicMock()
        oai.responses.create.return_value = resp
        mock_aipc.return_value.get_openai_client.return_value = oai

        client = build_byo_judge_client(
            {"byo_model": "my-conn/gpt-4o", "project_endpoint": "https://acct.services.ai.azure.com/api/projects/p1"},
            credential=MagicMock(),
        )
        # Judge/grader code calls chat.completions.create unchanged.
        result = client.chat.completions.create(
            model="ignored",
            messages=[{"role": "user", "content": "score this 1-5"}],
            temperature=0.0,
            max_tokens=10,
        )

        # chat.completions-shaped result over the Responses output.
        assert result.choices[0].message.content == "judge says 5"
        assert result.choices[0].message.role == "assistant"

        # Underlying call is responses.create with the BYO model + mapped input/params.
        mock_aipc.assert_called_once()
        _, pkwargs = mock_aipc.call_args
        assert pkwargs["endpoint"] == "https://acct.services.ai.azure.com/api/projects/p1"
        _, rkwargs = oai.responses.create.call_args
        assert rkwargs["model"] == "my-conn/gpt-4o"
        assert rkwargs["input"] == [{"type": "message", "role": "user", "content": "score this 1-5"}]
        assert rkwargs["temperature"] == 0.0
        assert rkwargs["max_output_tokens"] == 10

    def test_build_requires_project_endpoint(self):
        with pytest.raises(ValueError):
            build_byo_judge_client({"byo_model": "c/d"}, credential=MagicMock())

    def test_build_requires_credential(self):
        with pytest.raises(ValueError):
            build_byo_judge_client({"byo_model": "c/d", "project_endpoint": "https://x"}, credential=None)


class TestAzureOpenAIGraderByo:
    @patch("azure.ai.projects.AIProjectClient")
    def test_grader_get_client_returns_shim_for_byo(self, _mock_aipc):
        from azure.ai.evaluation._aoai.aoai_grader import AzureOpenAIGrader

        grader = AzureOpenAIGrader(
            model_config={
                "byo_model": "my-conn/gpt-4o",
                "project_endpoint": "https://acct.services.ai.azure.com/api/projects/p1",
            },
            grader_config={},
            credential=MagicMock(),
        )
        assert isinstance(grader.get_client(), ByoProjectResponsesClient)

    def test_grader_byo_requires_credential(self):
        from azure.ai.evaluation._aoai.aoai_grader import AzureOpenAIGrader
        from azure.ai.evaluation._exceptions import EvaluationException

        with pytest.raises(EvaluationException):
            AzureOpenAIGrader(
                model_config={
                    "byo_model": "my-conn/gpt-4o",
                    "project_endpoint": "https://acct.services.ai.azure.com/api/projects/p1",
                },
                grader_config={},
                credential=None,
            )
