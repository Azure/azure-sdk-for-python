# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

"""Offline tests for shared decision-model runners, base selection, and evaluation strategy."""

import asyncio
import hashlib
import json
import threading
from dataclasses import FrozenInstanceError
from concurrent.futures import ThreadPoolExecutor
from types import SimpleNamespace
from unittest.mock import AsyncMock, Mock, patch

import pytest
from azure.core.pipeline.policies import AsyncRedirectPolicy, AsyncRetryPolicy
from azure.core.pipeline.transport import AsyncHttpTransport, HttpResponse
from azure.core.exceptions import ServiceRequestError

from azure.ai.evaluation import FluencyEvaluator
from azure.ai.evaluation._evaluators._common import EvaluatorBase, ModelEvaluatorBase, PromptyEvaluatorBase
from azure.ai.evaluation._evaluators._common import DecisionExecutionPolicy, DecisionRequestObservation
from azure.ai.evaluation._evaluators._common import _model_runners
from azure.ai.evaluation._evaluators._common._decision_strategy import (
    BinaryScoring,
    DecisionEvaluationStrategy,
    LikertScoring,
)
from azure.ai.evaluation._evaluators._common._model_runners import (
    DecisionModelRunner,
    PromptyModelRunner,
    validate_noul_answer,
    validate_score_answer,
)
from azure.ai.evaluation._exceptions import ErrorBlame, ErrorTarget, EvaluationException

pytestmark = pytest.mark.unittest

DECISION_CONFIG = {
    "type": "decision",
    "azure_endpoint": "https://example.services.ai.azure.com",
    "azure_deployment": "Decision-1",
    "api_key": "test-key-value",
}
CHAT_CONFIG = {
    "azure_endpoint": "https://example.openai.azure.com",
    "azure_deployment": "chat-deployment",
    "api_key": "chat-key",
}


def score_answer(levels):
    """A consistent five-level score answer for the given level probabilities."""
    return {
        "type": "score",
        "score": sum(index * value for index, value in enumerate(levels)),
        "confidence": max(levels),
        "probabilities": {str(index): value for index, value in enumerate(levels)},
    }


def decision_payload(status=0.95, result=None, model="microsoft-decision-1", usage=(120, 3), **answers):
    payload = {
        "model": model,
        "answers": {"status": {"type": "noul", "noul": status}},
        "usage": {"input_tokens": usage[0], "output_tokens": usage[1]},
    }
    if result is not None:
        payload["answers"].update(result)
    payload["answers"].update(answers)
    return payload


def level_payload(level, status=0.95):
    levels = [0.0] * 5
    levels[level] = 1.0
    return decision_payload(status, {"tool_call_accuracy": score_answer(levels)})


class FakeResponse:
    def __init__(self, status_code=200, body=b"{}"):
        self.status_code = status_code
        self._body = body

    def body(self):
        return self._body


class FakeClient:
    def __init__(self, response=None, delay=0.0):
        self.response = response or FakeResponse()
        self.delay = delay
        self.calls = []
        self.policies = None

    def with_policies(self, **policies):
        self.policies = policies
        return self

    async def __aenter__(self):
        return self

    async def __aexit__(self, *_):
        return False

    async def post(self, url, content=None, headers=None, **options):
        self.calls.append(
            {"url": url, "json": json.loads(content), "content": content, "headers": dict(headers), "options": options}
        )
        if self.delay:
            await asyncio.sleep(self.delay)
        return self.response


@pytest.fixture
def client(monkeypatch):
    fake = FakeClient()
    monkeypatch.setattr(_model_runners, "get_async_http_client", lambda: fake)
    return fake


QUESTIONS = {
    "status": {"type": "noul", "instructions": "Applicable?"},
    "tool_call_accuracy": {"type": "score", "instructions": "How accurate?", "criteria": ["a", "b", "c", "d", "e"]},
}


def run(runner, **overrides):
    arguments = {"state": {"query": "q"}, "questions": QUESTIONS, "timeout": 5}
    arguments.update(overrides)
    return asyncio.run(runner(**arguments))


class TestDecisionModelRunnerConfiguration:
    @pytest.mark.parametrize(
        "changes",
        [
            {"type": "azure_openai"},
            {"extra": "field"},
            {"azure_endpoint": None},
            {"azure_endpoint": " "},
            {"azure_deployment": " "},
            {"azure_deployment": None},
            {"api_key": " "},
            {"probability_threshold": 0.5},
        ],
    )
    def test_invalid_configuration_is_a_user_error(self, changes):
        config = {**DECISION_CONFIG, **changes}
        with pytest.raises(EvaluationException) as raised:
            DecisionModelRunner(config)
        assert raised.value.blame == ErrorBlame.USER_ERROR
        assert "secret" not in str(raised.value)

    @pytest.mark.parametrize("value", [True, "0.5", None, float("nan"), -0.1, 1.1])
    def test_invalid_probability_threshold(self, value):
        with pytest.raises(EvaluationException):
            DecisionModelRunner({**DECISION_CONFIG, "probability_threshold": value}, binary=True)

    @pytest.mark.parametrize(
        "endpoint",
        [
            "https://example.services.ai.azure.com",
            "https://example.services.ai.azure.com/",
            "http://example.services.ai.azure.com",
            "https://user:secret@example.services.ai.azure.com",
            "https://example.services.ai.azure.com?x=1",
            "https://example.services.ai.azure.com#fragment",
            "https://example.services.ai.azure.com/api/projects/proj",
            "not-a-url",
        ],
    )
    def test_endpoint_format_is_left_to_http_client(self, endpoint):
        runner = DecisionModelRunner({**DECISION_CONFIG, "azure_endpoint": endpoint})
        assert runner._url == endpoint.rstrip("/") + "/providers/microsoft/v1/systemone"

    def test_binary_probability_threshold(self):
        assert DecisionModelRunner(DECISION_CONFIG, binary=True).probability_threshold == 0.75
        runner = DecisionModelRunner({**DECISION_CONFIG, "probability_threshold": 0.7}, binary=True)
        assert runner.probability_threshold == 0.7

    def test_api_key_wins_over_credential(self):
        runner = DecisionModelRunner(DECISION_CONFIG, credential=Mock())
        assert runner._credential is None and runner._api_key == DECISION_CONFIG["api_key"]


class TestDecisionModelRunnerRequests:
    def test_request_shape_with_api_key(self, client):
        client.response = FakeResponse(body=json.dumps(level_payload(4)).encode())
        result = run(DecisionModelRunner(DECISION_CONFIG, evaluator_name="Probe"), state={"query": "q"})
        call = client.calls[0]
        assert call["url"] == "https://example.services.ai.azure.com/providers/microsoft/v1/systemone"
        assert call["json"] == {"model": "Decision-1", "state": {"query": "q"}, "questions": QUESTIONS}
        assert call["headers"]["api-key"] == "test-key-value"
        assert "Authorization" not in call["headers"]
        assert call["headers"]["x-ms-useragent"].endswith("(type=evaluator subtype=Probe)")
        assert result["usage"] == {"input_tokens": 120, "output_tokens": 3}

    @pytest.mark.parametrize("asynchronous", [False, True])
    def test_credential_acquires_a_scoped_bearer_token(self, client, asynchronous):
        client.response = FakeResponse(body=json.dumps(level_payload(4)).encode())
        token = SimpleNamespace(token="bearer-value")
        credential = Mock()
        credential.get_token = AsyncMock(return_value=token) if asynchronous else Mock(return_value=token)
        config = {key: value for key, value in DECISION_CONFIG.items() if key != "api_key"}
        run(DecisionModelRunner(config, credential))
        credential.get_token.assert_called_once_with("https://cognitiveservices.azure.com/.default")
        headers = client.calls[0]["headers"]
        assert headers["Authorization"] == "Bearer bearer-value" and "api-key" not in headers

    def test_credential_in_configuration(self, client):
        client.response = FakeResponse(body=json.dumps(level_payload(4)).encode())
        credential = Mock(get_token=Mock(return_value=SimpleNamespace(token="from-config")))
        config = {key: value for key, value in DECISION_CONFIG.items() if key != "api_key"}
        run(DecisionModelRunner({**config, "credential": credential}))
        assert client.calls[0]["headers"]["Authorization"] == "Bearer from-config"

    def test_bounded_retries_without_redirects(self, client):
        client.response = FakeResponse(body=json.dumps(level_payload(4)).encode())
        run(DecisionModelRunner(DECISION_CONFIG))
        retry, redirect = client.policies["retry_policy"], client.policies["redirect_policy"]
        assert isinstance(retry, AsyncRetryPolicy) and retry.total_retries == 3
        assert isinstance(redirect, AsyncRedirectPolicy) and redirect.allow is False

    @pytest.mark.parametrize("status", _model_runners._DECISION_RETRY_STATUS_CODES)
    def test_transient_post_response_is_retried_without_retry_after(self, monkeypatch, status):
        from azure.ai.evaluation._http_utils import AsyncHttpPipeline

        class Response(HttpResponse):
            def __init__(self, request, status_code):
                super().__init__(request, None)
                self.status_code = status_code
                self.headers = {}

            def body(self):
                return json.dumps(level_payload(4)).encode()

        class Transport(AsyncHttpTransport):
            def __init__(self):
                self.calls = 0

            async def open(self):
                pass

            async def close(self):
                pass

            async def __aexit__(self, *args):
                await self.close()

            async def send(self, request, **kwargs):
                self.calls += 1
                return Response(request, status if self.calls == 1 else 200)

        transport = Transport()
        monkeypatch.setattr(_model_runners, "get_async_http_client", lambda: AsyncHttpPipeline(transport=transport))
        observations = []
        result = run(
            DecisionModelRunner(DECISION_CONFIG, execution_policy=DecisionExecutionPolicy(observer=observations.append))
        )
        assert transport.calls == 2
        assert result["model"] == "microsoft-decision-1"
        assert [receipt.attempt for receipt in observations] == [1, 2]
        assert [receipt.http_status for receipt in observations] == [status, 200]

    def test_default_credential_token_acquisition_runs_off_event_loop(self, client):
        from azure.ai.evaluation._legacy._common._async_token_provider import AsyncAzureTokenProvider

        client.response = FakeResponse(body=json.dumps(level_payload(4)).encode())
        loop_thread = threading.get_ident()
        token_threads = []

        def get_token(*scopes, **kwargs):
            token_threads.append(threading.get_ident())
            return SimpleNamespace(token="default-token")

        credential = Mock(get_token=get_token)
        config = {key: value for key, value in DECISION_CONFIG.items() if key != "api_key"}
        with patch.object(AsyncAzureTokenProvider, "_initialize_async", new=AsyncMock(return_value=credential)):
            run(DecisionModelRunner(config))
        assert token_threads and all(token_thread != loop_thread for token_thread in token_threads)
        assert client.calls[0]["headers"]["Authorization"] == "Bearer default-token"

    def test_default_credential_does_not_block_request_timeout(self, client):
        from azure.ai.evaluation._legacy._common._async_token_provider import AsyncAzureTokenProvider

        release = threading.Event()

        def get_token(*scopes, **kwargs):
            release.wait(timeout=2)
            return SimpleNamespace(token="default-token")

        credential = Mock(get_token=get_token)
        config = {key: value for key, value in DECISION_CONFIG.items() if key != "api_key"}

        async def request():
            try:
                with pytest.raises(EvaluationException, match="timed out"):
                    await DecisionModelRunner(config)(state={}, questions=QUESTIONS, timeout=0.02)
            finally:
                release.set()

        with patch.object(AsyncAzureTokenProvider, "_initialize_async", new=AsyncMock(return_value=credential)):
            asyncio.run(request())
        assert not client.calls

    @pytest.mark.parametrize(
        "status, blame",
        [
            (400, ErrorBlame.USER_ERROR),
            (401, ErrorBlame.USER_ERROR),
            (404, ErrorBlame.USER_ERROR),
            (429, ErrorBlame.SYSTEM_ERROR),
            (503, ErrorBlame.SYSTEM_ERROR),
        ],
    )
    def test_http_failures_are_sanitized(self, client, status, blame):
        client.response = FakeResponse(status, b"echoed test-key-value and secret detail")
        with pytest.raises(EvaluationException) as raised:
            run(DecisionModelRunner(DECISION_CONFIG))
        assert raised.value.blame == blame
        assert str(status) in str(raised.value)
        assert "test-key-value" not in str(raised.value) and "secret detail" not in str(raised.value)

    def test_transport_failure_is_sanitized(self, monkeypatch):
        class Broken(FakeClient):
            async def post(self, *_, **__):
                raise ConnectionError("https://example.services.ai.azure.com test-key-value")

        monkeypatch.setattr(_model_runners, "get_async_http_client", lambda: Broken())
        with pytest.raises(EvaluationException) as raised:
            run(DecisionModelRunner(DECISION_CONFIG))
        assert "test-key-value" not in str(raised.value) and "example.services" not in str(raised.value)

    def test_token_failure_is_a_user_error(self, client):
        credential = Mock(get_token=Mock(side_effect=RuntimeError("token-secret")))
        config = {key: value for key, value in DECISION_CONFIG.items() if key != "api_key"}
        with pytest.raises(EvaluationException) as raised:
            run(DecisionModelRunner(config, credential))
        assert raised.value.blame == ErrorBlame.USER_ERROR and "token-secret" not in str(raised.value)
        assert not client.calls

    def test_invalid_json(self, client):
        client.response = FakeResponse(body=b"not json")
        with pytest.raises(EvaluationException, match="invalid JSON"):
            run(DecisionModelRunner(DECISION_CONFIG))

    def test_timeout(self, client):
        client.delay = 1
        client.response = FakeResponse(body=json.dumps(decision_payload()).encode())
        with pytest.raises(EvaluationException, match="timed out"):
            run(DecisionModelRunner(DECISION_CONFIG), timeout=0.01)

    @pytest.mark.parametrize(
        "mutate",
        [
            lambda p: p.pop("answers"),
            lambda p: p["answers"].pop("status"),
            lambda p: p["answers"].update(extra={"type": "noul", "noul": 1}),
            lambda p: p["answers"]["status"].update(type="score"),
            lambda p: p.pop("usage"),
            lambda p: p["usage"].update(input_tokens=-1),
            lambda p: p["usage"].update(output_tokens=True),
            lambda p: p.update(model=" "),
        ],
    )
    def test_structurally_invalid_responses(self, client, mutate):
        payload = level_payload(4)
        mutate(payload)
        client.response = FakeResponse(body=json.dumps(payload).encode())
        with pytest.raises(EvaluationException, match="invalid response"):
            run(DecisionModelRunner(DECISION_CONFIG))

    def test_unsupported_question_type(self, client):
        with pytest.raises(EvaluationException, match="not supported") as raised:
            run(DecisionModelRunner(DECISION_CONFIG), questions={"team": {"type": "choice", "criteria": {}}})
        assert raised.value.blame == ErrorBlame.USER_ERROR
        assert not client.calls


class TestAnswerValidation:
    def test_noul(self):
        assert validate_noul_answer({"type": "noul", "noul": 0.25}) == 0.25
        for bad in (True, "0.5", None, float("nan"), -0.01, 1.01):
            with pytest.raises(ValueError):
                validate_noul_answer({"type": "noul", "noul": bad})

    def test_score_fields_do_not_require_consistency_checks(self):
        levels = [0.1, 0.2, 0.3, 0.4, 0.5]
        answer = score_answer(levels)
        answer["score"] = 0
        assert validate_score_answer(answer, 5) == levels

    @pytest.mark.parametrize(
        "mutate",
        [
            lambda a: a["probabilities"].pop("4"),
            lambda a: a["probabilities"].update({"5": 0.0}),
            lambda a: a["probabilities"].update({"4": 1.5}),
            lambda a: a.update(score=float("nan")),
            lambda a: a.update(score=True),
            lambda a: a.update(confidence=2),
        ],
    )
    def test_malformed_scores(self, mutate):
        answer = score_answer([0, 0, 0, 0, 1.0])
        mutate(answer)
        with pytest.raises(ValueError):
            validate_score_answer(answer, 5)


class ProbeModelEvaluator(ModelEvaluatorBase):
    _supports_decision_models = True

    async def _do_eval(self, eval_input):
        return await self._model_runner(timeout=self._LLM_CALL_TIMEOUT, **eval_input)


class TestSharedBaseSelection:
    def test_hierarchy(self):
        assert issubclass(ModelEvaluatorBase, EvaluatorBase)
        assert issubclass(PromptyEvaluatorBase, ModelEvaluatorBase)

    def test_decision_configuration_selects_the_decision_runner_without_loading_prompty(self):
        with patch.object(_model_runners.AsyncPrompty, "load", side_effect=AssertionError("prompty loaded")):
            evaluator = ProbeModelEvaluator(result_key="probe", model_config=DECISION_CONFIG)
        assert isinstance(evaluator._model_runner, DecisionModelRunner)
        assert evaluator._uses_decision_model and not hasattr(evaluator, "_flow")

    def test_decision_base_does_not_require_a_prompty_file(self):
        with patch.object(_model_runners.AsyncPrompty, "load", side_effect=AssertionError("prompty loaded")):
            evaluator = ProbeModelEvaluator(result_key="probe", model_config=DECISION_CONFIG)
        assert evaluator._decision_model_runner is evaluator._model_runner
        assert not hasattr(evaluator, "_flow")

    def test_chat_base_requires_a_prompty_file(self):
        with pytest.raises(EvaluationException, match="prompty_file"):
            ProbeModelEvaluator(result_key="probe", model_config=CHAT_CONFIG)

    def test_decision_runner_accessor_rejects_a_chat_runner(self):
        with patch.object(_model_runners.AsyncPrompty, "load"):
            evaluator = ProbeModelEvaluator(result_key="probe", prompty_file="probe.prompty", model_config=CHAT_CONFIG)
        with pytest.raises(RuntimeError, match="not configured"):
            _ = evaluator._decision_model_runner

    def test_replacing_legacy_flow_updates_runner_execution(self):
        with patch.object(_model_runners.AsyncPrompty, "load"):
            evaluator = ProbeModelEvaluator(result_key="probe", prompty_file="probe.prompty", model_config=CHAT_CONFIG)
        flow = AsyncMock(return_value={"llm_output": {"score": 1, "reason": "replacement", "properties": {}}})
        evaluator._flow = flow
        assert evaluator._prompty_model_runner.flow is flow
        inputs = {"query": "q", "response": "r"}
        assert asyncio.run(evaluator._do_eval(inputs)) == flow.return_value
        flow.assert_awaited_once_with(timeout=evaluator._LLM_CALL_TIMEOUT, **inputs)

    @pytest.mark.parametrize("tag", ["Decision", "system_one", "azure_openai", None, ""])
    def test_other_tags_are_not_decision_configurations(self, tag):
        assert not _model_runners.is_decision_model_config({**DECISION_CONFIG, "type": tag})
        with pytest.raises(EvaluationException):
            DecisionModelRunner({**DECISION_CONFIG, "type": tag})

    def test_chat_configuration_selects_the_prompty_runner_without_a_decision_runner(self):
        flow = AsyncMock()
        with patch.object(_model_runners.AsyncPrompty, "load", return_value=flow), patch.object(
            _model_runners, "DecisionModelRunner", side_effect=AssertionError("decision runner built")
        ):
            evaluator = ProbeModelEvaluator(result_key="probe", prompty_file="probe.prompty", model_config=CHAT_CONFIG)
        assert isinstance(evaluator._model_runner, PromptyModelRunner)
        assert evaluator._flow is flow and not evaluator._uses_decision_model

    def test_prompty_only_evaluators_reject_a_decision_configuration(self):
        with patch.object(_model_runners.AsyncPrompty, "load", side_effect=AssertionError("prompty loaded")):
            with pytest.raises(EvaluationException) as raised:
                FluencyEvaluator(DECISION_CONFIG)
        assert raised.value.blame == ErrorBlame.USER_ERROR
        assert "FluencyEvaluator" in str(raised.value)

    def test_wrapper_is_initialized_once(self):
        original = EvaluatorBase.__init__
        initialized = []

        def record(instance, **kwargs):
            initialized.append(instance)
            original(instance, **kwargs)

        with patch.object(EvaluatorBase, "__init__", record):
            evaluator = ProbeModelEvaluator(result_key="probe", model_config=DECISION_CONFIG)
        assert initialized == [evaluator]

    def test_prompty_load_parity(self):
        flow = AsyncMock()
        credential = object()
        with patch.object(_model_runners.AsyncPrompty, "load", return_value=flow) as load:
            evaluator = ProbeModelEvaluator(
                result_key="probe",
                prompty_file="probe.prompty",
                model_config=CHAT_CONFIG,
                credential=credential,
                threshold=4,
            )
        kwargs = load.call_args.kwargs
        assert kwargs["source"] == "probe.prompty"
        assert kwargs["token_credential"] is credential and kwargs["is_reasoning_model"] is False
        headers = kwargs["model"]["parameters"]["extra_headers"]
        assert headers["x-ms-useragent"].endswith("(type=evaluator subtype=ProbeModelEvaluator)")
        assert kwargs["model"]["configuration"]["api_version"] == "2024-02-15-preview"
        assert evaluator._threshold == 4 and evaluator._flow is flow

    def test_inherited_helpers_remain_available_to_prompty_evaluators(self):
        with patch.object(_model_runners.AsyncPrompty, "load"):
            evaluator = FluencyEvaluator(CHAT_CONFIG)
        assert isinstance(evaluator, PromptyEvaluatorBase)
        assert evaluator._get_binary_result(5) == "pass" and evaluator._get_binary_result(float("nan")) == "unknown"
        assert evaluator._get_token_metadata({"input_token_count": 3})["prompt_tokens"] == 3
        assert evaluator._return_not_applicable_result("why", 3)["fluency_status"] == "skipped"


def completion_payload(probability, status=0.95):
    return decision_payload(status, {"task_completion": {"type": "noul", "noul": probability}})


def strategy_with(payload, scoring, key="tool_call_accuracy", extra_properties=None):
    runner = AsyncMock(return_value=payload)
    runner.deployment = "Decision-1"
    return DecisionEvaluationStrategy(
        runner,
        result_key=key,
        error_target=ErrorTarget.TOOL_CALL_ACCURACY_EVALUATOR,
        questions={"status": {"type": "noul"}, key: {"type": "score"}},
        scoring=scoring,
        threshold=3,
        timeout=5,
        extra_properties=extra_properties,
    )


class TestSharedDecisionStrategy:
    @pytest.mark.parametrize("probability, score", [(0.6, 1.0), (0.5999, 0.0)])
    def test_binary_scoring_uses_its_own_cutoff(self, probability, score):
        strategy = strategy_with(completion_payload(probability), BinaryScoring(0.6), key="task_completion")
        assert asyncio.run(strategy.evaluate({}))["task_completion"] == score

    @pytest.mark.parametrize("minimum, score", [(0, 2.0), (1, 3.0)])
    def test_likert_scoring_offsets_the_level_by_the_scale_minimum(self, minimum, score):
        strategy = strategy_with(level_payload(2), LikertScoring(5, minimum=minimum))
        assert asyncio.run(strategy.evaluate({}))["tool_call_accuracy"] == score

    def test_likert_scoring_selects_the_lowest_tied_level(self):
        payload = decision_payload(0.95, {"tool_call_accuracy": score_answer([0.0, 0.5, 0.0, 0.5, 0.0])})
        assert asyncio.run(strategy_with(payload, LikertScoring(5)).evaluate({}))["tool_call_accuracy"] == 2.0

    def test_invalid_answer_reports_the_evaluator_error_target(self):
        payload = level_payload(4)
        payload["answers"]["tool_call_accuracy"]["probabilities"]["0"] = 1.5
        with pytest.raises(EvaluationException) as raised:
            asyncio.run(strategy_with(payload, LikertScoring(5)).evaluate({}))
        assert raised.value.target == ErrorTarget.TOOL_CALL_ACCURACY_EVALUATOR

    def test_extra_properties_are_added_with_the_decision_provenance(self):
        strategy = strategy_with(
            level_payload(4), LikertScoring(5), extra_properties=lambda eval_input: {"calls": len(eval_input["calls"])}
        )
        properties = asyncio.run(strategy.evaluate({"calls": [1, 2]}))["tool_call_accuracy_properties"]
        assert properties["calls"] == 2 and properties["decision_model"]["deployment"] == "Decision-1"

    def test_skipped_unusable_score_retains_known_usage_and_provenance(self):
        payload = level_payload(4, status=0.1)
        payload["answers"]["tool_call_accuracy"]["probabilities"] = None
        result = asyncio.run(strategy_with(payload, LikertScoring(5)).evaluate({}))
        assert result["tool_call_accuracy_status"] == "skipped"
        assert result["tool_call_accuracy"] is None
        properties = result["tool_call_accuracy_properties"]
        assert (properties["prompt_tokens"], properties["completion_tokens"], properties["total_tokens"]) == (
            120,
            3,
            123,
        )
        assert properties["model"] == "microsoft-decision-1"
        assert properties["decision_model"]["status_completion_probability"] == 0.1
        assert "native_answer" not in properties["decision_model"]
        assert "sample_input" not in properties and "finish_reason" not in properties

    def test_semantic_failure_retains_known_usage_and_provenance(self):
        payload = level_payload(4)
        payload["answers"]["tool_call_accuracy"]["confidence"] = float("nan")
        with pytest.raises(EvaluationException) as raised:
            asyncio.run(strategy_with(payload, LikertScoring(5)).evaluate({}))
        assert raised.value.properties["total_tokens"] == 123
        assert raised.value.properties["decision_model"]["deployment"] == "Decision-1"

    @pytest.mark.parametrize("status", [float("nan"), float("inf"), float("-inf"), "invalid", None, True, -0.1, 1.1])
    def test_invalid_status_error_properties_are_strict_json_with_known_metadata(self, client, status):
        client.response = FakeResponse(body=json.dumps(level_payload(4, status=status)).encode())
        strategy = DecisionEvaluationStrategy(
            DecisionModelRunner(DECISION_CONFIG),
            result_key="tool_call_accuracy",
            error_target=ErrorTarget.TOOL_CALL_ACCURACY_EVALUATOR,
            questions=QUESTIONS,
            scoring=LikertScoring(5),
            threshold=3,
            timeout=5,
        )
        with pytest.raises(EvaluationException) as raised:
            asyncio.run(strategy.evaluate({}))
        properties = raised.value.properties
        assert json.loads(json.dumps(properties, allow_nan=False)) == properties
        assert (properties["prompt_tokens"], properties["completion_tokens"], properties["total_tokens"]) == (
            120,
            3,
            123,
        )
        assert properties["model"] == "microsoft-decision-1"
        provenance = properties["decision_model"]
        assert provenance["deployment"] == "Decision-1"
        assert provenance["model"] == "microsoft-decision-1"
        for field, question_id in (("rubric_hash", "tool_call_accuracy"), ("status_rubric_hash", "status")):
            assert (
                provenance[field]
                == hashlib.sha256(json.dumps(QUESTIONS[question_id], sort_keys=True).encode("utf-8")).hexdigest()
            )
        assert "native_status_answer" not in provenance
        assert "status_completion_probability" not in provenance

    @pytest.mark.parametrize("status, expected", [(0.4999, "skipped"), (0.5, "completed")])
    def test_applicability_cutoff_remains_fixed(self, status, expected):
        payload = level_payload(4, status=status)
        result = asyncio.run(strategy_with(payload, LikertScoring(5)).evaluate({}))
        assert result["tool_call_accuracy_status"] == expected
        assert result["tool_call_accuracy_properties"]["decision_model"]["status_probability_threshold"] == 0.5
        assert result["tool_call_accuracy_properties"]["decision_model"]["native_status_answer"] == (
            payload["answers"]["status"]
        )

    def test_successful_properties_preserve_common_metadata_shape(self):
        properties = asyncio.run(strategy_with(level_payload(4), LikertScoring(5)).evaluate({}))[
            "tool_call_accuracy_properties"
        ]
        assert set(properties) == {
            "decision_model",
            "prompt_tokens",
            "completion_tokens",
            "total_tokens",
            "finish_reason",
            "model",
            "sample_input",
            "sample_output",
        }
        assert {key: value for key, value in properties.items() if key != "decision_model"} == (
            ModelEvaluatorBase._get_token_metadata(
                {
                    "input_token_count": 120,
                    "output_token_count": 3,
                    "total_token_count": 123,
                    "model_id": "microsoft-decision-1",
                }
            )
        )


class TestDecisionExecutionPolicy:
    def test_policy_and_receipts_are_immutable(self):
        with pytest.raises(FrozenInstanceError):
            DecisionExecutionPolicy().max_retries = 4
        with pytest.raises(FrozenInstanceError):
            DecisionRequestObservation(1, "response").attempt = 2

    @pytest.mark.parametrize(
        "options",
        [
            {"timeout_seconds": 0},
            {"timeout_seconds": True},
            {"timeout_seconds": float("nan")},
            {"deadline_seconds": -1},
            {"deadline_seconds": float("inf")},
            {"max_retries": True},
            {"max_retries": -1},
            {"max_retries": 1.5},
            {"max_request_bytes": 0},
            {"max_state_question_bytes": False},
            {"max_response_bytes": "100"},
            {"observer": "callback"},
            {"cancellation_requested": False},
        ],
    )
    def test_invalid_policy(self, options):
        with pytest.raises(ValueError):
            DecisionExecutionPolicy(**options)

    def test_base_forwards_policy_outside_strict_config(self):
        policy = DecisionExecutionPolicy(max_retries=0)
        evaluator = ProbeModelEvaluator(
            result_key="probe", model_config=DECISION_CONFIG, decision_execution_policy=policy
        )
        assert evaluator._decision_model_runner._execution_policy is policy
        with pytest.raises(EvaluationException, match="Unsupported"):
            DecisionModelRunner({**DECISION_CONFIG, "decision_execution_policy": policy})
        with pytest.raises(EvaluationException, match="DecisionExecutionPolicy"):
            DecisionModelRunner(DECISION_CONFIG, execution_policy={})

    def test_explicit_policy_on_prompty_is_rejected_without_loading_a_flow(self):
        with patch.object(_model_runners.AsyncPrompty, "load") as load:
            with pytest.raises(EvaluationException, match="only supported"):
                ProbeModelEvaluator(
                    result_key="probe",
                    prompty_file="probe.prompty",
                    model_config=CHAT_CONFIG,
                    decision_execution_policy=DecisionExecutionPolicy(),
                )
        load.assert_not_called()

    def test_transport_timeout_and_single_retry_policy(self, client):
        client.response = FakeResponse(body=json.dumps(level_payload(4)).encode())
        policy = DecisionExecutionPolicy(timeout_seconds=2, max_retries=7)
        run(DecisionModelRunner(DECISION_CONFIG, execution_policy=policy))
        retry = client.policies["retry_policy"]
        assert retry.total_retries == retry.connect_retries == retry.read_retries == retry.status_retries == 7
        assert client.calls[0]["options"]["connection_timeout"] == 2
        assert client.calls[0]["options"]["read_timeout"] == 2

    @pytest.mark.parametrize("field", ["max_request_bytes", "max_state_question_bytes"])
    def test_request_budget_exact_boundary_and_no_send_on_overflow(self, client, field):
        state = {"query": "\u00e9"}
        if field == "max_request_bytes":
            body = {"model": "Decision-1", "state": state, "questions": QUESTIONS}
            size = len(json.dumps(body, ensure_ascii=False, separators=(",", ":"), allow_nan=False).encode("utf-8"))
        else:
            size = max(
                len(
                    json.dumps(
                        {"state": state, "question": question},
                        ensure_ascii=False,
                        separators=(",", ":"),
                        allow_nan=False,
                    ).encode("utf-8")
                )
                for question in QUESTIONS.values()
            )
        client.response = FakeResponse(body=json.dumps(level_payload(4)).encode())
        run(
            DecisionModelRunner(DECISION_CONFIG, execution_policy=DecisionExecutionPolicy(**{field: size})), state=state
        )
        assert b"\xc3\xa9" in client.calls[0]["content"] and b"\\u00e9" not in client.calls[0]["content"]
        client.calls.clear()
        with pytest.raises(EvaluationException, match="byte budget") as raised:
            run(
                DecisionModelRunner(DECISION_CONFIG, execution_policy=DecisionExecutionPolicy(**{field: size - 1})),
                state=state,
            )
        assert not client.calls
        assert raised.value.observations == (DecisionRequestObservation(0, "request_rejected"),)

    def test_non_json_request_is_rejected_before_authentication_or_network(self, client):
        with pytest.raises(EvaluationException, match="JSON-serializable") as raised:
            run(DecisionModelRunner(DECISION_CONFIG), state={"value": float("nan")})
        assert not client.calls and raised.value.observations[0].outcome == "request_rejected"

    def test_response_budget_exact_boundary(self, client):
        content = json.dumps(level_payload(4)).encode()
        client.response = FakeResponse(body=content)
        run(
            DecisionModelRunner(
                DECISION_CONFIG, execution_policy=DecisionExecutionPolicy(max_response_bytes=len(content))
            )
        )
        with pytest.raises(EvaluationException, match="byte budget"):
            run(
                DecisionModelRunner(
                    DECISION_CONFIG, execution_policy=DecisionExecutionPolicy(max_response_bytes=len(content) - 1)
                )
            )

    def test_structural_failure_preserves_usage_before_answer_validation(self, client):
        payload = level_payload(4)
        payload["answers"] = {}
        client.response = FakeResponse(body=json.dumps(payload).encode())
        receipts = []
        with pytest.raises(EvaluationException, match="invalid response") as raised:
            run(
                DecisionModelRunner(DECISION_CONFIG, execution_policy=DecisionExecutionPolicy(observer=receipts.append))
            )
        assert receipts == list(raised.value.observations)
        assert receipts[0].input_tokens == 120 and receipts[0].output_tokens == 3
        assert receipts[0].model == "microsoft-decision-1"

    def test_unknown_or_invalid_usage_is_not_fabricated(self, client):
        client.response = FakeResponse(body=json.dumps({"usage": {"input_tokens": True, "output_tokens": 3}}).encode())
        with pytest.raises(EvaluationException) as raised:
            run(DecisionModelRunner(DECISION_CONFIG))
        receipt = raised.value.observations[0]
        assert receipt.input_tokens is None and receipt.output_tokens == 3 and receipt.model is None

    def test_observer_failure_is_explicit_sanitized_and_retains_receipt(self, client):
        client.response = FakeResponse(body=json.dumps(level_payload(4)).encode())
        observer = Mock(side_effect=RuntimeError("observer-secret"))
        with pytest.raises(EvaluationException, match="observer failed") as raised:
            run(DecisionModelRunner(DECISION_CONFIG, execution_policy=DecisionExecutionPolicy(observer=observer)))
        assert "observer-secret" not in str(raised.value)
        assert raised.value.observations[0].input_tokens == 120

    def test_deadline_caps_existing_evaluator_timeout(self, client):
        client.delay = 1
        with pytest.raises(EvaluationException, match="timed out") as raised:
            run(DecisionModelRunner(DECISION_CONFIG, execution_policy=DecisionExecutionPolicy(deadline_seconds=0.01)))
        assert raised.value.observations[-1].outcome == "timeout"

    def test_evaluator_timeout_still_wins_over_longer_policy_deadline(self, client):
        client.delay = 1
        with pytest.raises(EvaluationException, match="timed out"):
            run(
                DecisionModelRunner(DECISION_CONFIG, execution_policy=DecisionExecutionPolicy(deadline_seconds=5)),
                timeout=0.01,
            )

    def test_precancellation_does_not_send(self, client):
        with pytest.raises(EvaluationException, match="cancelled") as raised:
            run(
                DecisionModelRunner(
                    DECISION_CONFIG, execution_policy=DecisionExecutionPolicy(cancellation_requested=lambda: True)
                )
            )
        assert not client.calls and raised.value.observations[-1].outcome == "cancelled"

    def test_inflight_cancellation_cleans_up_request(self, monkeypatch):
        cleaned_up = []

        class WaitingClient(FakeClient):
            async def post(self, *args, **kwargs):
                try:
                    await asyncio.sleep(10)
                finally:
                    cleaned_up.append(True)

        monkeypatch.setattr(_model_runners, "get_async_http_client", WaitingClient)

        async def request():
            cancelled = False

            async def cancel():
                nonlocal cancelled
                await asyncio.sleep(0.01)
                cancelled = True

            cancellation = asyncio.create_task(cancel())
            try:
                runner = DecisionModelRunner(
                    DECISION_CONFIG, execution_policy=DecisionExecutionPolicy(cancellation_requested=lambda: cancelled)
                )
                with pytest.raises(EvaluationException, match="cancelled") as raised:
                    await runner(state={}, questions=QUESTIONS, timeout=1)
                assert raised.value.observations[-1].outcome == "cancelled"
            finally:
                await cancellation

        asyncio.run(request())
        assert cleaned_up == [True]

    @pytest.mark.parametrize("value", [None, "yes", 1])
    def test_cancellation_callback_requires_boolean(self, client, value):
        with pytest.raises(EvaluationException, match="boolean"):
            run(
                DecisionModelRunner(
                    DECISION_CONFIG, execution_policy=DecisionExecutionPolicy(cancellation_requested=lambda: value)
                )
            )
        assert not client.calls

    @pytest.mark.parametrize("field", ["max_request_bytes", "max_state_question_bytes"])
    def test_tiny_positive_budget_rejects_before_send(self, client, field):
        with pytest.raises(EvaluationException, match="byte budget"):
            run(DecisionModelRunner(DECISION_CONFIG, execution_policy=DecisionExecutionPolicy(**{field: 1})))
        assert not client.calls

    def test_callback_failure_during_authentication_retains_error_receipt(self, client):
        config = {key: value for key, value in DECISION_CONFIG.items() if key != "api_key"}
        credential = Mock(get_token=Mock(side_effect=RuntimeError("credential-secret")))
        observer = Mock(side_effect=RuntimeError("observer-secret"))
        with pytest.raises(EvaluationException, match="observer failed") as raised:
            run(DecisionModelRunner(config, credential, execution_policy=DecisionExecutionPolicy(observer=observer)))
        assert raised.value.observations == (DecisionRequestObservation(0, "error"),)
        assert "secret" not in str(raised.value)
        assert not client.calls

    @pytest.mark.parametrize("termination", ["timeout", "cancelled"])
    def test_termination_while_authenticating_does_not_send(self, client, termination):
        config = {key: value for key, value in DECISION_CONFIG.items() if key != "api_key"}
        cleaned_up = []

        async def get_token(*_):
            try:
                await asyncio.sleep(10)
            finally:
                cleaned_up.append(True)

        credential = Mock(get_token=get_token)

        async def request():
            cancel = asyncio.Event()
            loop = asyncio.get_running_loop()
            handle = loop.call_later(0.01, cancel.set)
            policy = DecisionExecutionPolicy(
                deadline_seconds=0.02 if termination == "timeout" else 1,
                cancellation_requested=cancel.is_set if termination == "cancelled" else None,
            )
            try:
                with pytest.raises(EvaluationException) as raised:
                    await DecisionModelRunner(config, credential, execution_policy=policy)(
                        state={}, questions=QUESTIONS, timeout=1
                    )
                assert raised.value.observations == (DecisionRequestObservation(0, termination),)
            finally:
                handle.cancel()

        asyncio.run(request())
        assert cleaned_up == [True] and not client.calls

    @pytest.mark.parametrize("termination", ["timeout", "cancelled"])
    def test_queued_default_auth_does_not_create_an_unawaited_coroutine(self, client, termination):
        config = {key: value for key, value in DECISION_CONFIG.items() if key != "api_key"}
        entered = threading.Event()
        release = threading.Event()

        def occupy_worker():
            entered.set()
            release.wait(timeout=5)

        async def request():
            loop = asyncio.get_running_loop()
            loop.set_default_executor(ThreadPoolExecutor(max_workers=1))
            occupied = loop.run_in_executor(None, occupy_worker)
            cancel = asyncio.Event()
            handle = None
            try:
                while not entered.is_set():
                    await asyncio.sleep(0)
                handle = loop.call_later(0.01, cancel.set)
                policy = DecisionExecutionPolicy(
                    deadline_seconds=0.03 if termination == "timeout" else 1,
                    cancellation_requested=cancel.is_set if termination == "cancelled" else None,
                )
                with patch.object(DecisionModelRunner, "_get_default_token", new_callable=AsyncMock) as get_token:
                    with pytest.raises(EvaluationException) as raised:
                        await DecisionModelRunner(config, execution_policy=policy)(
                            state={}, questions=QUESTIONS, timeout=1
                        )
                    assert raised.value.observations == (DecisionRequestObservation(0, termination),)
                    get_token.assert_not_called()
            finally:
                if handle is not None:
                    handle.cancel()
                release.set()
                await occupied

        asyncio.run(request())
        assert not client.calls

    @pytest.mark.parametrize("termination", ["timeout", "cancelled"])
    @pytest.mark.parametrize("waiting", ["send", "retry_backoff"])
    def test_real_pipeline_termination_retains_actual_attempt(self, monkeypatch, termination, waiting):
        from azure.ai.evaluation._http_utils import AsyncHttpPipeline

        cancelled = False
        cleaned_up = []

        class Response(HttpResponse):
            def __init__(self, request):
                super().__init__(request, None)
                self.status_code = 429
                self.headers = {"Retry-After": "10"}

            def body(self):
                return json.dumps(level_payload(4)).encode()

        class Transport(AsyncHttpTransport):
            def __init__(self):
                self.calls = 0

            async def open(self):
                pass

            async def close(self):
                pass

            async def __aexit__(self, *_):
                await self.close()

            async def send(self, request, **kwargs):
                self.calls += 1
                if waiting == "retry_backoff":
                    return Response(request)
                try:
                    await asyncio.sleep(10)
                finally:
                    cleaned_up.append(True)

        transport = Transport()
        monkeypatch.setattr(_model_runners, "get_async_http_client", lambda: AsyncHttpPipeline(transport=transport))

        async def request():
            nonlocal cancelled
            loop = asyncio.get_running_loop()

            def cancel():
                nonlocal cancelled
                cancelled = True

            handle = loop.call_later(0.01, cancel)
            policy = DecisionExecutionPolicy(
                deadline_seconds=0.08 if termination == "timeout" else 1,
                cancellation_requested=(lambda: cancelled) if termination == "cancelled" else None,
            )
            try:
                with pytest.raises(EvaluationException) as raised:
                    await DecisionModelRunner(DECISION_CONFIG, execution_policy=policy)(
                        state={}, questions=QUESTIONS, timeout=1
                    )
                receipts = raised.value.observations
                assert receipts[-1] == DecisionRequestObservation(1, termination)
                if waiting == "retry_backoff":
                    assert receipts[0].http_status == 429 and receipts[0].input_tokens == 120
            finally:
                handle.cancel()

        asyncio.run(request())
        assert transport.calls == 1
        assert cleaned_up == ([True] if waiting == "send" else [])

    @pytest.mark.parametrize("observer_fails", [False, True])
    def test_real_pipeline_transport_errors_retain_each_attempt(self, monkeypatch, observer_fails):
        from azure.ai.evaluation._http_utils import AsyncHttpPipeline

        class Transport(AsyncHttpTransport):
            def __init__(self):
                self.calls = 0

            async def open(self):
                pass

            async def close(self):
                pass

            async def __aexit__(self, *_):
                await self.close()

            async def send(self, request, **kwargs):
                self.calls += 1
                raise ServiceRequestError("transport-secret")

        transport = Transport()
        monkeypatch.setattr(_model_runners, "get_async_http_client", lambda: AsyncHttpPipeline(transport=transport))
        observer = Mock(side_effect=RuntimeError("observer-secret")) if observer_fails else Mock()
        policy = DecisionExecutionPolicy(max_retries=1, observer=observer)
        with pytest.raises(EvaluationException) as raised:
            run(DecisionModelRunner(DECISION_CONFIG, execution_policy=policy))
        expected = 1 if observer_fails else 2
        assert transport.calls == expected
        assert raised.value.observations == tuple(
            DecisionRequestObservation(i, "error") for i in range(1, expected + 1)
        )
        assert observer.call_count == expected
        assert "secret" not in str(raised.value)

    def test_real_pipeline_observer_failure_preserves_response_receipt(self, monkeypatch):
        from azure.ai.evaluation._http_utils import AsyncHttpPipeline

        class Response(HttpResponse):
            def __init__(self, request):
                super().__init__(request, None)
                self.status_code = 200
                self.headers = {}

            def body(self):
                return json.dumps(level_payload(4)).encode()

        class Transport(AsyncHttpTransport):
            async def open(self):
                pass

            async def close(self):
                pass

            async def __aexit__(self, *_):
                await self.close()

            async def send(self, request, **kwargs):
                return Response(request)

        monkeypatch.setattr(_model_runners, "get_async_http_client", lambda: AsyncHttpPipeline(transport=Transport()))
        observer = Mock(side_effect=RuntimeError("observer-secret"))
        with pytest.raises(EvaluationException, match="observer failed") as raised:
            run(DecisionModelRunner(DECISION_CONFIG, execution_policy=DecisionExecutionPolicy(observer=observer)))
        assert raised.value.observations == (
            DecisionRequestObservation(1, "response", 200, 120, 3, "microsoft-decision-1"),
        )
        assert observer.call_count == 1 and "secret" not in str(raised.value)
