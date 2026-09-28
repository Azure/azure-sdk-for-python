# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.
"""Compare explicit write tokens on the single-write-region localhost emulator.

Set COSMOS_WRITE_TOKEN_EMULATOR=1 and COSMOS_EMULATOR_KEY, then run:
python -m pytest --confcutdir=tests/common tests/common/test_write_session_token_emulator.py -q -s

Only uniquely named test resources are created and deleted. This does not test
multi-region replication, failover, or tokens from a recreated container.
"""

import asyncio
import os
import uuid

import pytest

from azure.cosmos import ConsistencyLevel, CosmosClient, PartitionKey, exceptions
from azure.cosmos.aio import CosmosClient as AsyncCosmosClient


pytestmark = pytest.mark.skipif(
    os.getenv("COSMOS_WRITE_TOKEN_EMULATOR") != "1",
    reason="Set COSMOS_WRITE_TOKEN_EMULATOR=1 and COSMOS_EMULATOR_KEY for localhost tests.",
)
HOST = "https://localhost:8081"
CUSTOMER = "customer-17"
SESSION_HEADER = "x-ms-session-token"


def _client_options(backend):
    options = {"_backend": backend, "consistency_level": ConsistencyLevel.Session}
    if backend == "core-python":
        options["connection_verify"] = False
    return options


@pytest.fixture(scope="module")
def orders():
    key = os.environ["COSMOS_EMULATOR_KEY"]
    with CosmosClient(HOST, key, **_client_options("core-python")) as setup:
        account = setup.get_database_account()
        assert not account._EnableMultipleWritableLocations
        assert len(account.WritableLocations) <= 1
        database_id = "write-token-review-" + uuid.uuid4().hex
        database = setup.create_database(database_id)
        try:
            container = database.create_container(
                id="orders", partition_key=PartitionKey(path="/customerId"),
            )
            first = container.create_item(
                {"id": "first-order", "customerId": CUSTOMER, "status": "approved"},
            )
            older_token = first.get_response_headers()[SESSION_HEADER]
            assert older_token
            yield key, database_id, container, older_token
        finally:
            setup.delete_database(database_id)
            with pytest.raises(exceptions.CosmosResourceNotFoundError):
                setup.get_database_client(database_id).read()


def _future_token(token):
    partition, vector = token.split(":", 1)
    parts = vector.split("#")
    assert len(parts) >= 2, f"Unexpected emulator session-token format: {token!r}"
    parts[1] = str(int(parts[1]) + 1_000_000)
    return partition + ":" + "#".join(parts)


def _deny_legacy_item_requests(connection):
    def deny(*args, **kwargs):
        raise AssertionError("Rust operation attempted a legacy item request")

    for name in ("CreateItem", "ReplaceItem", "UpsertItem", "DeleteItem", "ReadItem"):
        setattr(connection, name, deny)


def _invoke(container, operation, item_id, options):
    body = {"id": item_id, "customerId": CUSTOMER, "status": "dispatched"}
    if operation == "create":
        return container.create_item(body, **options)
    if operation in ("upsert-create", "upsert-replace"):
        return container.upsert_item(body, **options)
    if operation == "replace":
        return container.replace_item(item_id, body, **options)
    if operation == "delete":
        return container.delete_item(item_id, partition_key=CUSTOMER, **options)
    raise AssertionError(f"Unexpected operation: {operation}")


def _write(key, database_id, backend, asynchronous, operation, item_id, token):
    options = {} if token is None else {"session_token": token}
    try:
        if asynchronous:
            async def run():
                async with AsyncCosmosClient(HOST, key, **_client_options(backend)) as client:
                    if backend == "rust":
                        _deny_legacy_item_requests(client.client_connection)
                    container = client.get_database_client(database_id).get_container_client("orders")
                    return await _invoke(container, operation, item_id, options)

            result = asyncio.run(run())
        else:
            with CosmosClient(HOST, key, **_client_options(backend)) as client:
                if backend == "rust":
                    _deny_legacy_item_requests(client.client_connection)
                container = client.get_database_client(database_id).get_container_client("orders")
                result = _invoke(container, operation, item_id, options)
    except exceptions.CosmosHttpResponseError as error:
        assert error.status_code >= 400
        assert error.headers.get("x-ms-activity-id")
        if error.status_code == 400:
            assert "session" in error.message.lower()
        return error.status_code, error.sub_status

    if operation != "delete":
        assert result["id"] == item_id
        assert result["status"] == "dispatched"
        assert float(result.get_response_headers()["x-ms-request-charge"]) > 0
    return "success", None


def _assert_persisted_effect(container, item_id, operation, outcome):
    succeeded = outcome[0] == "success"
    absent = (operation == "delete" and succeeded) or (
        operation in ("create", "upsert-create") and not succeeded
    )
    if absent:
        with pytest.raises(exceptions.CosmosResourceNotFoundError):
            container.read_item(item_id, partition_key=CUSTOMER)
    else:
        stored = container.read_item(item_id, partition_key=CUSTOMER)
        assert stored["status"] == ("dispatched" if succeeded else "approved")


@pytest.mark.parametrize("asynchronous", [False, True], ids=["sync", "async"])
@pytest.mark.parametrize("operation", ["create", "replace", "upsert-create", "upsert-replace", "delete"])
@pytest.mark.parametrize("token_kind", ["omitted", "from-write", "from-read", "older", "future", "malformed"])
def test_explicit_write_session_token(orders, asynchronous, operation, token_kind):
    key, database_id, setup, older_token = orders
    outcomes = {}
    for backend in ("core-python", "rust"):
        item_id = "order-" + uuid.uuid4().hex
        if operation not in ("create", "upsert-create"):
            setup.create_item({"id": item_id, "customerId": CUSTOMER, "status": "approved"})
        observed_id = "observed-" + uuid.uuid4().hex
        written = setup.create_item({"id": observed_id, "customerId": CUSTOMER, "status": "approved"})
        read = setup.read_item(observed_id, partition_key=CUSTOMER)
        read_token = read.get_response_headers()[SESSION_HEADER]
        tokens = {
            "omitted": None,
            "from-write": written.get_response_headers()[SESSION_HEADER],
            "from-read": read_token,
            "older": older_token,
            "future": _future_token(read_token),
            "malformed": "not-a-session-token",
        }
        assert older_token != read_token
        outcome = _write(
            key, database_id, backend, asynchronous, operation, item_id, tokens[token_kind],
        )
        outcomes[backend] = outcome
        _assert_persisted_effect(setup, item_id, operation, outcome)
        expected = (400, None) if backend == "rust" and token_kind == "malformed" else ("success", None)
        assert outcome == expected

    print(f"{'async' if asynchronous else 'sync'} {operation} {token_kind}: {outcomes}")


@pytest.mark.parametrize("backend", ["core-python", "rust"])
@pytest.mark.parametrize("asynchronous", [False, True], ids=["sync", "async"])
def test_future_token_is_enforced_on_a_read(orders, backend, asynchronous):
    key, database_id, setup, _ = orders
    read = setup.read_item("first-order", partition_key=CUSTOMER)
    token = _future_token(read.get_response_headers()[SESSION_HEADER])
    with pytest.raises(exceptions.CosmosResourceNotFoundError) as failure:
        if asynchronous:
            async def run():
                async with AsyncCosmosClient(HOST, key, **_client_options(backend)) as client:
                    if backend == "rust":
                        _deny_legacy_item_requests(client.client_connection)
                    container = client.get_database_client(database_id).get_container_client("orders")
                    await container.read_item("first-order", partition_key=CUSTOMER, session_token=token)

            asyncio.run(run())
        else:
            with CosmosClient(HOST, key, **_client_options(backend)) as client:
                if backend == "rust":
                    _deny_legacy_item_requests(client.client_connection)
                container = client.get_database_client(database_id).get_container_client("orders")
                container.read_item("first-order", partition_key=CUSTOMER, session_token=token)
    assert failure.value.status_code == 404
    assert failure.value.sub_status == 1002
