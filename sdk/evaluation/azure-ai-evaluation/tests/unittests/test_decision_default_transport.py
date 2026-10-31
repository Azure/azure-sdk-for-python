# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

"""Actual localhost HTTP coverage for Decision async HTTP and the unchanged shared requests transport."""

import asyncio
import json
import threading
import time
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

import pytest
import aiohttp
import requests

from azure.ai.evaluation._evaluators._common._model_runners import DecisionModelRunner
from azure.ai.evaluation._evaluators._common._model_runners import validated_execution
from azure.ai.evaluation._evaluators._common._base_model_eval import ModelEvaluatorBase
from azure.ai.evaluation._exceptions import ErrorBlame, EvaluationException
from azure.ai.evaluation._http_utils import get_async_http_client
from azure.core.pipeline.policies import AsyncRetryPolicy
from azure.core.pipeline.transport import AsyncioRequestsTransport
from azure.core.exceptions import ServiceRequestTimeoutError

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


def assert_failure_execution(error, attempts, outcome):
    assert set(error.properties) == {"decision_model"}
    native = error.properties["decision_model"]
    assert set(native) == {"deployment", "execution", "protocol"} and native["deployment"] == "Decision-1"
    execution = native["execution"]
    assert validated_execution(execution) == execution
    assert execution["attempt_count"] == attempts and execution["retry_count"] == max(0, attempts - 1)
    assert execution["outcome"] == outcome


class SynchronousDecisionEvaluator(ModelEvaluatorBase):
    _supports_decision_models = True

    def __call__(self, *, query):
        return super().__call__(query=query)

    async def _do_eval(self, eval_input):
        return await self._decision_model_runner(state=eval_input, questions=QUESTIONS, timeout=self._LLM_CALL_TIMEOUT)


@pytest.mark.parametrize("timeout,timeout_seconds", [(0.05, None), (0.2, 0.02), (0.05, 0.2)])
def test_public_synchronous_overall_timeout_bounds_native_async_transport(
    localhost, monkeypatch, timeout, timeout_seconds
):
    endpoint, calls, delay, _ = localhost
    delay[0] = 0.65
    observed = []
    original = aiohttp.ClientSession.request

    def record(session, *args, **kwargs):
        observed.append(kwargs["timeout"].sock_connect)
        return original(session, *args, **kwargs)

    monkeypatch.setattr(aiohttp.ClientSession, "request", record)
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
    if (
        timeout_seconds is not None
        and timeout_seconds < timeout
        and isinstance(raised.value.__context__, ServiceRequestTimeoutError)
    ):
        assert not calls
    else:
        assert len(calls) == 1
    bound = min(timeout, timeout_seconds) if timeout_seconds is not None else timeout
    assert len(observed) == 1 and 0 < observed[0] <= bound + 1e-8
    if timeout_seconds is None or timeout_seconds > timeout:
        assert "timed out" in str(raised.value)
    assert_failure_execution(
        raised.value, 1, "deadline" if timeout_seconds is None or timeout_seconds > timeout else "error"
    )


def test_public_synchronous_authentication_consumes_transport_deadline(localhost, monkeypatch):
    endpoint, calls, delay, _ = localhost
    delay[0] = 0.65
    observed = []
    original = aiohttp.ClientSession.request

    def record(session, *args, **kwargs):
        observed.append(kwargs["timeout"].sock_connect)
        return original(session, *args, **kwargs)

    class Credential:
        async def get_token(self, *_):
            await asyncio.sleep(0.08)
            from azure.core.credentials import AccessToken

            return AccessToken("local-test", 9999999999)

    monkeypatch.setattr(aiohttp.ClientSession, "request", record)
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


@pytest.mark.parametrize("first_request_delay", [0, 0.16])
def test_public_synchronous_retries_and_backoff_share_remaining_deadline(localhost, monkeypatch, first_request_delay):
    endpoint, calls, delay, statuses = localhost
    delay[0] = 0.04
    statuses[:] = [429, 429, 200]
    observed = []
    original = aiohttp.ClientSession.request

    def record(session, *args, **kwargs):
        if not observed:
            time.sleep(first_request_delay)
        observed.append(kwargs["timeout"].sock_connect)
        return original(session, *args, **kwargs)

    monkeypatch.setattr(aiohttp.ClientSession, "request", record)
    evaluator = SynchronousDecisionEvaluator(
        result_key="status",
        model_config={
            "type": "decision",
            "azure_endpoint": endpoint,
            "azure_deployment": "Decision-1",
            "api_key": "local-test",
        },
        # Allow scheduling headroom for two responses, but expire before the native 1.6s backoff.
        timeout=0.8,
        max_retries=3,
    )
    started = time.monotonic()
    with pytest.raises(EvaluationException, match="timed out") as raised:
        evaluator(query="synthetic")
    assert time.monotonic() - started < 1.2
    assert len(calls) == len(observed) == 2
    assert 0 < observed[1] <= observed[0] - 0.03
    assert observed[0] <= 0.8 + 1e-8
    assert_failure_execution(raised.value, 2, "deadline")


def test_default_transport_sends_policy_request_and_retries(localhost, monkeypatch):
    endpoint, calls, _, statuses = localhost
    statuses[:] = [429, 200]
    observed_timeouts = []
    socket_read_timeouts = []
    original = aiohttp.ClientSession.request

    def record(session, *args, **kwargs):
        observed_timeouts.append(kwargs["timeout"].sock_connect)
        socket_read_timeouts.append(kwargs["timeout"].sock_read)
        assert "read_timeout" not in kwargs and "connection_timeout" not in kwargs
        return original(session, *args, **kwargs)

    monkeypatch.setattr(aiohttp.ClientSession, "request", record)
    result = invoke(endpoint, timeout_seconds=0.5, max_retries=1)
    assert result["usage"] == {"input_tokens": 12, "output_tokens": 4}
    assert observed_timeouts == [0.5, 0.5]
    assert socket_read_timeouts == [0.5, 0.5]
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
    assert_failure_execution(raised.value, 1, "error")


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


def test_decision_preserves_factory_injected_requests_transport(localhost, monkeypatch):
    from azure.ai.evaluation._evaluators._common import _model_runners

    endpoint, calls, _, _ = localhost
    observed = []
    original = requests.Session.request

    def record(session, *args, **kwargs):
        observed.append(kwargs["timeout"])
        assert "read_timeout" not in kwargs
        return original(session, *args, **kwargs)

    monkeypatch.setattr(requests.Session, "request", record)
    monkeypatch.setattr(
        _model_runners,
        "get_async_http_client",
        lambda **_: get_async_http_client(transport=AsyncioRequestsTransport()),
    )
    assert invoke(endpoint, timeout_seconds=0.7)["usage"] == {"input_tokens": 12, "output_tokens": 4}
    assert observed == [0.7]
    assert len(calls) == 1


def test_repeated_public_calls_close_async_sessions_on_their_own_loops(localhost, monkeypatch):
    endpoint, calls, _, _ = localhost
    closed = []
    original_close = aiohttp.ClientSession.close

    async def close(session):
        await original_close(session)
        closed.append((session, asyncio.get_running_loop()))

    monkeypatch.setattr(aiohttp.ClientSession, "close", close)
    evaluator = SynchronousDecisionEvaluator(
        result_key="status",
        model_config={
            "type": "decision",
            "azure_endpoint": endpoint,
            "azure_deployment": "Decision-1",
            "api_key": "local-test",
        },
    )
    for _ in range(2):
        assert evaluator(query="synthetic")["usage"] == {"input_tokens": 12, "output_tokens": 4}
    assert len(calls) == len(closed) == 2
    assert all(session.closed and loop.is_closed() for session, loop in closed)
    assert closed[0][1] is not closed[1][1]


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
            assert_failure_execution(raised.value, 1, "cancelled")
        finally:
            handle.cancel()

    asyncio.run(request())
    assert len(calls) == 1


@pytest.fixture
def trickling_endpoint():
    sent = []
    disconnected = threading.Event()
    disconnected_at = []
    payload = json.dumps(
        {
            "model": "native-decision",
            "answers": {"status": {"type": "noul", "noul": 0.9}},
            "usage": {"input_tokens": 12, "output_tokens": 4},
            "padding": "x" * 160,
        }
    ).encode()

    class Handler(BaseHTTPRequestHandler):
        def log_message(self, *_):
            pass

        def do_POST(self):
            self.rfile.read(int(self.headers["Content-Length"]))
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(payload)))
            self.end_headers()
            for offset in range(0, len(payload), 4):
                try:
                    self.wfile.write(payload[offset : offset + 4])
                    self.wfile.flush()
                    sent.append(len(payload[offset : offset + 4]))
                except (BrokenPipeError, ConnectionResetError, ConnectionAbortedError):
                    disconnected_at.append(time.monotonic())
                    disconnected.set()
                    break
                time.sleep(0.03)

    server = ThreadingHTTPServer(("127.0.0.1", 0), Handler)
    thread = threading.Thread(target=server.serve_forever)
    thread.start()
    try:
        yield f"http://127.0.0.1:{server.server_port}", sent, disconnected, disconnected_at, len(payload)
    finally:
        server.shutdown()
        server.server_close()
        thread.join()


@pytest.mark.parametrize("batch", [False, True], ids=["public_sync", "batch"])
@pytest.mark.parametrize("cancel", [False, True], ids=["deadline", "cancellation"])
def test_trickling_body_is_stopped_by_overall_deadline_or_cancellation(trickling_endpoint, monkeypatch, batch, cancel):
    import pandas as pd

    from azure.ai.evaluation._evaluate._batch_run import RunSubmitterClient

    endpoint, sent, disconnected, disconnected_at, length = trickling_endpoint
    closed_sessions = []
    original_close = aiohttp.ClientSession.close

    async def close(session):
        await original_close(session)
        closed_sessions.append(session)

    monkeypatch.setattr(aiohttp.ClientSession, "close", close)
    cancelled = threading.Event()
    evaluator = SynchronousDecisionEvaluator(
        result_key="status",
        model_config={
            "type": "decision",
            "azure_endpoint": endpoint,
            "azure_deployment": "Decision-1",
            "api_key": "local-test",
        },
        timeout=3 if cancel else 0.2,
        cancellation_requested=cancelled.is_set if cancel else None,
        max_retries=0,
    )
    client = RunSubmitterClient() if batch else None
    timer = threading.Timer(0.2, cancelled.set) if cancel else None
    try:
        if timer:
            timer.start()
        started = time.monotonic()
        if client:
            run = client.run(
                evaluator,
                pd.DataFrame([{"query": "synthetic"}]),
                evaluator_name="judge",
                column_mapping={"query": "${data.query}"},
            )
            summary = client.get_run_summary(run)
            assert summary["failed_lines"] == 1
            assert summary["completed_lines"] == 0
        else:
            with pytest.raises(EvaluationException, match="cancelled" if cancel else "timed out") as raised:
                evaluator(query="synthetic")
            assert_failure_execution(raised.value, 1, "cancelled" if cancel else "deadline")
        elapsed = time.monotonic() - started
        # The existing batch engine polls run completion every second; the HTTP read must stop sooner.
        assert elapsed < (1.5 if batch else 0.8)
        assert 0 < sum(sent) < length
        assert disconnected.wait(0.5), "The server must observe the HTTP body read stopping."
        assert disconnected_at[0] - started < 0.8
        assert len(closed_sessions) == 1 and closed_sessions[0].closed
        stopped_at = sum(sent)
        time.sleep(0.09)
        assert sum(sent) == stopped_at < length
        print(
            f"batch={batch} cancel={cancel}: returned={elapsed:.3f}s disconnected="
            f"{disconnected_at[0] - started:.3f}s bytes={stopped_at}/{length}"
        )
    finally:
        if timer:
            timer.cancel()
            timer.join()
        if client:
            client._thread_pool.shutdown(wait=True)
