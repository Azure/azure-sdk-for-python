# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

"""Offline tests for shared decision-model runners, base selection, and evaluation strategy."""

import asyncio
import json
import threading
from types import SimpleNamespace
from unittest.mock import AsyncMock, Mock, patch

import pytest
from azure.core.pipeline.policies import AsyncRedirectPolicy, AsyncRetryPolicy
from azure.core.pipeline.transport import AsyncHttpTransport, HttpResponse

from azure.ai.evaluation import FluencyEvaluator
from azure.ai.evaluation._evaluators._common import EvaluatorBase, ModelEvaluatorBase, PromptyEvaluatorBase
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

    async def post(self, url, json=None, headers=None, **options):  # pylint: disable=redefined-outer-name
        self.calls.append({"url": url, "json": json, "headers": dict(headers), "options": options})
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
        result = run(DecisionModelRunner(DECISION_CONFIG))
        assert transport.calls == 2
        assert result["model"] == "microsoft-decision-1"

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
