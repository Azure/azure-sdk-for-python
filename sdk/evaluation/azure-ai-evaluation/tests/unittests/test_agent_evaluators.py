import pytest
from azure.ai.evaluation import evaluate, ToolCallAccuracyEvaluator
from azure.ai.evaluation._exceptions import EvaluationException


@pytest.mark.usefixtures("mock_model_config")
@pytest.mark.unittest
class TestEvaluate:
    def test_tool_call_accuracy_evaluator_missing_inputs(self, mock_model_config):
        tool_call_accuracy = ToolCallAccuracyEvaluator(model_config=mock_model_config)

        # Test with missing tool_calls and response
        result = tool_call_accuracy(
            query="Where is the Eiffel Tower?",
            tool_definitions=[{
                "name": "fetch_weather",
                "description": "Fetches the weather information for the specified location.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "location": {
                            "type": "string",
                            "description": "The location to fetch weather for."
                        }
                    }
                }
            }]
        )
        assert not result["applicable"]
        assert result["tool_call_accuracy"] == "not applicable"
        assert "No tool calls found in response or provided tool_calls." in result["tool_call_accuracy_reason"]

        # Test with missing tool_definitions
        result = tool_call_accuracy(
            query="Where is the Eiffel Tower?",
            tool_definitions=[],
            tool_calls=[{
                "type": "tool_call",
                "name": "fetch_weather",
                "arguments": {
                    "location": "Tokyo"
                }
            }]
        )
        assert not result["applicable"]
        assert result["tool_call_accuracy"] == "not applicable"
        assert "Tool definitions must be provided." in result["tool_call_accuracy_reason"]

        # Test with response that has no tool calls
        result = tool_call_accuracy(
            query="Where is the Eiffel Tower?",
            response="The Eiffel Tower is in Paris.",
            tool_definitions=[{
                "name": "fetch_weather",
                "description": "Fetches the weather information for the specified location.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "location": {
                            "type": "string",
                            "description": "The location to fetch weather for."
                        }
                    }
                }
            }]
        )
        assert not result["applicable"]
        assert result["tool_call_accuracy"] == "not applicable"
        assert "No tool calls found in response or provided tool_calls." in result["tool_call_accuracy_reason"]

        # Test with tool call for which definition is not provided
        result = tool_call_accuracy(
            query="Where is the Eiffel Tower?",
            tool_calls=[{
                "type": "tool_call",
                "name": "some_other_tool",
                "arguments": {}
            }],
            tool_definitions=[{
                "name": "fetch_weather",
                "description": "Fetches the weather information for the specified location.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "location": {
                            "type": "string",
                            "description": "The location to fetch weather for."
                        }
                    }
                }
            }]
        )
        assert not result["applicable"]
        assert result["tool_call_accuracy"] == "not applicable"
        assert "Tool definitions for all tool calls must be provided." in result["tool_call_accuracy_reason"]