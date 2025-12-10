# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""
Base class for behavioral tests of evaluators using AIProjectClient.
Runs evaluations for testing.
"""

from typing import Any, Dict, List, Tuple
import time
from openai.types.evals.create_eval_jsonl_run_data_source_param import (
    CreateEvalJSONLRunDataSourceParam,
    SourceFileContent,
    SourceFileContentContent,
)
from openai.types.eval_create_params import DataSourceConfigCustom
from azure.ai.projects import AIProjectClient
from openai import OpenAI
from openai.types.evals.run_retrieve_response import RunRetrieveResponse
from openai.types.evals.runs.output_item_list_response import OutputItemListResponse


class BaseEvaluatorRunner:
    """
    Base class for running evaluators for testing.
    Subclasses should implement:
    - evaluator_name: str - name of the evaluator (e.g., "relevance")
    """

    # Subclasses must implement
    evaluator_name: str = None

    def _run_evaluation(self, evaluator_name: str, openai_client: OpenAI, model_deployment_name: str, query: List[Dict[str, Any]], response: List[Dict[str, Any]], tool_calls: List[Dict[str, Any]], tool_definitions: List[Dict[str, Any]]) -> Tuple[RunRetrieveResponse, List[OutputItemListResponse]]:
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

    def _extract_and_print_result(self, run: RunRetrieveResponse, outputs: List[OutputItemListResponse], test_label: str) -> Dict[str, Any]:
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

    def assert_pass(self, result_data: Dict[str, Any]):
        """Helper to assert a passing result."""
        assert result_data["status"] == "completed"
        assert result_data["label"] == "pass"
        assert result_data["is_passed"] is True
        assert type(result_data["score"]) is float
        assert result_data["score"] >= 1.0
    
    def assert_fail(self, result_data: Dict[str, Any]):
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
    
    def assert_error(self, result_data: Dict[str, Any], error_code: str="FAILED_EXECUTION"):
        """Helper to assert an error result."""
        assert result_data["status"] == "completed"
        assert result_data["label"] is None
        assert result_data["is_passed"] is None
        assert result_data["score"] is None
        assert result_data["error_code"] == error_code

    def assert_not_applicable(self, result_data: Dict[str, Any]):
        """Helper to assert a not applicable result."""
        assert result_data["status"] == "completed"
        assert result_data["label"] == "pass"  # TODO: this should be not applicable?
        assert result_data["is_passed"] == True  # TODO: this should be false?
        assert result_data["score"] == "not applicable"
