# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

"""Failed split conversations retain known usage through public calls and batch conversion."""

import asyncio
from copy import deepcopy
import json
import logging
from unittest.mock import Mock

import pandas as pd
import pytest
from azure.core.pipeline.transport import AsyncHttpTransport, HttpResponse

from azure.ai.evaluation._evaluate._batch_run import RunSubmitterClient
from azure.ai.evaluation._evaluate._evaluate import _convert_single_row_to_aoai_format
from azure.ai.evaluation._evaluators._common import ModelEvaluatorBase
from azure.ai.evaluation._evaluators._common import _model_runners
from azure.ai.evaluation._evaluators._common._decision_strategy import BinaryScoring, DecisionEvaluationStrategy
from azure.ai.evaluation._exceptions import ErrorBlame, ErrorCategory, ErrorTarget, EvaluationException
from azure.ai.evaluation._http_utils import AsyncHttpPipeline

pytestmark = pytest.mark.unittest

CONFIG = {
    "type": "decision",
    "azure_endpoint": "https://example.services.ai.azure.com",
    "azure_deployment": "Decision-1",
    "api_key": "offline-key",
}
QUESTIONS = {"status": {"type": "noul"}, "task_completion": {"type": "noul"}}
CONVERSATION = {
    "messages": [
        {"role": "user", "content": "first"},
        {"role": "assistant", "content": "one"},
        {"role": "user", "content": "second"},
        {"role": "assistant", "content": "two"},
    ]
}


class SplitDecisionEvaluator(ModelEvaluatorBase):
    _supports_decision_models = True

    def __init__(self):
        super().__init__(result_key="task_completion", model_config=CONFIG, timeout=1, max_retries=0)
        self.error = None
        self.original_properties = None

    def _derive_singleton_inputs(self):
        return [["query", "response"]]

    async def _do_eval(self, eval_input):
        try:
            return await DecisionEvaluationStrategy(
                self._decision_model_runner,
                result_key="task_completion",
                error_target=ErrorTarget.EVALUATE,
                questions=QUESTIONS,
                scoring=BinaryScoring(0.75),
                threshold=1,
                timeout=self._LLM_CALL_TIMEOUT,
            ).evaluate(eval_input)
        except EvaluationException as error:
            if not {"prompt_tokens", "completion_tokens", "total_tokens"}.intersection(error.properties or {}):
                # A caller's unmeasured-turn metadata must not label prior known usage unavailable.
                error.properties.setdefault("decision_model", {}).update(
                    usage_available=False, model="unmeasured-failure-model"
                )
            self.error = error
            self.original_properties = deepcopy(error.properties)
            raise


@pytest.mark.parametrize("batch", [False, True], ids=["public", "batch"])
@pytest.mark.parametrize(
    "failure,failed_turn,mixed",
    [
        ("semantic", 1, False),
        ("semantic", 1, True),
        ("partial", 1, False),
        ("timeout", 1, False),
        ("semantic", 0, False),
        ("timeout", 0, False),
    ],
)
def test_failed_split_conversation_preserves_known_usage(monkeypatch, tmp_path, batch, failure, failed_turn, mixed):
    calls = []

    class Response(HttpResponse):
        def __init__(self, request, body):
            super().__init__(request, None)
            self.status_code, self.headers, self._body = 200, {}, body

        def body(self):
            return self._body

    class Transport(AsyncHttpTransport):
        async def open(self):
            pass

        async def close(self):
            pass

        async def __aexit__(self, *_):
            await self.close()

        async def send(self, request, **kwargs):
            failing = len(calls) == failed_turn
            calls.append(json.loads(request.body))
            if failing and failure == "timeout":
                await asyncio.sleep(5)
            body = {
                "model": "other-model" if failing and mixed else "same-model",
                "usage": {"input_tokens": 34 if failing else 12, "output_tokens": 5 if failing else 3},
                "answers": {
                    "status": {"type": "noul", "noul": 0.9},
                    "task_completion": {"type": "noul", "noul": 2 if failing else 0.9},
                },
            }
            if failing and failure == "partial":
                body["usage"]["input_tokens"] = True
            return Response(request, json.dumps(body).encode())

    monkeypatch.setattr(_model_runners, "get_async_http_client", lambda **_: AsyncHttpPipeline(transport=Transport()))
    evaluator = SplitDecisionEvaluator()
    if batch:
        client = RunSubmitterClient()
        try:
            run = client.run(
                evaluator,
                pd.DataFrame([{"conversation": CONVERSATION}]),
                evaluator_name="judge",
                column_mapping={"conversation": "${data.conversation}"},
            )
            details = client.get_details(run, all_results=True).to_dict(orient="records")[0]
            summary = client.get_run_summary(run)
            row = {key.replace("outputs.", "outputs.judge.", 1): value for key, value in details.items()}
            converted = _convert_single_row_to_aoai_format(
                row,
                0,
                None,
                None,
                0,
                {"judge": {"metrics": ["task_completion"], "type": "azure_ai_evaluator"}},
                {"judge": summary},
                logging.getLogger("test"),
            )
            path = tmp_path / "failed-conversation.json"
            path.write_text(json.dumps(converted, allow_nan=False), encoding="utf-8")
            result = json.loads(path.read_text(encoding="utf-8"))["results"][0]
            assert summary["failed_lines"] == 1 and summary["completed_lines"] == 0
            assert result["status"] == "error" and result["score"] is None and result["passed"] is None
            assert result["sample"]["error"]["code"] == "FAILED_EXECUTION"
            assert result["sample"]["error"]["blame"] == "SystemError"
            properties = result["properties"]
        finally:
            client._thread_pool.shutdown(wait=True)
    else:
        with pytest.raises(EvaluationException) as raised:
            evaluator(conversation=CONVERSATION)
        assert raised.value is evaluator.error
        assert raised.value.category == ErrorCategory.FAILED_EXECUTION
        assert raised.value.blame == ErrorBlame.SYSTEM_ERROR
        properties = raised.value.properties

    assert len(calls) == failed_turn + 1
    if failed_turn:
        expected = {"prompt_tokens": 46, "completion_tokens": 8, "total_tokens": 54}
        if failure == "timeout":
            expected = {"prompt_tokens": 12, "completion_tokens": 3, "total_tokens": 15}
        elif failure == "partial":
            expected = {"prompt_tokens": 12, "completion_tokens": 8, "total_tokens": 15}
        assert {field: properties[field] for field in expected} == expected
        assert properties["decision_model"]["result_usage_scope"] == "reported_turns_only"
        assert properties["decision_model"]["usage_available"] is True
        assert "execution" not in properties["decision_model"]
        if mixed:
            assert "model" not in properties and "model" not in properties["decision_model"]
        else:
            assert properties["model"] == "same-model"
            assert properties["decision_model"]["model"] == "same-model"
        if batch:
            assert result["sample"]["usage"] == expected
            assert result["sample"].get("model") == (None if mixed else "same-model")
    else:
        assert "result_usage_scope" not in properties["decision_model"]
        assert properties["decision_model"]["execution"]["attempt_count"] == 1
        if failure == "semantic":
            assert properties["total_tokens"] == 39
        else:
            assert not {"prompt_tokens", "completion_tokens", "total_tokens"}.intersection(properties)
        if not batch:
            assert properties == evaluator.original_properties


def test_prompty_split_failure_preserves_existing_exception(monkeypatch):
    monkeypatch.setattr(_model_runners.AsyncPrompty, "load", Mock())
    error = EvaluationException(
        message="chat failure",
        internal_message="chat failure",
        target=ErrorTarget.EVALUATE,
        category=ErrorCategory.INVALID_VALUE,
        blame=ErrorBlame.USER_ERROR,
    )
    error.properties = {"model": "chat-model", "total_tokens": 39, "custom": "unchanged"}
    original = deepcopy(error.properties)

    class ChatEvaluator(ModelEvaluatorBase):
        def _derive_singleton_inputs(self):
            return [["query", "response"]]

        async def _do_eval(self, eval_input):
            if eval_input["query"] == "second":
                raise error
            return {"metric": 1, "metric_total_tokens": 15, "metric_model": "chat-model"}

    evaluator = ChatEvaluator(
        result_key="metric",
        prompty_file="unused.prompty",
        model_config={
            "azure_endpoint": "https://example.openai.azure.com",
            "azure_deployment": "chat",
            "api_key": "offline-key",
        },
    )
    with pytest.raises(EvaluationException) as raised:
        evaluator(conversation=CONVERSATION)
    assert raised.value is error and error.properties == original
    assert error.category == ErrorCategory.INVALID_VALUE and error.blame == ErrorBlame.USER_ERROR
