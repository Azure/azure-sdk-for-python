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

from azure.ai.evaluation._evaluators._common import DecisionExecutionPolicy
from azure.ai.evaluation._evaluators._common._model_runners import DecisionModelRunner
from azure.ai.evaluation._exceptions import EvaluationException
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


def invoke(endpoint, policy, timeout=3):
    runner = DecisionModelRunner(
        {"type": "decision", "azure_endpoint": endpoint, "azure_deployment": "Decision-1", "api_key": "local-test"},
        execution_policy=policy,
    )
    return asyncio.run(runner(state={"query": "é"}, questions=QUESTIONS, timeout=timeout))


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
    receipts = []
    result = invoke(endpoint, DecisionExecutionPolicy(timeout_seconds=0.5, max_retries=1, observer=receipts.append))
    assert result["usage"] == {"input_tokens": 12, "output_tokens": 4}
    assert observed_timeouts == [(0.5, 0.5), (0.5, 0.5)]
    assert socket_connect_timeouts == [0.5, 0.5]
    assert [receipt.http_status for receipt in receipts] == [429, 200]
    assert [receipt.attempt for receipt in receipts] == [1, 2]
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
        invoke(endpoint, DecisionExecutionPolicy(timeout_seconds=0.05, max_retries=0))
    assert time.monotonic() - started < 0.4
    assert len(calls) == 1
    assert raised.value.observations[0].attempt == 1
    assert raised.value.observations[0].outcome == "error"


def test_default_transport_numeric_retry_deadline_and_separate_timeout_bounds(localhost, monkeypatch):
    endpoint, _, _, _ = localhost
    original = requests.Session.request
    observed = []

    def record(session, *args, **kwargs):
        observed.append(kwargs["timeout"])
        return original(session, *args, **kwargs)

    monkeypatch.setattr(requests.Session, "request", record)

    async def request():
        async with get_async_http_client(retry_policy=AsyncRetryPolicy(retry_total=0)) as client:
            return await client.post(endpoint, content=b"{}", connection_timeout=2, read_timeout=0.3, timeout=0.8)

    assert asyncio.run(request()).status_code == 200
    assert 0 < observed[0][0] <= 0.8
    assert observed[0][1] == 0.3


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
