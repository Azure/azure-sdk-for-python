import pytest
from azure.ai.evaluation import evaluate, ToolCallAccuracyEvaluator
from azure.ai.evaluation._exceptions import EvaluationException


@pytest.mark.usefixtures("mock_model_config")
@pytest.mark.unittest
class TestEvaluate:
    def test_tool_call_accuracy_evaluator_missing_inputs(self, mock_model_config):
        tool_call_accuracy = ToolCallAccuracyEvaluator(model_config=mock_model_config)

        # Test with missing tool_calls and response
        with pytest.raises(EvaluationException) as exc_info:
            tool_call_accuracy(
                query="Where is the Eiffel Tower?",
                tool_definitions=[
                    {
                        "name": "fetch_weather",
                        "description": "Fetches the weather information for the specified location.",
                        "parameters": {
                            "type": "object",
                            "properties": {
                                "location": {
                                    "type": "string",
                                    "description": "The location to fetch weather for.",
                                }
                            },
                        },
                    }
                ],
            )
        assert ToolCallAccuracyEvaluator._NO_TOOL_CALLS_MESSAGE in str(exc_info.value)

        # Test with missing tool_definitions
        with pytest.raises(EvaluationException) as exc_info:
            tool_call_accuracy(
                query="Where is the Eiffel Tower?",
                tool_definitions=[],
                tool_calls=[
                    {
                        "type": "tool_call",
                        "name": "fetch_weather",
                        "arguments": {"location": "Tokyo"},
                    }
                ],
            )
        assert ToolCallAccuracyEvaluator._NO_TOOL_DEFINITIONS_MESSAGE in str(exc_info.value)

        # Test with response that has no tool calls
        result = tool_call_accuracy(
            query="Where is the Eiffel Tower?",
            response="The Eiffel Tower is in Paris.",
            tool_definitions=[
                {
                    "name": "fetch_weather",
                    "description": "Fetches the weather information for the specified location.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "location": {
                                "type": "string",
                                "description": "The location to fetch weather for.",
                            }
                        },
                    },
                }
            ],
        )
        assert result[ToolCallAccuracyEvaluator._RESULT_KEY] == ToolCallAccuracyEvaluator._NOT_APPLICABLE_RESULT
        assert (
            ToolCallAccuracyEvaluator._NO_TOOL_CALLS_MESSAGE
            in result[f"{ToolCallAccuracyEvaluator._RESULT_KEY}_reason"]
        )

        # Test with tool call for which definition is not provided
        result = tool_call_accuracy(
            query="Where is the Eiffel Tower?",
            tool_calls=[{"type": "tool_call", "name": "some_other_tool", "tool_call_id": "1", "arguments": {}}],
            tool_definitions=[
                {
                    "name": "fetch_weather",
                    "description": "Fetches the weather information for the specified location.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "location": {
                                "type": "string",
                                "description": "The location to fetch weather for.",
                            }
                        },
                    },
                }
            ],
        )
        assert result[ToolCallAccuracyEvaluator._RESULT_KEY] == ToolCallAccuracyEvaluator._NOT_APPLICABLE_RESULT
        assert (
            ToolCallAccuracyEvaluator._TOOL_DEFINITIONS_MISSING_MESSAGE
            in result[f"{ToolCallAccuracyEvaluator._RESULT_KEY}_reason"]
        )
