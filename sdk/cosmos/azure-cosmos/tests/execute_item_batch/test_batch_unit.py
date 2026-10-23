# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.
"""Check batch routing and public outcomes without a service."""

import asyncio
import ast
import json
import time
from copy import deepcopy
from pathlib import Path
from unittest.mock import MagicMock

import pytest

from azure.cosmos._backend.contracts import BackendResponse
from azure.cosmos._backend.cosmos_backend import CosmosBackend
from azure.cosmos._backend.errors import BindingProtocolError
from azure.cosmos._backend.operations import OP_TO_BINDING_FUNCTION_NAME
from azure.cosmos._cosmos_responses import CosmosList
from azure.cosmos._helpers._item_context import ItemClientContext, ItemClientDefaults
from azure.cosmos.aio._backend.cosmos_backend import AsyncCosmosBackend
from azure.cosmos.aio._container import ContainerProxy as AsyncContainerProxy
from azure.cosmos.container import ContainerProxy
from azure.cosmos.exceptions import CosmosBatchOperationError, CosmosHttpResponseError


class BatchBackend(CosmosBackend):
    name = "rust"

    def __init__(self):
        self.send = MagicMock(
            return_value=BackendResponse(
                200,
                headers={"x-ms-request-charge": "2.0", "x-ms-session-token": "0:1"},
                body=b'[{"statusCode":201,"resourceBody":{"id":"a","pk":"bank"}}]',
            )
        )

    def execute(self, prepared, *, deadline=None):
        return self.send(prepared, deadline=deadline)


class AsyncBatchBackend(AsyncCosmosBackend):
    name = "rust"

    def __init__(self):
        self.send = BatchBackend().send

    async def execute(self, prepared, *, deadline=None):
        return self.send(prepared, deadline=deadline)


@pytest.fixture(params=["sync", "async"])
def batch_client(request):
    asynchronous = request.param == "async"
    backend = AsyncBatchBackend() if asynchronous else BatchBackend()
    connection = MagicMock()
    connection.Batch.side_effect = AssertionError("Legacy batch must not run")
    context = ItemClientContext(
        backend,
        defaults=ItemClientDefaults(
            priority="High", throughput_bucket=7, operation_timeout_seconds=15
        ),
    )
    cls = AsyncContainerProxy if asynchronous else ContainerProxy
    container = cls(connection, "dbs/db", "orders", _item_context=context)
    container._get_properties_with_options = MagicMock(
        side_effect=AssertionError("Legacy metadata must not run")
    )

    def call(operations=None, partition_key="bank", **kwargs):
        operations = operations if operations is not None else [("create", ({"id": "a", "pk": "bank"},))]
        result = container.execute_item_batch(operations, partition_key, **kwargs)
        return asyncio.run(result) if asynchronous else result

    yield call, backend, context
    connection.Batch.assert_not_called()
    container._get_properties_with_options.assert_not_called()


def test_native_batch_request_and_result_rust(batch_client):
    call, backend, context = batch_client
    hook = MagicMock()
    before = time.monotonic()
    result = call(response_hook=hook, session_token="0:1")
    prepared = backend.send.call_args.args[0]
    assert OP_TO_BINDING_FUNCTION_NAME[prepared.op] == "execute_item_batch"
    assert prepared.container_link == "dbs/db/colls/orders"
    assert prepared.partition_key.values == ("bank",)
    assert json.loads(prepared.body_bytes) == [
        {"operationType": "Create", "resourceBody": {"id": "a", "pk": "bank"}}
    ]
    assert before < backend.send.call_args.kwargs["deadline"] <= time.monotonic() + 15
    assert isinstance(result, CosmosList)
    assert result[0]["resourceBody"]["id"] == "a"
    assert result.get_response_headers()["x-ms-request-charge"] == "2.0"
    assert context.response_state.last_response_headers["x-ms-session-token"] == "0:1"
    hook.assert_called_once()


def test_conditions_patch_and_caller_snapshot_rust(batch_client):
    call, backend, _ = batch_client
    operations = [
        ("replace", ("a", {"id": "a"}), {"if_match_etag": "etag"}),
        ("read", ("a",), {"if_none_match_etag": "other"}),
        ("patch", ("a", [{"op": "incr", "path": "/balance", "value": 1}]),
         {"filter_predicate": "from c where c.balance = 0"}),
    ]
    original = deepcopy(operations)
    call(operations, partition_key=["bank", "branch"])
    prepared = backend.send.call_args.args[0]
    body = json.loads(prepared.body_bytes)
    assert body[0]["ifMatch"] == "etag"
    assert body[1]["ifNoneMatch"] == "other"
    assert body[2]["resourceBody"]["condition"] == "from c where c.balance = 0"
    assert operations == original
    assert prepared.partition_key.values == ("bank", "branch")


@pytest.mark.parametrize("status", [400, 404, 409, 412])
def test_atomic_error_contract_rust(batch_client, status):
    call, backend, context = batch_client
    results = [{"statusCode": 424}, {"statusCode": status}, {"statusCode": 424}]
    backend.send.return_value = BackendResponse(
        207, body=json.dumps(results).encode(), headers={"x-ms-request-charge": "3.0"}
    )
    hook = MagicMock()
    with pytest.raises(CosmosBatchOperationError) as caught:
        call(response_hook=hook)
    assert caught.value.error_index == 1
    assert caught.value.status_code == status
    assert caught.value.operation_responses == results
    assert context.response_state.last_response_headers["x-ms-request-charge"] == "3.0"
    hook.assert_not_called()
    backend.send.assert_called_once()


@pytest.mark.parametrize("status", [400, 413, 429, 503])
def test_request_error_is_not_replayed_rust(batch_client, status):
    call, backend, _ = batch_client
    backend.send.return_value = BackendResponse(status, body=b'{"message":"rejected"}')
    with pytest.raises(CosmosHttpResponseError) as caught:
        call()
    assert caught.value.status_code == status
    backend.send.assert_called_once()


def test_hook_failure_is_not_replayed_rust(batch_client):
    call, backend, _ = batch_client
    with pytest.raises(RuntimeError, match="hook failed"):
        call(response_hook=MagicMock(side_effect=RuntimeError("hook failed")))
    backend.send.assert_called_once()


@pytest.mark.parametrize("options", [{"retry_write": 2}, {"connection_timeout": 2}, {"timeout": 0}])
def test_unsupported_options_fail_before_dispatch_rust(batch_client, options):
    call, backend, _ = batch_client
    with pytest.raises((NotImplementedError, ValueError)):
        call(**options)
    backend.send.assert_not_called()


@pytest.mark.parametrize("body", [b"{}", b'[{}]', b'[{"statusCode":424}]'])
def test_invalid_response_is_not_replayed_rust(batch_client, body):
    call, backend, _ = batch_client
    backend.send.return_value = BackendResponse(200, body=body)
    with pytest.raises(BindingProtocolError):
        call()
    backend.send.assert_called_once()


@pytest.mark.parametrize(
    "surface,filename", [
        ("sync", "test_transactional_batch.py"),
        ("aio", "test_transactional_batch_async.py"),
    ],
)
def test_copied_batch_assertions_match_originals_rust(surface, filename):
    root = Path(__file__).resolve().parents[1]
    original = ast.parse((root / filename).read_text(encoding="utf-8"))
    copied = ast.parse(
        (root / "execute_item_batch" / surface / "legacy" / filename).read_text(encoding="utf-8")
    )

    def methods(tree):
        return {
            node.name.removesuffix("_rust"): [ast.dump(statement) for statement in node.body]
            for node in ast.walk(tree)
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) and node.name.startswith("test_")
        }

    assert len(methods(original)) == 9
    assert methods(original) == methods(copied)
