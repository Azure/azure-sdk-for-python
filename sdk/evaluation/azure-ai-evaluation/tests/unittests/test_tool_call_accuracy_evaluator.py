from unittest.mock import MagicMock

import pytest
from azure.ai.evaluation import ToolCallAccuracyEvaluator
from azure.ai.evaluation._exceptions import EvaluationException


# This mock should return a dictionary that mimics the output of the prompty (the _flow call),
# which is then processed by the _do_eval method.
async def flow_side_effect(timeout, **kwargs):
    tool_calls = kwargs.get("tool_calls", [])
    query = kwargs.get("query", "")

    # Handle built-in tool calls first - count them as relevant
    builtin_calls = 0
    custom_function_calls = []

    for tc in tool_calls:
        tool_type = tc.get("type", "")
        tool_name = tc.get("name", "")

        # Only support converter format: {type: "tool_call", name: "tool_name", arguments: {...}}
        if tool_type == "tool_call":
            if tool_name in [
                "bing_custom_search",
                "bing_grounding",
                "file_search",
                "azure_ai_search",
                "fabric_dataagent",
                "code_interpreter",
                "sharepoint_grounding",
                "openapi",
            ]:
                builtin_calls += 1
            else:
                # custom function tool call
                custom_function_calls.append(tc)

    # Handle traditional function tool calls with tool_call_id only for non-built-in tools
    good_calls = sum(1 for tc in custom_function_calls if "good" in tc.get("tool_call_id", ""))
    bad_calls = sum(1 for tc in custom_function_calls if "bad" in tc.get("tool_call_id", ""))
    invalid_calls = sum(1 for tc in custom_function_calls if "invalid" in tc.get("tool_call_id", ""))

    total_calls = len(tool_calls)
    total_good_calls = good_calls + builtin_calls

    if invalid_calls > 0:
        # Return a non-numeric score to trigger an exception in the evaluator's check_score_is_valid
        return {
            "llm_output": {
                "chain_of_thought": "The tool calls were very correct that I returned a huge number!",
                "tool_calls_success_level": 25,
                "details": {},
            }
        }

    score = 1  # Default score for "all bad"
    if total_calls > 0:
        if total_good_calls == total_calls:
            score = 5  # All good
        elif total_good_calls > 0:
            score = 3  # Mixed good and bad

    return {
        "llm_output": {
            "chain_of_thought": f"Evaluated {total_calls} tool calls with {total_good_calls} correct calls.",
            "tool_calls_success_level": score,
            "details": {
                "tool_calls_made_by_agent": total_calls,
                "correct_tool_calls_made_by_agent": total_good_calls,
            },
        }
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
        assert f"{key}_details" in result

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
        assert f"{key}_details" in result

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
        assert f"{key}_details" in result

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
        assert result[f"{key}_details"] == {}

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
        assert result[f"{key}_details"] == {}

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
        assert result[f"{key}_details"] == {}

    def test_evaluate_bing_custom_search(self, mock_model_config):
        evaluator = ToolCallAccuracyEvaluator(model_config=mock_model_config)
        evaluator._flow = MagicMock(side_effect=flow_side_effect)

        # Test relevant bing custom search - converter format
        query = "Find medical pillows prices on Amazon Egypt"
        tool_calls = [
            {
                "type": "tool_call",
                "tool_call_id": "call_builtin_good",
                "name": "bing_custom_search",
                "arguments": {
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

        # Test relevant bing grounding for house prices - converter format
        query = "What is the average price for a house with a pool in Los Angeles in 2025?"
        tool_calls = [
            {
                "type": "tool_call",
                "tool_call_id": "call_builtin_good",
                "name": "bing_grounding",
                "arguments": {
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

        # Test file search for credit card statement - converter format
        query = "Find information in my credit card statement"
        tool_calls = [
            {
                "type": "tool_call",
                "tool_call_id": "call_builtin_good",
                "name": "file_search",
                "arguments": {"ranking_options": {"ranker": "default_2024_08_21", "score_threshold": 0.0}},
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

        # Test Azure AI Search for real estate - converter format
        query = "Find a 3-bedroom apartment with garage"
        tool_calls = [
            {
                "type": "tool_call",
                "tool_call_id": "call_builtin_good",
                "name": "azure_ai_search",
                "arguments": {"input": "3-bedroom apartment with garage"},
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

        # Test Fabric Data Agent for financial analysis - converter format
        query = "Are there any unusual patterns in financial data?"
        tool_calls = [
            {
                "type": "tool_call",
                "tool_call_id": "call_builtin_good",
                "name": "fabric_dataagent",
                "arguments": {"input": "unusual patterns in financial data"},
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

        # Test code interpreter for statistical analysis - converter format
        query = "Find outliers in transaction amounts"
        tool_calls = [
            {
                "type": "tool_call",
                "tool_call_id": "call_builtin_good",
                "name": "code_interpreter",
                "arguments": {
                    "input": "import numpy as np\n\n# Calculate basic statistics\namounts = df['amount']\nmean = amounts.mean()\nstd = amounts.std()\n\n# Define outliers as transactions that are more than 2 standard deviations from the mean\noutlier_mask = (amounts < mean - 2*std) | (amounts > mean + 2*std)\noutliers = df[outlier_mask]\n\noutliers, mean, std"
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

        # Test SharePoint grounding for document search - converter format
        query = "Find information about monthly saving rules"
        tool_calls = [
            {
                "type": "tool_call",
                "tool_call_id": "call_builtin_good",
                "name": "sharepoint_grounding",
                "arguments": {"input": "monthly saving rules"},
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

        # Test OpenAPI function call for exchange rates - converter format
        query = "What is the exchange rate from GBP to EUR?"
        tool_calls = [
            {
                "type": "tool_call",
                "tool_call_id": "call_builtin_good",
                "name": "openapi",
                "arguments": {"name": "exchange_rates_getExchangeRates", "arguments": '{"base":"GBP","symbols":"EUR"}'},
            },
        ]
        tool_definitions = []
        result = evaluator(query=query, tool_calls=tool_calls, tool_definitions=tool_definitions)

        key = ToolCallAccuracyEvaluator._RESULT_KEY
        assert result is not None
        assert result[key] == "not applicable"
        assert result[f"{key}_result"] == "pass"

    def test_evaluate_open_api_with_tool_definition(self, mock_model_config):
        evaluator = ToolCallAccuracyEvaluator(model_config=mock_model_config)
        evaluator._flow = MagicMock(side_effect=flow_side_effect)

        # Test OpenAPI function call for exchange rates - converter format
        query = "What is the exchange rate from GBP to EUR?"
        tool_calls = [
            {
                "type": "tool_call",
                "tool_call_id": "call_builtin_good",
                "name": "get_countries_LookupCountryByCurrency",
                "arguments": {"currency": "GBP"},
            },
        ]
        tool_definitions = [
            {
                "name": "get_countries",
                "type": "openapi",
                "description": "Retrieve a list of countries",
                "spec": {
                    "openapi": "3.1.0",
                    "info": {
                        "title": "RestCountries.NET API",
                        "description": "Web API version 3.1 for managing country items, based on previous implementations from restcountries.eu and restcountries.com.",
                        "version": "v3.1",
                    },
                    "servers": [{"url": "https://restcountries.net"}],
                    "auth": [],
                    "paths": {
                        "/v3.1/currency": {
                            "get": {
                                "description": "Search by currency.",
                                "operationId": "LookupCountryByCurrency",
                                "parameters": [
                                    {
                                        "name": "currency",
                                        "in": "query",
                                        "description": "The currency to search for.",
                                        "required": "true",
                                        "schema": {"type": "string"},
                                    }
                                ],
                                "responses": {
                                    "200": {
                                        "description": "Success",
                                        "content": {"text/plain": {"schema": {"type": "string"}}},
                                    }
                                },
                            }
                        }
                    },
                    "components": {"schemes": {}},
                },
                "auth": {"type": "anonymous", "security_scheme": {}},
                "functions": [
                    {
                        "name": "get_countries_LookupCountryByCurrency",
                        "type": "function",
                        "description": "Search by currency.",
                        "parameters": {
                            "type": "object",
                            "properties": {
                                "currency": {"type": "string", "description": "The currency to search for."}
                            },
                            "required": ["currency"],
                        },
                    }
                ],
            }
        ]
        result = evaluator(query=query, tool_calls=tool_calls, tool_definitions=tool_definitions)

        key = ToolCallAccuracyEvaluator._RESULT_KEY
        assert result is not None
        assert result[key] == 5.0
        assert result[f"{key}_result"] == "pass"

    def test_evaluate_missing_query(self, mock_model_config):
        """Test that evaluator raises exception when query is None or missing."""
        evaluator = ToolCallAccuracyEvaluator(model_config=mock_model_config)
        evaluator._flow = MagicMock(side_effect=flow_side_effect)

        tool_calls = [
            {
                "type": "tool_call",
                "tool_call_id": "call_good",
                "name": "get_weather",
                "arguments": {"location": "Paris"},
            }
        ]
        tool_definitions = [
            {
                "name": "get_weather",
                "type": "function",
                "description": "Get weather information",
                "parameters": {
                    "type": "object",
                    "properties": {"location": {"type": "string", "description": "The location"}},
                    "required": ["location"],
                },
            }
        ]

        # Test with query=None
        with pytest.raises(EvaluationException) as exc_info:
            evaluator(query=None, tool_calls=tool_calls, tool_definitions=tool_definitions)

        assert "Query is a required input" in str(exc_info.value)

        # Test with query not provided at all
        with pytest.raises(EvaluationException) as exc_info:
            evaluator(tool_calls=tool_calls, tool_definitions=tool_definitions)

        assert "Query is a required input" in str(exc_info.value)
