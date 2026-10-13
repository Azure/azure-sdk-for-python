# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

"""Actual localhost HTTP coverage for the default requests-backed async transport."""

import asyncio
import json
import threading
import time
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

import pytest
import requests
from urllib3.util import connection

from azure.ai.evaluation._evaluators._common._model_runners import DecisionModelRunner
from azure.ai.evaluation._evaluators._common._base_model_eval import ModelEvaluatorBase
from azure.ai.evaluation._exceptions import ErrorBlame, EvaluationException
from azure.ai.evaluation._http_utils import get_async_http_client
from azure.core.pipeline.policies import AsyncRetryPolicy

pytestmark = pytest.mark.unittest
QUESTIONS = {"status": {"type": "noul", "instructions": "Applicable?"}}


@pytest.fixture
def localhost():
    calls = []
    delay = [0]
    statuses = [200]
    payload = {
        "model": "native-decision",
        "answers": {"status": {"type": "noul", "noul": 0.9}},
        "usage": {"input_tokens": 12, "output_tokens": 4},
    }

    class Handler(BaseHTTPRequestHandler):
        def log_message(self, *_):
            pass

        def do_POST(self):
            body = self.rfile.read(int(self.headers["Content-Length"]))
            calls.append({"path": self.path, "body": body, "content_type": self.headers.get("Content-Type")})
            time.sleep(delay[0])
            content = json.dumps(payload).encode()
            self.send_response(statuses.pop(0) if len(statuses) > 1 else statuses[0])
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(content)))
            self.end_headers()
            try:
                self.wfile.write(content)
            except (BrokenPipeError, ConnectionResetError, ConnectionAbortedError):
                pass

    server = ThreadingHTTPServer(("127.0.0.1", 0), Handler)
    thread = threading.Thread(target=server.serve_forever)
    thread.start()
    try:
        yield f"http://127.0.0.1:{server.server_port}", calls, delay, statuses
    finally:
        server.shutdown()
        server.server_close()
        thread.join()


def invoke(endpoint, timeout=3, **controls):
    runner = DecisionModelRunner(
        {"type": "decision", "azure_endpoint": endpoint, "azure_deployment": "Decision-1", "api_key": "local-test"},
        **controls,
    )
    return asyncio.run(runner(state={"query": "é"}, questions=QUESTIONS, timeout=timeout))


class SynchronousDecisionEvaluator(ModelEvaluatorBase):
    _supports_decision_models = True

    def __call__(self, *, query):
        return super().__call__(query=query)

    async def _do_eval(self, eval_input):
        return await self._decision_model_runner(state=eval_input, questions=QUESTIONS, timeout=self._LLM_CALL_TIMEOUT)


@pytest.mark.parametrize("timeout,timeout_seconds", [(0.05, None), (0.2, 0.02), (0.05, 0.2)])
def test_public_synchronous_overall_timeout_bounds_default_requests_worker(
    localhost, monkeypatch, timeout, timeout_seconds
):
    endpoint, calls, delay, _ = localhost
    delay[0] = 0.65
    observed = []
    original = requests.Session.request

    def record(session, *args, **kwargs):
        observed.append(kwargs["timeout"])
        return original(session, *args, **kwargs)

    monkeypatch.setattr(requests.Session, "request", record)
    evaluator = SynchronousDecisionEvaluator(
        result_key="status",
        model_config={
            "type": "decision",
            "azure_endpoint": endpoint,
            "azure_deployment": "Decision-1",
            "api_key": "local-test",
        },
        timeout=timeout,
        timeout_seconds=timeout_seconds,
        max_retries=0,
    )
    started = time.monotonic()
    with pytest.raises(EvaluationException) as raised:
        evaluator(query="synthetic")
    elapsed = time.monotonic() - started
    print(f"Entire public synchronous evaluator call: {elapsed:.3f}s")
    assert elapsed < 0.4
    assert len(calls) == 1
    bound = min(timeout, timeout_seconds) if timeout_seconds is not None else timeout
    assert len(observed) == 1 and 0 < observed[0] <= bound + 1e-8
    if timeout_seconds is None or timeout_seconds > timeout:
        assert "timed out" in str(raised.value)
    assert raised.value.properties == {"decision_model": {"deployment": "Decision-1"}}


def test_public_synchronous_authentication_consumes_transport_deadline(localhost, monkeypatch):
    endpoint, calls, delay, _ = localhost
    delay[0] = 0.65
    observed = []
    original = requests.Session.request

    def record(session, *args, **kwargs):
        observed.append(kwargs["timeout"])
        return original(session, *args, **kwargs)

    class Credential:
        async def get_token(self, *_):
            await asyncio.sleep(0.08)
            from azure.core.credentials import AccessToken

            return AccessToken("local-test", 9999999999)

    monkeypatch.setattr(requests.Session, "request", record)
    evaluator = SynchronousDecisionEvaluator(
        result_key="status",
        model_config={"type": "decision", "azure_endpoint": endpoint, "azure_deployment": "Decision-1"},
        credential=Credential(),
        timeout=0.15,
        max_retries=0,
    )
    started = time.monotonic()
    with pytest.raises(EvaluationException, match="timed out"):
        evaluator(query="synthetic")
    assert time.monotonic() - started < 0.4
    assert len(calls) == 1 and len(observed) == 1
    assert 0 < observed[0] <= 0.075


def test_public_synchronous_retries_and_backoff_share_remaining_deadline(localhost, monkeypatch):
    endpoint, calls, delay, statuses = localhost
    delay[0] = 0.04
    statuses[:] = [429, 429, 200]
    observed = []
    original = requests.Session.request

    def record(session, *args, **kwargs):
        observed.append(kwargs["timeout"])
        return original(session, *args, **kwargs)

    monkeypatch.setattr(requests.Session, "request", record)
    evaluator = SynchronousDecisionEvaluator(
        result_key="status",
        model_config={
            "type": "decision",
            "azure_endpoint": endpoint,
            "azure_deployment": "Decision-1",
            "api_key": "local-test",
        },
        timeout=0.2,
        max_retries=3,
    )
    started = time.monotonic()
    with pytest.raises(EvaluationException, match="timed out") as raised:
        evaluator(query="synthetic")
    assert time.monotonic() - started < 0.4
    assert len(calls) == len(observed) == 2
    assert 0 < observed[1] <= observed[0] - 0.03
    assert observed[0] <= 0.2 + 1e-8
    assert raised.value.properties == {"decision_model": {"deployment": "Decision-1"}}


def test_default_transport_sends_policy_request_and_retries(localhost, monkeypatch):
    endpoint, calls, _, statuses = localhost
    statuses[:] = [429, 200]
    observed_timeouts = []
    socket_connect_timeouts = []
    original = requests.Session.request
    original_connect = connection.create_connection

    def record_connect(address, timeout=None, *args, **kwargs):
        socket_connect_timeouts.append(timeout)
        return original_connect(address, timeout, *args, **kwargs)

    def record(session, *args, **kwargs):
        observed_timeouts.append(kwargs["timeout"])
        assert "read_timeout" not in kwargs and "connection_timeout" not in kwargs
        return original(session, *args, **kwargs)

    monkeypatch.setattr(requests.Session, "request", record)
    monkeypatch.setattr(connection, "create_connection", record_connect)
    result = invoke(endpoint, timeout_seconds=0.5, max_retries=1)
    assert result["usage"] == {"input_tokens": 12, "output_tokens": 4}
    assert observed_timeouts == [0.5, 0.5]
    assert socket_connect_timeouts == [0.5, 0.5]
    assert len(calls) == 2 and calls[0]["body"] == calls[1]["body"]
    assert calls[0]["path"] == "/providers/microsoft/v1/systemone"
    assert calls[0]["content_type"] == "application/json"
    assert json.loads(calls[0]["body"]) == {"model": "Decision-1", "state": {"query": "é"}, "questions": QUESTIONS}
    assert b"\xc3\xa9" in calls[0]["body"]


def test_default_transport_read_timeout_is_enforced(localhost):
    endpoint, calls, delay, _ = localhost
    delay[0] = 0.5
    started = time.monotonic()
    with pytest.raises(EvaluationException) as raised:
        invoke(endpoint, timeout_seconds=0.05, max_retries=0)
    assert time.monotonic() - started < 0.4
    assert len(calls) == 1
    assert raised.value.properties == {"decision_model": {"deployment": "Decision-1"}}


def test_default_transport_native_scalar_timeout_preserves_numeric_retry_deadline(localhost, monkeypatch):
    endpoint, _, _, _ = localhost
    original = requests.Session.request
    observed = []

    def record(session, *args, **kwargs):
        observed.append(kwargs["timeout"])
        return original(session, *args, **kwargs)

    monkeypatch.setattr(requests.Session, "request", record)

    async def request():
        async with get_async_http_client(retry_policy=AsyncRetryPolicy(retry_total=0)) as client:
            return await client.post(endpoint, content=b"{}", connection_timeout=2, timeout=0.8)

    assert asyncio.run(request()).status_code == 200
    assert 0 < observed[0] <= 0.8


def test_default_transport_without_read_override_preserves_scalar_timeout(localhost, monkeypatch):
    endpoint, _, _, _ = localhost
    original = requests.Session.request
    observed = []

    def record(session, *args, **kwargs):
        observed.append(kwargs["timeout"])
        return original(session, *args, **kwargs)

    monkeypatch.setattr(requests.Session, "request", record)

    async def request():
        async with get_async_http_client() as client:
            return await client.post(endpoint, content=b"{}", connection_timeout=0.7)

    assert asyncio.run(request()).status_code == 200
    assert observed == [0.7]


def test_default_transport_cancellation_interrupts_awaiting_a_real_request(localhost):
    endpoint, calls, delay, _ = localhost
    delay[0] = 0.5

    async def request():
        cancelled = asyncio.Event()
        runner = DecisionModelRunner(
            {"type": "decision", "azure_endpoint": endpoint, "azure_deployment": "Decision-1", "api_key": "local-test"},
            timeout_seconds=1,
            max_retries=0,
            cancellation_requested=cancelled.is_set,
        )
        started = time.monotonic()
        handle = asyncio.get_running_loop().call_later(0.05, cancelled.set)
        try:
            with pytest.raises(EvaluationException, match="cancelled") as raised:
                await runner(state={}, questions=QUESTIONS, timeout=3)
            assert time.monotonic() - started < 0.4
            assert raised.value.blame == ErrorBlame.USER_ERROR
            assert raised.value.properties == {"decision_model": {"deployment": "Decision-1"}}
        finally:
            handle.cancel()

    asyncio.run(request())
    assert len(calls) == 1
