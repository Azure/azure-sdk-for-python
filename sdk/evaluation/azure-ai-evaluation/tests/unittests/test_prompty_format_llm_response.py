# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

import asyncio
import traceback
from types import SimpleNamespace

import pytest

from azure.ai.evaluation._legacy.prompty._exceptions import InvalidLLMOutputError
from azure.ai.evaluation._legacy.prompty._utils import format_llm_response


class _FakeResponse:
    def __init__(self, content="test-output", finish_reason="stop", completion_tokens=2, usage=True):
        self.usage = (
            SimpleNamespace(prompt_tokens=1, completion_tokens=completion_tokens, total_tokens=3) if usage else None
        )
        self.choices = [
            SimpleNamespace(
                finish_reason=finish_reason,
                message=SimpleNamespace(role="assistant", content=content),
            )
        ]
        self.model = "test-model"
        self._content = content

    def model_dump(self):
        return {
            "choices": [
                {
                    "message": {
                        "role": "assistant",
                        "content": self._content,
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
@pytest.mark.parametrize(
    "content, finish_reason, expected",
    [
        ('{"score": 3, "explanation": "SECRET', "length", "truncated at the output token limit"),
        (None, "content_filter", "blocked by the content filter"),
        ("   ", "stop", "returned an empty response"),
        ("SECRET not json", "stop", "not valid JSON (Expecting value, position 0)"),
        ('{"SECRET": "x"', "stop", "not valid JSON (Expecting ',' delimiter, position 14)"),
        ('"SECRET', "stop", "not valid JSON (Unterminated string starting at, position 0)"),
        ("[" * 100000, "stop", "the model response was not valid JSON (finish_reason"),
        ('{"SECRET": ' + "9" * 5000 + "}", "stop", "the model response was not valid JSON (finish_reason"),
    ],
    ids=["truncated", "filtered", "empty", "not-json", "delimiter", "unterminated", "too-deep", "digit-limit"],
)
def test_format_llm_response_reports_invalid_json_output(content, finish_reason, expected):
    with pytest.raises(InvalidLLMOutputError) as exc_info:
        _format_json(_FakeResponse(content=content, finish_reason=finish_reason, completion_tokens=800))

    error = exc_info.value
    message = str(error)
    blame = "UserError" if finish_reason == "content_filter" else "InternalError"
    assert message.startswith(f"({blame}) Model returned invalid output: the model ")
    assert expected in message
    assert f"(finish_reason={finish_reason}, output_tokens=800)." in message
    assert error.properties == {"prompt_tokens": 1, "completion_tokens": 800, "total_tokens": 3, "model": "test-model"}
    # The decoding error holds the model output, so it must not be chained or captured by AzureError.
    assert error.__context__ is None
    assert error.__cause__ is None
    assert error.exc_value is None
    for text in (message, error.exc_msg, "".join(traceback.format_exception(type(error), error, error.__traceback__))):
        assert "SECRET" not in text


@pytest.mark.unittest
def test_format_llm_response_reports_missing_usage_as_unknown():
    with pytest.raises(InvalidLLMOutputError) as exc_info:
        _format_json(_FakeResponse(content="not json", usage=False))
    assert "(finish_reason=stop, output_tokens=unknown)." in str(exc_info.value)
    assert exc_info.value.properties == {"model": "test-model"}


@pytest.mark.unittest
def test_format_llm_response_keeps_the_reported_usage():
    result = _format_json(_FakeResponse(content='{"score": 1}', usage=False))
    assert result["output_token_count"] == 0
    assert result["reported_usage"] == {
        "prompt_tokens": None,
        "completion_tokens": None,
        "total_tokens": None,
        "model": "test-model",
    }


@pytest.mark.unittest
@pytest.mark.parametrize("content", ["null", "7", '["SECRET"]'])
def test_format_llm_response_with_outputs_rejects_a_non_object(content):
    with pytest.raises(InvalidLLMOutputError, match="the model response was not a JSON object") as exc_info:
        _format_json(_FakeResponse(content=content), outputs={"score": {}})
    assert "SECRET" not in str(exc_info.value)


@pytest.mark.unittest
@pytest.mark.parametrize("content, expected", [("null", None), ("7", 7), ('{"score": 1}', {"score": 1})])
def test_format_llm_response_returns_valid_json_without_outputs(content, expected):
    assert _format_json(_FakeResponse(content=content))["llm_output"] == expected
