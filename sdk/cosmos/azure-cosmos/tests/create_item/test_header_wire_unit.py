# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.
"""Public create calls reach a local HTTP server through the real Rust transport."""

import asyncio
import json
import os
import subprocess
from unittest.mock import patch

import pytest

from common.local_cosmos_server import local_cosmos_server
from common.sdk_subprocess import sdk_python_command


@pytest.mark.parametrize("surface", ["sync", "async"])
@pytest.mark.parametrize(
    "client_options,request_options,expected",
    [
        pytest.param({"throughput_bucket": 2}, {}, {"x-ms-cosmos-throughput-bucket": "2"},
                     id="client-bucket"),
        pytest.param({"throughput_bucket": 2}, {"throughput_bucket": 3},
                     {"x-ms-cosmos-throughput-bucket": "3"}, id="request-bucket"),
        pytest.param({"priority": "Low"}, {}, {"x-ms-cosmos-priority-level": "Low"},
                     id="client-priority"),
        pytest.param({"priority": "Low"}, {"priority": "High"},
                     {"x-ms-cosmos-priority-level": "High"}, id="request-priority"),
        pytest.param({}, {}, {}, id="unset"),
    ],
)
def test_create_headers_reach_wire_rust(surface, client_options, request_options, expected):
    # Native runtime configuration must not inherit another test's caches or mocks.
    result = subprocess.run(
        sdk_python_command(
            "import json\n"
            "from create_item.test_header_wire_unit import _check_create_headers\n"
            "_check_create_headers(sys.argv[1], *json.loads(sys.argv[2]))",
            surface, json.dumps([client_options, request_options, expected]),
        ),
        capture_output=True, text=True, timeout=30, check=False,
    )
    assert result.returncode == 0, result.stdout + result.stderr


def _create_response(request):
    # cspell:ignore AQAAAAEAAAA
    path = request.path.rstrip("/")
    if request.method == "GET" and path == "/dbs/db/colls/coll":
        return 200, {
            "id": "coll", "_rid": "AQAAAAEAAAA=", "_self": "dbs/AQAAAA==/colls/AQAAAAEAAAA=/",
            "_etag": '"container"', "_ts": 1,
            "partitionKey": {"paths": ["/pk"], "kind": "Hash", "version": 2},
        }
    if request.method == "GET" and path.endswith("/pkranges"):
        return 200, {
            "_rid": "AQAAAAEAAAA=", "_count": 1,
            "PartitionKeyRanges": [{"id": "0", "minInclusive": "", "maxExclusive": "FF"}],
        }
    if request.method == "POST" and path == "/dbs/db/colls/coll/docs":
        return 201, dict(json.loads(request.body), _etag='"item"', _ts=1)
    return 500, {"code": "UnexpectedRequest", "message": f"Unexpected {request.method} {request.path}"}


def _check_create_headers(surface, client_options, request_options, expected):
    os.environ["AZURE_COSMOS_CONNECTION_POOL_IS_HTTP2_ALLOWED"] = "false"
    from azure.cosmos import ConnectionPoolOptions, CosmosClient, CosmosRuntime
    from azure.cosmos.aio import CosmosClient as AsyncCosmosClient

    runtime = CosmosRuntime.create(connection_pool=ConnectionPoolOptions(proxy_allowed=False))
    body = {"id": "header-check", "pk": "mypk"}
    with local_cosmos_server(_create_response) as server:
        options = {"_backend": "rust", "runtime": runtime, "timeout": 5, **client_options}
        if surface == "async":
            async def create():
                async with AsyncCosmosClient(server.endpoint, "ZmFrZQ==", **options) as client:
                    with patch.object(client.client_connection, "CreateItem",
                                      side_effect=AssertionError("Legacy create must not run")):
                        container = client.get_database_client("db").get_container_client("coll")
                        return await container.create_item(body, **request_options)

            created = asyncio.run(create())
        else:
            with CosmosClient(server.endpoint, "ZmFrZQ==", **options) as client:
                with patch.object(client.client_connection, "CreateItem",
                                  side_effect=AssertionError("Legacy create must not run")):
                    container = client.get_database_client("db").get_container_client("coll")
                    created = container.create_item(body, **request_options)
        assert created["id"] == body["id"]
        writes = [request for request in server.requests if request.method == "POST"]
        assert len(writes) == 1
        request = writes[0]
        assert request.path.rstrip("/") == "/dbs/db/colls/coll/docs"
        assert json.loads(request.body) == body
        headers = {
            name: request.headers[name]
            for name in ("x-ms-cosmos-priority-level", "x-ms-cosmos-throughput-bucket")
            if name in request.headers
        }
        assert headers == expected
