# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

import asyncio
from types import SimpleNamespace

import pytest

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
