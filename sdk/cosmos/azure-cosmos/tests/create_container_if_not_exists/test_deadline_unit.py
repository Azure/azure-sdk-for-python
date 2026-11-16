# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.
"""Shared container workflow budgets across the real Python adapter boundary."""
import asyncio
import inspect
import json
import os
import subprocess
import sys
import threading
import time
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from unittest.mock import MagicMock

import pytest

from azure.cosmos import PartitionKey
from azure.cosmos.exceptions import CosmosClientTimeoutError
from common.test_client_timeout_defaults_unit import case as case, clock as clock


def _complete(value):
    return asyncio.run(value) if inspect.isawaitable(value) else value


def _response(status):
    body = {"message": "missing"} if status == 404 else {"id": "orders", "_rid": "rid"}
    return status, 0, {"x-ms-request-charge": "1"}, json.dumps(body).encode(), None


def _invoke(case, **kwargs):
    return _complete(case.client.get_database_client("sales").create_container_if_not_exists(
        "orders", PartitionKey(path="/pk"), **kwargs
    ))


@pytest.mark.parametrize("existing", [False, True])
@pytest.mark.parametrize("options,budget", [
    ({}, 1), ({"timeout": None}, 1), ({"timeout": 2}, 2),
    ({"timeout": 2, "request_options": {"timeout": 3}}, 2),
])
def test_read_and_create_share_budget_and_next_call_starts_fresh_rust(case, clock, existing, options, budget):
    calls = []

    def read(*_args, **kwargs):
        calls.append(("read", kwargs["timeout_seconds"]))
        clock[0] += 0.75
        return _response(200 if existing else 404)

    def create(*_args, **kwargs):
        calls.append(("create", kwargs["timeout_seconds"]))
        return _response(201)

    case.install("read_container", side_effect=read)
    case.install("create_container", side_effect=create)
    hook = MagicMock()
    assert _invoke(case, response_hook=hook, **options).id == "orders"
    assert calls == [("read", budget)] + ([] if existing else [("create", budget - 0.75)])
    hook.assert_called_once()
    calls.clear()
    assert _invoke(case).id == "orders"
    assert calls == [("read", 1)] + ([] if existing else [("create", 0.25)])


@pytest.mark.parametrize("phase", ["missing-read", "existing-read", "create"])
def test_expiry_prevents_later_requests_and_success_hook_rust(case, clock, phase):
    calls = []

    def read(*_args, **_kwargs):
        calls.append("read")
        clock[0] += 0.25 if phase == "create" else 1.25
        return _response(200 if phase == "existing-read" else 404)

    def create(*_args, **kwargs):
        calls.append("create")
        assert kwargs["timeout_seconds"] == 0.75
        clock[0] += 1
        return _response(201)

    case.install("read_container", side_effect=read)
    case.install("create_container", side_effect=create)
    hook = MagicMock()
    with pytest.raises(CosmosClientTimeoutError):
        _invoke(case, response_hook=hook)
    assert calls == (["read", "create"] if phase == "create" else ["read"])
    hook.assert_not_called()
    assert not case.client.client_connection._container_properties_cache


@pytest.mark.parametrize("existing", [False, True])
def test_customer_hook_timeout_is_not_reclassified_or_replayed_rust(case, clock, existing):
    read = case.install("read_container", result=_response(200 if existing else 404))
    create = case.install("create_container", result=_response(201))
    failure = TimeoutError("customer callback")

    def hook(*_args):
        clock[0] += 2
        raise failure

    with pytest.raises(TimeoutError) as caught:
        _invoke(case, response_hook=hook)
    assert caught.value is failure
    assert read.call_count == 1
    assert create.call_count == int(not existing)


@pytest.mark.parametrize("expires", [False, True])
def test_conflict_reread_uses_remaining_budget_rust(case, clock, expires):
    calls = []

    def read(*_args, **kwargs):
        calls.append(("read", kwargs["timeout_seconds"]))
        if len(calls) == 1:
            clock[0] += 0.25
            return _response(404)
        return _response(200)

    def create(*_args, **kwargs):
        calls.append(("create", kwargs["timeout_seconds"]))
        clock[0] += 1 if expires else 0.25
        return _response(409)

    case.install("read_container", side_effect=read)
    case.install("create_container", side_effect=create)
    hook = MagicMock()
    if expires:
        with pytest.raises(CosmosClientTimeoutError):
            _invoke(case, response_hook=hook)
        hook.assert_not_called()
        assert not case.client.client_connection._container_properties_cache
    else:
        assert _invoke(case, response_hook=hook).id == "orders"
        hook.assert_called_once()
    assert calls == [("read", 1), ("create", 0.75)] + ([] if expires else [("read", 0.5)])


@pytest.mark.parametrize("asynchronous", [False, True], ids=["sync", "async"])
@pytest.mark.parametrize("operation", ["create-if-missing", "delete", "replace"])
def test_real_binding_bounds_container_workflows_rust(asynchronous, operation):
    # Isolate native runtimes from the mocked clocks and adapters in this suite.
    environment = dict(os.environ)
    environment["PYTHONPATH"] = os.pathsep.join(
        [str(Path(__file__).resolve().parents[1]), *sys.path]
    )
    result = subprocess.run(
        [sys.executable, "-c",
         "from create_container_if_not_exists.test_deadline_unit import _run_delayed_container_workflow; "
         f"_run_delayed_container_workflow({asynchronous!r}, {operation!r})"],
        env=environment,
        capture_output=True,
        text=True,
        timeout=30,
        check=False,
    )
    assert result.returncode == 0, result.stdout + result.stderr


def _run_delayed_container_workflow(asynchronous, operation):
    """Two 600 ms loopback responses must not fit into a one-second operation."""
    from azure.cosmos import ConnectionPoolOptions, CosmosClient, CosmosRuntime
    from azure.cosmos.aio import CosmosClient as AsyncCosmosClient

    finished = threading.Event()
    requests = []
    properties = {
        "id": "orders", "_rid": "AQAAAIABAAA=", "_self": "dbs/AQAAAA==/colls/AQAAAIABAAA=/",
        "partitionKey": {"paths": ["/pk"], "kind": "Hash", "version": 2},
    }
    write_operation = "create" if operation == "create-if-missing" else operation

    class Handler(BaseHTTPRequestHandler):
        def do_GET(self):  # pylint: disable=invalid-name
            if self.path == "/":
                location = {"name": "East US", "databaseAccountEndpoint": endpoint}
                body = {"id": "test", "_rid": "AQAAAA==", "_self": "",
                        "writableLocations": [location], "readableLocations": [location]}
                status = 200
            else:
                requests.append(("read", time.monotonic()))
                finished.wait(0.6)
                body, status = (
                    ({"code": "NotFound", "message": "missing"}, 404)
                    if operation == "create-if-missing" else (properties, 200)
                )
            self.respond(status, body)

        def do_POST(self):  # pylint: disable=invalid-name
            self.rfile.read(int(self.headers.get("Content-Length", 0)))
            requests.append((write_operation, time.monotonic()))
            finished.wait(0.6)
            self.respond({"create": 201, "replace": 200, "delete": 204}[write_operation], properties)

        do_PUT = do_POST
        do_DELETE = do_POST

        def respond(self, status, body):
            data = b"" if status == 204 else json.dumps(body).encode()
            try:
                self.send_response(status)
                self.send_header("Content-Type", "application/json")
                self.send_header("Content-Length", str(len(data)))
                self.end_headers()
                self.wfile.write(data)
            except (BrokenPipeError, ConnectionResetError, ConnectionAbortedError):
                pass  # The expired native request can close its connection.

        def log_message(self, *_args):
            pass

    runtime = CosmosRuntime.create(connection_pool=ConnectionPoolOptions(proxy_allowed=False))
    server = ThreadingHTTPServer(("127.0.0.1", 0), Handler)
    endpoint = f"http://127.0.0.1:{server.server_port}"
    worker = threading.Thread(target=server.serve_forever, daemon=True)
    worker.start()
    client_type = AsyncCosmosClient if asynchronous else CosmosClient
    client = client_type(endpoint, "ZmFrZQ==", _backend="rust", timeout=1, runtime=runtime)
    hook = MagicMock()

    async def run():
        try:
            if asynchronous:
                await asyncio.wait_for(client._adapter.initialize(), 5)
            else:
                client._adapter._ensure_driver_handle(deadline=time.monotonic() + 5)
            started = time.monotonic()
            with pytest.raises(CosmosClientTimeoutError):
                database = client.get_database_client("sales")
                if operation == "delete":
                    result = database.delete_container("orders", response_hook=hook)
                elif operation == "replace":
                    result = database.replace_container(
                        "orders", PartitionKey(path="/pk"), response_hook=hook
                    )
                else:
                    result = database.create_container_if_not_exists(
                        "orders", PartitionKey(path="/pk"), response_hook=hook
                    )
                if inspect.isawaitable(result):
                    await result
            elapsed = time.monotonic() - started
            assert 0.8 <= elapsed < 1.5, elapsed
            assert [name for name, _ in requests] == ["read", write_operation]
            assert requests[1][1] - started >= 0.5
            hook.assert_not_called()
        finally:
            result = client.close()
            if inspect.isawaitable(result):
                await result

    try:
        asyncio.run(run())
    finally:
        finished.set()
        server.shutdown()
        server.server_close()
        worker.join(3)


@pytest.mark.parametrize("expire_source_read", [False, True])
def test_gsi_source_read_shares_get_or_create_budget_rust(case, clock, expire_source_read):
    calls = []

    def read(*_args, **kwargs):
        calls.append(("read", kwargs["timeout_seconds"]))
        if len(calls) == 1:
            clock[0] += 0.25
            return _response(404)
        clock[0] += 1 if expire_source_read else 0.25
        return _response(200)

    def create(*_args, **kwargs):
        calls.append(("create", kwargs["timeout_seconds"]))
        return _response(201)

    case.install("read_container", side_effect=read)
    case.install("create_container", side_effect=create)
    hook = MagicMock()
    options = {"global_secondary_index": {"sourceCollectionId": "source"}, "response_hook": hook}
    if expire_source_read:
        with pytest.raises(CosmosClientTimeoutError):
            _invoke(case, **options)
        hook.assert_not_called()
    else:
        assert _invoke(case, **options).id == "orders"
        hook.assert_called_once()
    assert calls == [("read", 1), ("read", 0.75)] + (
        [] if expire_source_read else [("create", 0.5)]
    )
