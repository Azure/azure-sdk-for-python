# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.
"""Exercise real binding handles against the configured Windows Cosmos DB Emulator."""

import asyncio
from copy import deepcopy
from dataclasses import replace
import inspect
import json
import logging
import os
from types import SimpleNamespace
from urllib.parse import urlsplit
import uuid

import pytest

from azure.cosmos import CosmosClient, PartitionKey, _rust
from azure.cosmos._backend.binding_adapter import build_binding_request_from_page
from azure.cosmos._backend.contracts import PreparedPageRequest
from azure.cosmos._helpers._request_container import (
    build_create_container_prepared,
    build_read_container_prepared,
)
from azure.cosmos._helpers._request_database import (
    build_create_database_prepared,
    build_delete_database_prepared,
    build_read_database_prepared,
)
from azure.cosmos._helpers._request_item import build_read_item_request
from azure.cosmos._helpers._request_throughput import (
    build_get_throughput_request,
    build_replace_throughput_request,
)
from common._parity_helpers import skip_unless_emulator, skip_unless_rust_binding
from azure.cosmos.exceptions import CosmosHttpResponseError, CosmosResourceNotFoundError

pytestmark = [pytest.mark.cosmosEmulator, skip_unless_emulator(), skip_unless_rust_binding()]

PAGE_OPERATIONS = (
    "query_items",
    "read_all_items",
    "list_databases",
    "query_databases",
    "list_containers",
    "query_containers",
)
POINT_OPERATIONS = (
    "create_database",
    "read_database",
    "delete_database",
    "create_container",
    "read_container",
    "get_throughput",
    "replace_throughput",
)


@pytest.fixture(scope="module")
def account():
    """Own one database; never reuse or remove another test's resources."""
    endpoint, key = os.environ["ACCOUNT_HOST"], os.environ["ACCOUNT_KEY"]
    assert urlsplit(endpoint).hostname in (
        "localhost",
        "127.0.0.1",
        "::1",
    ), "These binding tests require the local Windows Cosmos DB Emulator, not a cloud account."
    with CosmosClient(endpoint, key, _backend="core-python") as legacy:
        database = legacy.create_database("binding_contract_" + uuid.uuid4().hex)
        try:
            container = database.create_container(
                "orders", partition_key=PartitionKey(path="/pk"), offer_throughput=400
            )
            item = container.create_item({"id": "order-42", "pk": "Contoso", "amount": 25})
            properties = container.read()
            offer_query = {
                "query": "SELECT * FROM root r WHERE r.resource=@link",
                "parameters": [{"name": "@link", "value": properties["_self"]}],
            }
            offers = list(legacy.client_connection.QueryOffers(offer_query))
            assert len(offers) == 1
            with CosmosClient(endpoint, key, _backend="rust") as rust:
                yield SimpleNamespace(
                    legacy=legacy,
                    rust=rust,
                    database=database,
                    container=container,
                    item=dict(item),
                    offer=offers[0],
                    offer_query=offer_query,
                    handle=rust._adapter._ensure_driver_handle(),
                )
        finally:
            legacy.delete_database(database.id)


def prepared_request(account, operation, resource_id=None):
    """Use the same request builders as the SDK, not synthetic service responses."""
    database_link = "dbs/" + account.database.id
    container_link = database_link + "/colls/orders"
    resource_id = resource_id or account.database.id
    if operation == "create_database":
        return build_create_database_prepared({"id": resource_id}, {})
    if operation == "read_database":
        return build_read_database_prepared(resource_id, {})
    if operation == "delete_database":
        return build_delete_database_prepared("dbs/" + resource_id, {})
    if operation == "create_container":
        return build_create_container_prepared(
            database_link,
            {
                "id": resource_id,
                "partitionKey": {"paths": ["/pk"], "kind": "Hash"},
            },
            {"offerThroughput": 400},
        )
    if operation == "read_container":
        return build_read_container_prepared(container_link, {})
    if operation in ("get_throughput", "replace_throughput"):
        common = {"resource_link": container_link, "request_options": {}, "default_headers": {}}
        if operation == "get_throughput":
            return build_get_throughput_request(offer_query=account.offer_query, **common)
        offer = deepcopy(account.offer)
        offer["content"]["offerThroughput"] = 500
        return build_replace_throughput_request(offer_body=offer, **common)
    link = (
        "" if operation.endswith("databases") else database_link if operation.endswith("containers") else container_link
    )
    return build_binding_request_from_page(
        PreparedPageRequest(
            op=operation,
            container_link=link,
            query="SELECT * FROM c",
        )
    )


def invoke(account, operation, prepared, asynchronous, timeout=None, attempts=False):
    """Call sync/async binding exports with an acquired handle."""
    function = getattr(_rust, operation + ("_async" if asynchronous else ""))
    kwargs = {"timeout_seconds": timeout}
    if "include_attempts" in inspect.signature(function).parameters:
        kwargs["include_attempts"] = attempts

    async def run():
        return await function(account.handle, prepared, **kwargs)

    return asyncio.run(run()) if asynchronous else function(account.handle, prepared, **kwargs)


@pytest.mark.parametrize("asynchronous", [False, True], ids=["sync", "async"])
@pytest.mark.parametrize("operation", POINT_OPERATIONS + PAGE_OPERATIONS + ("get_container_metadata",))
@pytest.mark.parametrize("seconds", [0, -1, float("inf"), float("nan"), 2**64])
def test_binding_rejects_invalid_timeout_with_real_handle(account, asynchronous, operation, seconds):
    """Invalid durations must be rejected, not mistaken for invalid handles."""
    resource_id = (
        "must_not_delete_" + uuid.uuid4().hex
        if operation == "delete_database"
        else "orders" if operation == "create_container" else account.database.id
    )
    prepared = (
        account.container.container_link
        if operation == "get_container_metadata"
        else prepared_request(account, operation, resource_id)
    )
    with pytest.raises(ValueError, match="timeout_seconds"):
        invoke(account, operation, prepared, asynchronous, timeout=seconds)


@pytest.mark.parametrize("asynchronous", [False, True], ids=["sync", "async"])
@pytest.mark.parametrize("attempts", [False, True])
@pytest.mark.parametrize("timeout", [None, 30])
@pytest.mark.parametrize("operation", POINT_OPERATIONS)
def test_binding_point_operations_return_service_results(account, asynchronous, attempts, timeout, operation):
    """Compare created/read resources with legacy reads from the same emulator."""
    resource_id = "contract_" + uuid.uuid4().hex
    cleanup = None
    if operation == "delete_database":
        database = account.legacy.create_database(resource_id)
        cleanup = lambda: account.legacy.delete_database(database.id)
    elif operation == "create_database":
        cleanup = lambda: account.legacy.delete_database(resource_id)
    elif operation == "create_container":
        cleanup = lambda: account.database.delete_container(resource_id)
    else:
        resource_id = account.database.id
    try:
        response = invoke(
            account,
            operation,
            prepared_request(account, operation, resource_id),
            asynchronous,
            timeout=timeout,
            attempts=attempts,
        )
        if attempts:
            response, diagnostics = response
            assert diagnostics is not None
        status, _, _, body, _ = response
        expected_status = 201 if operation.startswith("create_") else 204 if operation == "delete_database" else 200
        assert status == expected_status
        if operation == "delete_database":
            cleanup = None
            assert not body
            with pytest.raises(CosmosResourceNotFoundError):
                account.legacy.get_database_client(resource_id).read()
        elif operation == "create_database":
            assert json.loads(body) == dict(account.legacy.get_database_client(resource_id).read())
        elif operation == "read_database":
            assert json.loads(body) == dict(account.database.read())
        elif operation == "create_container":
            assert json.loads(body) == dict(account.database.get_container_client(resource_id).read())
        elif operation == "read_container":
            assert json.loads(body) == dict(account.container.read())
        elif operation == "get_throughput":
            assert json.loads(body)["Offers"] == list(account.legacy.client_connection.QueryOffers(account.offer_query))
        else:
            assert json.loads(body)["content"]["offerThroughput"] == 500
            assert account.container.get_throughput().offer_throughput == 500
    finally:
        if cleanup is not None:
            try:
                cleanup()
            except CosmosResourceNotFoundError:
                # A failed create or a completed delete can leave nothing to remove.
                logging.getLogger(__name__).info("Owned resource %s is already absent during cleanup", resource_id)


@pytest.mark.parametrize("asynchronous", [False, True], ids=["sync", "async"])
@pytest.mark.parametrize("operation", PAGE_OPERATIONS)
def test_binding_pages_return_service_results(account, asynchronous, operation):
    field = (
        "Databases"
        if operation.endswith("databases")
        else "DocumentCollections" if operation.endswith("containers") else "Documents"
    )
    expected = (
        dict(account.database.read())
        if field == "Databases"
        else dict(account.container.read()) if field == "DocumentCollections" else account.item
    )
    prepared = prepared_request(account, operation)
    seen_tokens = set()
    while True:
        status, _, headers, body, _ = invoke(account, operation, prepared, asynchronous, timeout=30)
        assert status == 200
        values = json.loads(body)[field]
        matches = [value for value in values if value["id"] == expected["id"]]
        if matches:
            assert matches == [expected]
            break
        token = headers.get("x-ms-continuation")
        assert token, "Owned resource was missing from the service feed"
        assert token not in seen_tokens, "Service feed repeated a continuation token"
        seen_tokens.add(token)
        prepared = replace(
            prepared, settings=replace(prepared.settings, query=replace(prepared.settings.query, continuation=token))
        )


@pytest.mark.parametrize("asynchronous", [False, True], ids=["sync", "async"])
def test_binding_metadata_matches_legacy_container(account, asynchronous):
    properties = account.container.read()
    result = invoke(account, "get_container_metadata", account.container.container_link, asynchronous, timeout=30)
    assert result == (
        properties["_rid"],
        tuple(properties["partitionKey"]["paths"]),
        properties["partitionKey"]["kind"],
        None,
    )


@pytest.mark.parametrize("asynchronous", [False, True], ids=["sync", "async"])
@pytest.mark.parametrize("level", [None, "Eventual", "ConsistentPrefix", "Session", "BoundedStaleness", "Strong"])
@pytest.mark.parametrize("raw_header", [False, True])
@pytest.mark.parametrize("saved_address", [False, True])
def test_binding_read_address_and_consistency_match_legacy(account, asynchronous, level, raw_header, saved_address):
    """Compare the same stored document; account restrictions are not successful reads."""
    options = {} if level is None else {"consistencyLevel": level}
    headers = {"x-ms-consistency-level": level} if raw_header and level is not None else {}
    target = {"_self": account.item["_self"]} if saved_address else account.item["id"]
    expected_status = 200
    expected = None
    try:
        expected = account.container.read_item(
            target,
            partition_key="Contoso",
            **({"initial_headers": headers} if raw_header else {"request_options": options}),
        )
    except CosmosHttpResponseError as error:
        # A request cannot strengthen the configured account consistency.
        assert level in ("Strong", "BoundedStaleness")
        assert error.status_code == 400
        expected_status = 400
    prepared = build_read_item_request(
        container_link=account.container.container_link,
        item_id=None if saved_address else account.item["id"],
        item_self_link=account.item["_self"] if saved_address else None,
        partition_key_value="Contoso",
        container_rid=None,
        request_options={} if raw_header else options,
    )
    if raw_header:
        prepared = replace(prepared, headers=headers)
    status, _, _, body, _ = invoke(account, "read_item", prepared, asynchronous, timeout=30)
    assert status == expected_status
    if expected_status == 200:
        assert dict(expected) == account.item
        assert json.loads(body) == account.item
