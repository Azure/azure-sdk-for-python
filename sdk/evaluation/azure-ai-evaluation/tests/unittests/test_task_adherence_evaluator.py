# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
from unittest.mock import MagicMock

import pytest
from azure.ai.evaluation import TaskAdherenceEvaluator


# Mock flow side effect that mimics the output of the prompty (the _flow call)
async def flow_side_effect(timeout, **kwargs):
    return {
        "llm_output": {
            "score": 1,
            "reason": "The assistant adhered to the task.",
            "properties": {},
        },
    }


def _make_evaluator(mock_model_config):
    evaluator = TaskAdherenceEvaluator(model_config=mock_model_config)
    evaluator._flow = MagicMock(side_effect=flow_side_effect)
    return evaluator


def _prompty_inputs(evaluator):
    assert evaluator._flow.call_count == 1
    return evaluator._flow.call_args.kwargs


@pytest.mark.usefixtures("mock_model_config")
@pytest.mark.unittest
class TestTaskAdherenceEvaluator:
    def test_explicit_system_message_and_tool_calls_are_forwarded(self, mock_model_config):
        """system_message and tool_calls passed as keyword arguments must reach the prompty."""
        evaluator = _make_evaluator(mock_model_config)

        result = evaluator(
            system_message="You must always verify order status before responding.",
            query="What is the status of order #123?",
            response="Your order has been shipped.",
            tool_calls='[{"name": "get_order", "arguments": {"id": "123"}}]',
        )

        prompty_inputs = _prompty_inputs(evaluator)
        assert prompty_inputs["system_message"] == "You must always verify order status before responding."
        assert prompty_inputs["tool_calls"] == '[{"name": "get_order", "arguments": {"id": "123"}}]'
        assert prompty_inputs["query"] == "What is the status of order #123?"
        assert prompty_inputs["response"] == "Your order has been shipped."
        assert result["task_adherence"] == 1.0

    def test_explicit_tool_calls_as_list_of_dicts(self, mock_model_config):
        """tool_calls passed as a list of dicts are serialized into the prompty input."""
        evaluator = _make_evaluator(mock_model_config)
        tool_calls = [
            {
                "type": "tool_call",
                "tool_call_id": "call_1",
                "name": "get_order",
                "arguments": {"id": "123"},
            }
        ]

        evaluator(
            query="What is the status of order #123?",
            response="Your order has been shipped.",
            tool_calls=tool_calls,
        )

        prompty_tool_calls = _prompty_inputs(evaluator)["tool_calls"]
        assert "get_order" in prompty_tool_calls
        assert "call_1" in prompty_tool_calls

    def test_explicit_inputs_with_message_lists(self, mock_model_config):
        """Explicit system_message/tool_calls are forwarded when query/response are message lists too."""
        evaluator = _make_evaluator(mock_model_config)

        evaluator(
            system_message="Explicit system message.",
            query=[
                {"role": "system", "content": "System message from query."},
                {"role": "user", "content": [{"type": "text", "text": "What is the status of order #123?"}]},
            ],
            response=[
                {
                    "role": "assistant",
                    "content": [
                        {
                            "type": "tool_call",
                            "tool_call_id": "call_from_response",
                            "name": "get_order",
                            "arguments": {"id": "123"},
                        }
                    ],
                },
                {"role": "assistant", "content": [{"type": "text", "text": "Your order has been shipped."}]},
            ],
            tool_calls='[{"name": "explicit_tool"}]',
        )

        prompty_inputs = _prompty_inputs(evaluator)
        assert prompty_inputs["system_message"] == "Explicit system message."
        assert prompty_inputs["tool_calls"] == '[{"name": "explicit_tool"}]'

    def test_system_message_and_tool_calls_derived_from_messages(self, mock_model_config):
        """Without explicit kwargs, system_message and tool_calls are still derived from query/response."""
        evaluator = _make_evaluator(mock_model_config)

        evaluator(
            query=[
                {"role": "system", "content": "System message from query."},
                {"role": "user", "content": [{"type": "text", "text": "What is the status of order #123?"}]},
            ],
            response=[
                {
                    "role": "assistant",
                    "content": [
                        {
                            "type": "tool_call",
                            "tool_call_id": "call_from_response",
                            "name": "get_order",
                            "arguments": {"id": "123"},
                        }
                    ],
                },
                {"role": "assistant", "content": [{"type": "text", "text": "Your order has been shipped."}]},
            ],
        )

        prompty_inputs = _prompty_inputs(evaluator)
        assert "System message from query." in prompty_inputs["system_message"] + prompty_inputs["query"]
        assert "get_order" in prompty_inputs["tool_calls"] + prompty_inputs["response"]
        assert "Your order has been shipped." in prompty_inputs["response"]

    def test_plain_strings_without_optional_inputs(self, mock_model_config):
        """Plain query/response strings still work and produce empty system_message/tool_calls."""
        evaluator = _make_evaluator(mock_model_config)

        evaluator(query="What is the status of order #123?", response="Your order has been shipped.")

        prompty_inputs = _prompty_inputs(evaluator)
        assert prompty_inputs["system_message"] == ""
        assert prompty_inputs["tool_calls"] == ""
