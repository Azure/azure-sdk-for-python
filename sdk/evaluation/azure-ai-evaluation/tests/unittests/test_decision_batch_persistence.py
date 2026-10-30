# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

"""Decision failure metadata through the actual batch summary and row conversion."""

import asyncio
import json
import logging

import pandas as pd
import pytest
from azure.core.pipeline.transport import AsyncHttpTransport, HttpResponse

from azure.ai.evaluation import F1ScoreEvaluator
from azure.ai.evaluation._evaluate._batch_run import RunSubmitterClient
from azure.ai.evaluation._evaluate._batch_run._run_submitter_client import _decision_error_metadata
from azure.ai.evaluation._evaluate._evaluate import (
    _calculate_aoai_evaluation_summary,
    _convert_single_row_to_aoai_format,
    _extract_testing_criteria_metadata,
)
from azure.ai.evaluation._evaluators._common._base_model_eval import ModelEvaluatorBase
from azure.ai.evaluation._evaluators._common._decision_strategy import BinaryScoring, DecisionEvaluationStrategy
from azure.ai.evaluation._evaluators._common._model_runners import DecisionModelRunner
from azure.ai.evaluation._evaluators._common import _model_runners
from azure.ai.evaluation._exceptions import ErrorBlame, ErrorCategory, ErrorTarget, EvaluationException
from azure.ai.evaluation._http_utils import AsyncHttpPipeline

pytestmark = pytest.mark.unittest

CONFIG = {
    "type": "decision",
    "azure_endpoint": "https://example.services.ai.azure.com",
    "azure_deployment": "Decision-1",
    "api_key": "test-key-not-for-persistence",
}
QUESTIONS = {
    "status": {"type": "noul", "instructions": "Applicable?"},
    "task_completion": {"type": "noul", "instructions": "Completed?"},
}
CRITERIA = {
    "judge": {"metrics": ["task_completion"], "type": "azure_ai_evaluator"},
    "f1": {"metrics": ["f1_score"], "type": "azure_ai_evaluator"},
}


def payload(status=0.9):
    return {
        "model": "decision-native",
        "answers": {"status": {"type": "noul", "noul": status}, "task_completion": {"type": "noul", "noul": 0.9}},
        "usage": {"input_tokens": 120, "output_tokens": 3},
    }


@pytest.fixture
def batch_client():
    client = RunSubmitterClient()
    try:
        yield client
    finally:
        client._thread_pool.shutdown(wait=True)


def convert_batch(client, judge, tmp_path, rows=1, criteria=None):
    data = pd.DataFrame([{"query": "synthetic", "response": "synthetic", "ground_truth": "synthetic"}] * rows)
    judge_run = client.run(judge, data, evaluator_name="judge", column_mapping={"query": "${data.query}"})
    f1_run = client.run(
        F1ScoreEvaluator(),
        data,
        evaluator_name="f1",
        column_mapping={"response": "${data.response}", "ground_truth": "${data.ground_truth}"},
    )
    judge_details = client.get_details(judge_run, all_results=True)
    f1_details = client.get_details(f1_run, all_results=True)
    summaries = {"judge": client.get_run_summary(judge_run), "f1": client.get_run_summary(f1_run)}
    converted = []
    for index in range(rows):
        row = {}
        for name, details in (("judge", judge_details), ("f1", f1_details)):
            for key, value in details.to_dict(orient="records")[index].items():
                row[key.replace("outputs.", f"outputs.{name}.", 1)] = value
        converted.append(
            _convert_single_row_to_aoai_format(
                row, index, None, None, 0, criteria or CRITERIA, summaries, logging.getLogger("test")
            )
        )
    path = tmp_path / "persisted.json"
    path.write_text(json.dumps(converted, allow_nan=False), encoding="utf-8")
    persisted = json.loads(path.read_text(encoding="utf-8"))
    for row in persisted:
        f1 = next(result for result in row["results"] if result["name"] == "f1")
        assert f1["score"] == 1 and f1["status"] == "completed"
        assert "error" not in (f1.get("sample") or {})
    return summaries, persisted


def strategy(runner):
    return DecisionEvaluationStrategy(
        runner,
        result_key="task_completion",
        error_target=ErrorTarget.EVALUATE,
        questions=QUESTIONS,
        scoring=BinaryScoring(0.75),
        threshold=1,
        timeout=2,
    )


class TestDecisionBatchPersistence:
    EXECUTION = {
        "operation_id": "a" * 32,
        "attempt_count": 1,
        "unknown_usage_attempt_count": 0,
        "result_usage_scope": "final_response_only",
        "usage_completeness": "all_attempts_reported",
    }

    @pytest.mark.parametrize("field", ["status_completion_probability", "status_probability_threshold"])
    @pytest.mark.parametrize(
        "value",
        [
            pytest.param(10**309, id="oversized_positive"),
            pytest.param(-(10**309), id="oversized_negative"),
            pytest.param(float("nan"), id="nan"),
            pytest.param(float("inf"), id="infinity"),
            pytest.param(True, id="boolean"),
            pytest.param("0.5", id="string"),
        ],
    )
    def test_invalid_failure_probability_preserves_batch_error_and_usage(self, batch_client, tmp_path, field, value):
        error = EvaluationException(
            "original custom evaluator failure",
            blame=ErrorBlame.USER_ERROR,
            category=ErrorCategory.FAILED_EXECUTION,
            target=ErrorTarget.EVALUATE,
            properties={
                "prompt_tokens": 41,
                "completion_tokens": 3,
                "total_tokens": 44,
                "model": "custom-judge",
                "decision_model": {"deployment": "Decision-1", field: value, "usage_available": True},
            },
        )

        async def judge(query):
            raise error

        summaries, rows = convert_batch(batch_client, judge, tmp_path)
        metric = next(item for item in rows[0]["results"] if item["name"] == "judge")
        assert summaries["judge"]["failed_lines"] == 1
        assert metric["status"] == "error" and metric["score"] is None and metric["passed"] is None
        assert metric["sample"]["error"]["code"] == "FAILED_EXECUTION"
        assert metric["sample"]["error"]["blame"] == "UserError"
        assert metric["sample"]["usage"] == {"prompt_tokens": 41, "completion_tokens": 3, "total_tokens": 44}
        assert metric["sample"]["model"] == "custom-judge"
        assert field not in metric["properties"]["decision_model"]
        assert error.properties["decision_model"][field] is value

    @pytest.mark.parametrize(
        "backend,known,attempted",
        [("system_one", False, False), ("foundry_decision", False, True), ("system_one", True, True)],
    )
    def test_independent_failed_metadata_preserves_distinct_scopes_and_known_fields(self, backend, known, attempted):
        expected = {
            "backend": backend,
            "protocol": "system_one",
            "usage_available": known,
            "result_usage_scope": "reported_attempts_only",
        }
        if attempted:
            expected["execution"] = {
                **self.EXECUTION,
                "unknown_usage_attempt_count": int(not known),
                "usage_completeness": "all_attempts_reported" if known else "no_attempts_reported",
            }
        usage = dict(prompt_tokens=41, completion_tokens=3, total_tokens=44, model="independent-model") if known else {}
        error = EvaluationException(
            "synthetic failure",
            properties={
                **usage,
                "decision_model": {**expected, "private": "never-persist"},
                "private": "never-persist",
            },
        )
        assert _decision_error_metadata(error)["properties"] == {**usage, "decision_model": expected}

    @pytest.mark.parametrize(
        "changes",
        [
            {"operation_id": "A" * 32},
            {"operation_id": "a" * 31},
            {"operation_id": 42},
            {"attempt_count": True},
            {"attempt_count": -1},
            {"unknown_usage_attempt_count": True},
            {"unknown_usage_attempt_count": -1},
            {"result_usage_scope": "reported_attempts_only"},
            {"usage_completeness": "unknown"},
            {"extra": "private"},
        ],
    )
    def test_malformed_independent_summary_is_dropped_not_rewritten(self, changes):
        error = EvaluationException(
            "synthetic failure",
            properties={"decision_model": {"execution": {**self.EXECUTION, **changes}, "usage_available": False}},
        )
        assert _decision_error_metadata(error)["properties"]["decision_model"] == {"usage_available": False}

    def test_failed_metadata_rejects_untyped_and_unrecognized_provenance(self):
        error = EvaluationException(
            "synthetic failure",
            properties={
                "decision_model": {
                    "backend": "private",
                    "protocol": ["system_one"],
                    "usage_available": 1,
                    "result_usage_scope": True,
                    "execution": "private",
                }
            },
        )
        assert _decision_error_metadata(error)["properties"] == {"decision_model": {}}

    @pytest.mark.parametrize("members", [5, 6])
    @pytest.mark.parametrize("case", ["completed", "skipped", "mixed", "semantic_error"])
    @pytest.mark.parametrize("primary_first", [False, True])
    @pytest.mark.parametrize("metadata_source", ["manual", "sdk_instance", "sdk_builtin"])
    def test_shared_composite_request_is_counted_once_for_all_parsed_members(
        self, batch_client, tmp_path, monkeypatch, members, case, primary_first, metadata_source
    ):
        calls = []
        keys = [f"member_{index}" for index in range(members)]
        root = "overall"
        if metadata_source != "manual":
            if members == 6:
                root = "output_quality"
                keys = [
                    "fluency",
                    "coherence",
                    "intent_resolution",
                    "task_adherence",
                    "groundedness",
                    "task_completion",
                ]
            else:
                root = "tool_use_quality"
                keys = [
                    "tool_call_accuracy",
                    "tool_call_success",
                    "tool_input_accuracy",
                    "tool_output_utilization",
                    "tool_selection",
                ]
        questions = {
            key: {"type": "noul", "instructions": key} for member in keys for key in (member, f"{member}_status")
        }
        answers = {}
        for index, key in enumerate(keys):
            status = 0.1 if case == "skipped" or (case == "mixed" and index == 0) else 0.9
            score = (
                float("nan")
                if case == "semantic_error" and index == members - 1
                else 0.1 if case == "mixed" and index == members - 1 else 0.9
            )
            answers[key] = {"type": "noul", "noul": score}
            answers[f"{key}_status"] = {"type": "noul", "noul": status}

        class Response(HttpResponse):
            def __init__(self, request):
                super().__init__(request, None)
                self.status_code = 200
                self.headers = {}

            def body(self):
                return json.dumps(
                    {
                        "model": "decision-native",
                        "answers": answers,
                        "usage": {
                            "input_tokens": 120,
                            "output_tokens": 3,
                        },
                    }
                ).encode()

        class Transport(AsyncHttpTransport):
            async def open(self):
                pass

            async def close(self):
                pass

            async def __aexit__(self, *_):
                await self.close()

            async def send(self, request, **kwargs):
                calls.append(json.loads(request.body))
                return Response(request)

        monkeypatch.setattr(
            _model_runners, "get_async_http_client", lambda **_: AsyncHttpPipeline(transport=Transport())
        )

        async def judge(query, runner=None):
            if runner is None:
                runner = DecisionModelRunner(CONFIG, max_retries=0)
            shared = await runner(state={"query": query}, questions=questions, timeout=2)
            result = {}
            for key in keys:
                member_strategy = DecisionEvaluationStrategy(
                    runner,
                    result_key=key,
                    error_target=ErrorTarget.EVALUATE,
                    questions={"status": questions[f"{key}_status"], key: questions[key]},
                    scoring=BinaryScoring(0.75),
                    threshold=1,
                    timeout=2,
                )
                member_response = {
                    **shared,
                    "answers": {
                        "status": shared["answers"][f"{key}_status"],
                        key: shared["answers"][key],
                    },
                }
                result.update(member_strategy.parse(member_response, {"query": query}))
            result.update(
                {
                    root: None if case == "skipped" else float(case == "completed"),
                    f"{root}_status": "skipped" if case == "skipped" else "completed",
                    f"{root}_passed": None if case == "skipped" else case == "completed",
                    f"{root}_result": (
                        "not_applicable" if case == "skipped" else "pass" if case == "completed" else "fail"
                    ),
                    f"{root}_prompt_tokens": 120,
                    f"{root}_completion_tokens": 3,
                    f"{root}_total_tokens": 123,
                    f"{root}_model": shared["model"],
                }
            )
            return result

        criteria = {
            **CRITERIA,
            "judge": {
                "metrics": [root, *keys] if primary_first else [*keys, root],
                "type": "azure_ai_evaluator",
                "evaluator_name": f"builtin.{root}",
            },
        }
        evaluator = judge
        if metadata_source != "manual":

            class OutputQualityEvaluator(ModelEvaluatorBase):
                _supports_decision_models = True
                _binary_decision = True

                def __call__(self, *, query):
                    return super().__call__(query=query)

                async def _do_eval(self, eval_input):
                    return await judge(eval_input["query"], self._decision_model_runner)

            class ToolUseQualityEvaluator(OutputQualityEvaluator):
                pass

            evaluator_class = OutputQualityEvaluator if members == 6 else ToolUseQualityEvaluator
            evaluator = evaluator_class(result_key=root, model_config=CONFIG, threshold=1, max_retries=0)
            metadata = None
            if metadata_source == "sdk_builtin":
                metadata = {
                    "testing_criteria": [
                        {"name": "judge", "type": "azure_ai_evaluator", "evaluator_name": f"builtin.{root}"}
                    ]
                }
            criteria = _extract_testing_criteria_metadata(
                {"judge": evaluator, "f1": F1ScoreEvaluator()}, metadata, None, logging.getLogger("test"), None, None
            )
            assert criteria["judge"]["metrics"] == [root, *keys]
            assert criteria["judge"]["evaluator_name"] == (root if metadata is None else f"builtin.{root}")
            assert criteria["judge"]["is_inverse"] is False
            if not primary_first:
                criteria["judge"]["metrics"] = [*keys, root]
        _, rows = convert_batch(batch_client, evaluator, tmp_path, criteria=criteria)
        assert len(calls) == 1 and len(calls[0]["questions"]) == members * 2
        assert {result["metric"] for result in rows[0]["results"] if result["name"] == "judge"} == {root, *keys}
        for result in rows[0]["results"]:
            if case == "semantic_error" and result["name"] == "judge":
                assert result["status"] == "error" and result["score"] is None and result["passed"] is None
                assert result["sample"]["error"]["blame"] == "SystemError"
                assert result["properties"]["total_tokens"] == 123
                assert "native_answer" not in result["properties"]["decision_model"]
            elif result["metric"] in keys:
                assert "usage" not in (result.get("sample") or {})
                assert result["properties"]["total_tokens"] == 123
                assert len(result["properties"]["decision_model"]["rubric_hash"]) == 64
                if case == "skipped":
                    assert result["status"] == "skipped" and result["score"] is None and result["passed"] is None
        assert sum("usage" in (result.get("sample") or {}) for result in rows[0]["results"]) == 1
        overall = next(result for result in rows[0]["results"] if result["metric"] == root)
        assert overall["sample"]["usage"]["total_tokens"] == 123
        rollup = _calculate_aoai_evaluation_summary(rows, logging.getLogger("test"), criteria)
        if metadata_source != "manual":
            criteria_rollup = next(
                item for item in rollup["per_testing_criteria_results"] if item["testing_criteria"] == "judge"
            )
            expected = {"passed": 0, "failed": 0, "skipped": 0, "errored": 0}
            expected[
                {"completed": "passed", "mixed": "failed", "skipped": "skipped", "semantic_error": "errored"}[case]
            ] = 1
            assert criteria_rollup == {"testing_criteria": "judge", **expected}
        assert rollup["per_model_usage"] == [
            {
                "model_name": "decision-native",
                "invocation_count": 1,
                "prompt_tokens": 120,
                "completion_tokens": 3,
                "total_tokens": 123,
                "cached_tokens": 0,
            }
        ]

    @pytest.mark.parametrize(
        "status", [float("nan"), float("inf"), "bad", pytest.param(10**309, id="oversized_integer")]
    )
    def test_semantic_failure_retains_measured_usage_and_hashes(self, batch_client, tmp_path, status):
        class Runner:
            deployment = "Decision-1"
            decision_protocol = "microsoft"

            async def __call__(self, **kwargs):
                return payload(status)

        async def judge(query):
            return await strategy(Runner()).evaluate({"query": query})

        summary, rows = convert_batch(batch_client, judge, tmp_path)
        result = next(item for item in rows[0]["results"] if item["name"] == "judge")
        assert result["status"] == "error" and result["score"] is None and result["passed"] is None
        assert result["sample"]["error"]["blame"] == "SystemError"
        assert result["sample"]["error"]["code"] == "FAILED_EXECUTION"
        assert result["sample"]["usage"] == {"prompt_tokens": 120, "completion_tokens": 3, "total_tokens": 123}
        assert result["sample"]["model"] == "decision-native"
        assert result["properties"]["total_tokens"] == 123
        assert len(result["properties"]["decision_model"]["rubric_hash"]) == 64
        assert "native_status_answer" not in result["properties"]["decision_model"]
        assert summary["judge"]["failed_lines"] == 1
        rollup = _calculate_aoai_evaluation_summary(rows, logging.getLogger("test"), CRITERIA)
        assert rollup["per_model_usage"] == [
            {
                "model_name": "decision-native",
                "invocation_count": 1,
                "prompt_tokens": 120,
                "completion_tokens": 3,
                "total_tokens": 123,
                "cached_tokens": 0,
            }
        ]

    @pytest.mark.parametrize("status, expected", [(0.9, "completed"), (0.1, "skipped")])
    def test_success_and_skip_are_not_stamped_as_errors(self, batch_client, tmp_path, status, expected):
        class Runner:
            deployment = "Decision-1"
            decision_protocol = "microsoft"

            async def __call__(self, **kwargs):
                return payload(status)

        async def judge(query):
            return await strategy(Runner()).evaluate({"query": query})

        summary, rows = convert_batch(batch_client, judge, tmp_path)
        result = next(item for item in rows[0]["results"] if item["name"] == "judge")
        assert result["status"] == expected
        assert "error" not in (result.get("sample") or {})
        assert "per_line_error_metadata" not in summary["judge"]
        assert result["sample"]["usage"] == {"prompt_tokens": 120, "completion_tokens": 3, "total_tokens": 123}
        assert result["sample"]["model"] == "decision-native"
        assert result["properties"]["total_tokens"] == 123
        if expected == "skipped":
            assert result["score"] is None and result["passed"] is None
        else:
            assert result["score"] == 1 and result["passed"] is True
        rollup = _calculate_aoai_evaluation_summary(rows, logging.getLogger("test"), CRITERIA)
        assert rollup["per_model_usage"] == [
            {
                "model_name": "decision-native",
                "invocation_count": 1,
                "prompt_tokens": 120,
                "completion_tokens": 3,
                "total_tokens": 123,
                "cached_tokens": 0,
            }
        ]

    @pytest.mark.parametrize(
        "case", ["malformed_shape", "invalid_json", "partial_usage", "precancel", "inflight_cancel", "billed_cancel"]
    )
    def test_real_pipeline_failure_metadata_survives_batch_conversion(self, batch_client, tmp_path, monkeypatch, case):
        cancelled = False

        class Response(HttpResponse):
            def __init__(self, request):
                super().__init__(request, None)
                self.status_code = 429 if case == "billed_cancel" else 200
                self.headers = {"Retry-After": "10"} if case == "billed_cancel" else {}

            def body(self):
                if case == "invalid_json":
                    return b"not-json"
                return json.dumps(
                    {
                        "model": "decision-native",
                        "answers": {},
                        "usage": {"input_tokens": True if case == "partial_usage" else 12, "output_tokens": 4},
                    }
                ).encode()

        class Transport(AsyncHttpTransport):
            async def open(self):
                pass

            async def close(self):
                pass

            async def __aexit__(self, *_):
                await self.close()

            async def send(self, request, **kwargs):
                nonlocal cancelled
                if case == "inflight_cancel":
                    await asyncio.sleep(10)
                if case == "billed_cancel":
                    cancelled = True
                return Response(request)

        monkeypatch.setattr(
            _model_runners, "get_async_http_client", lambda **_: AsyncHttpPipeline(transport=Transport())
        )

        async def judge(query):
            nonlocal cancelled
            cancelled = case == "precancel"
            handle = None
            if case == "inflight_cancel":

                def cancel():
                    nonlocal cancelled
                    cancelled = True

                handle = asyncio.get_running_loop().call_later(0.02, cancel)
            try:
                runner = DecisionModelRunner(
                    CONFIG,
                    max_retries=1,
                    cancellation_requested=lambda: cancelled,
                )
                return await strategy(runner).evaluate({"query": query})
            finally:
                if handle is not None:
                    handle.cancel()

        _, rows = convert_batch(batch_client, judge, tmp_path)
        result = next(item for item in rows[0]["results"] if item["name"] == "judge")
        assert result["status"] == "error" and result["score"] is None and result["passed"] is None
        assert "decision_request_observations" not in result["properties"]
        execution = result["properties"]["decision_model"].pop("execution")
        assert execution["attempt_count"] == (0 if case == "precancel" else 1)
        assert execution["outcome"] == ("cancelled" if "cancel" in case else "error")
        assert execution["usage_state"] == (
            "known"
            if case in ("malformed_shape", "billed_cancel")
            else "partial" if case == "partial_usage" else "unknown"
        )
        if case == "malformed_shape":
            assert result["sample"]["usage"] == {"prompt_tokens": 12, "completion_tokens": 4, "total_tokens": 16}
            assert result["sample"]["model"] == "decision-native"
        elif case == "partial_usage":
            assert result["sample"]["usage"] == {"completion_tokens": 4}
            assert result["sample"]["model"] == "decision-native"
            assert "total_tokens" not in result["properties"] and "prompt_tokens" not in result["properties"]
        else:
            assert "usage" not in result["sample"] and "model" not in result["sample"]
            assert result["properties"] == {"decision_model": {"deployment": "Decision-1", "protocol": "microsoft"}}
        if "cancel" in case:
            assert result["sample"]["error"]["blame"] == "UserError"
        else:
            assert result["sample"]["error"]["blame"] == "SystemError"
        assert "test-key-not-for-persistence" not in json.dumps(result)
        assert "synthetic" not in json.dumps(result["properties"])

    def test_per_line_classification_and_metadata_do_not_bleed(self, batch_client, tmp_path):
        calls = 0

        async def judge(query):
            nonlocal calls
            index = calls
            calls += 1
            if index == 0:
                raise EvaluationException(
                    "Cancelled.",
                    category=ErrorCategory.FAILED_EXECUTION,
                    blame=ErrorBlame.USER_ERROR,
                    properties={"decision_model": {}},
                )
            if index == 1:
                raise EvaluationException(
                    "Invalid.",
                    category=ErrorCategory.INVALID_VALUE,
                    blame=ErrorBlame.SYSTEM_ERROR,
                    properties={
                        "prompt_tokens": 7,
                        "completion_tokens": True,
                        "total_tokens": float("nan"),
                        "evidence": "secret",
                        "model": "decision-native",
                        "decision_model": {"rubric_hash": "known", "native_answer": {"noul": float("nan")}},
                    },
                )
            return {"task_completion": 1, "task_completion_score": 1, "task_completion_passed": True}

        _, rows = convert_batch(batch_client, judge, tmp_path, rows=3)
        first, second, third = [next(item for item in row["results"] if item["name"] == "judge") for row in rows]
        assert first["sample"]["error"]["blame"] == "UserError"
        assert first["sample"]["error"]["code"] == "FAILED_EXECUTION"
        assert second["sample"]["error"]["blame"] == "SystemError"
        assert second["sample"]["error"]["code"] == "INVALID VALUE"
        assert second["sample"]["usage"] == {"prompt_tokens": 7}
        assert second["properties"] == {
            "prompt_tokens": 7,
            "model": "decision-native",
            "decision_model": {"rubric_hash": "known"},
        }
        assert third["status"] == "completed" and "error" not in (third.get("sample") or {})

    def test_other_exceptions_preserve_summary_and_error_row_shape(self, batch_client, tmp_path):
        async def judge(query):
            raise EvaluationException(
                "Ordinary error.", category=ErrorCategory.INVALID_VALUE, blame=ErrorBlame.USER_ERROR
            )

        summaries, rows = convert_batch(batch_client, judge, tmp_path)
        assert set(summaries["judge"]) == {
            "status",
            "duration",
            "completed_lines",
            "failed_lines",
            "log_path",
            "per_line_errors",
            "error_message",
            "error_code",
        }
        result = next(item for item in rows[0]["results"] if item["name"] == "judge")
        assert result == {
            "type": "azure_ai_evaluator",
            "name": "judge",
            "metric": "task_completion",
            "score": None,
            "label": None,
            "reason": None,
            "threshold": None,
            "passed": None,
            "status": "error",
            "sample": {"error": {"code": summaries["judge"]["error_code"], "message": "(UserError) Ordinary error."}},
        }
