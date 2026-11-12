# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

import asyncio
import json
import logging
from types import SimpleNamespace
from unittest.mock import AsyncMock

import pytest

from azure.ai.evaluation._evaluators._common import _model_runners
from azure.ai.evaluation._evaluators._common._prompty_strategy import PromptyEvaluationStrategy
from azure.ai.evaluation._exceptions import EvaluationException
from azure.ai.evaluation._legacy.prompty._exceptions import InvalidInputError
from azure.ai.evaluation._legacy.prompty._utils import format_llm_response


class _FakeResponse:
    def __init__(self):
        self.usage = SimpleNamespace(prompt_tokens=1, completion_tokens=2, total_tokens=3)
        self.choices = [
            SimpleNamespace(
                finish_reason="stop",
                message=SimpleNamespace(role="assistant", content="test-output"),
            )
        ]
        self.model = "test-model"

    def model_dump(self):
        return {
            "choices": [
                {
                    "message": {
                        "role": "assistant",
                        "content": "test-output",
                    }
                }
            ]
        }


@pytest.mark.unittest
def test_format_llm_response_with_no_inputs_sets_empty_sample_input():
    response = _FakeResponse()

    result = asyncio.run(
        format_llm_response(
            response=response,
            is_first_choice=True,
            response_format={"type": "text"},
            outputs=None,
            inputs=None,
        )
    )

    assert result["llm_output"] == "test-output"
    assert result["sample_input"] == ""


def _json_response(content, finish_reason="stop", completion_tokens=2, choices=True):
    response = _FakeResponse()
    response.usage = SimpleNamespace(prompt_tokens=1, completion_tokens=completion_tokens, total_tokens=3)
    response.choices = (
        [SimpleNamespace(finish_reason=finish_reason, message=SimpleNamespace(role="assistant", content=content))]
        if choices
        else []
    )
    return response


def _format_json(response, outputs=None):
    return asyncio.run(
        format_llm_response(
            response=response,
            is_first_choice=True,
            response_format={"type": "json_object"},
            outputs=outputs,
            inputs=None,
        )
    )


@pytest.mark.unittest
def test_format_llm_response_logs_metadata_and_reraises_invalid_json(caplog):
    with pytest.raises(json.JSONDecodeError) as exc_info:
        _format_json(_json_response('{"score": 4, "reason": "secret', finish_reason="length", completion_tokens=800))

    assert "truncated" in caplog.text
    assert "finish_reason=length, output_tokens=800, model=test-model" in caplog.text
    assert "finish_reason=length, output_tokens=800, model=test-model" in str(exc_info.value)
    assert "secret" not in caplog.text
    assert "secret" not in str(exc_info.value)
    assert all(record.levelno == logging.WARNING and not record.exc_info for record in caplog.records)


@pytest.mark.unittest
def test_format_llm_response_missing_output_keeps_key_list_and_adds_metadata(caplog):
    with pytest.raises(InvalidInputError) as exc_info:
        _format_json(_json_response('{"reason": "secret"}'), outputs={"score": {}})

    message = str(exc_info.value)
    assert "Cannot find 'score' in response ['reason']" in message
    assert "finish_reason=stop, output_tokens=2, model=test-model" in message
    assert "secret" not in caplog.text


@pytest.mark.unittest
def test_format_llm_response_logs_empty_choices_and_reraises(caplog):
    with pytest.raises(IndexError):
        _format_json(_json_response("{}", choices=False))

    assert "contained no choices" in caplog.text


@pytest.mark.unittest
def test_missing_usage_is_unknown_in_later_diagnostics():
    response = _json_response("[]")
    response.usage = None
    result = _format_json(response)
    strategy = PromptyEvaluationStrategy(AsyncMock(), result_key="metric", threshold=3, timeout=1)

    with pytest.raises(EvaluationException) as exc_info:
        strategy.parse(result)

    assert "finish_reason=stop, output_tokens=unknown, model=test-model" in exc_info.value.message


@pytest.mark.unittest
def test_promptflow_json_decode_error_logs_diagnostic_and_reraises(monkeypatch, caplog):
    runner = _model_runners.PromptyModelRunner.__new__(_model_runners.PromptyModelRunner)
    runner.flow = AsyncMock(side_effect=json.JSONDecodeError("invalid", "{", 0))
    monkeypatch.setattr(_model_runners, "_USE_PF_PROMPTY", True)

    with pytest.raises(json.JSONDecodeError) as exc_info:
        asyncio.run(runner(timeout=1))

    assert "the model response was not valid JSON" in caplog.text
    assert "finish_reason=unknown, output_tokens=unknown, model=unknown" in caplog.text
    assert "finish_reason=unknown, output_tokens=unknown, model=unknown" in str(exc_info.value)


@pytest.mark.unittest
def test_logging_handler_failure_does_not_replace_json_error(capsys):
    class FailingHandler(logging.Handler):
        def emit(self, _record):
            raise RuntimeError("synthetic handler failure")

    logger = logging.getLogger("azure.ai.evaluation._legacy.prompty._utils")
    handler = FailingHandler()
    logger.addHandler(handler)
    try:
        with pytest.raises(json.JSONDecodeError):
            _format_json(_json_response("{"))
    finally:
        logger.removeHandler(handler)

    assert "Model returned invalid output." in capsys.readouterr().err
