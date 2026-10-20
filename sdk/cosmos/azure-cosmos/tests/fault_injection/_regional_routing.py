# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.
"""F02 controls: simulated regions, real installed-emulator storage."""
import copy
import asyncio
import json
import os
from pathlib import Path
import subprocess
import sys
import time
from urllib.parse import urlsplit

import pytest

from azure.cosmos import CosmosClient, exceptions
from _fault_injection_transport import FaultInjectionTransport

from fault_injection._delayed_create import emit
from _client_transport import create_client_with_transport

WRITE_REGION = "East US"
READ_REGION = "West US"
READ_SECONDS = 2
TIMEOUT = 30

REGIONAL_ROUTING_CASES = [
    pytest.param("routing", id="routing-rust"),
    pytest.param("guard", id="guard-rust"),
    pytest.param("guard-disabled", id="guard-disabled-rust"),
]


def emulator_endpoints(endpoint):
    parsed = urlsplit(endpoint)
    if (parsed.scheme != "https" or parsed.hostname not in ("localhost", "127.0.0.1")
            or parsed.username or parsed.password or parsed.path not in ("", "/")
            or parsed.query or parsed.fragment):
        raise ValueError("F02 requires an HTTPS localhost/127.0.0.1 emulator endpoint, not a cloud account")
    port = parsed.port or 443
    return f"https://127.0.0.1:{port}/", f"https://localhost:{port}/"


def topology(account, write_endpoint, read_endpoint, target_guard):
    result = copy.deepcopy(account)
    east = {"name": WRITE_REGION, "databaseAccountEndpoint": write_endpoint}
    west = {"name": READ_REGION, "databaseAccountEndpoint": read_endpoint}
    result["readableLocations"] = [east, west]
    # The guard control deliberately directs the write to the forbidden alias.
    result["writableLocations"] = [west if target_guard else east]
    result["enableMultipleWriteLocations"] = False
    result["enablePerPartitionFailoverBehavior"] = False
    # This copied legacy scenario exercises Gateway V1, not a thin-client proxy.
    result.pop("thinClientReadableLocations", None)
    result.pop("thinClientWritableLocations", None)
    return result


def load_account(endpoint, key):
    accounts = []
    transport = FaultInjectionTransport()

    def capture(request, inner):
        response = inner()
        assert response.status_code == 200, "Account discovery failed"
        accounts.append(json.loads(response.body()))
        return response

    transport.add_response_transformation(
        FaultInjectionTransport.predicate_is_database_account_call, capture)
    with create_client_with_transport(CosmosClient, endpoint, key, _backend="core-python", transport=transport, timeout=TIMEOUT):
        pass
    assert accounts, "No account discovery response was observed"
    return accounts[-1]


def rules(rule_id, container_id, account, inject=True):
    return [
        {
            "id": rule_id + "-topology",
            "operation_type": "MetadataReadDatabaseAccount",  # Only post-bootstrap account refreshes.
            "status_code": 200,  # Supply the simulated account document, not an error.
            "response_body": json.dumps(account).encode("utf-8"),  # Preserve unrelated account fields.
            "probability": 1.0,  # Keep later refreshes consistent with the test topology.
        },
        {
            "id": rule_id,
            "operation_type": "CreateItem",  # Leave setup, metadata and reads alone.
            "container_id": container_id,  # Unique test-owned container only.
            "region": READ_REGION,  # Reject creates routed to West US.
            "status_code": 403,
            "sub_status": 3,  # WriteForbidden, as in the legacy test.
            "probability": 1.0 if inject else 0.0,  # Disabled control must reach storage.
            "hit_limit": None,  # Retries must not escape by exhausting the rule.
        },
    ]


def assert_fields(actual, expected):
    assert isinstance(actual, dict), "Expected an item dictionary"
    for field, value in expected.items():
        assert field in actual and actual[field] == value, f"Customer field mismatch: {field}"


def assert_destination(records, endpoint, status):
    assert records, "No item-attempt destination evidence"
    for record in records:
        actual = urlsplit(record["endpoint"])
        expected = urlsplit(endpoint)
        assert (actual.scheme, actual.hostname, actual.port) == (
            expected.scheme, expected.hostname, expected.port), "Wrong item-attempt destination"
        assert record["status"] == status, "Unexpected item-attempt status"


def native_records(payload):
    assert isinstance(payload, dict), "Missing Rust operation diagnostics"
    assert payload.get("activity_id"), "Missing Rust operation association"
    assert payload["request_count"] == payload["retained_request_count"] == len(payload["requests"]), (
        "Incomplete Rust attempt history")
    records = [record for record in payload["requests"] if record["pipeline"] == "data_plane"]
    assert records, "No Rust data-plane attempt evidence"
    return records


def assert_guard(error, records, read_endpoint, hits, rule_id):
    assert isinstance(error, exceptions.CosmosHttpResponseError), "Guard did not reject the create"
    assert error.status_code == 403 and error.sub_status == 3, "Expected WriteForbidden 403/3"
    assert hits > 0, "Forbidden-write rule was not applied"
    assert_destination(records, read_endpoint, 403)
    applied = sum(
        entry["rule_id"] == rule_id and entry["applied"]
        for record in records for entry in record["evaluations"]
    )
    assert applied == hits, "Named guard hits do not match the operation's attempts"
    assert all(record["sub_status"] == 3 for record in records)


def capture_native(monkeypatch, records, asynchronous=False):
    if asynchronous:
        from azure.cosmos.aio._backend import binding_adapter as module
    else:
        from azure.cosmos._backend import binding_adapter as module
    original = module._binding_function_for_op

    def record(payload, operation):
        records.extend(native_records(payload))
        emit("regional_diagnostics", operation=operation, **payload)

    def select(operation):
        function = original(operation)
        if operation not in ("create_item", "read_item"):
            return function

        def capture(*args, **kwargs):
            try:
                response, payload = function(*args, **kwargs, include_fault_diagnostics=True)
            except module._DRIVER_TRANSPORT_ERROR as error:
                payload = getattr(error, "_cosmos_fault_diagnostics", None)
                if payload is not None:
                    record(payload, operation)
                raise
            record(payload, operation)
            return response

        async def capture_async(*args, **kwargs):
            try:
                response, payload = await function(*args, **kwargs, include_fault_diagnostics=True)
            except module._DRIVER_TRANSPORT_ERROR as error:
                payload = getattr(error, "_cosmos_fault_diagnostics", None)
                if payload is not None:
                    record(payload, operation)
                raise
            record(payload, operation)
            return response

        return capture_async if asynchronous else capture

    monkeypatch.setattr(module, "_binding_function_for_op", select)


def expected_regions(target_guard):
    return (["westus" if target_guard else "eastus"], ["eastus", "westus"])


def wait_topology(client, rule_id, target_guard):
    from azure.cosmos import _rust

    handle = client._adapter._ensure_driver_handle()
    deadline = time.monotonic() + TIMEOUT
    while True:
        cached = _rust._debug_cached_account_regions(handle)
        hits = _rust._debug_fault_injection_rule_hit_count(handle, rule_id + "-topology")
        if cached == expected_regions(target_guard) and hits > 0:
            emit("regional_topology", writable=cached[0], readable=cached[1], hits=hits)
            return
        assert time.monotonic() < deadline, f"Rust did not observe simulated topology: {cached!r}; hits={hits}"
        time.sleep(0.05)


async def wait_topology_async(client, rule_id, target_guard):
    from azure.cosmos import _rust

    handle = await client._adapter._ensure_driver_handle()
    deadline = time.monotonic() + TIMEOUT
    while True:
        cached = await asyncio.to_thread(_rust._debug_cached_account_regions, handle)
        hits = await client._adapter._debug_fault_injection_rule_hit_count(rule_id + "-topology")
        if cached == expected_regions(target_guard) and hits > 0:
            emit("regional_topology", writable=cached[0], readable=cached[1], hits=hits)
            return
        assert time.monotonic() < deadline, f"Rust did not observe simulated topology: {cached!r}; hits={hits}"
        await asyncio.sleep(0.05)


def isolate(request, target):
    """Parent owns resources even when a child times out or fails."""
    if request.config.getoption("--f02-worker"):
        return False
    database_id, container = target
    root = Path(__file__).resolve().parents[2]
    node = str(request.node.path.relative_to(root)) + "::" + request.node.name
    environment = dict(os.environ)
    environment["F02_DATABASE_ID"] = database_id
    environment["F02_CONTAINER_ID"] = container.id
    # Existing driver E2E control: wait for observed topology, never a fixed sleep.
    environment["AZURE_COSMOS_E2E_BACKGROUND_ACCOUNT_REFRESH_INTERVAL_MS"] = "100"
    command = [
        sys.executable, "-m", "pytest", "-q", "-s", "-o", "pythonpath=tests",
        "--confcutdir=tests\\fault_injection", "--f02-worker", node,
    ]
    result = subprocess.run(command, cwd=root, env=environment, capture_output=True, text=True, timeout=150)
    print(result.stdout, end="")
    if result.stderr:
        print(result.stderr, end="", file=sys.stderr)
    assert result.returncode == 0, f"Isolated F02 worker failed with exit {result.returncode}"
    emit("regional_worker", nodeid=node, exit_code=result.returncode)
    return True
