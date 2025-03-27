import pytest
from azure.ai.evaluation import evaluate, ToolCallAccuracyEvaluator
from azure.ai.evaluation._exceptions import EvaluationException


@pytest.mark.usefixtures("mock_model_config")
@pytest.mark.unittest
class TestEvaluate:
    def test_tool_call_accuracy_evaluator_missing_inputs(self, mock_model_config):
        tool_call_accuracy = ToolCallAccuracyEvaluator(model_config=mock_model_config)

        # Test tool_calls provided but missing response
        with pytest.raises(EvaluationException) as exc_info:
            tool_call_accuracy(
                query="Where is the Eiffel Tower?",
                response="The Eiffel Tower is in Paris.",
                tool_calls="Test",
                tool_definitions={
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
                }
            )

        # Test with missing tool_definitions
        with pytest.raises(EvaluationException) as exc_info:
            tool_call_accuracy(
                query="Where is the Eiffel Tower?",
                tool_calls={
                    "type": "tool_call",
                    "tool_call": {
                        "id": "call_K21dwOxgCN2syn4qjutMVV7Z",
                        "type": "function",
                    "function": {
                        "name": "fetch_weather",
                        "arguments": {
                            "location": "Tokyo"
                        }
                    }
                    }
                }
            )
        assert "Tool definitions must be provided." in str(exc_info.value)

        # Test with missing tool_cools
        with pytest.raises(EvaluationException) as exc_info:
            tool_call_accuracy(
                query="Where is the Eiffel Tower?",
                tool_definitions={
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
	            }
            )

        assert "Either response or tool_calls must be provided." in str(exc_info.value)

        # Test response provided but missing tool_calls
        with pytest.raises(EvaluationException) as exc_info:
            tool_call_accuracy(
                query="Where is the Eiffel Tower?",
                response="The Eiffel Tower is in Paris.",
                tool_definitions={
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
                }
            )

        assert "response does not have tool calls. Either provide tool_calls or response with tool calls." in str(exc_info.value)

        # Test tool_calls provided but missing response
        with pytest.raises(EvaluationException) as exc_info:
            tool_call_accuracy(
                query="Where is the Eiffel Tower?",
                response="The Eiffel Tower is in Paris.",
                tool_calls="Test",
                tool_definitions={
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
                }
            )

            assert "Tool definition not found" in str(exc_info.value)