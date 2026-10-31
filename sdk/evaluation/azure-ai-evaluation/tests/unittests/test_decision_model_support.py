# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

"""Offline tests for shared decision-model runners, base selection, and evaluation strategy."""

import asyncio
import gc
import hashlib
import json
import logging
import math
import sys
import threading
import time
import weakref
from copy import deepcopy
from logging.handlers import BufferingHandler
from concurrent.futures import ThreadPoolExecutor
from types import ModuleType, SimpleNamespace
from unittest.mock import AsyncMock, Mock, call, patch

import pytest
from openai.types.chat import ChatCompletion
from azure.core.credentials import AccessToken
from azure.core.pipeline.policies import AsyncRedirectPolicy, AsyncRetryPolicy
from azure.core.pipeline.transport import AsyncHttpTransport, HttpResponse
from azure.core.exceptions import ServiceRequestError

from azure.ai.evaluation import CoherenceEvaluator, FluencyEvaluator
from azure.ai.evaluation._evaluators._common import EvaluatorBase, ModelEvaluatorBase, PromptyEvaluatorBase
from azure.ai.evaluation._evaluators._common import _model_runners
from azure.ai.evaluation._evaluators._common._decision_strategy import (
    BinaryScoring,
    DecisionEvaluationStrategy,
    DecisionRefusalError,
    LikertScoring,
)
from azure.ai.evaluation._evaluators._common._model_runners import (
    DecisionModelRunner,
    PromptyModelRunner,
    validate_noul_answer,
    validate_score_answer,
)
from azure.ai.evaluation._exceptions import ErrorBlame, ErrorCategory, ErrorTarget, EvaluationException
from azure.ai.evaluation._evaluators._common._model_runners import DecisionExecution, validated_execution

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


class FakeResponse(HttpResponse):
    def __init__(self, status_code=200, body=b"{}", request=None):
        super().__init__(request, None)
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
    monkeypatch.setattr(_model_runners, "get_async_http_client", lambda **_: fake)
    return fake


QUESTIONS = {
    "status": {"type": "noul", "instructions": "Applicable?"},
    "tool_call_accuracy": {"type": "score", "instructions": "How accurate?", "criteria": ["a", "b", "c", "d", "e"]},
}


def run(runner, **overrides):
    arguments = {"state": {"query": "q"}, "questions": QUESTIONS, "timeout": 5}
    arguments.update(overrides)
    return asyncio.run(runner(**arguments))


def watch_token_queue(credential, requests):
    """Return an event set once ``requests`` threads have queued for the credential's Decision token request.

    Each request reads the cache's attempt count before it queues, so a token request released after this event
    fails while every request is queued, whatever the thread scheduling.
    """
    entry = _model_runners._TOKENS._entry(credential, _model_runners._DECISION_TOKEN_SCOPE, create=True)
    lock, queued, all_queued = entry.lock, set(), threading.Event()

    class QueueWatchingLock:
        def acquire(self, *args, **kwargs):
            queued.add(threading.get_ident())
            if len(queued) >= requests:
                all_queued.set()
            return lock.acquire(*args, **kwargs)

        def release(self):
            lock.release()

    entry.lock = QueueWatchingLock()
    return all_queued


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
    def test_endpoint_requires_secure_resource_url(self, endpoint):
        if endpoint in (
            "https://example.services.ai.azure.com",
            "https://example.services.ai.azure.com/",
            "https://example.services.ai.azure.com/api/projects/proj",
        ):
            runner = DecisionModelRunner({**DECISION_CONFIG, "azure_endpoint": endpoint})
            assert runner._url == endpoint.rstrip("/") + "/providers/microsoft/v1/systemone"
        else:
            with pytest.raises(EvaluationException, match="HTTPS"):
                DecisionModelRunner({**DECISION_CONFIG, "azure_endpoint": endpoint})

    @pytest.mark.parametrize(
        "endpoint",
        ["http://localhost:8080", "http://LOCALHOST", "http://127.0.0.1:8080", "http://127.1.2.3", "http://[::1]:8080"],
    )
    def test_http_is_allowed_for_loopback(self, endpoint):
        runner = DecisionModelRunner({**DECISION_CONFIG, "azure_endpoint": endpoint})
        assert runner._url == endpoint.rstrip("/") + "/providers/microsoft/v1/systemone"

    @pytest.mark.parametrize("authentication", ["key", "credential", "default"])
    @pytest.mark.parametrize(
        "endpoint",
        [
            "http://example.services.ai.azure.com",
            "http://localhost.example.com",
            "http://example-localhost",
            "http://127.0.0.1.example.com",
            "http://localhost@evil.example",
            "http://evil.example@localhost",
            "http://0.0.0.0",
            "http://192.168.1.1",
            "http://[::2]",
            "http://local\thost",
            "https://example.com\\@localhost",
            "https://example.com?x=1",
            "https://example.com#fragment",
            "https://",
            "https://example.com:bad",
            "https://example.com:70000",
            "https://example.com:",
            "https://bad^host",
            "https://bad..host",
            "http://[::1%25anything]",
            "https://example.com?",
            "ftp://localhost",
            "not-a-url",
        ],
    )
    def test_invalid_endpoint_is_rejected_before_authentication_or_transport(self, client, endpoint, authentication):
        config = {**DECISION_CONFIG, "azure_endpoint": endpoint}
        credential = Mock()
        if authentication != "key":
            config.pop("api_key")
        with pytest.raises(EvaluationException, match="HTTPS") as raised:
            DecisionModelRunner(config, credential if authentication == "credential" else None)
        assert raised.value.blame == ErrorBlame.USER_ERROR
        assert endpoint not in str(raised.value)
        credential.get_token.assert_not_called()
        assert not client.calls

    def test_binary_probability_threshold(self):
        assert DecisionModelRunner(DECISION_CONFIG, binary=True).probability_threshold == 0.75
        runner = DecisionModelRunner({**DECISION_CONFIG, "probability_threshold": 0.7}, binary=True)
        assert runner.probability_threshold == 0.7

    def test_api_key_wins_over_credential(self):
        class IgnoredCredential:
            @property
            def get_token(self):
                raise AssertionError("Ignored credential must not be inspected.")

        runner = DecisionModelRunner(DECISION_CONFIG, credential=IgnoredCredential())
        assert runner._credential is None and runner._api_key == DECISION_CONFIG["api_key"]

    @pytest.mark.parametrize(
        "credential", [None, object(), "token-secret", {"get_token": "secret"}, SimpleNamespace(get_token=3)]
    )
    @pytest.mark.parametrize("in_config", [False, True])
    def test_missing_or_invalid_explicit_auth_is_rejected_at_construction(self, client, credential, in_config):
        config = {key: value for key, value in DECISION_CONFIG.items() if key != "api_key"}
        if in_config:
            config["credential"] = credential
        with pytest.raises(EvaluationException, match="callable 'get_token'") as raised:
            DecisionModelRunner(config, None if in_config else credential)
        assert raised.value.blame == ErrorBlame.USER_ERROR
        assert raised.value.category == ErrorCategory.INVALID_VALUE
        assert raised.value.target == ErrorTarget.EVALUATE
        assert "token-secret" not in str(raised.value)
        assert not client.calls

    def test_constructor_credential_takes_precedence_without_identity_fallback(self):
        config = {key: value for key, value in DECISION_CONFIG.items() if key != "api_key"}
        configured = Mock()
        supplied = Mock()
        assert DecisionModelRunner({**config, "credential": configured}, supplied)._credential is supplied
        with pytest.raises(EvaluationException, match="callable 'get_token'"):
            DecisionModelRunner({**config, "credential": configured}, object())


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
        monkeypatch.setattr(_model_runners, "get_async_http_client", lambda **_: AsyncHttpPipeline(transport=transport))
        result = run(DecisionModelRunner(DECISION_CONFIG))
        assert transport.calls == 2
        assert result["model"] == "microsoft-decision-1"

    def test_explicit_sync_credential_token_acquisition_runs_off_event_loop(self, client):
        client.response = FakeResponse(body=json.dumps(level_payload(4)).encode())
        loop_thread = threading.get_ident()
        token_threads = []

        def get_token(*scopes, **kwargs):
            token_threads.append(threading.get_ident())
            return SimpleNamespace(token="default-token")

        credential = Mock(get_token=get_token)
        config = {key: value for key, value in DECISION_CONFIG.items() if key != "api_key"}
        run(DecisionModelRunner(config, credential))
        assert token_threads and all(token_thread != loop_thread for token_thread in token_threads)
        credential.close.assert_not_called()
        assert client.calls[0]["headers"]["Authorization"] == "Bearer default-token"

    def test_explicit_sync_credential_does_not_block_request_timeout(self, client):
        release = threading.Event()

        def get_token(*scopes, **kwargs):
            release.wait(timeout=2)
            return SimpleNamespace(token="default-token")

        credential = Mock(get_token=get_token)
        config = {key: value for key, value in DECISION_CONFIG.items() if key != "api_key"}

        async def request():
            try:
                with pytest.raises(EvaluationException, match="timed out"):
                    await DecisionModelRunner(config, credential)(state={}, questions=QUESTIONS, timeout=0.02)
            finally:
                release.set()

        asyncio.run(request())
        assert not client.calls
        credential.close.assert_not_called()

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

    @pytest.mark.parametrize(
        "status,response_limit,code",
        [
            (404, 1024, "DeploymentNotFound"),
            (500, 1024, "InvalidRequest"),
            (404, 1024, "RateLimitExceeded"),
            (404, 1024, "secret_like_identifier_123"),
            (500, 1024, "A" * 128),
            (404, 1, "DeploymentNotFound"),
            (500, 1, "InvalidRequest"),
        ],
    )
    def test_provider_http_error_code_preserves_classification_and_accepted_metadata(
        self, client, status, response_limit, code
    ):
        payload = decision_payload()
        payload["error"] = {
            "code": code,
            "message": "test-key-value and private-message",
            "details": "private-details",
        }
        client.response = FakeResponse(status, json.dumps(payload).encode())
        with pytest.raises(EvaluationException) as raised:
            run(DecisionModelRunner(DECISION_CONFIG, max_retries=0, max_response_bytes=response_limit))
        diagnostic = f" ({code})" if response_limit == 1024 else ""
        prefix = "UserError" if status == 404 else "InternalError"
        assert str(raised.value) == f"({prefix}) The decision model returned HTTP {status}{diagnostic}."
        assert raised.value.blame == (ErrorBlame.USER_ERROR if status == 404 else ErrorBlame.SYSTEM_ERROR)
        assert raised.value.category == ErrorCategory.FAILED_EXECUTION
        assert raised.value.target == ErrorTarget.EVALUATE
        execution = raised.value.properties["decision_model"].pop("execution")
        assert validated_execution(execution) == execution
        assert execution["outcome"] == "error"
        assert raised.value.properties == (
            {
                "decision_model": {"deployment": "Decision-1", "protocol": "microsoft"},
                "prompt_tokens": 120,
                "completion_tokens": 3,
                "total_tokens": 123,
                "model": "microsoft-decision-1",
            }
            if response_limit == 1024
            else {"decision_model": {"deployment": "Decision-1", "protocol": "microsoft"}}
        )

    @pytest.mark.parametrize(
        "protocol, status, code, fix",
        [
            ("microsoft", 400, "unknown_model", "set decision_protocol to 'openai'."),
            ("openai", 404, "model_not_found", "set decision_protocol to 'microsoft' or remove it."),
        ],
    )
    def test_a_deployment_that_serves_the_other_protocol_names_the_fix(self, client, protocol, status, code, fix):
        payload = {"error": {"code": code, "message": "test-key-value and private-message"}}
        client.response = FakeResponse(status, json.dumps(payload).encode())
        with pytest.raises(EvaluationException) as raised:
            run(DecisionModelRunner({**DECISION_CONFIG, "decision_protocol": protocol}, max_retries=0))
        message = str(raised.value)
        assert message.startswith(f"(UserError) The decision model returned HTTP {status} ({code}). The deployment")
        assert message.endswith(fix)
        assert "test-key-value" not in message and "private-message" not in message
        assert raised.value.blame == ErrorBlame.USER_ERROR
        assert raised.value.properties["decision_model"]["protocol"] == protocol

    @pytest.mark.parametrize(
        "protocol, code",
        [
            ("microsoft", "model_not_found"),
            ("openai", "unknown_model"),
            ("microsoft", "DeploymentNotFound"),
            ("openai", "DeploymentNotFound"),
        ],
    )
    def test_other_error_codes_get_no_protocol_hint(self, client, protocol, code):
        client.response = FakeResponse(404, json.dumps({"error": {"code": code}}).encode())
        with pytest.raises(EvaluationException) as raised:
            run(DecisionModelRunner({**DECISION_CONFIG, "decision_protocol": protocol}, max_retries=0))
        assert str(raised.value) == f"(UserError) The decision model returned HTTP 404 ({code})."

    @pytest.mark.parametrize(
        "payload",
        [
            {"error": {"code": ""}},
            {"error": {"code": "InvalidRequest\nprivate-message"}},
            {"error": {"code": "A" * 129}},
            {"error": {"code": "DeploymentNotFound "}},
            {"error": {"code": None}},
            {"error": {"code": 404}},
            {"error": {"code": True}},
            {"error": {"code": ["DeploymentNotFound"]}},
            {"error": {"code": {"value": "DeploymentNotFound"}}},
            {"error": {"message": "private-message", "details": "private-details"}},
            {"error": "DeploymentNotFound"},
            {"error": ["DeploymentNotFound"]},
            {"error": None},
            {"code": "DeploymentNotFound"},
            ["DeploymentNotFound"],
            None,
        ],
    )
    def test_malformed_or_missing_nested_http_error_codes_are_not_exposed(self, client, payload):
        client.response = FakeResponse(404, json.dumps(payload).encode())
        with pytest.raises(EvaluationException) as raised:
            run(DecisionModelRunner(DECISION_CONFIG))
        assert str(raised.value) == "(UserError) The decision model returned HTTP 404."
        assert raised.value.blame == ErrorBlame.USER_ERROR

    def test_non_json_http_error_cannot_surface_code_text(self, client):
        client.response = FakeResponse(404, b"DeploymentNotFound private-message test-key-value")
        with pytest.raises(EvaluationException) as raised:
            run(DecisionModelRunner(DECISION_CONFIG))
        assert str(raised.value) == "(UserError) The decision model returned HTTP 404."

    def test_transport_failure_is_sanitized(self, monkeypatch):
        class Broken(FakeClient):
            async def post(self, *_, **__):
                raise ConnectionError("https://example.services.ai.azure.com test-key-value")

        monkeypatch.setattr(_model_runners, "get_async_http_client", lambda **_: Broken())
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


class TestDecisionTokenReuse:
    """A credential's token serves repeated and concurrent requests until shortly before it expires."""

    CONFIG = {key: value for key, value in DECISION_CONFIG.items() if key != "api_key"}

    @staticmethod
    def access_token(value, lifetime=3600):
        return AccessToken(value, int(time.time()) + lifetime)

    @staticmethod
    def authorizations(client):
        return [call["headers"]["Authorization"] for call in client.calls]

    @pytest.mark.parametrize("asynchronous", [False, True])
    def test_fresh_token_is_reused_across_requests_and_runners(self, client, asynchronous):
        client.response = FakeResponse(body=json.dumps(level_payload(4)).encode())
        token = self.access_token("shared-token")
        credential = Mock()
        credential.get_token = AsyncMock(return_value=token) if asynchronous else Mock(return_value=token)
        first, second = DecisionModelRunner(self.CONFIG, credential), DecisionModelRunner(self.CONFIG, credential)
        for runner in (first, second, first):
            run(runner)
        credential.get_token.assert_called_once_with("https://cognitiveservices.azure.com/.default")
        assert self.authorizations(client) == ["Bearer shared-token"] * 3

    @pytest.mark.parametrize("lifetime", [None, 60], ids=["no-expiry", "near-expiry"])
    def test_tokens_without_a_usable_expiry_are_requested_each_time(self, client, lifetime):
        client.response = FakeResponse(body=json.dumps(level_payload(4)).encode())
        token = SimpleNamespace(token="per-request") if lifetime is None else self.access_token("per-request", lifetime)
        credential = Mock(get_token=Mock(return_value=token))
        runner = DecisionModelRunner(self.CONFIG, credential)
        run(runner)
        run(runner)
        assert credential.get_token.call_count == 2

    def test_concurrent_requests_share_one_synchronous_token_request(self, client):
        client.response = FakeResponse(body=json.dumps(level_payload(4)).encode())
        requested = []

        def get_token(*scopes, **_):
            requested.append(scopes)
            time.sleep(0.2)
            return self.access_token("single-request")

        credential = Mock(get_token=Mock(side_effect=get_token))
        runners = [DecisionModelRunner(self.CONFIG, credential) for _ in range(6)]
        # Like evaluate(), each runner awaits on its own thread and event loop.
        with ThreadPoolExecutor(max_workers=6) as pool:
            list(pool.map(run, runners))
        assert len(requested) == 1
        assert self.authorizations(client) == ["Bearer single-request"] * 6

    def test_rejected_token_is_not_reused(self, client):
        client.response = FakeResponse(status_code=401, body=b"{}")
        tokens = iter([self.access_token("rejected"), self.access_token("renewed")])
        credential = Mock(get_token=Mock(side_effect=lambda *_, **__: next(tokens)))
        runner = DecisionModelRunner(self.CONFIG, credential)
        with pytest.raises(EvaluationException, match="HTTP 401"):
            run(runner)
        client.response = FakeResponse(body=json.dumps(level_payload(4)).encode())
        run(runner)
        run(runner)
        assert credential.get_token.call_count == 2
        assert self.authorizations(client) == ["Bearer rejected", "Bearer renewed", "Bearer renewed"]

    def test_a_token_the_credential_reissues_after_a_rejection_is_cached_again(self, client):
        client.response = FakeResponse(status_code=401, body=b"{}")
        credential = Mock(get_token=Mock(return_value=self.access_token("same")))
        runner = DecisionModelRunner(self.CONFIG, credential)
        with pytest.raises(EvaluationException, match="HTTP 401"):
            run(runner)
        assert _model_runners._TOKENS.cached(credential, _model_runners._DECISION_TOKEN_SCOPE) is None
        # The service accepts the token now, for example after a role assignment propagated. The credential
        # re-issues the same token: it is requested once more, then reused again instead of once per request.
        client.response = FakeResponse(body=json.dumps(level_payload(4)).encode())
        for _ in range(3):
            run(runner)
        assert credential.get_token.call_count == 2
        assert self.authorizations(client) == ["Bearer same"] * 4
        assert _model_runners._TOKENS.cached(credential, _model_runners._DECISION_TOKEN_SCOPE).token == "same"

    def test_an_acquisition_that_began_before_two_rejections_is_not_stored(self):
        scope = _model_runners._DECISION_TOKEN_SCOPE

        async def scenario():
            gate = asyncio.Event()
            calls = []

            class AsyncCredential:
                async def get_token(self, *_, **__):
                    calls.append(1)
                    call = len(calls)
                    if call == 1:
                        await gate.wait()
                    # The delayed first acquisition and the second return token A; later ones return token B.
                    return TestDecisionTokenReuse.access_token("token-A" if call <= 2 else "token-B")

            credential = AsyncCredential()
            runner = DecisionModelRunner(self.CONFIG, credential)
            deadline = time.monotonic() + 10
            pending = asyncio.ensure_future(runner._get_token(deadline))
            await asyncio.sleep(0)
            # Two later acquisitions complete first, and the service rejects each token with a 401.
            for expected in ("token-A", "token-B"):
                assert await runner._get_token(deadline) == expected
                _model_runners._TOKENS.discard(credential, scope, expected)
            gate.set()
            # The delayed acquisition returns a token the service already rejected; it must not be cached.
            assert await pending == "token-A"
            assert _model_runners._TOKENS.cached(credential, scope) is None
            # The next acquisition is cached again.
            assert await runner._get_token(deadline) == "token-B"
            assert _model_runners._TOKENS.cached(credential, scope).token == "token-B"

        asyncio.run(scenario())

    def test_credential_without_weak_references_is_used_without_caching(self, client):
        client.response = FakeResponse(body=json.dumps(level_payload(4)).encode())
        requested = []
        credential = SimpleNamespace(get_token=lambda *scopes, **_: requested.append(scopes) or self.access_token("t"))
        runner = DecisionModelRunner(self.CONFIG, credential)
        run(runner)
        run(runner)
        assert len(requested) == 2

    def test_unhashable_credential_is_cached_by_identity(self, client):
        from dataclasses import dataclass

        @dataclass
        class Credential:
            requested: int = 0

            def get_token(self, *_, **__):
                self.requested += 1
                return TestDecisionTokenReuse.access_token("by-identity")

        client.response = FakeResponse(body=json.dumps(level_payload(4)).encode())
        credential = Credential()
        runner = DecisionModelRunner(self.CONFIG, credential)
        run(runner)
        run(runner)
        assert credential.requested == 1

    def test_equal_credentials_keep_their_own_tokens(self, client):
        class Credential:
            def __init__(self, token):
                self.token = token

            def __eq__(self, other):
                return isinstance(other, Credential)

            def __hash__(self):
                return 0

            def get_token(self, *_, **__):
                return TestDecisionTokenReuse.access_token(self.token)

        client.response = FakeResponse(body=json.dumps(level_payload(4)).encode())
        first, second = Credential("first-identity"), Credential("second-identity")
        assert first == second
        run(DecisionModelRunner(self.CONFIG, first))
        run(DecisionModelRunner(self.CONFIG, second))
        assert self.authorizations(client) == ["Bearer first-identity", "Bearer second-identity"]

    def test_request_whose_deadline_passes_while_waiting_does_not_request_a_token(self, client):
        client.response = FakeResponse(body=json.dumps(level_payload(4)).encode())
        release = threading.Event()
        requested = []

        def get_token(*_, **__):
            requested.append(1)
            release.wait(5)
            raise RuntimeError("Azure CLI is not logged in")

        credential = Mock(get_token=Mock(side_effect=get_token))
        outcomes = {}

        def request(name, timeout):
            try:
                run(DecisionModelRunner(self.CONFIG, credential), timeout=timeout)
            except EvaluationException as error:
                outcomes[name] = str(error)

        leader = threading.Thread(target=request, args=("leader", 5))
        leader.start()
        while not requested:
            time.sleep(0.01)
        waiter = threading.Thread(target=request, args=("waiter", 0.3))
        waiter.start()
        waiter.join(5)
        release.set()
        leader.join(5)
        assert len(requested) == 1
        assert "timed out" in outcomes["waiter"]
        assert "Could not acquire a token" in outcomes["leader"]

    def test_requests_waiting_on_a_failed_token_request_share_its_failure(self, client):
        client.response = FakeResponse(body=json.dumps(level_payload(4)).encode())
        release = threading.Event()
        requested = []

        def get_token(*_, **__):
            requested.append(1)
            release.wait(10)
            raise EvaluationException(
                message="Service-owned Decision credential acquisition failed (RuntimeError, status unknown).",
                blame=ErrorBlame.SYSTEM_ERROR,
                category=ErrorCategory.FAILED_EXECUTION,
                target=ErrorTarget.EVALUATE,
            )

        credential = Mock(get_token=Mock(side_effect=get_token))
        all_queued = watch_token_queue(credential, 4)
        errors = {}

        def request(name):
            try:
                run(DecisionModelRunner(self.CONFIG, credential), timeout=10)
            except EvaluationException as error:
                errors[name] = error

        leader = threading.Thread(target=request, args=("leader",))
        leader.start()
        while not requested:
            time.sleep(0.01)
        waiters = [threading.Thread(target=request, args=(f"waiter-{index}",)) for index in range(3)]
        for waiter in waiters:
            waiter.start()
        assert all_queued.wait(10)
        release.set()
        for thread in [leader, *waiters]:
            thread.join(10)
        # The queued requests fail with the same typed error instead of each starting another request.
        assert len(requested) == 1 and len(errors) == 4
        assert all(
            error.blame == ErrorBlame.SYSTEM_ERROR and "acquisition failed" in str(error) for error in errors.values()
        )
        credential.get_token.side_effect = lambda *_, **__: self.access_token("recovered")
        run(DecisionModelRunner(self.CONFIG, credential))
        assert len(requested) == 1 and self.authorizations(client) == ["Bearer recovered"]

    def test_a_token_rejected_before_its_request_resumes_is_not_stored_again(self, client, monkeypatch):
        client.response = FakeResponse(body=json.dumps(level_payload(4)).encode())
        credential = Mock(get_token=Mock(return_value=self.access_token("shared")))
        fetch = _model_runners._TOKENS.fetch
        scope = _model_runners._DECISION_TOKEN_SCOPE

        def fetch_then_reject(*args, **kwargs):
            token = fetch(*args, **kwargs)
            # Another request's 401 discards the token before this request's event loop resumes.
            _model_runners._TOKENS.discard(credential, scope, token.token)
            return token

        monkeypatch.setattr(_model_runners._TOKENS, "fetch", fetch_then_reject)
        run(DecisionModelRunner(self.CONFIG, credential))
        assert _model_runners._TOKENS.cached(credential, scope) is None

    def test_failed_token_request_does_not_keep_the_credential_alive(self, client):
        class Credential:
            def get_token(self, *_, **__):
                raise RuntimeError("Azure CLI is not logged in")

        credential = Credential()
        with pytest.raises(EvaluationException, match="Could not acquire a token"):
            run(DecisionModelRunner(self.CONFIG, credential))
        reference = weakref.ref(credential)
        del credential
        gc.collect()
        assert reference() is None

    def test_cancelled_request_stops_waiting_for_another_token_request(self, client):
        client.response = FakeResponse(body=json.dumps(level_payload(4)).encode())
        release = threading.Event()
        requested = []

        def get_token(*_, **__):
            requested.append(1)
            release.wait(5)
            return self.access_token("late")

        credential = Mock(get_token=Mock(side_effect=get_token))
        cancelled = threading.Event()
        outcomes = {}

        def waiter():
            try:
                run(DecisionModelRunner(self.CONFIG, credential, cancellation_requested=cancelled.is_set), timeout=10)
            except EvaluationException as error:
                outcomes["waiter"] = str(error)

        leader = threading.Thread(target=lambda: run(DecisionModelRunner(self.CONFIG, credential), timeout=10))
        leader.start()
        while not requested:
            time.sleep(0.01)
        waiting = threading.Thread(target=waiter)
        waiting.start()
        time.sleep(0.2)
        cancelled.set()
        # The cancelled request returns while the first request still holds the credential's lock.
        waiting.join(2)
        still_waiting = waiting.is_alive()
        release.set()
        leader.join(5)
        waiting.join(5)
        assert not still_waiting and "cancelled" in outcomes["waiter"]
        assert len(requested) == 1

    def test_cache_does_not_keep_the_credential_alive(self, client):
        client.response = FakeResponse(body=json.dumps(level_payload(4)).encode())
        token = self.access_token("caller-owned")

        class Credential:
            def get_token(self, *_, **__):
                return token

        credential = Credential()
        run(DecisionModelRunner(self.CONFIG, credential))
        assert _model_runners._TOKENS.cached(credential, _model_runners._DECISION_TOKEN_SCOPE) is token
        reference = weakref.ref(credential)
        del credential
        gc.collect()
        assert reference() is None


class TestAnswerValidation:
    def test_noul(self):
        assert validate_noul_answer({"type": "noul", "noul": 0.25}) == 0.25
        for bad in (True, "0.5", None, float("nan"), -0.01, 1.01):
            with pytest.raises(ValueError):
                validate_noul_answer({"type": "noul", "noul": bad})

    def test_score_mean_does_not_require_distribution_consistency(self):
        levels = [0.1, 0.2, 0.3, 0.2, 0.2]
        answer = score_answer(levels)
        answer["score"] = 0
        assert validate_score_answer(answer, 5) == levels

    def test_score_accepts_rounded_distribution_without_normalizing(self):
        levels = [0.333333, 0.333333, 0.333334]
        assert validate_score_answer(score_answer(levels), 3) == levels
        levels = [0.3333333] * 3
        assert validate_score_answer(score_answer(levels), 3) == levels

    @pytest.mark.parametrize(
        "levels",
        [
            [0.19, 0.34, 0.11, 0.07, 0.28],
            [0.20, 0.34, 0.11, 0.07, 0.29],
            [0.19, 0.34, 0.11, 0.07, 0.27],
            [0.21, 0.34, 0.11, 0.07, 0.29],
        ],
    )
    def test_score_accepts_hundredths_rounding_without_normalizing(self, levels):
        assert validate_score_answer(score_answer(levels), 5) == levels

    @pytest.mark.parametrize(
        "levels",
        [
            [0.22, 0.34, 0.11, 0.07, 0.29],
            [0.18, 0.34, 0.11, 0.07, 0.27],
            [0.191, 0.339, 0.11, 0.07, 0.28],
            [0.201, 0.339, 0.11, 0.07, 0.29],
        ],
    )
    def test_score_rejects_outside_hundredths_or_finer_precision_tolerance(self, levels):
        with pytest.raises(ValueError, match="sum to one"):
            validate_score_answer(score_answer(levels), 5)

    @pytest.mark.parametrize("levels", [[0] * 5, [0.1] * 5, [0.3] * 5])
    def test_score_rejects_nonunit_distribution(self, levels):
        with pytest.raises(ValueError, match="sum to one"):
            validate_score_answer(score_answer(levels), 5)

    @pytest.mark.parametrize("direction", [-1, 1])
    @pytest.mark.parametrize("inside", [False, True])
    def test_score_sum_tolerance_boundary(self, direction, inside):
        boundary = 1 + direction * 0.001
        total = math.nextafter(boundary, 1.0 if inside else direction * math.inf)
        levels = [0.5, total - 0.5]
        assert math.fsum(levels) == total
        if inside:
            assert validate_score_answer(score_answer(levels), 2) == levels
        else:
            with pytest.raises(ValueError, match="sum to one"):
                validate_score_answer(score_answer(levels), 2)

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
    def test_common_exports_match_existing_private_imports(self):
        from azure.ai.evaluation._evaluators import _common
        from azure.ai.evaluation._evaluators._common._prompty_strategy import PromptyEvaluationStrategy

        for name, implementation in (
            ("DecisionModelRunner", DecisionModelRunner),
            ("PromptyModelRunner", PromptyModelRunner),
            ("DecisionEvaluationStrategy", DecisionEvaluationStrategy),
            ("PromptyEvaluationStrategy", PromptyEvaluationStrategy),
            ("BinaryScoring", BinaryScoring),
            ("LikertScoring", LikertScoring),
        ):
            assert getattr(_common, name) is implementation
            assert name in _common.__all__

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
        with (
            patch.object(_model_runners.AsyncPrompty, "load", return_value=flow),
            patch.object(_model_runners, "DecisionModelRunner", side_effect=AssertionError("decision runner built")),
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

    def test_bundled_fluency_public_call_uses_legacy_prompty_parsing(self):
        flow = AsyncMock(
            return_value={
                "llm_output": "<S1>Clear prose</S1><S2>4</S2>",
                "input_token_count": 12,
                "output_token_count": 3,
                "total_token_count": 15,
                "model_id": "chat-model",
            }
        )
        with patch.object(_model_runners.AsyncPrompty, "load", return_value=flow):
            evaluator = FluencyEvaluator(CHAT_CONFIG)
        result = evaluator(response="A clear sentence.")
        assert result["fluency"] == 4
        assert result["fluency_reason"] == "Clear prose"
        assert result["fluency_result"] == "pass"
        assert result["fluency_properties"]["model"] == "chat-model"
        assert result["fluency_properties"]["prompt_tokens"] == 12
        flow.assert_awaited_once_with(timeout=600, response="A clear sentence.")

    @pytest.mark.parametrize(
        "evaluator_type,metric", [(FluencyEvaluator, "fluency"), (CoherenceEvaluator, "coherence")]
    )
    @pytest.mark.parametrize("multi_turn", [False, True])
    def test_bundled_prompty_public_call_loads_real_template(self, evaluator_type, metric, multi_turn):
        completion = ChatCompletion(
            id="offline-completion",
            created=0,
            object="chat.completion",
            model="offline-chat-model",
            choices=[
                {
                    "index": 0,
                    "finish_reason": "stop",
                    "message": {
                        "role": "assistant",
                        "content": json.dumps({"reason": "Clear prose", "score": 4, "status": "completed"}),
                    },
                }
            ],
            usage={"prompt_tokens": 12, "completion_tokens": 3, "total_tokens": 15},
        )

        async def send(*, api_client, params, timeout):
            await api_client.close()
            assert timeout == 600
            assert params["response_format"] == {"type": "json_object"}
            assert params["messages"]
            assert any("A clear sentence." in str(message["content"]) for message in params["messages"])
            return completion

        with patch.object(_model_runners.AsyncPrompty, "_send_with_retries", side_effect=send) as request:
            evaluator = evaluator_type(CHAT_CONFIG)
            assert evaluator._flow.path.is_file()
            assert evaluator._flow.path.name == f"{metric}.prompty"
            if multi_turn:
                result = evaluator(
                    conversation={
                        "messages": [
                            {"role": "user", "content": "Explain clearly."},
                            {"role": "assistant", "content": "A clear sentence."},
                            {"role": "user", "content": "Explain again."},
                            {"role": "assistant", "content": "A clear sentence."},
                        ]
                    }
                )
            else:
                inputs = {"response": "A clear sentence."}
                if metric == "coherence":
                    inputs["query"] = "Explain clearly."
                result = evaluator(**inputs)
        assert result[metric] == 4
        assert request.await_count == (2 if multi_turn else 1)
        if multi_turn:
            assert result["evaluation_per_turn"][metric] == [4, 4]
            assert result["evaluation_per_turn"][f"{metric}_reason"] == ["Clear prose"] * 2
        else:
            assert result[f"{metric}_reason"] == "Clear prose"
            assert result[f"{metric}_result"] == "pass"
            assert result[f"{metric}_properties"]["model"] == "offline-chat-model"
            assert result[f"{metric}_properties"]["prompt_tokens"] == 12


def completion_payload(probability, status=0.95):
    return decision_payload(status, {"task_completion": {"type": "noul", "noul": probability}})


def strategy_with(payload, scoring, key="tool_call_accuracy", extra_properties=None):
    runner = AsyncMock(return_value=payload)
    runner.deployment = "Decision-1"
    runner.decision_protocol = "microsoft"
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
    @pytest.mark.parametrize("question", ["status", "tool_call_accuracy"])
    @pytest.mark.parametrize("extra", [math.inf, -math.inf, math.nan, {"nested": [math.inf]}])
    def test_nonfinite_answer_extras_raise_a_json_safe_metadata_preserving_error(self, question, extra):
        """Validate retained provenance without discarding the paid response's known usage."""
        response = level_payload(4)
        response["answers"][question]["diagnostic"] = extra
        configured = strategy_with(response, LikertScoring(5))
        with pytest.raises(EvaluationException, match="JSON-safe") as raised:
            asyncio.run(configured.evaluate({}))
        assert raised.value.blame == ErrorBlame.SYSTEM_ERROR
        assert raised.value.properties["total_tokens"] == 123
        assert raised.value.properties["model"] == "microsoft-decision-1"
        json.dumps(raised.value.properties, allow_nan=False)

    def test_json_numeric_overflow_in_an_extra_is_rejected_after_real_response_parsing(self, client):
        """A valid JSON exponent must not become infinity in a completed result."""
        response = level_payload(4)
        response["answers"]["status"]["diagnostic"] = "OVERFLOW"
        client.response = FakeResponse(body=json.dumps(response).replace('"OVERFLOW"', "1e309").encode())
        configured = strategy_with(response, LikertScoring(5))
        configured.runner = DecisionModelRunner(DECISION_CONFIG)
        with pytest.raises(EvaluationException, match="JSON-safe") as raised:
            asyncio.run(configured.evaluate({}))
        assert raised.value.properties["total_tokens"] == 123
        json.dumps(raised.value.properties, allow_nan=False)

    def test_json_safe_answer_extras_are_preserved_without_mutating_the_response(self):
        """Do not remove valid provider diagnostics while validating durable metadata."""
        response = level_payload(4)
        diagnostic = {"optional": None, "values": [True, 0, "kept"]}
        response["answers"]["status"]["diagnostic"] = diagnostic
        response["answers"]["tool_call_accuracy"]["diagnostic"] = diagnostic
        original = deepcopy(response)
        result = asyncio.run(strategy_with(response, LikertScoring(5)).evaluate({}))
        native = result["tool_call_accuracy_properties"]["decision_model"]
        assert native["native_status_answer"]["diagnostic"] == diagnostic
        assert native["native_answer"]["diagnostic"] == diagnostic
        assert response == original
        json.dumps(result, allow_nan=False)

    def test_skipped_unusable_answer_extras_are_not_validated_or_persisted(self):
        """A false applicability verdict still ignores the unused score answer."""
        response = level_payload(4, status=0.1)
        response["answers"]["tool_call_accuracy"]["diagnostic"] = math.inf
        result = asyncio.run(strategy_with(response, LikertScoring(5)).evaluate({}))
        assert result["tool_call_accuracy_status"] == "skipped"
        assert "native_answer" not in result["tool_call_accuracy_properties"]["decision_model"]
        json.dumps(result, allow_nan=False)

    @pytest.mark.parametrize("field", ["status", "noul", "probability", "confidence", "score"])
    def test_oversized_integer_preserves_typed_failure_metadata(self, field):
        from azure.ai.evaluation._evaluate._batch_run._run_submitter_client import _decision_error_metadata

        response = completion_payload(0.9) if field == "noul" else level_payload(4)
        if field == "status":
            response["answers"]["status"]["noul"] = 10**309
        elif field == "noul":
            response["answers"]["task_completion"]["noul"] = 10**309
        elif field == "probability":
            response["answers"]["tool_call_accuracy"]["probabilities"]["0"] = 10**309
        else:
            response["answers"]["tool_call_accuracy"][field] = 10**309
        response = json.loads(json.dumps(response))
        strategy = (
            strategy_with(response, BinaryScoring(0.75), "task_completion")
            if field == "noul"
            else strategy_with(response, LikertScoring(5))
        )
        with pytest.raises(EvaluationException) as raised:
            strategy.parse(response, {})
        assert raised.value.blame == ErrorBlame.SYSTEM_ERROR
        assert raised.value.category == ErrorCategory.FAILED_EXECUTION
        metadata = _decision_error_metadata(raised.value)
        assert metadata["properties"]["total_tokens"] == 123
        assert metadata["properties"]["model"] == "microsoft-decision-1"
        assert metadata["properties"]["decision_model"]["deployment"] == "Decision-1"
        assert len(metadata["properties"]["decision_model"]["rubric_hash"]) == 64
        json.dumps(metadata, allow_nan=False)

    @pytest.mark.parametrize("status", [0.1, 0.9])
    def test_parse_reuses_shared_response_without_http_or_usage_suffixes(self, status):
        strategy = strategy_with(level_payload(4, status=status), LikertScoring(5))
        strategy.runner = Mock(deployment="Decision-1")
        parsed = strategy.parse(level_payload(4, status=status), {})
        assert parsed["tool_call_accuracy_status"] == ("skipped" if status < 0.5 else "completed")
        assert parsed["tool_call_accuracy_properties"]["total_tokens"] == 123
        assert not any(
            key.endswith(("_prompt_tokens", "_completion_tokens", "_total_tokens", "_model")) for key in parsed
        )
        strategy.runner.assert_not_called()

    @pytest.mark.parametrize("probability, score", [(0.6, 1.0), (0.5999, 0.0)])
    def test_binary_scoring_uses_its_own_cutoff(self, probability, score):
        strategy = strategy_with(completion_payload(probability), BinaryScoring(0.6), key="task_completion")
        assert asyncio.run(strategy.evaluate({}))["task_completion"] == score

    def test_standalone_binary_result_does_not_use_score_threshold(self):
        strategy = strategy_with(completion_payload(0.1), BinaryScoring(0.6), key="task_completion")
        strategy.threshold = 0
        result = asyncio.run(strategy.evaluate({}))
        assert result["task_completion"] == 0
        assert result["task_completion_threshold"] == 0
        assert result["task_completion_passed"] is False

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

    @pytest.mark.parametrize("levels", [[0] * 5, [0.1] * 5, [0.3] * 5])
    @pytest.mark.parametrize("minimum", [0, 1])
    def test_invalid_distribution_is_system_error_before_argmax(self, levels, minimum):
        payload = decision_payload(0.95, {"tool_call_accuracy": score_answer(levels)})
        with pytest.raises(EvaluationException, match="sum to one") as raised:
            asyncio.run(strategy_with(payload, LikertScoring(5, minimum=minimum)).evaluate({}))
        assert raised.value.blame == ErrorBlame.SYSTEM_ERROR
        assert raised.value.category == ErrorCategory.FAILED_EXECUTION
        assert raised.value.target == ErrorTarget.TOOL_CALL_ACCURACY_EVALUATOR
        assert raised.value.properties["total_tokens"] == 123
        assert raised.value.properties["model"] == "microsoft-decision-1"

    def test_public_call_rejects_invalid_distribution_with_evaluation_system_error(self, client):
        class ScoredEvaluator(ModelEvaluatorBase):
            _supports_decision_models = True

            def _derive_singleton_inputs(self):
                return [["query", "response"]]

            async def _do_eval(self, eval_input):
                return await DecisionEvaluationStrategy(
                    self._decision_model_runner,
                    result_key="tool_call_accuracy",
                    error_target=ErrorTarget.TOOL_CALL_ACCURACY_EVALUATOR,
                    questions=QUESTIONS,
                    scoring=LikertScoring(5),
                    threshold=3,
                    timeout=self._LLM_CALL_TIMEOUT,
                ).evaluate(eval_input)

        payload = decision_payload(0.95, {"tool_call_accuracy": score_answer([0.3] * 5)})
        client.response = FakeResponse(body=json.dumps(payload).encode())
        evaluator = ScoredEvaluator(result_key="tool_call_accuracy", model_config=DECISION_CONFIG)
        with pytest.raises(EvaluationException, match="sum to one") as raised:
            evaluator(query="synthetic", response="synthetic")
        assert raised.value.blame == ErrorBlame.SYSTEM_ERROR
        assert raised.value.category == ErrorCategory.FAILED_EXECUTION
        assert raised.value.target == ErrorTarget.TOOL_CALL_ACCURACY_EVALUATOR
        assert raised.value.properties["total_tokens"] == 123

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

    def test_successful_properties_only_contain_decision_metadata(self):
        properties = asyncio.run(strategy_with(level_payload(4), LikertScoring(5)).evaluate({}))[
            "tool_call_accuracy_properties"
        ]
        assert set(properties) == {
            "decision_model",
            "prompt_tokens",
            "completion_tokens",
            "total_tokens",
            "model",
        }
        assert {key: value for key, value in properties.items() if key != "decision_model"} == {
            "prompt_tokens": 120,
            "completion_tokens": 3,
            "total_tokens": 123,
            "model": "microsoft-decision-1",
        }

    def test_likert_provenance_omits_legend_without_mutating_shared_response(self):
        payload = level_payload(4)
        answer = payload["answers"]["tool_call_accuracy"]
        answer["legend"] = {str(index): "Repeated rubric description " * 20 for index in range(5)}
        strategy = strategy_with(payload, LikertScoring(5))
        result = asyncio.run(strategy.evaluate({}))
        native = result["tool_call_accuracy_properties"]["decision_model"]["native_answer"]
        assert native == {name: value for name, value in answer.items() if name != "legend"}
        assert "legend" in answer
        assert result["tool_call_accuracy"] == 5
        assert result["tool_call_accuracy_properties"]["total_tokens"] == 123


class TestDecisionConversationUsage:
    def test_public_split_conversation_sums_native_usage_and_retains_model(self, client):
        import logging

        from azure.ai.evaluation._evaluate._evaluate import _convert_single_row_to_aoai_format

        class SplitEvaluator(ModelEvaluatorBase):
            _supports_decision_models = True

            def _derive_singleton_inputs(self):
                return [["query", "response"]]

            async def _do_eval(self, eval_input):
                return await DecisionEvaluationStrategy(
                    self._decision_model_runner,
                    result_key="tool_call_accuracy",
                    error_target=ErrorTarget.TOOL_CALL_ACCURACY_EVALUATOR,
                    questions=QUESTIONS,
                    scoring=LikertScoring(5),
                    threshold=3,
                    timeout=self._LLM_CALL_TIMEOUT,
                ).evaluate(eval_input)

        payloads = [level_payload(0), level_payload(4)]
        payloads[0]["usage"] = {"input_tokens": 12, "output_tokens": 3}
        payloads[1]["usage"] = {"input_tokens": 34, "output_tokens": 5}
        client.post = AsyncMock(side_effect=[FakeResponse(body=json.dumps(payload).encode()) for payload in payloads])
        evaluator = SplitEvaluator(result_key="tool_call_accuracy", model_config=DECISION_CONFIG)
        result = evaluator(
            conversation={
                "messages": [
                    {"role": "user", "content": "first"},
                    {"role": "assistant", "content": "one"},
                    {"role": "user", "content": "second"},
                    {"role": "assistant", "content": "two"},
                ]
            }
        )
        assert client.post.await_count == 2
        assert result["tool_call_accuracy"] == 3
        assert result["tool_call_accuracy_prompt_tokens"] == 46
        assert result["tool_call_accuracy_completion_tokens"] == 8
        assert result["tool_call_accuracy_total_tokens"] == 54
        assert result["tool_call_accuracy_model"] == "microsoft-decision-1"
        assert result["evaluation_per_turn"]["tool_call_accuracy_prompt_tokens"] == [12, 34]
        assert result["evaluation_per_turn"]["tool_call_accuracy_model"] == ["microsoft-decision-1"] * 2
        assert [json.loads(call.kwargs["content"])["state"]["query"] for call in client.post.await_args_list] == [
            "first",
            "second",
        ]
        converted = _convert_single_row_to_aoai_format(
            {f"outputs.judge.{key}": value for key, value in result.items()},
            0,
            None,
            None,
            0,
            {"judge": {"metrics": ["tool_call_accuracy"], "type": "azure_ai_evaluator"}},
            None,
            logging.getLogger("test"),
        )
        persisted = converted["results"][0]
        assert persisted["sample"]["usage"] == {"prompt_tokens": 46, "completion_tokens": 8, "total_tokens": 54}
        assert persisted["sample"]["model"] == "microsoft-decision-1"
        properties = result["tool_call_accuracy_properties"]
        assert {field: properties[field] for field in ("prompt_tokens", "completion_tokens", "total_tokens")} == {
            "prompt_tokens": 46,
            "completion_tokens": 8,
            "total_tokens": 54,
        }
        assert properties["model"] == "microsoft-decision-1"
        assert properties["decision_model"]["result_usage_scope"] == "reported_turns_only"
        assert properties["decision_model"]["protocol"] == "microsoft"
        assert "execution" not in properties["decision_model"]
        assert persisted["properties"] == properties
        turns = result["evaluation_per_turn"]["tool_call_accuracy_properties"]
        assert [turn["total_tokens"] for turn in turns] == [15, 39]
        assert all("native_answer" in turn["decision_model"] for turn in turns)
        assert properties["decision_model"]["native_answer"] == turns[-1]["decision_model"]["native_answer"]

        payloads[1]["model"] = "another-model"
        client.post = AsyncMock(side_effect=[FakeResponse(body=json.dumps(payload).encode()) for payload in payloads])
        mixed = evaluator(
            conversation={
                "messages": [
                    {"role": "user", "content": "first"},
                    {"role": "assistant", "content": "one"},
                    {"role": "user", "content": "second"},
                    {"role": "assistant", "content": "two"},
                ]
            }
        )
        mixed_properties = mixed["tool_call_accuracy_properties"]
        assert mixed_properties["total_tokens"] == mixed["tool_call_accuracy_total_tokens"] == 54
        assert "tool_call_accuracy_model" not in mixed
        assert "model" not in mixed_properties and "model" not in mixed_properties["decision_model"]
        converted = _convert_single_row_to_aoai_format(
            {f"outputs.judge.{key}": value for key, value in mixed.items()},
            0,
            None,
            None,
            0,
            {"judge": {"metrics": ["tool_call_accuracy"], "type": "azure_ai_evaluator"}},
            None,
            logging.getLogger("test"),
        )
        persisted = converted["results"][0]
        assert persisted["properties"] == mixed_properties
        assert persisted["sample"]["usage"]["total_tokens"] == 54
        assert persisted["sample"].get("model") is None

    @pytest.mark.parametrize(
        "case",
        [
            "same_model",
            "mixed_models",
            "missing_model",
            "partial_usage",
            "unknown_usage",
            "last_free_skip",
            "all_free_skips",
            "first_free_skip",
            "final_paid_skip",
        ],
    )
    def test_aggregate_properties_match_known_usage_without_mutating_turns(self, case):
        from copy import deepcopy

        evaluator = ProbeModelEvaluator(result_key="probe", model_config=DECISION_CONFIG)
        turns = []
        for index, count in enumerate((15, 39)):
            model = "model-b" if case == "mixed_models" and index else "model-a"
            if case == "missing_model" and index:
                model = None
            usage = {"prompt_tokens": count - 3, "completion_tokens": 3, "total_tokens": count}
            if case == "partial_usage":
                usage = {"prompt_tokens": 0} if index == 0 else {"completion_tokens": 3}
            elif case == "unknown_usage":
                usage = {}
            native = {
                "deployment": "Decision-1",
                "model": model,
                "rubric_hash": "a" * 64,
                "status_rubric_hash": "b" * 64,
                "status_probability_threshold": 0.5,
                "status_completion_probability": 0.9,
                "native_answer": {"type": "noul", "noul": 0.8},
                "execution": {"attempt_count": 1},
            }
            properties = {**usage, "model": model, "decision_model": native}
            turn = {
                "probe": index + 1,
                **{f"probe_{field}": value for field, value in usage.items()},
                "probe_model": model,
                "probe_properties": properties,
            }
            if case == "final_paid_skip" and index:
                turn["probe"] = None
                native.pop("native_answer")
                native["status_completion_probability"] = 0.1
                native["native_status_answer"] = {"type": "noul", "noul": 0.1}
            if (
                case == "all_free_skips"
                or (case == "last_free_skip" and index)
                or (case == "first_free_skip" and index == 0)
            ):
                turn = {"probe": None, "probe_properties": None}
            turns.append(turn)
        original = deepcopy(turns)
        result = evaluator._aggregate_results(turns)
        properties = result["probe_properties"]
        assert turns == original
        assert result["evaluation_per_turn"]["probe_properties"] == [turn["probe_properties"] for turn in original]
        if case in ("last_free_skip", "all_free_skips"):
            assert properties is None
            if case == "last_free_skip":
                assert result["probe_total_tokens"] == 15
            return
        for field in ("prompt_tokens", "completion_tokens", "total_tokens"):
            if f"probe_{field}" in result:
                assert properties[field] == result[f"probe_{field}"]
            else:
                assert field not in properties
        if "probe_model" in result:
            assert properties["model"] == result["probe_model"]
            assert properties["decision_model"]["model"] == result["probe_model"]
        else:
            assert "model" not in properties and "model" not in properties["decision_model"]
        assert properties["decision_model"]["usage_available"] is bool(
            {"prompt_tokens", "completion_tokens", "total_tokens"}.intersection(properties)
        )
        assert properties["decision_model"]["result_usage_scope"] == "reported_turns_only"
        assert "execution" not in properties["decision_model"]
        assert properties["decision_model"]["status_completion_probability"] == (
            original[-1]["probe_properties"]["decision_model"]["status_completion_probability"]
        )
        if case == "final_paid_skip":
            assert properties["decision_model"]["native_status_answer"] == {"type": "noul", "noul": 0.1}
            assert "native_answer" not in properties["decision_model"]
        else:
            assert properties["decision_model"]["native_answer"] == {"type": "noul", "noul": 0.8}

    @pytest.mark.parametrize("models", [("first", "second"), ("first", None)])
    def test_different_or_unknown_models_remain_per_turn(self, models):
        evaluator = ProbeModelEvaluator(result_key="probe", model_config=DECISION_CONFIG)
        turns = [{"probe": 1, "probe_model": model} for model in models]
        result = evaluator._aggregate_results(turns)
        assert "probe_model" not in result
        assert result["evaluation_per_turn"]["probe_model"] == list(models)
        assert "probe_prompt_tokens" not in result

    def test_only_known_usage_is_summed_without_fabricating_totals(self):
        evaluator = ProbeModelEvaluator(result_key="probe", model_config=DECISION_CONFIG)
        result = evaluator._aggregate_results(
            [{"probe": 1, "probe_prompt_tokens": 0}, {"probe": 5, "probe_completion_tokens": 4}]
        )
        assert result["probe"] == 3
        assert result["probe_prompt_tokens"] == 0
        assert result["probe_completion_tokens"] == 4
        assert "probe_total_tokens" not in result

    def test_chat_aggregation_is_unchanged(self):
        with patch.object(_model_runners.AsyncPrompty, "load"):
            evaluator = ProbeModelEvaluator(result_key="probe", prompty_file="probe.prompty", model_config=CHAT_CONFIG)
        turns = [
            {"probe": 1, "probe_prompt_tokens": 12, "probe_model": "chat"},
            {"probe": 5, "probe_prompt_tokens": 34, "probe_model": "chat"},
        ]
        assert evaluator._aggregate_results(turns) == EvaluatorBase._aggregate_results(evaluator, turns)

    def test_usage_details_are_summed_over_the_turns_that_reported_them(self):
        evaluator = ProbeModelEvaluator(result_key="probe", model_config=DECISION_CONFIG)
        first = {"input_tokens_details": {"cached_tokens": 4}, "output_tokens_details": {"reasoning_tokens": 2}}
        second = {"input_tokens_details": {"cached_tokens": 6, "cache_write_tokens": 1}}
        turns = [
            {"probe": 1, "probe_prompt_tokens": 12, "probe_properties": {"decision_model": {"usage_details": first}}},
            {"probe": 5, "probe_prompt_tokens": 34, "probe_properties": {"decision_model": {"usage_details": second}}},
            {"probe": 3, "probe_prompt_tokens": 7, "probe_properties": {"decision_model": {}}},
        ]
        result = evaluator._aggregate_results(turns)
        native = result["probe_properties"]["decision_model"]
        assert native["usage_details"] == {
            "input_tokens_details": {"cached_tokens": 10, "cache_write_tokens": 1},
            "output_tokens_details": {"reasoning_tokens": 2},
        }
        assert native["result_usage_scope"] == "reported_turns_only"
        assert result["probe_prompt_tokens"] == 53
        per_turn = result["evaluation_per_turn"]["probe_properties"]
        assert [turn["decision_model"].get("usage_details") for turn in per_turn] == [first, second, None]

    def test_last_turn_usage_details_are_not_reported_as_conversation_totals(self):
        evaluator = ProbeModelEvaluator(result_key="probe", model_config=DECISION_CONFIG)
        invalid = {"input_tokens_details": {"cached_tokens": -1}, "output_tokens_details": {"reasoning_tokens": True}}
        turns = [
            {"probe": 1, "probe_prompt_tokens": 12, "probe_properties": {"decision_model": {}}},
            {"probe": 5, "probe_prompt_tokens": 34, "probe_properties": {"decision_model": {"usage_details": invalid}}},
        ]
        native = evaluator._aggregate_results(turns)["probe_properties"]["decision_model"]
        assert "usage_details" not in native

    def test_usage_details_of_turns_without_counted_usage_are_not_summed(self):
        evaluator = ProbeModelEvaluator(result_key="probe", model_config=DECISION_CONFIG)
        counted = {"input_tokens_details": {"cached_tokens": 4}}
        uncounted = {"input_tokens_details": {"cached_tokens": 90}, "output_tokens_details": {"reasoning_tokens": 9}}
        turns = [
            {"probe": 1, "probe_prompt_tokens": 12, "probe_properties": {"decision_model": {"usage_details": counted}}},
            {"probe": 5, "probe_properties": {"decision_model": {"usage_details": uncounted}}},
            {"probe": 3, "probe_prompt_tokens": 7, "probe_properties": {"decision_model": {}}},
        ]
        result = evaluator._aggregate_results(turns)
        assert result["probe_prompt_tokens"] == 19
        assert result["probe_properties"]["decision_model"]["usage_details"] == counted


class TestDecisionEvaluationMetrics:
    """Every Decision evaluation records one outcome count and one duration with the same bounded attributes."""

    EVALUATIONS = "azure.ai.evaluation.decision.evaluations"
    DURATION = "azure.ai.evaluation.decision.evaluation.duration"

    @pytest.fixture
    def recorded(self):
        records = []

        class Instrument:
            def __init__(self, name, **_):
                self.name = name

            def add(self, value, attributes):
                records.append((self.name, value, dict(attributes)))

            record = add

        meter = SimpleNamespace(create_counter=Instrument, create_histogram=Instrument)
        with patch.dict(sys.modules, {"opentelemetry.metrics": SimpleNamespace(get_meter=lambda _: meter)}):
            yield records

    def evaluation_attributes(self, records):
        evaluations = [record for record in records if record[0] in (self.EVALUATIONS, self.DURATION)]
        assert [name for name, _, _ in evaluations] == [self.EVALUATIONS, self.DURATION]
        (_, count, attributes), (_, duration, duration_attributes) = evaluations
        assert count == 1 and duration >= 0 and attributes == duration_attributes
        assert set(attributes) == {"backend", "protocol", "metric", "outcome", "blame", "error_kind"}
        return attributes

    def test_completed_evaluation(self, recorded):
        result = asyncio.run(strategy_with(level_payload(4), LikertScoring(5)).evaluate({}))
        assert result["tool_call_accuracy_status"] != "skipped"
        assert self.evaluation_attributes(recorded) == {
            "backend": "decision",
            "protocol": "microsoft",
            "metric": "tool_call_accuracy",
            "outcome": "completed",
            "blame": "none",
            "error_kind": "none",
        }

    def test_not_applicable_evaluation_is_skipped(self, recorded):
        result = asyncio.run(strategy_with(level_payload(4, status=0.1), LikertScoring(5)).evaluate({}))
        assert result["tool_call_accuracy_status"] == "skipped"
        assert self.evaluation_attributes(recorded)["outcome"] == "skipped"

    def test_invalid_response_is_a_system_error(self, recorded):
        response = level_payload(4)
        response["answers"]["status"]["diagnostic"] = math.inf
        with pytest.raises(EvaluationException):
            asyncio.run(strategy_with(response, LikertScoring(5)).evaluate({}))
        attributes = self.evaluation_attributes(recorded)
        assert (attributes["outcome"], attributes["blame"], attributes["error_kind"]) == ("error", "system", "none")

    @pytest.mark.parametrize("protocol", ["microsoft", "openai"])
    def test_request_error_keeps_its_blame_and_protocol(self, recorded, protocol):
        configured = strategy_with(level_payload(4), LikertScoring(5))
        configured.runner.side_effect = EvaluationException(
            message="rejected",
            blame=ErrorBlame.USER_ERROR,
            category=ErrorCategory.INVALID_VALUE,
            target=ErrorTarget.EVALUATE,
        )
        configured.runner.decision_protocol = protocol
        with pytest.raises(EvaluationException):
            asyncio.run(configured.evaluate({}))
        attributes = self.evaluation_attributes(recorded)
        assert (attributes["outcome"], attributes["blame"], attributes["protocol"]) == ("error", "user", protocol)

    def test_refusal_is_a_user_error_with_its_kind(self, recorded):
        response = level_payload(4)
        response["answers"]["tool_call_accuracy"] = {"type": "refusal"}
        with pytest.raises(DecisionRefusalError):
            asyncio.run(strategy_with(response, LikertScoring(5)).evaluate({}))
        attributes = self.evaluation_attributes(recorded)
        assert (attributes["outcome"], attributes["blame"], attributes["error_kind"]) == (
            "error",
            "user",
            "model_refusal",
        )

    def test_content_filter_rejection_keeps_its_kind(self, recorded):
        error = EvaluationException(
            message="The decision model returned HTTP 400 (content_filter).",
            blame=ErrorBlame.USER_ERROR,
            category=ErrorCategory.FAILED_EXECUTION,
            target=ErrorTarget.EVALUATE,
        )
        error.properties = {"decision_model": {"error_kind": "content_filter"}}
        configured = strategy_with(level_payload(4), LikertScoring(5))
        configured.runner.side_effect = error
        with pytest.raises(EvaluationException):
            asyncio.run(configured.evaluate({}))
        attributes = self.evaluation_attributes(recorded)
        assert (attributes["outcome"], attributes["blame"], attributes["error_kind"]) == (
            "error",
            "user",
            "content_filter",
        )

    def test_cancellation_is_not_counted_as_an_error(self, recorded):
        configured = strategy_with(level_payload(4), LikertScoring(5))
        configured.runner.side_effect = asyncio.CancelledError()
        with pytest.raises(asyncio.CancelledError):
            asyncio.run(configured.evaluate({}))
        attributes = self.evaluation_attributes(recorded)
        assert (attributes["outcome"], attributes["blame"]) == ("cancelled", "none")

    @staticmethod
    def runner_strategy(runner):
        return DecisionEvaluationStrategy(
            runner,
            result_key="tool_call_accuracy",
            error_target=ErrorTarget.TOOL_CALL_ACCURACY_EVALUATOR,
            questions=QUESTIONS,
            scoring=LikertScoring(5),
            threshold=3,
            timeout=5,
        )

    @pytest.mark.parametrize("summary_kept", [True, False], ids=["summary", "summary_over_bounds"])
    def test_callback_cancellation_is_not_counted_as_an_error(self, client, recorded, monkeypatch, summary_kept):
        if not summary_kept:
            # A summary beyond the hosted bounds, such as one after more than 20 retries, is omitted.
            monkeypatch.setattr(_model_runners, "validated_execution", lambda _: None)
        runner = DecisionModelRunner(DECISION_CONFIG, cancellation_requested=lambda: True)
        with pytest.raises(EvaluationException, match="cancelled") as raised:
            asyncio.run(self.runner_strategy(runner).evaluate({}))
        # The exception is unchanged; only the evaluation metric reads the runner's cancellation marker.
        assert raised.value.blame == ErrorBlame.USER_ERROR and not client.calls
        execution = (raised.value.properties.get("decision_model") or {}).get("execution") or {}
        assert execution.get("outcome") == ("cancelled" if summary_kept else None)
        attributes = self.evaluation_attributes(recorded)
        assert (attributes["outcome"], attributes["blame"], attributes["error_kind"]) == ("cancelled", "none", "none")

    def test_cancellation_callback_failure_stays_a_user_error(self, client, recorded):
        def broken():
            raise RuntimeError("callback down")

        runner = DecisionModelRunner(DECISION_CONFIG, cancellation_requested=broken)
        with pytest.raises(EvaluationException, match="cancellation callback failed"):
            asyncio.run(self.runner_strategy(runner).evaluate({}))
        attributes = self.evaluation_attributes(recorded)
        assert (attributes["outcome"], attributes["blame"], attributes["error_kind"]) == ("error", "user", "none")

    def test_metric_sink_failure_does_not_change_the_result(self):
        broken = SimpleNamespace(get_meter=Mock(side_effect=RuntimeError("sink down")))
        with patch.dict(sys.modules, {"opentelemetry.metrics": broken}):
            result = asyncio.run(strategy_with(level_payload(4), LikertScoring(5)).evaluate({}))
        assert result["tool_call_accuracy_status"] != "skipped"
        broken.get_meter.assert_called()

    def test_broken_opentelemetry_import_does_not_change_the_result_or_error(self):
        broken = ModuleType("opentelemetry.metrics")

        def unavailable(name):
            raise RuntimeError(f"broken opentelemetry installation: {name}")

        broken.__getattr__ = unavailable
        refused = level_payload(4)
        refused["answers"]["tool_call_accuracy"] = {"type": "refusal"}
        with patch.dict(sys.modules, {"opentelemetry.metrics": broken}):
            result = asyncio.run(strategy_with(level_payload(4), LikertScoring(5)).evaluate({}))
            with pytest.raises(DecisionRefusalError):
                asyncio.run(strategy_with(refused, LikertScoring(5)).evaluate({}))
        assert result["tool_call_accuracy_status"] != "skipped"

    def test_missing_opentelemetry_is_ignored(self):
        with patch.dict(sys.modules, {"opentelemetry.metrics": None}):
            result = asyncio.run(strategy_with(level_payload(4), LikertScoring(5)).evaluate({}))
        assert result["tool_call_accuracy_status"] != "skipped"

    def test_public_evaluator_records_request_and_evaluation_metrics(self, client, recorded):
        class Judge(ModelEvaluatorBase):
            _supports_decision_models = True

            def _derive_singleton_inputs(self):
                return [["query", "response"]]

            async def _do_eval(self, eval_input):
                return await DecisionEvaluationStrategy(
                    self._decision_model_runner,
                    result_key="tool_call_accuracy",
                    error_target=ErrorTarget.TOOL_CALL_ACCURACY_EVALUATOR,
                    questions=QUESTIONS,
                    scoring=LikertScoring(5),
                    threshold=3,
                    timeout=self._LLM_CALL_TIMEOUT,
                ).evaluate(eval_input)

        client.post = AsyncMock(return_value=FakeResponse(body=json.dumps(level_payload(4)).encode()))
        Judge(result_key="tool_call_accuracy", model_config=DECISION_CONFIG)(query="q", response="r")
        assert "azure.ai.evaluation.decision.operations" in [name for name, _, _ in recorded]
        attributes = self.evaluation_attributes(recorded)
        assert (attributes["outcome"], attributes["protocol"]) == ("completed", "microsoft")


class TestDecisionExecutionControls:
    @pytest.mark.parametrize(
        "value",
        [
            pytest.param(10**309, id="oversized_positive"),
            pytest.param(-(10**309), id="oversized_negative"),
        ],
    )
    @pytest.mark.parametrize("control", ["probability_threshold", "timeout_seconds", "timeout", "call_timeout"])
    def test_oversized_numeric_controls_raise_typed_user_error(self, client, control, value):
        with pytest.raises(EvaluationException) as raised:
            if control == "probability_threshold":
                DecisionModelRunner({**DECISION_CONFIG, control: value}, binary=True)
            elif control == "timeout_seconds":
                DecisionModelRunner(DECISION_CONFIG, timeout_seconds=value)
            elif control == "timeout":
                ProbeModelEvaluator(result_key="probe", model_config=DECISION_CONFIG, timeout=value)
            else:
                asyncio.run(DecisionModelRunner(DECISION_CONFIG)(state={}, questions=QUESTIONS, timeout=value))
        assert raised.value.blame == ErrorBlame.USER_ERROR
        assert raised.value.category == ErrorCategory.INVALID_VALUE
        assert not client.calls

    def test_overall_timeout_defaults_are_backend_specific(self):
        decision = ProbeModelEvaluator(result_key="probe", model_config=DECISION_CONFIG)
        with patch.object(_model_runners.AsyncPrompty, "load"):
            chat = ProbeModelEvaluator(result_key="probe", prompty_file="probe.prompty", model_config=CHAT_CONFIG)
        assert decision._LLM_CALL_TIMEOUT == 120
        assert chat._LLM_CALL_TIMEOUT == 600

    @pytest.mark.parametrize("timeout,expected", [(5, 5), (300, 300), (900, 600)])
    def test_explicit_overall_timeout_retains_existing_cap(self, timeout, expected):
        evaluator = ProbeModelEvaluator(result_key="probe", model_config=DECISION_CONFIG, timeout=timeout)
        assert evaluator._LLM_CALL_TIMEOUT == expected

    @pytest.mark.parametrize("name", ["execution_policy", "observer", "deadline_seconds"])
    def test_obsolete_controls_are_not_accepted(self, name):
        with pytest.raises(TypeError, match=name):
            DecisionModelRunner(DECISION_CONFIG, **{name: object()})

    @pytest.mark.parametrize(
        "options",
        [
            {"timeout_seconds": 0},
            {"timeout_seconds": True},
            {"timeout_seconds": float("nan")},
            {"max_retries": True},
            {"max_retries": -1},
            {"max_retries": 1.5},
            {"max_request_bytes": 0},
            {"max_state_question_bytes": False},
            {"max_response_bytes": "100"},
            {"cancellation_requested": False},
        ],
    )
    def test_invalid_controls(self, options):
        with pytest.raises(EvaluationException) as raised:
            DecisionModelRunner(DECISION_CONFIG, **options)
        assert raised.value.blame == ErrorBlame.USER_ERROR

    def test_base_forwards_controls_outside_strict_config(self):
        evaluator = ProbeModelEvaluator(
            result_key="probe", model_config=DECISION_CONFIG, max_retries=0, timeout=5, timeout_seconds=2
        )
        assert evaluator._decision_model_runner._max_retries == 0
        assert evaluator._decision_model_runner._timeout_seconds == 2
        assert evaluator._LLM_CALL_TIMEOUT == 5
        with pytest.raises(EvaluationException, match="Unsupported"):
            DecisionModelRunner({**DECISION_CONFIG, "max_retries": 0})

    @pytest.mark.parametrize("timeout", [0, -1, True, float("nan"), float("inf"), "30"])
    def test_invalid_overall_timeouts_are_rejected(self, client, timeout):
        with pytest.raises(EvaluationException, match="positive finite"):
            ProbeModelEvaluator(result_key="probe", model_config=DECISION_CONFIG, timeout=timeout)
        with pytest.raises(EvaluationException, match="positive finite"):
            run(DecisionModelRunner(DECISION_CONFIG), timeout=timeout)
        assert not client.calls

    @pytest.mark.parametrize("status", [400, 429, 500])
    @pytest.mark.parametrize("response_limit", [1, 1024])
    def test_final_http_error_keeps_classification_and_only_accepted_known_usage(self, client, status, response_limit):
        client.response = FakeResponse(status, json.dumps(level_payload(4)).encode())
        with pytest.raises(EvaluationException, match=f"HTTP {status}") as raised:
            run(DecisionModelRunner(DECISION_CONFIG, max_retries=0, max_response_bytes=response_limit))
        assert raised.value.blame == (ErrorBlame.USER_ERROR if status == 400 else ErrorBlame.SYSTEM_ERROR)
        execution = raised.value.properties["decision_model"].pop("execution")
        assert validated_execution(execution) == execution
        assert execution["outcome"] == "error"
        if response_limit == 1:
            assert raised.value.properties == {"decision_model": {"deployment": "Decision-1", "protocol": "microsoft"}}
        else:
            assert raised.value.properties["total_tokens"] == 123
            assert raised.value.properties["model"] == "microsoft-decision-1"

    @pytest.mark.parametrize(
        "controls",
        [
            {"timeout": 10},
            {"timeout_seconds": 2},
            {"max_retries": 0},
            {"cancellation_requested": lambda: False},
            {"max_request_bytes": 10},
            {"max_state_question_bytes": 10},
            {"max_response_bytes": 10},
        ],
    )
    def test_explicit_controls_on_prompty_are_rejected_without_loading_a_flow(self, controls):
        with patch.object(_model_runners.AsyncPrompty, "load") as load:
            with pytest.raises(EvaluationException, match="only supported"):
                ProbeModelEvaluator(
                    result_key="probe",
                    prompty_file="probe.prompty",
                    model_config=CHAT_CONFIG,
                    **controls,
                )
        load.assert_not_called()

    def test_transport_timeout_and_single_retry_policy(self, client):
        client.response = FakeResponse(body=json.dumps(level_payload(4)).encode())
        run(DecisionModelRunner(DECISION_CONFIG, timeout_seconds=2, max_retries=7))
        retry = client.policies["retry_policy"]
        assert retry.total_retries == retry.connect_retries == retry.read_retries == retry.status_retries == 7
        assert client.calls[0]["options"]["connection_timeout"] == 2
        assert "read_timeout" not in client.calls[0]["options"]

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
        run(DecisionModelRunner(DECISION_CONFIG, **{field: size}), state=state)
        assert b"\xc3\xa9" in client.calls[0]["content"] and b"\\u00e9" not in client.calls[0]["content"]
        client.calls.clear()
        with pytest.raises(EvaluationException, match="byte budget") as raised:
            run(
                DecisionModelRunner(DECISION_CONFIG, **{field: size - 1}),
                state=state,
            )
        assert not client.calls
        assert raised.value.blame == ErrorBlame.USER_ERROR

    @pytest.mark.parametrize("request_cap", [None, 10000])
    def test_uncapped_state_question_pairs_are_not_serialized(self, client, request_cap, caplog):
        caplog.set_level(logging.INFO, logger=_model_runners.__name__)
        client.response = FakeResponse(body=json.dumps(level_payload(4)).encode())
        with patch.object(_model_runners.json, "dumps", wraps=json.dumps) as serialize:
            run(DecisionModelRunner(DECISION_CONFIG, max_request_bytes=request_cap))
        request_serializations = [entry for entry in serialize.call_args_list if "state" in entry.args[0]]
        assert request_serializations == [
            call(
                {"model": "Decision-1", "state": {"query": "q"}, "questions": QUESTIONS},
                ensure_ascii=False,
                separators=(",", ":"),
                allow_nan=False,
            )
        ]

    def test_non_json_request_is_rejected_before_authentication_or_network(self, client):
        with pytest.raises(EvaluationException, match="JSON-serializable") as raised:
            run(DecisionModelRunner(DECISION_CONFIG), state={"value": float("nan")})
        assert not client.calls and raised.value.blame == ErrorBlame.USER_ERROR

    def test_response_budget_exact_boundary(self, client):
        content = json.dumps(level_payload(4)).encode()
        client.response = FakeResponse(body=content)
        run(DecisionModelRunner(DECISION_CONFIG, max_response_bytes=len(content)))
        with pytest.raises(EvaluationException, match="byte budget"):
            run(DecisionModelRunner(DECISION_CONFIG, max_response_bytes=len(content) - 1))

    def test_structural_failure_preserves_usage_before_answer_validation(self, client):
        payload = level_payload(4)
        payload["answers"] = {}
        client.response = FakeResponse(body=json.dumps(payload).encode())
        with pytest.raises(EvaluationException, match="invalid response") as raised:
            run(DecisionModelRunner(DECISION_CONFIG))
        assert raised.value.properties["prompt_tokens"] == 120
        assert raised.value.properties["completion_tokens"] == 3
        assert raised.value.properties["total_tokens"] == 123
        assert raised.value.properties["model"] == "microsoft-decision-1"

    def test_unknown_or_invalid_usage_is_not_fabricated(self, client):
        client.response = FakeResponse(body=json.dumps({"usage": {"input_tokens": True, "output_tokens": 3}}).encode())
        with pytest.raises(EvaluationException) as raised:
            run(DecisionModelRunner(DECISION_CONFIG))
        execution = raised.value.properties["decision_model"].pop("execution")
        assert execution["usage_state"] == "unknown"
        assert raised.value.properties == {
            "decision_model": {"deployment": "Decision-1", "protocol": "microsoft"},
            "completion_tokens": 3,
        }

    def test_default_pipeline_owns_an_execution_observer(self, client):
        client.response = FakeResponse(body=json.dumps(level_payload(4)).encode())
        run(DecisionModelRunner(DECISION_CONFIG))
        assert isinstance(client.policies["custom_hook_policy"], DecisionExecution)
        assert type(client.policies["retry_policy"]) is AsyncRetryPolicy

    def test_base_timeout_caps_existing_evaluator_timeout(self, client):
        client.delay = 1
        evaluator = ProbeModelEvaluator(result_key="probe", model_config=DECISION_CONFIG, timeout=0.01)
        with pytest.raises(EvaluationException, match="timed out") as raised:
            run(evaluator._decision_model_runner, timeout=evaluator._LLM_CALL_TIMEOUT)
        assert raised.value.blame == ErrorBlame.SYSTEM_ERROR

    def test_evaluator_timeout_still_wins_over_longer_constructor_timeout(self, client):
        client.delay = 1
        evaluator = ProbeModelEvaluator(result_key="probe", model_config=DECISION_CONFIG, timeout=900)
        assert evaluator._LLM_CALL_TIMEOUT == 600
        with pytest.raises(EvaluationException, match="timed out"):
            run(evaluator._decision_model_runner, timeout=0.01)

    def test_precancellation_does_not_send(self, client):
        with pytest.raises(EvaluationException, match="cancelled") as raised:
            run(DecisionModelRunner(DECISION_CONFIG, cancellation_requested=lambda: True))
        assert not client.calls and raised.value.blame == ErrorBlame.USER_ERROR

    def test_inflight_cancellation_cleans_up_request(self, monkeypatch):
        cleaned_up = []

        class WaitingClient(FakeClient):
            async def post(self, *args, **kwargs):
                try:
                    await asyncio.sleep(10)
                finally:
                    cleaned_up.append(True)

        monkeypatch.setattr(_model_runners, "get_async_http_client", lambda **_: WaitingClient())

        async def request():
            cancelled = False

            async def cancel():
                nonlocal cancelled
                await asyncio.sleep(0.01)
                cancelled = True

            cancellation = asyncio.create_task(cancel())
            try:
                runner = DecisionModelRunner(DECISION_CONFIG, cancellation_requested=lambda: cancelled)
                with pytest.raises(EvaluationException, match="cancelled") as raised:
                    await runner(state={}, questions=QUESTIONS, timeout=1)
                assert raised.value.blame == ErrorBlame.USER_ERROR
            finally:
                await cancellation

        asyncio.run(request())
        assert cleaned_up == [True]

    @pytest.mark.parametrize("value", [None, "yes", 1])
    def test_cancellation_callback_requires_boolean(self, client, value):
        with pytest.raises(EvaluationException, match="boolean"):
            run(DecisionModelRunner(DECISION_CONFIG, cancellation_requested=lambda: value))
        assert not client.calls

    def test_cancellation_callback_failure_is_explicit_and_sanitized(self, client):
        callback = Mock(side_effect=RuntimeError("cancellation-secret"))
        with pytest.raises(EvaluationException, match="cancellation callback failed") as raised:
            run(DecisionModelRunner(DECISION_CONFIG, cancellation_requested=callback))
        assert raised.value.blame == ErrorBlame.USER_ERROR
        assert "secret" not in str(raised.value)
        assert not client.calls

    @pytest.mark.parametrize("field", ["max_request_bytes", "max_state_question_bytes"])
    def test_tiny_positive_budget_rejects_before_send(self, client, field):
        with pytest.raises(EvaluationException, match="byte budget"):
            run(DecisionModelRunner(DECISION_CONFIG, **{field: 1}))
        assert not client.calls

    def test_authentication_failure_is_sanitized_and_has_no_fabricated_usage(self, client):
        config = {key: value for key, value in DECISION_CONFIG.items() if key != "api_key"}
        credential = Mock(get_token=Mock(side_effect=RuntimeError("credential-secret")))
        with pytest.raises(EvaluationException, match="acquire a token") as raised:
            run(DecisionModelRunner(config, credential))
        execution = raised.value.properties["decision_model"].pop("execution")
        assert execution["attempt_count"] == 0
        assert execution["usage_state"] == "unknown"
        assert raised.value.properties == {"decision_model": {"deployment": "Decision-1", "protocol": "microsoft"}}
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
            try:
                with pytest.raises(EvaluationException) as raised:
                    await DecisionModelRunner(
                        config, credential, cancellation_requested=cancel.is_set if termination == "cancelled" else None
                    )(state={}, questions=QUESTIONS, timeout=0.02 if termination == "timeout" else 1)
                assert raised.value.blame == (
                    ErrorBlame.SYSTEM_ERROR if termination == "timeout" else ErrorBlame.USER_ERROR
                )
            finally:
                handle.cancel()

        asyncio.run(request())
        assert cleaned_up == [True] and not client.calls

    @pytest.mark.parametrize("termination", ["timeout", "cancelled"])
    def test_queued_explicit_auth_is_not_started_after_timeout_or_cancellation(self, client, termination):
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
                credential = Mock(get_token=Mock(return_value=SimpleNamespace(token="unused")))
                with pytest.raises(EvaluationException) as raised:
                    await DecisionModelRunner(
                        config, credential, cancellation_requested=cancel.is_set if termination == "cancelled" else None
                    )(state={}, questions=QUESTIONS, timeout=0.03 if termination == "timeout" else 1)
                assert raised.value.blame == (
                    ErrorBlame.SYSTEM_ERROR if termination == "timeout" else ErrorBlame.USER_ERROR
                )
                credential.get_token.assert_not_called()
                credential.close.assert_not_called()
            finally:
                if handle is not None:
                    handle.cancel()
                release.set()
                await occupied

        asyncio.run(request())
        assert not client.calls

    @pytest.mark.parametrize("termination", ["timeout", "cancelled"])
    @pytest.mark.parametrize("waiting", ["send", "retry_backoff"])
    def test_real_pipeline_termination_interrupts_send_and_retry_wait(self, monkeypatch, termination, waiting):
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
        monkeypatch.setattr(_model_runners, "get_async_http_client", lambda **_: AsyncHttpPipeline(transport=transport))

        async def request():
            nonlocal cancelled
            loop = asyncio.get_running_loop()

            def cancel():
                nonlocal cancelled
                cancelled = True

            handle = loop.call_later(0.01, cancel)
            try:
                with pytest.raises(EvaluationException) as raised:
                    await DecisionModelRunner(
                        DECISION_CONFIG,
                        cancellation_requested=(lambda: cancelled) if termination == "cancelled" else None,
                    )(state={}, questions=QUESTIONS, timeout=0.08 if termination == "timeout" else 1)
                assert raised.value.blame == (
                    ErrorBlame.SYSTEM_ERROR if termination == "timeout" else ErrorBlame.USER_ERROR
                )
                execution = raised.value.properties["decision_model"].pop("execution")
                assert execution["attempt_count"] == 1
                assert execution["outcome"] == ("deadline" if termination == "timeout" else "cancelled")
                assert raised.value.properties == {
                    "decision_model": {"deployment": "Decision-1", "protocol": "microsoft"}
                }
            finally:
                handle.cancel()

        asyncio.run(request())
        assert transport.calls == 1
        assert cleaned_up == ([True] if waiting == "send" else [])

    @pytest.mark.parametrize("max_retries", [0, 1])
    def test_real_pipeline_transport_errors_respect_retry_bound(self, monkeypatch, max_retries):
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
        monkeypatch.setattr(_model_runners, "get_async_http_client", lambda **_: AsyncHttpPipeline(transport=transport))
        with pytest.raises(EvaluationException) as raised:
            run(DecisionModelRunner(DECISION_CONFIG, max_retries=max_retries))
        expected = max_retries + 1
        assert transport.calls == expected
        execution = raised.value.properties["decision_model"].pop("execution")
        assert execution["attempt_count"] == expected
        assert execution["retry_count"] == max_retries
        assert execution["outcome"] == "error"
        assert raised.value.properties == {"decision_model": {"deployment": "Decision-1", "protocol": "microsoft"}}
        assert "secret" not in str(raised.value)

    def test_real_pipeline_success_has_no_hook_failure_or_billed_replay(self, monkeypatch):
        from azure.ai.evaluation._http_utils import AsyncHttpPipeline

        class Response(HttpResponse):
            def __init__(self, request):
                super().__init__(request, None)
                self.status_code = 200
                self.headers = {}

            def body(self):
                return json.dumps(level_payload(4)).encode()

        class Transport(AsyncHttpTransport):
            calls = 0

            async def open(self):
                pass

            async def close(self):
                pass

            async def __aexit__(self, *_):
                await self.close()

            async def send(self, request, **kwargs):
                self.calls += 1
                return Response(request)

        transport = Transport()
        monkeypatch.setattr(_model_runners, "get_async_http_client", lambda **_: AsyncHttpPipeline(transport=transport))
        assert run(DecisionModelRunner(DECISION_CONFIG))["usage"] == {"input_tokens": 120, "output_tokens": 3}
        assert transport.calls == 1


class TestDecisionExecutionObservations:
    SUMMARY = {
        "attempt_count": 1,
        "retry_count": 0,
        "elapsed_ms": 12.5,
        "outcome": "completed",
        "last_http_status": 200,
        "usage_state": "known",
    }

    @pytest.mark.parametrize(
        "case,sink",
        [
            ("completed", "normal"),
            ("retry", "normal"),
            ("error", "normal"),
            ("deadline", "normal"),
            ("cancelled", "normal"),
            ("external_cancelled", "normal"),
            ("completed", "info_off"),
            ("completed", "log_failure"),
            ("completed", "metric_failure"),
        ],
    )
    def test_actual_pipeline_observations_are_owned_once_and_sinks_are_independent(self, monkeypatch, case, sink):
        from azure.ai.evaluation._http_utils import AsyncHttpPipeline

        logger = logging.Logger("decision-test", logging.WARNING if sink == "info_off" else logging.INFO)
        handler = BufferingHandler(20)
        logger.addHandler(handler)
        adapter = logging.LoggerAdapter(logger, {"run_id": "private-run", "correlation_id": "private-correlation"})
        instruments = {}

        def instrument(name, **_):
            value = instruments.setdefault(name, Mock())
            if sink == "metric_failure":
                value.add.side_effect = RuntimeError("metric-secret")
                value.record.side_effect = RuntimeError("metric-secret")
            return value

        meter = SimpleNamespace(create_counter=instrument, create_histogram=instrument)

        async def send(request, **_):
            if case in ("deadline", "cancelled", "external_cancelled"):
                await asyncio.sleep(10)
            failed = case == "error" or (case == "retry" and transport.send.await_count == 1)
            payload = {"error": {"message": "provider-secret"}} if failed else level_payload(4)
            response = FakeResponse(500 if failed else 200, json.dumps(payload).encode(), request)
            response.headers["Retry-After"] = "0"
            return response

        transport = AsyncMock(spec=AsyncHttpTransport)
        transport.send.side_effect = send

        monkeypatch.setattr(_model_runners, "get_async_http_client", lambda **_: AsyncHttpPipeline(transport=transport))
        if sink == "log_failure":
            monkeypatch.setattr(logger, "info", Mock(side_effect=RuntimeError("logger-secret")))

        async def request():
            cancelled = asyncio.Event()
            runner = DecisionModelRunner(
                DECISION_CONFIG,
                max_retries=1 if case == "retry" else 0,
                cancellation_requested=cancelled.is_set if case == "cancelled" else None,
            )
            runner._bind_execution_logger(adapter)
            task = asyncio.current_task()
            handle = asyncio.get_running_loop().call_later(
                0.02, task.cancel if case == "external_cancelled" else cancelled.set
            )
            try:
                call = runner(state="private-evidence", questions=QUESTIONS, timeout=0.04 if case == "deadline" else 1)
                if case in ("completed", "retry"):
                    response = await call
                    summary = response["_decision_execution"]
                    assert response["usage"]["input_tokens"] == 120
                else:
                    with pytest.raises(
                        asyncio.CancelledError if case == "external_cancelled" else EvaluationException
                    ) as error:
                        await call
                    summary = error.value.properties["decision_model"]["execution"]
                assert validated_execution(summary) == summary
                assert summary["attempt_count"] == (2 if case == "retry" else 1)
                assert summary["retry_count"] == (1 if case == "retry" else 0)
                assert summary["outcome"] == (
                    "completed" if case == "retry" else "cancelled" if case == "external_cancelled" else case
                )
                assert summary["usage_state"] == (
                    "known" if case == "completed" else "partial" if case == "retry" else "unknown"
                )
                assert summary["last_http_status"] == (
                    200 if case in ("completed", "retry") else 500 if case == "error" else None
                )
            finally:
                handle.cancel()

        with patch.dict(sys.modules, {"opentelemetry.metrics": SimpleNamespace(get_meter=lambda _: meter)}):
            asyncio.run(request())
        expected = 2 if case == "retry" else 1
        assert transport.send.await_count == expected
        transport.__aexit__.assert_awaited_once()
        if sink not in ("info_off", "log_failure"):
            assert len(handler.buffer) == expected + 1
            dimensions = [json.loads(record.decision_dimensions) for record in handler.buffer]
            assert [item["phase"] for item in dimensions] == ["attempt"] * expected + ["execution"]
            for record in handler.buffer:
                assert record.run_id == "private-run" and record.correlation_id == "private-correlation"
                assert "private-evidence" not in record.decision_execution + record.getMessage()
                assert "secret" not in record.decision_execution + record.getMessage()
        else:
            assert not handler.buffer
        if sink != "metric_failure":
            prefix = "azure.ai.evaluation.decision."
            assert instruments[prefix + "provider.attempts"].add.call_count == expected
            assert instruments[prefix + "provider.duration"].record.call_count == expected
            instruments[prefix + "operations"].add.assert_called_once()
            assert instruments[prefix + "provider.retries"].add.call_count == expected - 1
            for value in instruments.values():
                for call in value.add.call_args_list + value.record.call_args_list:
                    attributes = call.kwargs["attributes"]
                    assert set(attributes) == {
                        "backend",
                        "route",
                        "protocol",
                        "phase",
                        "outcome",
                        "usage_state",
                        "http_status_class",
                        "throttled",
                    }
                    assert "private" not in str(attributes) and "Decision-1" not in str(attributes)
        handler.close()

    @pytest.mark.parametrize("outcome", ["completed", "skipped", "semantic_error"])
    def test_strategy_projects_valid_execution_without_reemitting(self, outcome):
        response = level_payload(4, status=0.1 if outcome == "skipped" else 0.9)
        summary = self.SUMMARY
        response["_decision_execution"] = summary
        if outcome == "semantic_error":
            response["answers"]["tool_call_accuracy"]["probabilities"]["4"] = 0.5
        strategy = DecisionEvaluationStrategy(
            DecisionModelRunner(DECISION_CONFIG),
            result_key="tool_call_accuracy",
            error_target=ErrorTarget.EVALUATE,
            questions=QUESTIONS,
            scoring=LikertScoring(5),
            threshold=3,
            timeout=1,
        )
        with patch.object(DecisionExecution, "emit") as emit:
            if outcome == "semantic_error":
                with pytest.raises(EvaluationException) as error:
                    strategy.parse(response, {})
                properties = error.value.properties
            else:
                properties = strategy.parse(response, {})["tool_call_accuracy_properties"]
            assert properties["decision_model"]["execution"] == summary
            assert properties["decision_model"]["execution"] is not summary
            emit.assert_not_called()

    @pytest.mark.parametrize(
        "changes",
        [
            {"attempt_count": True},
            {"attempt_count": 1.0},
            {"attempt_count": 22},
            {"retry_count": 21},
            {"elapsed_ms": True},
            {"elapsed_ms": float("nan")},
            {"elapsed_ms": float("inf")},
            {"elapsed_ms": 86400001},
            {"elapsed_ms": 10**1000},
            {"last_http_status": True},
            {"last_http_status": 99},
            {"last_http_status": 600},
            {"outcome": "private-outcome"},
            {"usage_state": "private-usage"},
        ],
    )
    def test_malformed_shared_carrier_is_rejected_without_coercion(self, changes):
        assert validated_execution({**self.SUMMARY, **changes}) is None

    def test_hosted_summary_bounds_do_not_restrict_public_retry_configuration(self, caplog):
        runner = DecisionModelRunner(DECISION_CONFIG, max_retries=100)
        assert runner._max_retries == 100
        execution = DecisionExecution(None, None)
        execution.attempt_count = 21
        execution.known_usage_attempts = 21
        assert validated_execution(execution.summary("completed"))["retry_count"] == 20
        execution.attempt_count = 22
        with patch.object(DecisionExecution, "emit"):
            assert execution.finish("completed") is None
        assert "summary omitted" in caplog.text

    def test_optional_metrics_absence_does_not_change_summary_or_require_a_logger(self):
        execution = DecisionExecution(None, None)
        with patch.dict(sys.modules, {"opentelemetry.metrics": None}):
            summary = execution.finish("error")
        assert summary["attempt_count"] == 0 and summary["usage_state"] == "unknown"
