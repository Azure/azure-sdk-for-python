# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""
Base class for behavioral tests of evaluators using AIProjectClient.
Tests various input scenarios: query, and response.
"""

import time
from openai.types.evals.create_eval_jsonl_run_data_source_param import (
    CreateEvalJSONLRunDataSourceParam,
    SourceFileContent,
    SourceFileContentContent,
)
from openai.types.eval_create_params import DataSourceConfigCustom


class BaseEvaluatorBehaviorTest:
    """
    Base class for evaluator behavioral tests with query and response inputs.
    Subclasses should implement:
    - evaluator_name: str - name of the evaluator (e.g., "relevance")
    - MINIMAL_RESPONSE: list - minimal valid response format for the evaluator
    """

    # Subclasses must implement
    evaluator_name = None

    # Subclasses may override
    # Test Configs
    requires_valid_format = True
    requires_query = True

    MINIMAL_RESPONSE = [
            {
                "role": "assistant",
                "content": [
                    {
                        "type": "text",
                        "text": "I have successfully sent you an email with the weather information for Seattle. The current weather is rainy with a temperature of 14\u00b0C.",
                    }
                ],
            },
        ]
    
    # Tool-related test data (can be overridden by subclasses)
    VALID_TOOL_CALLS = None
    INVALID_TOOL_CALLS = None
    VALID_TOOL_DEFINITIONS = None
    INVALID_TOOL_DEFINITIONS = None

    # Common test data for query and response
    STRING_QUERY = "Can you send me an email to your_email@example.com with weather information for Seattle?"
    
    STRING_RESPONSE = "I have successfully sent you an email with the weather information for Seattle. The current weather is rainy with a temperature of 14\u00b0C."
    
    VALID_QUERY = [
        {
            "role": "user",
            "content": {
                "type": "text",
                "text": "Can you send me an email to your_email@example.com with weather information for Seattle?",
            }
        },
    ]

    VALID_RESPONSE = [
            {
                "role": "assistant",
                "content": [
                    {
                        "type": "tool_call",
                        "tool_call_id": "call_1",
                        "name": "fetch_weather",
                        "arguments": {"location": "Seattle"},
                    }
                ],
            },
            {
                "tool_call_id": "call_1",
                "role": "tool",
                "content": [{"type": "tool_result", "tool_result": {"weather": "Rainy, 14\u00b0C"}}],
            },
            {
                "role": "assistant",
                "content": [
                    {
                        "type": "tool_call",
                        "tool_call_id": "call_2",
                        "name": "send_email",
                        "arguments": {
                            "recipient": "your_email@example.com",
                            "subject": "Weather Information for Seattle",
                            "body": "The current weather in Seattle is rainy with a temperature of 14\u00b0C.",
                        },
                    }
                ],
            },
            {
                "tool_call_id": "call_2",
                "role": "tool",
                "content": [
                    {
                        "type": "tool_result",
                        "tool_result": {"message": "Email successfully sent to your_email@example.com."},
                    }
                ],
            },
            {
                "role": "assistant",
                "content": [
                    {
                        "type": "text",
                        "text": "I have successfully sent you an email with the weather information for Seattle. The current weather is rainy with a temperature of 14\u00b0C.",
                    }
                ],
            },
        ]

    INVALID_QUERY = [
        {
            "user": "Can you send me an email to your_email@example.com with weather information for Seattle?",
        },
    ]

    INVALID_RESPONSE = [
            {
                "tool_call": [
                    {
                        "name": "fetch_weather",
                        "arguments": {"location": "Seattle"},
                    }
                ],
            },
            {
                "tool_result": {"weather": "Rainy, 14\u00b0C"},
            },
            {
                "tool_call": [
                    {
                        "name": "send_email",
                        "arguments": {
                            "recipient": "your_email@example.com",
                            "subject": "Weather Information for Seattle",
                            "body": "The current weather in Seattle is rainy with a temperature of 14\u00b0C.",
                        },
                    }
                ],
            },
            {
                "tool_result": {"message": "Email successfully sent to your_email@example.com."},
            },
            {
                "assistant": "I have successfully sent you an email with the weather information for Seattle. The current weather is rainy with a temperature of 14\u00b0C.",
            },
        ]
    
    def _run_evaluation(self, evaluator_name, openai_client, model_deployment_name, query, response, tool_calls, tool_definitions):
        """Helper to run evaluation and return results."""
        data_source_config = DataSourceConfigCustom({
            "type": "custom",
            "item_schema": {
                "type": "object",
            },
        })

        testing_criteria = [{
            "type": "azure_ai_evaluator",
            "name": evaluator_name,
            "evaluator_name": f"builtin.{evaluator_name}",
            "initialization_parameters": {"deployment_name": model_deployment_name},
            "data_mapping": {
                "query": "{{item.query}}",
                "response": "{{item.response}}",
                "tool_calls": "{{item.tool_calls}}",
                "tool_definitions": "{{item.tool_definitions}}",
            },
        }]

        eval_obj = openai_client.evals.create(
            name=f"{evaluator_name} Behavioral Test",
            data_source_config=data_source_config,
            testing_criteria=testing_criteria,
        )

        eval_run = openai_client.evals.runs.create(
            eval_id=eval_obj.id,
            name="test_run",
            data_source=CreateEvalJSONLRunDataSourceParam(
                type="jsonl",
                source=SourceFileContent(
                    type="file_content",
                    content=[SourceFileContentContent(item={
                        "query": query,
                        "response": response,
                        "tool_calls": tool_calls,
                        "tool_definitions": tool_definitions,
                    })],
                ),
            ),
        )

        # Wait for completion
        for _ in range(30):  # 60 seconds max
            run = openai_client.evals.runs.retrieve(run_id=eval_run.id, eval_id=eval_obj.id)
            if run.status in ["completed", "failed"]:
                outputs = list(openai_client.evals.runs.output_items.list(run_id=run.id, eval_id=eval_obj.id))
                return run, outputs
            time.sleep(2)
        
        raise TimeoutError("Evaluation did not complete")

    def _extract_and_print_result(self, run, outputs, test_label):
        """Helper to extract result fields and print them."""
        result = outputs[0].results[0]
        label = result.model_extra.get("label")
        reason = result.model_extra.get("reason")
        is_passed = result.passed
        score = result.score
        error = result.sample.get("error", {}) if result.sample else {}
        error_message = error.get("message")
        error_code = error.get("code")
        status = run.status

        print(f"\n[{test_label}] Status: {status}")
        print(f"  Result: {label}")
        print(f"  Score: {score}")
        print(f"  Reason: {reason}")
        if error_message or error_code:
            print(f"  Error Message: {error_message}")
            print(f"  Error Code: {error_code}")

        return {
            "status": status,
            "label": label,
            "reason": reason,
            "is_passed": is_passed,
            "score": score,
            "error_message": error_message,
            "error_code": error_code,
        }

    def assert_pass(self, result_data):
        """Helper to assert a passing result."""
        assert result_data["status"] == "completed"
        assert result_data["label"] == "pass"
        assert result_data["is_passed"] is True
        assert type(result_data["score"]) is float
        assert result_data["score"] >= 1.0
    
    def assert_fail(self, result_data):
        """Helper to assert a failing result."""
        assert result_data["status"] == "completed"
        assert result_data["label"] == "fail"
        assert result_data["is_passed"] is False
        assert type(result_data["score"]) is float
        assert result_data["score"] == 0.0

    def assert_pass_or_fail(self, result_data):
        """Helper to assert a pass or fail result."""
        assert result_data["status"] == "completed"
        assert result_data["label"] in ["pass", "fail"]
        assert result_data["is_passed"] in [True, False]
        assert type(result_data["score"]) is float
        assert result_data["score"] >= 0.0
    
    def assert_error(self, result_data, error_code="FAILED_EXECUTION"):
        """Helper to assert an error result."""
        assert result_data["status"] == "completed"
        assert result_data["label"] is None
        assert result_data["is_passed"] is None
        assert result_data["score"] is None
        assert result_data["error_code"] == error_code

    def assert_not_applicable(self, result_data):
        """Helper to assert a not applicable result."""
        assert result_data["status"] == "completed"
        assert result_data["label"] == "pass"  # TODO: this should be not applicable?
        assert result_data["is_passed"] == True  # TODO: this should be false?
        assert result_data["score"] == "not applicable"

    # ==================== All Valid ====================

    def test_all_valid_inputs(self, openai_client, model_deployment_name):
        """All inputs valid and in correct format."""
        run, outputs = self._run_evaluation(
            self.evaluator_name,
            openai_client, model_deployment_name,
            query=self.VALID_QUERY,
            response=self.VALID_RESPONSE,
            tool_calls=self.VALID_TOOL_CALLS,
            tool_definitions=self.VALID_TOOL_DEFINITIONS,
        )
        result_data = self._extract_and_print_result(run, outputs, "All Valid")

        self.assert_pass(result_data)

    # ==================== QUERY TESTS ====================

    def test_query_not_present(self, openai_client, model_deployment_name):
        """Query not present - evaluator raises exception."""
        run, outputs = self._run_evaluation(
            self.evaluator_name,
            openai_client, model_deployment_name,
            query=None,
            response=self.VALID_RESPONSE,
            tool_calls=self.VALID_TOOL_CALLS,
            tool_definitions=self.VALID_TOOL_DEFINITIONS,
        )
        result_data = self._extract_and_print_result(run, outputs, "Query Not Present")

        if self.requires_query:
            # TODO: This should be not applicable instead of raising exception
            self.assert_error(result_data)
        else:
            self.assert_pass(result_data)

    def test_query_as_string(self, openai_client, model_deployment_name):
        """Query as string - should pass."""
        run, outputs = self._run_evaluation(
            self.evaluator_name,
            openai_client, model_deployment_name,
            query=self.STRING_QUERY,
            response=self.VALID_RESPONSE,
            tool_calls=self.VALID_TOOL_CALLS,
            tool_definitions=self.VALID_TOOL_DEFINITIONS,
        )
        result_data = self._extract_and_print_result(run, outputs, "Query String")

        self.assert_pass(result_data)

    def test_query_invalid_format(self, openai_client, model_deployment_name):
        """Query in invalid format - should pass."""
        run, outputs = self._run_evaluation(
            self.evaluator_name,
            openai_client, model_deployment_name,
            query=self.INVALID_QUERY,
            response=self.VALID_RESPONSE,
            tool_calls=self.VALID_TOOL_CALLS,
            tool_definitions=self.VALID_TOOL_DEFINITIONS,
        )
        result_data = self._extract_and_print_result(run, outputs, "Query Invalid")

        self.assert_pass(result_data)

    # ==================== RESPONSE TESTS ====================

    def test_response_not_present(self, openai_client, model_deployment_name):
        """Response not present - should return not applicable."""
        run, outputs = self._run_evaluation(
            self.evaluator_name,
            openai_client, model_deployment_name,
            query=self.VALID_QUERY,
            response=None,
            tool_calls=self.VALID_TOOL_CALLS,
            tool_definitions=self.VALID_TOOL_DEFINITIONS,
        )
        result_data = self._extract_and_print_result(run, outputs, "Response Not Present")

        self.assert_not_applicable(result_data)

    def test_response_as_string(self, openai_client, model_deployment_name):
        """Response as string - should pass."""
        run, outputs = self._run_evaluation(
            self.evaluator_name,
            openai_client, model_deployment_name,
            query=self.VALID_QUERY,
            response=self.STRING_RESPONSE,
            tool_calls=self.VALID_TOOL_CALLS,
            tool_definitions=self.VALID_TOOL_DEFINITIONS,
        )
        result_data = self._extract_and_print_result(run, outputs, "Response String")

        self.assert_pass(result_data)

    def test_response_invalid_format(self, openai_client, model_deployment_name):
        """Response in invalid format - should return not_applicable."""
        run, outputs = self._run_evaluation(
            self.evaluator_name,
            openai_client, model_deployment_name,
            query=self.VALID_QUERY,
            response=self.INVALID_RESPONSE,
            tool_calls=self.VALID_TOOL_CALLS,
            tool_definitions=self.VALID_TOOL_DEFINITIONS,
        )
        result_data = self._extract_and_print_result(run, outputs, "Response Invalid")

        if self.requires_valid_format:
            self.assert_not_applicable(result_data)
        else:
            self.assert_pass(result_data)
    
    def test_response_minimal_format(self, openai_client, model_deployment_name):
        """Response in minimal format - should pass."""
        run, outputs = self._run_evaluation(
            self.evaluator_name,
            openai_client, model_deployment_name,
            query=self.VALID_QUERY,
            response=self.MINIMAL_RESPONSE,
            tool_calls=self.VALID_TOOL_CALLS,
            tool_definitions=self.VALID_TOOL_DEFINITIONS,
        )
        result_data = self._extract_and_print_result(run, outputs, "Response Minimal")

        self.assert_pass(result_data)
