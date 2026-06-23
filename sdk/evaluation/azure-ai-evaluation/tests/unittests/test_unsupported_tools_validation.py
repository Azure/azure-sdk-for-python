# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""
Regression tests for the change that lets the three tool evaluators
(ToolCallAccuracy, _ToolInputAccuracy, _ToolCallSuccess) accept
conversations containing restricted built-in tools.

These evaluators previously rejected any conversation containing tools in
``ConversationValidator.UNSUPPORTED_TOOLS`` (e.g. ``bing_grounding``,
``azure_ai_search``). Because none of the three grades require the
(redacted) tool output body, the rejection has been lifted by setting
``check_for_unsupported_tools=False`` on each evaluator's input validator.

The tests below exercise the validator directly so they do not need the
prompty flow or a real model deployment. They also confirm that the
underlying validator class still rejects restricted tools when
``check_for_unsupported_tools=True``, so the behavior change is limited
to the evaluator wiring.
"""

import pytest

from azure.ai.evaluation import ToolCallAccuracyEvaluator
from azure.ai.evaluation._evaluators._tool_call_success import _ToolCallSuccessEvaluator
from azure.ai.evaluation._evaluators._tool_input_accuracy import _ToolInputAccuracyEvaluator
from azure.ai.evaluation._evaluators._common._validators import (
    ToolCallsValidator,
    ToolDefinitionsValidator,
)
from azure.ai.evaluation._exceptions import ErrorTarget, EvaluationException


RESTRICTED_TOOL_NAMES = [
    "bing_grounding",
    "bing_custom_search",
    "azure_ai_search",
    "azure_fabric",
    "sharepoint_grounding",
]


def _restricted_response(tool_name: str):
    return [
        {
            "role": "assistant",
            "content": [
                {
                    "type": "tool_call",
                    "tool_call_id": "call_restricted",
                    "name": tool_name,
                    "arguments": {"query": "anything"},
                }
            ],
        }
    ]


def _restricted_tool_definition(tool_name: str):
    return {
        "name": tool_name,
        "description": f"Built-in {tool_name} tool.",
        "parameters": {
            "type": "object",
            "properties": {"query": {"type": "string"}},
        },
    }


@pytest.mark.usefixtures("mock_model_config")
@pytest.mark.unittest
class TestRestrictedToolValidationLifted:
    """Validator should no longer reject restricted tools for these three evaluators."""

    @pytest.mark.parametrize("tool_name", RESTRICTED_TOOL_NAMES)
    def test_tool_call_accuracy_accepts_restricted_tool(self, mock_model_config, tool_name):
        evaluator = ToolCallAccuracyEvaluator(model_config=mock_model_config)
        eval_input = {
            "query": "Look it up.",
            "response": _restricted_response(tool_name),
            "tool_definitions": [_restricted_tool_definition(tool_name)],
        }
        # Should not raise EvaluationException; flag flip made this path legal.
        assert evaluator._validator.validate_eval_input(eval_input) is True

    @pytest.mark.parametrize("tool_name", RESTRICTED_TOOL_NAMES)
    def test_tool_input_accuracy_accepts_restricted_tool(self, mock_model_config, tool_name):
        evaluator = _ToolInputAccuracyEvaluator(model_config=mock_model_config)
        eval_input = {
            "query": "Look it up.",
            "response": _restricted_response(tool_name),
            "tool_definitions": [_restricted_tool_definition(tool_name)],
        }
        assert evaluator._validator.validate_eval_input(eval_input) is True

    @pytest.mark.parametrize("tool_name", RESTRICTED_TOOL_NAMES)
    def test_tool_call_success_accepts_restricted_tool(self, mock_model_config, tool_name):
        evaluator = _ToolCallSuccessEvaluator(model_config=mock_model_config)
        eval_input = {
            "response": _restricted_response(tool_name),
            "tool_definitions": [_restricted_tool_definition(tool_name)],
        }
        assert evaluator._validator.validate_eval_input(eval_input) is True

    def test_mixed_function_and_restricted_tool_accepted(self, mock_model_config):
        """Conversation containing both a function call and a restricted tool call validates cleanly."""
        evaluator = ToolCallAccuracyEvaluator(model_config=mock_model_config)
        eval_input = {
            "query": "Find stock price and weather.",
            "response": [
                {
                    "role": "assistant",
                    "content": [
                        {
                            "type": "tool_call",
                            "tool_call_id": "call_func",
                            "name": "get_weather",
                            "arguments": {"location": "Paris"},
                        },
                        {
                            "type": "tool_call",
                            "tool_call_id": "call_restricted",
                            "name": "bing_grounding",
                            "arguments": {"query": "MSFT stock price"},
                        },
                    ],
                }
            ],
            "tool_definitions": [
                {
                    "name": "get_weather",
                    "type": "function",
                    "description": "Weather lookup.",
                    "parameters": {
                        "type": "object",
                        "properties": {"location": {"type": "string"}},
                        "required": ["location"],
                    },
                },
                _restricted_tool_definition("bing_grounding"),
            ],
        }
        assert evaluator._validator.validate_eval_input(eval_input) is True


@pytest.mark.unittest
class TestUnderlyingValidatorUnchanged:
    """The validator class itself still rejects restricted tools when the flag is on.

    Ensures the behavior change is limited to per-evaluator wiring; the validator
    keeps its option to enforce the restricted-tool block for other consumers
    (e.g. GroundednessEvaluator).
    """

    @pytest.mark.parametrize("tool_name", RESTRICTED_TOOL_NAMES)
    def test_tool_calls_validator_still_rejects_when_flag_enabled(self, tool_name):
        validator = ToolCallsValidator(
            error_target=ErrorTarget.TOOL_CALL_ACCURACY_EVALUATOR,
            check_for_unsupported_tools=True,
        )
        eval_input = {
            "query": "Look it up.",
            "response": _restricted_response(tool_name),
            "tool_definitions": [_restricted_tool_definition(tool_name)],
        }
        with pytest.raises(EvaluationException) as exc_info:
            validator.validate_eval_input(eval_input)
        assert "currently not supported" in str(exc_info.value)

    @pytest.mark.parametrize("tool_name", RESTRICTED_TOOL_NAMES)
    def test_tool_definitions_validator_still_rejects_when_flag_enabled(self, tool_name):
        validator = ToolDefinitionsValidator(
            error_target=ErrorTarget.TOOL_CALL_SUCCESS_EVALUATOR,
            requires_query=False,
            check_for_unsupported_tools=True,
        )
        eval_input = {
            "response": _restricted_response(tool_name),
            "tool_definitions": [_restricted_tool_definition(tool_name)],
        }
        with pytest.raises(EvaluationException) as exc_info:
            validator.validate_eval_input(eval_input)
        assert "currently not supported" in str(exc_info.value)
