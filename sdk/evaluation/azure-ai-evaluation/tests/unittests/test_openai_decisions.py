# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

"""The OpenAI Decisions protocol on the shared Decision runner and scoring strategy."""

import asyncio
import copy
import json
import logging
import pickle
from logging.handlers import BufferingHandler
from unittest.mock import AsyncMock

import pytest
from azure.core.pipeline.transport import AsyncHttpTransport, HttpResponse

from azure.ai.evaluation._evaluate._batch_run._run_submitter_client import _decision_error_metadata
from azure.ai.evaluation._evaluators._common import _model_runners
from azure.ai.evaluation._evaluators._common._decision_protocols import OpenAIDecisionProtocol
from azure.ai.evaluation._evaluators._common._decision_strategy import (
    DecisionEvaluationStrategy,
    DecisionRefusalError,
    LikertScoring,
)
from azure.ai.evaluation._evaluators._common._model_runners import DecisionExecution, DecisionModelRunner
from azure.ai.evaluation._exceptions import ErrorBlame, ErrorCategory, ErrorTarget, EvaluationException
from azure.ai.evaluation._http_utils import AsyncHttpPipeline

pytestmark = pytest.mark.unittest

CONFIG = {
    "type": "decision",
    "decision_protocol": "openai",
    "azure_endpoint": "https://test.openai.azure.com",
    "azure_deployment": "judge",
    "api_key": "test-only",
}
QUESTIONS = {
    "status": {"type": "noul", "instructions": "Applicable?", "criteria": {"true": "Has evidence", "false": "Empty"}},
    "quality": {"type": "score", "instructions": "Quality?", "criteria": ["Bad", "Okay", "Good"]},
}


def response(status=0.9, quality=None):
    """An Azure OpenAI Decisions response; Azure returns the deployment alias as the model."""
    return {
        "model": "judge",
        "usage": {
            "input_tokens": 12,
            "output_tokens": 3,
            "total_tokens": 15,
            "input_tokens_details": {"cached_tokens": 4, "cache_write_tokens": 2},
            "output_tokens_details": {"reasoning_tokens": 1},
        },
        "answers": [
            {"type": "predicate", "name": "status", "probability": status},
            quality
            or {
                "type": "score",
                "name": "quality",
                "confidence": 0.4,
                "score": 0.8,
                "probabilities": [
                    {"value": 0, "label": "Level 1", "probability": 0.4},
                    {"value": 1, "label": "Level 2", "probability": 0.4},
                    {"value": 2, "label": "Level 3", "probability": 0.2},
                ],
            },
        ],
    }


def strategy(payload, config=CONFIG):
    runner = DecisionModelRunner(config)
    runner._post = AsyncMock(return_value=payload)
    return DecisionEvaluationStrategy(
        runner,
        result_key="quality",
        error_target=ErrorTarget.EVALUATE,
        questions=QUESTIONS,
        scoring=LikertScoring(3),
        threshold=2,
        timeout=30,
    )


def evaluate(payload):
    return asyncio.run(strategy(payload).evaluate({"response": "Evidence"}))


class FakeResponse(HttpResponse):
    def __init__(self, request, status_code, body):
        super().__init__(request, None)
        self.status_code = status_code
        self.headers = {}
        self._body = json.dumps(body).encode()

    def body(self):
        return self._body


class FakeTransport(AsyncHttpTransport):
    """Answers each request with the next ``(status, body)`` reply and records the requests."""

    def __init__(self, *replies):
        self.replies = list(replies)
        self.requests = []

    async def open(self):
        pass

    async def close(self):
        pass

    async def __aexit__(self, *args):
        await self.close()

    async def send(self, request, **kwargs):
        self.requests.append(request)
        status, body = self.replies.pop(0)
        return FakeResponse(request, status, body)


class TestRequest:
    def test_encode_keeps_evidence_and_both_boolean_criteria(self):
        request = OpenAIDecisionProtocol().encode("judge", {"response": "\u00e9vidence"}, QUESTIONS)
        assert json.loads(request["input"]) == {"response": "\u00e9vidence"}
        assert request["model"] == "judge" and "state" not in request
        assert request["questions"][0] == {
            "name": "status",
            "type": "predicate",
            "instructions": "Applicable?\n\nThe predicate is true when: Has evidence\nThe predicate is false when: Empty",
        }
        assert request["questions"][1]["levels"] == [
            {"label": f"Level {position}", "description": value}
            for position, value in enumerate(["Bad", "Okay", "Good"], start=1)
        ]

    @pytest.mark.parametrize("protocol", ["microsoft", "openai"])
    @pytest.mark.parametrize("state", [{"response": float("nan")}, {"response": object()}])
    def test_invalid_evidence_is_the_same_user_error_on_every_protocol(self, protocol, state):
        endpoint = "https://test.services.ai.azure.com" if protocol == "microsoft" else CONFIG["azure_endpoint"]
        runner = DecisionModelRunner({**CONFIG, "decision_protocol": protocol, "azure_endpoint": endpoint})
        runner._post = AsyncMock()
        with pytest.raises(EvaluationException) as raised:
            asyncio.run(runner(state=state, questions=QUESTIONS, timeout=30))
        assert str(raised.value).endswith(") Decision evidence must be finite JSON-serializable data.")
        assert (raised.value.category, raised.value.blame) == (ErrorCategory.FAILED_EXECUTION, ErrorBlame.USER_ERROR)
        runner._post.assert_not_awaited()

    @pytest.mark.parametrize(
        "questions",
        [
            {str(i): QUESTIONS["status"] for i in range(401)},
            {"q": {"type": "score", "instructions": "Score", "criteria": ["one"]}},
            {"q": {"type": "noul", "instructions": "Boolean", "criteria": {"true": "yes"}}},
            {"q": {"type": "noul", "instructions": " "}},
        ],
    )
    def test_requests_the_protocol_cannot_express_fail_before_transport(self, questions):
        runner = DecisionModelRunner(CONFIG)
        runner._post = AsyncMock()
        with pytest.raises(EvaluationException) as raised:
            asyncio.run(runner(state="evidence", questions=questions, timeout=30))
        assert raised.value.category == ErrorCategory.INVALID_VALUE
        runner._post.assert_not_awaited()

    @pytest.mark.parametrize(
        "endpoint",
        [
            "https://test.openai.azure.com",
            "https://test.openai.azure.com/openai/",
            "https://test.openai.azure.com/openai/v1/",
        ],
    )
    def test_endpoint_forms(self, endpoint):
        runner = DecisionModelRunner({**CONFIG, "azure_endpoint": endpoint})
        assert runner._url == "https://test.openai.azure.com/openai/v1/decisions"
        assert runner.decision_protocol == "openai"

    def test_selection_is_explicit_and_preserves_the_microsoft_default(self):
        config = {key: value for key, value in CONFIG.items() if key != "decision_protocol"}
        runner = DecisionModelRunner({**config, "azure_endpoint": "https://test.services.ai.azure.com/base"})
        assert runner._url == "https://test.services.ai.azure.com/base/providers/microsoft/v1/systemone"
        assert runner.decision_protocol == "microsoft"
        assert DecisionModelRunner.SUPPORTED_PROTOCOLS == frozenset({"microsoft", "openai"})
        for changes in (
            {"decision_protocol": "invalid"},
            {"decision_protocol": []},
            {"azure_endpoint": "https://test.services.ai.azure.com/api/projects/test"},
        ):
            with pytest.raises(EvaluationException):
                DecisionModelRunner({**CONFIG, **changes})

    def test_byte_budgets_measure_the_canonical_request_on_every_protocol(self):
        """Budgets bound what the model reads, so escaping evidence into OpenAI's text input admits no less evidence."""
        state = {"response": '"quoted"' * 20}

        def size(value):
            return len(json.dumps(value, ensure_ascii=False, separators=(",", ":")).encode("utf-8"))

        canonical = size({"model": "judge", "state": state, "questions": QUESTIONS})
        unit = max(size({"state": state, "question": question}) for question in QUESTIONS.values())
        assert size(OpenAIDecisionProtocol().encode("judge", state, QUESTIONS)) > canonical
        for limits in ({"max_request_bytes": canonical - 1}, {"max_state_question_bytes": unit - 1}):
            runner = DecisionModelRunner(CONFIG, **limits)
            runner._post = AsyncMock()
            with pytest.raises(EvaluationException, match="byte budget") as raised:
                asyncio.run(runner(state=state, questions=QUESTIONS, timeout=30))
            assert raised.value.blame == ErrorBlame.USER_ERROR
            runner._post.assert_not_awaited()
        runner = DecisionModelRunner(CONFIG, max_request_bytes=canonical, max_state_question_bytes=unit)
        runner._post = AsyncMock(return_value=response())
        asyncio.run(runner(state=state, questions=QUESTIONS, timeout=30))
        runner._post.assert_awaited_once()


class TestResponse:
    def test_answers_bind_by_name_into_the_canonical_shape(self):
        payload = response()
        payload["answers"].reverse()
        payload["answers"][0]["additive_field"] = "ignored"
        runner = DecisionModelRunner(CONFIG)
        runner._post = AsyncMock(return_value=payload)
        result = asyncio.run(runner(state="evidence", questions=QUESTIONS, timeout=30))
        assert result["answers"] == {
            "status": {"type": "noul", "noul": 0.9},
            "quality": {
                "type": "score",
                "score": 0.8,
                "confidence": 0.4,
                "probabilities": {"0": 0.4, "1": 0.4, "2": 0.2},
            },
        }
        assert result["usage"] == {"input_tokens": 12, "output_tokens": 3}
        assert result["usage_details"] == {
            "input_tokens_details": {"cached_tokens": 4, "cache_write_tokens": 2},
            "output_tokens_details": {"reasoning_tokens": 1},
        }

    @pytest.mark.parametrize(
        "mutation",
        [
            lambda p: p.update(answers={"status": {"type": "noul", "noul": 0.9}}),
            lambda p: p["answers"].pop(),
            lambda p: p["answers"].append(dict(p["answers"][0])),
            lambda p: p["answers"][0].update(name="unknown"),
            lambda p: p["answers"][0].update(name=None),
            lambda p: p["answers"][1].update(type="predicate"),
            lambda p: p["answers"][0].update(type="choice"),
        ],
    )
    def test_answers_that_cannot_bind_to_the_questions_are_invalid(self, mutation):
        payload = response()
        mutation(payload)
        runner = DecisionModelRunner(CONFIG)
        runner._post = AsyncMock(return_value=payload)
        with pytest.raises(EvaluationException, match="invalid response") as raised:
            asyncio.run(runner(state="evidence", questions=QUESTIONS, timeout=30))
        assert raised.value.blame == ErrorBlame.SYSTEM_ERROR
        assert raised.value.properties["total_tokens"] == 15

    def test_the_microsoft_protocol_still_rejects_a_refusal_answer(self):
        config = {key: value for key, value in CONFIG.items() if key != "decision_protocol"}
        runner = DecisionModelRunner(config)
        runner._post = AsyncMock(
            return_value={
                "model": "Microsoft-Decision-1",
                "usage": {"input_tokens": 1, "output_tokens": 1},
                "answers": {"status": {"type": "refusal"}, "quality": {"type": "refusal"}},
            }
        )
        with pytest.raises(EvaluationException, match="invalid response"):
            asyncio.run(runner(state="evidence", questions=QUESTIONS, timeout=30))

    def test_transport_uses_the_decisions_route_and_key_and_retries(self, monkeypatch):
        transport = FakeTransport((429, {"error": {"code": "RateLimitExceeded"}}), (200, response()))
        monkeypatch.setattr(_model_runners, "get_async_http_client", lambda **_: AsyncHttpPipeline(transport=transport))
        result = asyncio.run(DecisionModelRunner(CONFIG, max_retries=1)(state="text", questions=QUESTIONS, timeout=30))
        assert len(transport.requests) == 2
        request = transport.requests[0]
        assert request.url == "https://test.openai.azure.com/openai/v1/decisions"
        assert request.headers["api-key"] == "test-only" and "Authorization" not in request.headers
        assert json.loads(request.content) == OpenAIDecisionProtocol().encode("judge", "text", QUESTIONS)
        assert result["answers"]["status"] == {"type": "noul", "noul": 0.9}

    def test_a_content_filter_rejection_is_the_callers_content_and_is_marked(self, monkeypatch):
        transport = FakeTransport((400, {"error": {"code": "content_filter", "message": "private filter detail"}}))
        monkeypatch.setattr(_model_runners, "get_async_http_client", lambda **_: AsyncHttpPipeline(transport=transport))
        with pytest.raises(EvaluationException, match=r"HTTP 400 \(content_filter\)") as raised:
            asyncio.run(DecisionModelRunner(CONFIG)(state="text", questions=QUESTIONS, timeout=30))
        assert raised.value.blame == ErrorBlame.USER_ERROR
        assert "private filter detail" not in str(raised.value)
        persisted = _decision_error_metadata(raised.value)["properties"]["decision_model"]
        assert persisted["error_kind"] == "content_filter" and persisted["protocol"] == "openai"
        assert persisted["execution"]["last_http_status"] == 400

    def test_execution_observations_name_the_protocol(self):
        handler = BufferingHandler(10)
        logger = logging.Logger("decision-execution")
        logger.addHandler(handler)
        execution = DecisionExecution(logger, None, "openai")
        execution.emit("execution", "completed", execution.summary("completed"), 1.0, "known")
        dimensions = json.loads(handler.buffer[0].decision_dimensions)
        assert dimensions["protocol"] == "openai" and dimensions["route"] == "shared_sdk"


class TestScoring:
    def test_shared_strategy_keeps_argmax_ties_threshold_and_usage(self):
        result = evaluate(response())
        assert result["quality"] == 1 and result["quality_passed"] is False
        assert result["quality_total_tokens"] == 15 and result["quality_model"] == "judge"
        provenance = result["quality_properties"]["decision_model"]
        assert provenance["protocol"] == "openai"
        assert provenance["native_status_answer"] == {"type": "noul", "noul": 0.9}
        assert provenance["native_answer"] == {
            "type": "score",
            "score": 0.8,
            "confidence": 0.4,
            "probabilities": {"0": 0.4, "1": 0.4, "2": 0.2},
        }
        assert provenance["usage_details"]["input_tokens_details"]["cached_tokens"] == 4

    def test_rounded_probabilities_use_the_shared_tolerance(self):
        quality = {
            "type": "score",
            "name": "quality",
            "confidence": 0.33,
            "score": 1.0,
            "probabilities": [{"value": i, "label": str(i), "probability": 0.33} for i in range(3)],
        }
        assert evaluate(response(quality=quality))["quality"] == 1

    @pytest.mark.parametrize(
        "quality",
        [
            {"type": "refusal", "name": "quality"},
            {"type": "score", "name": "quality", "score": 9, "confidence": 2, "probabilities": "invalid"},
            {
                "type": "score",
                "name": "quality",
                "score": 0,
                "confidence": 1,
                "probabilities": [{"value": 0, "probability": 1}, {"value": 0, "probability": 0}],
            },
        ],
    )
    def test_a_skipped_evaluation_never_reads_its_grade(self, quality):
        result = evaluate(response(status=0.1, quality=quality))
        assert result["quality_status"] == "skipped" and result["quality"] is None
        assert "native_answer" not in result["quality_properties"]["decision_model"]

    @pytest.mark.parametrize("refused", ["status", "quality"])
    def test_a_refused_answer_that_is_read_fails_without_a_score(self, refused):
        payload = response()
        index = 0 if refused == "status" else 1
        payload["answers"][index] = {"type": "refusal", "name": refused}
        with pytest.raises(DecisionRefusalError, match=f"refused to answer question '{refused}'") as raised:
            evaluate(payload)
        error = raised.value
        assert error.blame == ErrorBlame.USER_ERROR and error.category == ErrorCategory.FAILED_EXECUTION
        assert error.properties["total_tokens"] == 15
        provenance = error.properties["decision_model"]
        assert provenance["protocol"] == "openai" and provenance["error_kind"] == "model_refusal"
        persisted = _decision_error_metadata(error)
        assert persisted["blame"] == "UserError"
        assert persisted["properties"]["decision_model"]["error_kind"] == "model_refusal"
        assert persisted["properties"]["decision_model"]["protocol"] == "openai"
        assert persisted["properties"]["decision_model"]["usage_details"]["input_tokens_details"]["cached_tokens"] == 4

    def test_a_refusal_survives_copies_and_pickles_with_its_metadata(self):
        payload = response()
        payload["answers"][1] = {"type": "refusal", "name": "quality"}
        with pytest.raises(DecisionRefusalError) as raised:
            evaluate(payload)
        for copied in (copy.deepcopy(raised.value), pickle.loads(pickle.dumps(raised.value))):
            assert isinstance(copied, DecisionRefusalError) and str(copied) == str(raised.value)
            assert copied.properties == raised.value.properties and copied.target == raised.value.target

    def test_a_malformed_grade_that_is_read_is_an_invalid_response(self):
        quality = {
            "type": "score",
            "name": "quality",
            "score": 0,
            "confidence": 1,
            "probabilities": [{"value": 0, "probability": 1}, {"value": 0, "probability": 0}],
        }
        with pytest.raises(EvaluationException, match="invalid response") as raised:
            evaluate(response(quality=quality))
        assert not isinstance(raised.value, DecisionRefusalError)
        assert raised.value.blame == ErrorBlame.SYSTEM_ERROR
