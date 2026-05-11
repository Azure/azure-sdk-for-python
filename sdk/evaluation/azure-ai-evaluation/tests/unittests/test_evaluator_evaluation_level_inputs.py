# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from azure.ai.evaluation._evaluators._coherence import CoherenceEvaluator
from azure.ai.evaluation._evaluators._common import PromptyEvaluatorBase
from azure.ai.evaluation._evaluators._common._validators import (
    MessagesOrQueryResponseInputValidator,
    MessagesOrQueryResponseToolDefinitionsValidator,
)
from azure.ai.evaluation._evaluators._task_adherence import TaskAdherenceEvaluator
from azure.ai.evaluation._evaluators._task_completion import _TaskCompletionEvaluator
from azure.ai.evaluation._exceptions import ErrorTarget, EvaluationException


@pytest.mark.usefixtures("mock_model_config")
@pytest.mark.unittest
class TestEvaluatorEvaluationLevelInputs:
    def test_coherence_messages_auto_detect_conversation(self, mock_model_config):
        evaluator = CoherenceEvaluator(model_config=mock_model_config)
        evaluator._validator.validate_eval_input = MagicMock(return_value=True)

        messages = [
            {"role": "user", "content": "What is 2+2?"},
            {"role": "assistant", "content": "4"},
        ]

        with patch.object(PromptyEvaluatorBase, "_real_call", new_callable=AsyncMock) as real_call_mock:
            real_call_mock.return_value = {"coherence": 4.0}
            result = evaluator(messages=messages)

        assert result == {"coherence": 4.0}
        real_call_mock.assert_awaited_once_with(conversation={"messages": messages})

    def test_coherence_messages_forced_conversation(self, mock_model_config):
        evaluator = CoherenceEvaluator(model_config=mock_model_config, evaluation_level="conversation")
        evaluator._validator.validate_eval_input = MagicMock(return_value=True)

        messages = [
            {"role": "user", "content": "What is 2+2?"},
            {"role": "assistant", "content": "4"},
        ]

        with patch.object(PromptyEvaluatorBase, "_real_call", new_callable=AsyncMock) as real_call_mock:
            real_call_mock.return_value = {"coherence": 4.0}
            result = evaluator(messages=messages)

        assert result == {"coherence": 4.0}
        real_call_mock.assert_awaited_once_with(conversation={"messages": messages})

    def test_task_completion_turn_level_splits_messages(self, mock_model_config):
        evaluator = _TaskCompletionEvaluator(model_config=mock_model_config, evaluation_level="turn")
        evaluator._validator.validate_eval_input = MagicMock(return_value=True)

        messages = [
            {"role": "user", "content": "Book a flight to Seattle."},
            {"role": "assistant", "content": "Booked. Confirmation #123."},
        ]
        tool_definitions = [{"name": "book_flight", "parameters": {"type": "object", "properties": {}}}]

        with patch.object(PromptyEvaluatorBase, "_real_call", new_callable=AsyncMock) as real_call_mock:
            real_call_mock.return_value = {"task_completion": 1}
            result = evaluator(messages=messages, tool_definitions=tool_definitions)

        assert result == {"task_completion": 1}
        real_call_mock.assert_awaited_once_with(
            query=[messages[0]],
            response=[messages[1]],
            tool_definitions=tool_definitions,
        )

    def test_task_adherence_invalid_evaluation_level_raises(self, mock_model_config):
        with pytest.raises(EvaluationException) as exc:
            TaskAdherenceEvaluator(model_config=mock_model_config, evaluation_level="invalid")
        assert "Invalid evaluation_level" in str(exc.value)

    def test_task_adherence_turn_level_splits_messages(self, mock_model_config):
        evaluator = TaskAdherenceEvaluator(model_config=mock_model_config, evaluation_level="turn")
        evaluator._validator.validate_eval_input = MagicMock(return_value=True)

        messages = [
            {"role": "user", "content": "Find my order status."},
            {"role": "assistant", "content": "Your order arrives tomorrow."},
        ]
        tool_definitions = [{"name": "get_order", "parameters": {"type": "object", "properties": {}}}]

        with patch.object(PromptyEvaluatorBase, "_real_call", new_callable=AsyncMock) as real_call_mock:
            real_call_mock.return_value = {"task_adherence": 1}
            result = evaluator(messages=messages, tool_definitions=tool_definitions)

        assert result == {"task_adherence": 1}
        real_call_mock.assert_awaited_once_with(
            query=[messages[0]],
            response=[messages[1]],
            tool_definitions=tool_definitions,
        )

    def test_messages_validator_accepts_messages_input(self):
        validator = MessagesOrQueryResponseInputValidator(error_target=ErrorTarget.COHERENCE_EVALUATOR)
        eval_input = {"messages": [{"role": "user", "content": "Hello"}, {"role": "assistant", "content": "Hi"}]}
        assert validator.validate_eval_input(eval_input)

    def test_messages_tool_definitions_validator_accepts_messages_input(self):
        validator = MessagesOrQueryResponseToolDefinitionsValidator(error_target=ErrorTarget.TASK_COMPLETION_EVALUATOR)
        eval_input = {
            "messages": [{"role": "user", "content": "Book a flight"}, {"role": "assistant", "content": "Booked"}],
            "tool_definitions": [{"name": "book_flight", "parameters": {"type": "object", "properties": {}}}],
        }
        assert validator.validate_eval_input(eval_input)
