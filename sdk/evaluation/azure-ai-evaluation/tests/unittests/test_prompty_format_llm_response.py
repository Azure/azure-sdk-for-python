# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

import asyncio
from types import SimpleNamespace

import pytest

from azure.ai.evaluation._legacy.prompty._exceptions import InvalidLLMOutputError
from azure.ai.evaluation._legacy.prompty._utils import format_llm_response


class _FakeResponse:
    def __init__(self, content="test-output", finish_reason="stop", completion_tokens=2):
        self.usage = SimpleNamespace(prompt_tokens=1, completion_tokens=completion_tokens, total_tokens=3)
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


@pytest.mark.unittest
@pytest.mark.parametrize(
    "content, finish_reason, expected",
    [
        ('{"score": 3, "explanation": "SECRET', "length", "truncated at the output token limit"),
        (None, "content_filter", "blocked by the content filter"),
        ("   ", "stop", "returned an empty response"),
        ("SECRET not json", "stop", "not valid JSON (Expecting value at character 0)"),
    ],
)
def test_format_llm_response_reports_invalid_json_output(content, finish_reason, expected):
    with pytest.raises(InvalidLLMOutputError) as exc_info:
        asyncio.run(
            format_llm_response(
                response=_FakeResponse(content=content, finish_reason=finish_reason, completion_tokens=800),
                is_first_choice=True,
                response_format={"type": "json_object"},
                outputs=None,
                inputs=None,
            )
        )

    message = str(exc_info.value)
    assert message.startswith("(InternalError) Evaluator returned invalid output: ")
    assert expected in message
    assert f"(finish_reason={finish_reason}, output_tokens=800)." in message
    assert "SECRET" not in message
    assert exc_info.value.__cause__ is None
