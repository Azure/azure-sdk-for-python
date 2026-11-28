# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.
"""Real SIGINT checks in isolated processes, with no external service traffic."""
import json
import os
import signal
import subprocess
import sys
import threading
import time
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from unittest.mock import MagicMock

import pytest

from common.sdk_subprocess import sdk_python_command


@pytest.mark.parametrize("phase", ["setup-reuse", "setup-close", "read-item", "create-item", "metadata", "page", "offers"])
def test_sync_wait_honors_sigint_rust(phase):
    result = subprocess.run(
        sdk_python_command(
            "from common.test_sync_interrupt_unit import _interrupt_case; _interrupt_case(sys.argv[1])",
            phase,
        ),
        capture_output=True, text=True, timeout=30,
    )
    assert result.returncode == 0, result.stdout + result.stderr


@pytest.mark.parametrize("phase", ["setup-reuse", "read-item", "create-item"])
def test_sync_wait_preserves_returning_signal_handler_rust(phase):
    result = subprocess.run(
        sdk_python_command(
            "from common.test_sync_interrupt_unit import _interrupt_case; _interrupt_case(sys.argv[1], True)",
            phase,
        ),
        capture_output=True, text=True, timeout=30,
    )
    assert result.returncode == 0, result.stdout + result.stderr


def _interrupt_case(phase, continue_after_signal=False):
    # This local test server supports HTTP/1.x only, not the driver's HTTP/2 probe.
    os.environ["AZURE_COSMOS_CONNECTION_POOL_IS_HTTP2_ALLOWED"] = "false"
    from azure.cosmos import CosmosClient, exceptions
    from azure.cosmos._backend import binding_adapter

    started = threading.Event()
    finish = threading.Event()
    sent = []
    requests = []
    handled = []
    hook = MagicMock()

    class Handler(BaseHTTPRequestHandler):
        def do_GET(self):  # pylint: disable=invalid-name
            if self.path == "/":
                body = {
                    "id": "interrupt-test",
                    "_rid": "AQAAAA==",
                    "_self": "",
                    "writableLocations": [{"name": "East US", "databaseAccountEndpoint": endpoint}],
                    "readableLocations": [{"name": "East US", "databaseAccountEndpoint": endpoint}],
                    "enableMultipleWriteLocations": False,
                    "userConsistencyPolicy": {
                        "defaultConsistencyLevel": "Session",
                        "maxStalenessPrefix": 100,
                        "maxIntervalInSeconds": 5,
                    },
                }
                status = 200
            else:
                requests.append(self.path)
                started.set()
                finish.wait(5)
                body = {"code": "NotFound", "message": "Interrupt test resource"}
                status = 404
            data = json.dumps(body).encode()
            try:
                self.send_response(status)
                self.send_header("Content-Type", "application/json")
                self.send_header("Content-Length", str(len(data)))
                self.end_headers()
                self.wfile.write(data)
            except (BrokenPipeError, ConnectionResetError, ConnectionAbortedError):
                pass  # The interrupted caller can close its connection.

        do_POST = do_GET

        def log_message(self, *_args):
            pass

    server = ThreadingHTTPServer(("127.0.0.1", 0), Handler)
    endpoint = f"http://127.0.0.1:{server.server_port}"
    server_thread = threading.Thread(target=server.serve_forever, daemon=True)
    server_thread.start()
    client = CosmosClient(endpoint, "ZmFrZQ==", _backend="rust")
    adapter = client._adapter
    acquired = object()
    release = MagicMock()
    if phase.startswith("setup-"):
        def initialize(*_args, **_kwargs):
            started.set()
            assert finish.wait(5), "acquisition worker was not released"
            return acquired

        adapter._initialize_driver = MagicMock(side_effect=initialize)
        binding_adapter._rust_module.release_driver_handle = release
    else:
        adapter._ensure_driver_handle(deadline=time.monotonic() + 5)

    def interrupt():
        if started.wait(10):
            time.sleep(0.1)
            sent.append(time.monotonic())
            signal.raise_signal(signal.SIGINT)

    sender = threading.Thread(target=interrupt, daemon=True)

    def handle_signal(*_args):
        handled.append(time.monotonic())
        finish.set()

    signal.signal(signal.SIGINT, handle_signal if continue_after_signal else signal.default_int_handler)
    sender.start()

    def invoke():
        if phase.startswith("setup-"):
            return adapter._ensure_driver_handle(
                deadline=time.monotonic() + 4 if phase == "setup-close" else None
            )
        if phase == "read-item":
            return client.get_database_client("db").get_container_client("items").read_item(
                "one", partition_key="A", timeout=4, response_hook=hook
            )
        if phase == "create-item":
            return client.get_database_client("db").get_container_client("items").create_item(
                {"id": "one", "pk": "A"}, timeout=4, response_hook=hook
            )
        if phase == "metadata":
            return adapter.get_container_metadata("dbs/db/colls/items", deadline=time.monotonic() + 4)
        if phase == "page":
            return list(client.get_database_client("db").get_container_client("items").read_all_items(timeout=4))
        database = client.get_database_client("db")
        database._properties = {"_self": "dbs/AQAAAA==/"}
        return database.get_throughput(timeout=4)

    try:
        if continue_after_signal:
            if phase == "setup-reuse":
                assert invoke() is acquired
                adapter._initialize_driver.assert_called_once()
            else:
                with pytest.raises(exceptions.CosmosResourceNotFoundError):
                    invoke()
                assert len(requests) == 1, "Signal processing restarted the request"
            assert len(handled) == 1
            assert handled[0] - sent[0] < 1.5
            return
        with pytest.raises(KeyboardInterrupt):
            invoke()
        elapsed = time.monotonic() - sent[0]
        assert elapsed < 1.5, f"{phase}: SIGINT took {elapsed:.3f}s"
        hook.assert_not_called()
        print(f"{phase}: SIGINT raised KeyboardInterrupt after {elapsed:.3f}s")
        if phase.startswith("setup-"):
            pending = adapter._init_future
            assert pending is not None and not pending.done()
            if phase == "setup-close":
                client.close()
            finish.set()
            if phase == "setup-close":
                with pytest.raises(RuntimeError, match="closed during initialization"):
                    pending.result(timeout=3)
                assert adapter._driver_handle is None
            else:
                assert pending.result(timeout=3) is acquired
                assert adapter._ensure_driver_handle() is acquired
                adapter._initialize_driver.assert_called_once()
            client.close()
            release.assert_called_once_with(acquired)
        else:
            finish.set()
            with pytest.raises(exceptions.CosmosResourceNotFoundError):
                client.get_database_client("db").read(timeout=2)
    finally:
        finish.set()
        sender.join(3)
        client.close()
        server.shutdown()
        server.server_close()
        server_thread.join(3)


if __name__ == "__main__":
    _interrupt_case(sys.argv[1], len(sys.argv) > 2 and sys.argv[2] == "continue")
