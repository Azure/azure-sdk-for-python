from unittest.mock import MagicMock

import pytest
from azure.ai.evaluation import ToolCallAccuracyEvaluator
from azure.ai.evaluation._exceptions import EvaluationException


# This mock should return a dictionary that mimics the output of the prompty (the _flow call),
# which is then processed by the _do_eval method.
async def flow_side_effect(timeout, **kwargs):
    tool_calls = kwargs.get("tool_calls", [])
    query = kwargs.get("query", "")

    # Handle traditional function tool calls with tool_call_id
    good_calls = sum(1 for tc in tool_calls if "good" in tc.get("tool_call_id", ""))
    bad_calls = sum(1 for tc in tool_calls if "bad" in tc.get("tool_call_id", ""))
    invalid_calls = sum(1 for tc in tool_calls if "invalid" in tc.get("tool_call_id", ""))

    # Handle built-in tool calls - check if tool type matches query intent
    builtin_calls = 0

    for tc in tool_calls:
        tool_type = tc.get("type", "")

        if tool_type == "bing_custom_search":
            builtin_calls += 1
        elif tool_type == "bing_grounding":
            builtin_calls += 1
        elif tool_type == "file_search":
            builtin_calls += 1
        elif tool_type == "azure_ai_search":
            builtin_calls += 1
        elif tool_type == "fabric_dataagent":
            builtin_calls += 1
        elif tool_type == "code_interpreter":
            builtin_calls += 1
        elif tool_type == "sharepoint_grounding":
            builtin_calls += 1
        elif tool_type == "openapi":
            builtin_calls += 1

    total_calls = len(tool_calls)
    total_good_calls = good_calls + builtin_calls

    if invalid_calls > 0:
        # Return a non-numeric score to trigger an exception in the evaluator's check_score_is_valid
        return {
            "chain_of_thought": "The tool calls were very correct that I returned a huge number!",
            "tool_calls_success_level": 25,
            "additional_details": {},
        }

    score = 1  # Default score for "all bad"
    if total_calls > 0:
        if total_good_calls == total_calls:
            score = 5  # All good
        elif total_good_calls > 0:
            score = 3  # Mixed good and bad

    return {
        "chain_of_thought": f"Evaluated {total_calls} tool calls with {total_good_calls} correct calls.",
        "tool_calls_success_level": score,
        "additional_details": {
            "tool_calls_made_by_agent": total_calls,
            "correct_tool_calls_made_by_agent": total_good_calls,
        },
    }


@pytest.mark.usefixtures("mock_model_config")
@pytest.mark.unittest
class TestToolCallAccuracyEvaluator:
    def test_evaluate_tools_valid1(self, mock_model_config):
        evaluator = ToolCallAccuracyEvaluator(model_config=mock_model_config)
        evaluator._flow = MagicMock(side_effect=flow_side_effect)

        # Test evaluation with one good and one bad tool call
        query = "Where is the Eiffel Tower?"
        tool_calls = [
            {
                "type": "tool_call",
                "tool_call_id": "call_good",
                "name": "fetch_weather",
                "arguments": {"location": "Paris"},
            },
            {
                "type": "tool_call",
                "tool_call_id": "call_bad",
                "name": "buy_jacket",
                "arguments": {"type": "raincoat"},
            },
        ]
        tool_definitions = [
            {
                "name": "fetch_weather",
                "type": "function",
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
            },
            {
                "name": "buy_jacket",
                "type": "function",
                "description": "Buy a jacket of the given type.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "type": {
                            "type": "string",
                            "description": "The type of jacket to buy.",
                        }
                    },
                },
            },
        ]
        result = evaluator(query=query, tool_calls=tool_calls, tool_definitions=tool_definitions)

        key = ToolCallAccuracyEvaluator._RESULT_KEY
        assert result is not None
        assert key in result and f"{key}_result" in result and f"{key}_threshold" in result
        assert result[key] == 3.0  # Mixed good/bad gets score 3
        assert result[f"{key}_result"] == "pass"
        assert result[f"{key}_threshold"] == ToolCallAccuracyEvaluator._DEFAULT_TOOL_CALL_ACCURACY_SCORE
        assert f"{key}_reason" in result
        assert result[f"{key}_reason"] == "Evaluated 2 tool calls with 1 correct calls."
        assert "details" in result

    def test_evaluate_tools_valid2(self, mock_model_config):
        evaluator = ToolCallAccuracyEvaluator(model_config=mock_model_config)
        evaluator._flow = MagicMock(side_effect=flow_side_effect)

        # Test evaluation with two bad tool calls
        query = "Where is the Eiffel Tower?"
        tool_calls = [
            {
                "type": "tool_call",
                "tool_call_id": "call_bad",
                "name": "fetch_weather",
                "arguments": {"location": "Tokyo"},
            },
            {
                "type": "tool_call",
                "tool_call_id": "call_bad",
                "name": "buy_jacket",
                "arguments": {"type": "raincoat"},
            },
        ]
        tool_definitions = [
            {
                "name": "fetch_weather",
                "type": "function",
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
            },
            {
                "name": "buy_jacket",
                "type": "function",
                "description": "Buy a jacket of the given type.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "type": {
                            "type": "string",
                            "description": "The type of jacket to buy.",
                        }
                    },
                },
            },
        ]
        result = evaluator(query=query, tool_calls=tool_calls, tool_definitions=tool_definitions)

        key = ToolCallAccuracyEvaluator._RESULT_KEY
        assert result is not None
        assert key in result and f"{key}_result" in result and f"{key}_threshold" in result
        assert result[key] == 1.0  # All bad gets score 1
        assert result[f"{key}_result"] == "fail"
        assert result[f"{key}_threshold"] == ToolCallAccuracyEvaluator._DEFAULT_TOOL_CALL_ACCURACY_SCORE
        assert f"{key}_reason" in result
        assert result[f"{key}_reason"] == "Evaluated 2 tool calls with 0 correct calls."
        assert "details" in result

    def test_evaluate_tools_valid3(self, mock_model_config):
        evaluator = ToolCallAccuracyEvaluator(model_config=mock_model_config)
        evaluator._flow = MagicMock(side_effect=flow_side_effect)

        # Test evaluation with two good tool calls
        query = "Where is the Eiffel Tower?"
        tool_calls = [
            {
                "type": "tool_call",
                "tool_call_id": "call_good",
                "name": "fetch_weather",
                "arguments": {"location": "Paris"},
            },
            {
                "type": "tool_call",
                "tool_call_id": "call_good",
                "name": "buy_jacket",
                "arguments": {"type": "jacket"},
            },
        ]
        tool_definitions = [
            {
                "name": "fetch_weather",
                "type": "function",
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
            },
            {
                "name": "buy_jacket",
                "type": "function",
                "description": "Buy a jacket of the given type.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "type": {
                            "type": "string",
                            "description": "The type of jacket to buy.",
                        }
                    },
                },
            },
        ]
        result = evaluator(query=query, tool_calls=tool_calls, tool_definitions=tool_definitions)

        key = ToolCallAccuracyEvaluator._RESULT_KEY
        assert result is not None
        assert key in result and f"{key}_result" in result and f"{key}_threshold" in result
        assert result[key] == 5.0  # All good gets score 5
        assert result[f"{key}_result"] == "pass"
        assert result[f"{key}_threshold"] == ToolCallAccuracyEvaluator._DEFAULT_TOOL_CALL_ACCURACY_SCORE
        assert f"{key}_reason" in result
        assert result[f"{key}_reason"] == "Evaluated 2 tool calls with 2 correct calls."
        assert "details" in result

    def test_evaluate_tools_one_eval_fails(self, mock_model_config):
        with pytest.raises(EvaluationException) as exc_info:
            evaluator = ToolCallAccuracyEvaluator(model_config=mock_model_config)
            evaluator._flow = MagicMock(side_effect=flow_side_effect)

            # Test evaluation with an invalid tool call ID to trigger failure
            query = "Where is the Eiffel Tower?"
            tool_calls = [
                {
                    "type": "tool_call",
                    "tool_call_id": "call_invalid",
                    "name": "fetch_weather",
                    "arguments": {"location": "Tokyo"},
                },
            ]
            tool_definitions = [
                {
                    "name": "fetch_weather",
                    "type": "function",
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
                },
            ]
            evaluator(query=query, tool_calls=tool_calls, tool_definitions=tool_definitions)

        assert "Invalid score value" in str(exc_info.value)

    def test_evaluate_tools_some_not_applicable(self, mock_model_config):
        evaluator = ToolCallAccuracyEvaluator(model_config=mock_model_config)
        evaluator._flow = MagicMock(side_effect=flow_side_effect)

        # Test with one function tool and one non-function tool
        query = "Where is the Eiffel Tower?"
        tool_calls = [
            {
                "type": "tool_call",
                "tool_call_id": "call_good",
                "name": "fetch_weather",
                "arguments": {"location": "Tokyo"},
            },
            {
                "type": "tool_call",
                "tool_call_id": "call_bad",
                "name": "buy_jacket",
                "arguments": {"type": "raincoat"},
            },
        ]
        tool_definitions = [
            {
                "name": "fetch_weather",
                "type": "function",
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
            },
            {
                "name": "buy_jacket",
                "type": "another_built_in",  # This tool will be filtered out
                "description": "Buy a jacket of the given type.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "type": {
                            "type": "string",
                            "description": "The type of jacket to buy.",
                        }
                    },
                },
            },
        ]
        result = evaluator(query=query, tool_calls=tool_calls, tool_definitions=tool_definitions)

        key = ToolCallAccuracyEvaluator._RESULT_KEY
        assert result is not None
        assert result[key] == ToolCallAccuracyEvaluator._NOT_APPLICABLE_RESULT
        assert result[f"{key}_result"] == "pass"
        assert result[f"{key}_threshold"] == ToolCallAccuracyEvaluator._DEFAULT_TOOL_CALL_ACCURACY_SCORE
        assert result[f"{key}_reason"] == ToolCallAccuracyEvaluator._TOOL_DEFINITIONS_MISSING_MESSAGE
        assert result["details"] == {}

    def test_evaluate_tools_all_not_applicable(self, mock_model_config):
        evaluator = ToolCallAccuracyEvaluator(model_config=mock_model_config)
        evaluator._flow = MagicMock(side_effect=flow_side_effect)

        # Test with only non-function tools
        query = "Where is the Eiffel Tower?"
        tool_calls = [
            {
                "type": "tool_call",
                "tool_call_id": "call_good",
                "name": "fetch_weather",
                "arguments": {"location": "Tokyo"},
            },
        ]
        tool_definitions = [
            {
                "name": "fetch_weather",
                "type": "some_built_in",  # Not a 'function' type
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
            },
        ]
        result = evaluator(query=query, tool_calls=tool_calls, tool_definitions=tool_definitions)

        key = ToolCallAccuracyEvaluator._RESULT_KEY
        assert result is not None
        assert result[key] == ToolCallAccuracyEvaluator._NOT_APPLICABLE_RESULT
        assert result[f"{key}_result"] == "pass"
        assert result[f"{key}_threshold"] == ToolCallAccuracyEvaluator._DEFAULT_TOOL_CALL_ACCURACY_SCORE
        assert result[f"{key}_reason"] == ToolCallAccuracyEvaluator._TOOL_DEFINITIONS_MISSING_MESSAGE
        assert result["details"] == {}

    def test_evaluate_tools_no_tools(self, mock_model_config):
        evaluator = ToolCallAccuracyEvaluator(model_config=mock_model_config)
        evaluator._flow = MagicMock(side_effect=flow_side_effect)

        # Test with no tool calls provided
        query = "Where is the Eiffel Tower?"
        tool_calls = []
        tool_definitions = [
            {
                "name": "fetch_weather",
                "type": "function",
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
            },
        ]
        result = evaluator(query=query, tool_calls=tool_calls, tool_definitions=tool_definitions)

        key = ToolCallAccuracyEvaluator._RESULT_KEY
        assert result is not None
        assert result[key] == ToolCallAccuracyEvaluator._NOT_APPLICABLE_RESULT
        assert result[f"{key}_result"] == "pass"
        assert result[f"{key}_threshold"] == ToolCallAccuracyEvaluator._DEFAULT_TOOL_CALL_ACCURACY_SCORE
        assert result[f"{key}_reason"] == ToolCallAccuracyEvaluator._NO_TOOL_CALLS_MESSAGE
        assert result["details"] == {}

    def test_evaluate_bing_custom_search(self, mock_model_config):
        evaluator = ToolCallAccuracyEvaluator(model_config=mock_model_config)
        evaluator._flow = MagicMock(side_effect=flow_side_effect)

        # Test relevant bing custom search
        query = "Find medical pillows prices on Amazon Egypt"
        tool_calls = [
            {
                "type": "bing_custom_search",
                "bing_custom_search": {
                    "requesturl": "https://api.bing.microsoft.com/v7.0/search?q=medical pillows prices site=amazon.eg"
                },
            },
        ]
        tool_definitions = []
        result = evaluator(query=query, tool_calls=tool_calls, tool_definitions=tool_definitions)

        key = ToolCallAccuracyEvaluator._RESULT_KEY
        assert result is not None
        assert result[key] == 5.0
        assert result[f"{key}_result"] == "pass"

    def test_evaluate_bing_grounding(self, mock_model_config):
        evaluator = ToolCallAccuracyEvaluator(model_config=mock_model_config)
        evaluator._flow = MagicMock(side_effect=flow_side_effect)

        # Test relevant bing grounding for house prices
        query = "What is the average price for a house with a pool in Los Angeles in 2025?"
        tool_calls = [
            {
                "type": "bing_grounding",
                "bing_grounding": {
                    "requesturl": "https://api.bing.microsoft.com/v7.0/search?q=average price for a house with a pool in Los Angeles 2025"
                },
            },
        ]
        tool_definitions = []
        result = evaluator(query=query, tool_calls=tool_calls, tool_definitions=tool_definitions)

        key = ToolCallAccuracyEvaluator._RESULT_KEY
        assert result is not None
        assert result[key] == 5.0
        assert result[f"{key}_result"] == "pass"

    def test_evaluate_file_search(self, mock_model_config):
        evaluator = ToolCallAccuracyEvaluator(model_config=mock_model_config)
        evaluator._flow = MagicMock(side_effect=flow_side_effect)

        # Test file search for credit card statement
        query = "Find information in my credit card statement"
        tool_calls = [
            {
                "type": "file_search",
                "file_search": {
                    "ranking_options": {"ranker": "default_2024_08_21", "score_threshold": 0.0},
                    "results": [{"file_name": "Credit Card Statement.pdf", "score": 0.03333333507180214}],
                },
            },
        ]
        tool_definitions = []
        result = evaluator(query=query, tool_calls=tool_calls, tool_definitions=tool_definitions)

        key = ToolCallAccuracyEvaluator._RESULT_KEY
        assert result is not None
        assert result[key] == 5.0
        assert result[f"{key}_result"] == "pass"

    def test_evaluate_azure_ai_search(self, mock_model_config):
        evaluator = ToolCallAccuracyEvaluator(model_config=mock_model_config)
        evaluator._flow = MagicMock(side_effect=flow_side_effect)

        # Test Azure AI Search for real estate
        query = "Find a 3-bedroom apartment with garage"
        tool_calls = [
            {
                "type": "azure_ai_search",
                "azure_ai_search": {
                    "input": "3-bedroom apartment with garage",
                    "output": "{'summary': 'Retrieved 5 documents.', 'metadata': {'urls': ['doc_0', 'doc_1', 'doc_2', 'doc_3', 'doc_4']}}",
                },
            },
        ]
        tool_definitions = []
        result = evaluator(query=query, tool_calls=tool_calls, tool_definitions=tool_definitions)

        key = ToolCallAccuracyEvaluator._RESULT_KEY
        assert result is not None
        assert result[key] == 5.0
        assert result[f"{key}_result"] == "pass"

    def test_evaluate_fabric_dataagent(self, mock_model_config):
        evaluator = ToolCallAccuracyEvaluator(model_config=mock_model_config)
        evaluator._flow = MagicMock(side_effect=flow_side_effect)

        # Test Fabric Data Agent for financial analysis
        query = "Are there any unusual patterns in financial data?"
        tool_calls = [
            {
                "type": "fabric_dataagent",
                "fabric_dataagent": {
                    "input": "unusual patterns in financial data",
                    "output": "The financial data shows an unusual pattern where the total spending has significantly exceeded the total income in certain months.",
                },
            },
        ]
        tool_definitions = []
        result = evaluator(query=query, tool_calls=tool_calls, tool_definitions=tool_definitions)

        key = ToolCallAccuracyEvaluator._RESULT_KEY
        assert result is not None
        assert result[key] == 5.0
        assert result[f"{key}_result"] == "pass"

    def test_evaluate_code_interpreter(self, mock_model_config):
        evaluator = ToolCallAccuracyEvaluator(model_config=mock_model_config)
        evaluator._flow = MagicMock(side_effect=flow_side_effect)

        # Test code interpreter for statistical analysis
        query = "Find outliers in transaction amounts"
        tool_calls = [
            {
                "type": "code_interpreter",
                "code_interpreter": {
                    "input": "import numpy as np\n\n# Calculate basic statistics\namounts = df['amount']\nmean = amounts.mean()\nstd = amounts.std()\n\n# Define outliers as transactions that are more than 2 standard deviations from the mean\noutlier_mask = (amounts < mean - 2*std) | (amounts > mean + 2*std)\noutliers = df[outlier_mask]\n\noutliers, mean, std",
                    "outputs": [],
                },
            },
        ]
        tool_definitions = []
        result = evaluator(query=query, tool_calls=tool_calls, tool_definitions=tool_definitions)

        key = ToolCallAccuracyEvaluator._RESULT_KEY
        assert result is not None
        assert result[key] == 5.0
        assert result[f"{key}_result"] == "pass"

    def test_evaluate_sharepoint_grounding(self, mock_model_config):
        evaluator = ToolCallAccuracyEvaluator(model_config=mock_model_config)
        evaluator._flow = MagicMock(side_effect=flow_side_effect)

        # Test SharePoint grounding for document search
        query = "Find information about monthly saving rules"
        tool_calls = [
            {
                "type": "sharepoint_grounding",
                "sharepoint_grounding": {"input": "monthly saving rules", "output": "[redacted]"},
            },
        ]
        tool_definitions = []
        result = evaluator(query=query, tool_calls=tool_calls, tool_definitions=tool_definitions)

        key = ToolCallAccuracyEvaluator._RESULT_KEY
        assert result is not None
        assert result[key] == 5.0
        assert result[f"{key}_result"] == "pass"

    def test_evaluate_open_api(self, mock_model_config):
        evaluator = ToolCallAccuracyEvaluator(model_config=mock_model_config)
        evaluator._flow = MagicMock(side_effect=flow_side_effect)

        # Test OpenAPI function call for exchange rates
        query = "What is the exchange rate from GBP to EUR?"
        tool_calls = [
            {
                "type": "openapi",
                "function": {
                    "name": "exchange_rates_getExchangeRates",
                    "arguments": '{"base":"GBP","symbols":"EUR"}',
                    "output": "{'amount': 1.0, 'base': 'GBP', 'date': '2025-07-28', 'rates': {'EUR': 1.1522}}",
                },
            },
        ]
        tool_definitions = []
        result = evaluator(query=query, tool_calls=tool_calls, tool_definitions=tool_definitions)

        key = ToolCallAccuracyEvaluator._RESULT_KEY
        assert result is not None
        assert result[key] == 5.0
        assert result[f"{key}_result"] == "pass"
