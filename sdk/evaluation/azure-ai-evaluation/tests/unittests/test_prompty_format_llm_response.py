# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

import asyncio
import json
import logging
from types import SimpleNamespace

import pytest

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
    with pytest.raises(json.JSONDecodeError):
        _format_json(_json_response('{"score": 4, "reason": "secret', finish_reason="length", completion_tokens=800))

    assert "truncated" in caplog.text
    assert "finish_reason=length, output_tokens=800, model=test-model" in caplog.text
    assert "secret" not in caplog.text
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
