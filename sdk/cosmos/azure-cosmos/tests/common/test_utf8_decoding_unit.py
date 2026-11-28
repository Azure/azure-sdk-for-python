# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.
"""UTF-8 options and real binding calls against controlled localhost responses."""

import asyncio
import json
import os
import subprocess
import sys
import threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

import pytest

from common.sdk_subprocess import sdk_python_command

from azure.cosmos._backend.client_config import build_client_config
from azure.cosmos._helpers._request_settings import (
    build_request_headers_and_settings,
    compose_item_options,
)


@pytest.mark.parametrize("mode", [True, 1, "", "lossy", "REPLACE", "IGNORE"])
def test_utf8_decoding_rejects_invalid_client_and_request_modes_rust(mode):
    error = TypeError if type(mode) is not str else ValueError
    with pytest.raises(error, match="utf8_decoding_mode"):
        build_client_config(utf8_decoding_mode=mode)
    with pytest.raises(error, match="utf8_decoding_mode"):
        build_request_headers_and_settings({"utf8DecodingMode": mode})


def test_utf8_decoding_keyword_overrides_nested_option_without_becoming_header_rust():
    kwargs = {
        "request_options": {"utf8DecodingMode": "Lossy"},
        "utf8_decoding_mode": "Strict",
    }
    original = kwargs["request_options"]
    headers, settings = build_request_headers_and_settings(compose_item_options(kwargs))
    assert settings.utf8_decoding_mode == "Strict"
    assert headers == {} and kwargs == {}
    assert original == {"utf8DecodingMode": "Lossy"}


@pytest.mark.parametrize("asynchronous", [False, True])
@pytest.mark.parametrize(
    "operation",
    [
        "read_item",
        "create_item",
        "upsert_item",
        "replace_item",
        "patch_item",
        "delete_item",
    ],
)
def test_utf8_decoding_reaches_point_request_rust(asynchronous, operation):
    from common.test_connection_free_items_unit import AsyncFakeSender, FakeSender, invoke
    from azure.cosmos._helpers._item_operations import ItemHelper
    from azure.cosmos.aio._helpers._item_operations import AsyncItemHelper

    backend = AsyncFakeSender() if asynchronous else FakeSender()
    helper = (AsyncItemHelper if asynchronous else ItemHelper)(backend)
    invoke(helper, operation, utf8_decoding_mode="Lossy")
    assert backend.events[-1].settings.utf8_decoding_mode == "Lossy"


@pytest.mark.parametrize(
    "operation", ["query_items", "read_all_items", "query_items_change_feed"]
)
def test_utf8_decoding_reaches_retained_feed_request_rust(operation):
    from types import SimpleNamespace
    from common.test_connection_free_items_unit import FakeSender
    from azure.cosmos._helpers._feed_paging import FeedConfig
    from azure.cosmos._helpers._client_context import CosmosClientContext

    backend = FakeSender()
    proxy = SimpleNamespace(
        _client_context=CosmosClientContext(backend), container_link="dbs/db/colls/c"
    )
    config = FeedConfig(
        proxy, {"utf8_decoding_mode": "Lossy"}, operation=operation, backend=backend
    )
    prepared = config.prepared(None, object(), None)
    assert prepared.settings.utf8_decoding_mode == "Lossy"


@pytest.mark.parametrize("surface", ["sync", "async"])
def test_utf8_decoding_real_binding_rust(surface):
    # Isolate native connection-pool settings and cached client configurations.
    result = subprocess.run(
        sdk_python_command(
            "from common.test_utf8_decoding_unit import _run_binding_cases; _run_binding_cases(sys.argv[1])",
            surface,
        ),
        capture_output=True,
        text=True,
        timeout=90,
        check=False,
    )
    assert result.returncode == 0, result.stdout + result.stderr


def _run_binding_cases(surface):
    os.environ["AZURE_COSMOS_CONNECTION_POOL_IS_HTTP2_ALLOWED"] = "false"
    env_name = "AZURE_COSMOS_CHARSET_DECODER_ERROR_ACTION_ON_MALFORMED_INPUT"
    os.environ[env_name] = "REPLACE"

    from azure.cosmos import CosmosClient, exceptions
    from azure.cosmos.aio import CosmosClient as AsyncCosmosClient

    # Same malformed payload as tests/test_request_response_decoding.py.
    malformed = b'{"note":"hello \xc3\x28 world"}'
    replacement = "hello \ufffd( world"
    state = {"body": malformed, "status": 200}
    received = []

    class Handler(BaseHTTPRequestHandler):
        def do_GET(self):  # pylint: disable=invalid-name
            received.append(self.path)
            if self.path == "/":
                body = json.dumps(
                    {
                        "id": "utf8-test",
                        "_rid": "AQAAAA==",
                        "_self": "",
                        "writableLocations": [
                            {"name": "East US", "databaseAccountEndpoint": endpoint}
                        ],
                        "readableLocations": [
                            {"name": "East US", "databaseAccountEndpoint": endpoint}
                        ],
                        "enableMultipleWriteLocations": False,
                        "userConsistencyPolicy": {
                            "defaultConsistencyLevel": "Session",
                            "maxStalenessPrefix": 100,
                            "maxIntervalInSeconds": 5,
                        },
                    }
                ).encode()
                status = 200
            elif self.path.rstrip("/") in ("/dbs/db", "/dbs"):
                body, status = state["body"], state["status"]
                if self.path.rstrip("/") == "/dbs":
                    body = b'{"Databases":[' + body + b'],"_count":1}'
            else:
                body, status = (
                    b'{"code":"NotFound","message":"unexpected test route"}',
                    404,
                )
            self.send_response(status)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)

        def log_message(self, *_args):
            pass

    server = ThreadingHTTPServer(("127.0.0.1", 0), Handler)
    endpoint = f"http://127.0.0.1:{server.server_port}"
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()

    async def read(client, mode, *, feed=False):
        kwargs = {"timeout": 5}
        if mode is not None:
            kwargs["utf8_decoding_mode"] = mode
        if feed:
            pager = client.list_databases(**kwargs)
            rows = [row async for row in pager] if surface == "async" else list(pager)
            assert len(rows) == 1
            return rows[0]
        result = client.get_database_client("db").read(**kwargs)
        return await result if surface == "async" else result

    async def check(client, default):
        for mode in (None, "Lossy", "Strict", None):
            for feed in (False, True):
                if (mode or default) == "Lossy":
                    assert (await read(client, mode, feed=feed))["note"] == replacement
                else:
                    with pytest.raises(UnicodeDecodeError):
                        await read(client, mode, feed=feed)
        state["body"] = b'{"note":"healthy"}'
        assert (await read(client, None))["note"] == "healthy"
        # json.loads(bytes) accepts UTF-8-encoded surrogate code points;
        # Strict must reject them before JSON parsing.
        state["body"] = b'{"note":"\xed\xa0\x80"}'
        with pytest.raises(UnicodeDecodeError):
            await read(client, "Strict")
        assert (await read(client, "Lossy"))["note"] == "\ufffd\ufffd\ufffd"
        state["body"] = b"{\xff}"
        with pytest.raises(json.JSONDecodeError):
            await read(client, "Lossy")
        state.update(body=malformed, status=404)
        with pytest.raises(exceptions.CosmosResourceNotFoundError):
            await read(client, "Lossy")
        state["status"] = 200

    async def run():
        client_type = AsyncCosmosClient if surface == "async" else CosmosClient
        for mode in (None, "Lossy", "Strict"):
            kwargs = {"_backend": "rust", "timeout": 5}
            if mode is not None:
                kwargs["utf8_decoding_mode"] = mode
            if surface == "async":
                async with client_type(endpoint, "ZmFrZQ==", **kwargs) as client:
                    await check(client, mode)
            else:
                with client_type(endpoint, "ZmFrZQ==", **kwargs) as client:
                    await check(client, mode)
        # Compare actual legacy decoding with the new Rust Lossy behavior.
        if surface == "async":
            async with client_type(
                endpoint, "ZmFrZQ==", _backend="core-python", timeout=5
            ) as client:
                assert (await read(client, None))["note"] == replacement
        else:
            with client_type(
                endpoint, "ZmFrZQ==", _backend="core-python", timeout=5
            ) as client:
                assert (await read(client, None))["note"] == replacement
        assert any(path.rstrip("/") == "/dbs/db" for path in received)
        assert any(path.rstrip("/") == "/dbs" for path in received)

    try:
        asyncio.run(run())
    finally:
        server.shutdown()
        server.server_close()
        thread.join(5)
        assert not thread.is_alive()


if __name__ == "__main__":
    _run_binding_cases(sys.argv[1])
