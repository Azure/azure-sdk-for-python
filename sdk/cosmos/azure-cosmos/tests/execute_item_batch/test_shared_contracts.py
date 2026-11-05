# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.
"""Batch portions of original composite tests, with configured key/AAD clients."""

import uuid

import pytest

from azure.core import MatchConditions
from azure.cosmos import PartitionKey, partition_key
from config import resources
from execute_item_batch.test_service_failures import invoke

pytest_plugins = ["execute_item_batch.test_service_failures"]
pytestmark = [
    pytest.mark.cosmosEmulator,
    pytest.mark.cosmosAADLong,
    pytest.mark.asyncio,
]


async def test_batch_none_options_rust(fault_client):
    run = await fault_client()
    pk_value = "batch-pk"
    id1, id2 = str(uuid.uuid4()), str(uuid.uuid4())
    ops = [
        ("create", ({"id": id1, "pk": pk_value},)),
        ("create", ({"id": id2, "pk": pk_value},)),
    ]
    batch_result = await invoke(
        run.container.execute_item_batch,
        ops,
        partition_key=pk_value,
        session_token=None,
        priority=None,
        throughput_bucket=None,
    )
    run.native.assert_called_once()
    assert any(r.get("resourceBody").get("id") == id1 for r in batch_result) or any(
        r.get("resourceBody").get("id") == id2 for r in batch_result
    )
    assert {item["resourceBody"]["id"] for item in batch_result} == {id1, id2}


async def test_batch_headers_lsn_and_session_progression_rust(fault_client):
    run = await fault_client()
    container = run.container
    upsert_response = await invoke(container.upsert_item, {"id": "seed", "pk": "p"})
    lsn = upsert_response.get_response_headers()["lsn"]
    response_session_token = upsert_response.get_response_headers()[
        "x-ms-session-token"
    ]
    await invoke(
        container.replace_item, "seed", {"id": "seed", "pk": "p", "replace": True}
    )
    batch = [("create", ({"id": "item" + str(i), "pk": "p"},)) for i in range(50)]
    batch_response = await invoke(
        container.execute_item_batch, batch, partition_key="p"
    )
    run.native.assert_called_once()
    assert len(batch_response.get_response_headers()) > 0
    assert int(lsn) + 1 < int(batch_response.get_response_headers()["lsn"])
    batch_response_token = batch_response.get_response_headers()["x-ms-session-token"]
    assert response_session_token
    assert batch_response_token
    assert batch_response_token != response_session_token


async def test_batch_ignored_top_level_conditions_rust(fault_client):
    run = await fault_client()
    item = await invoke(run.container.create_item, {"id": "first", "pk": 0})
    item2 = await invoke(run.container.upsert_item, {"id": "second", "pk": 0})
    batch_operations = [
        ("create", ({"id": str(uuid.uuid4()), "pk": 0},)),
        ("replace", (item2["id"], {"id": str(uuid.uuid4()), "pk": 0})),
        ("read", (item["id"],)),
        ("upsert", ({"id": str(uuid.uuid4()), "pk": 0},)),
    ]
    batch_results = await invoke(
        run.container.execute_item_batch,
        batch_operations,
        partition_key=0,
        etag=str(uuid.uuid4()),
        match_condition=MatchConditions.IfModified,
    )
    run.native.assert_called_once()
    assert len(batch_results) == 4
    for result in batch_results:
        assert result["statusCode"] in (200, 201)


async def test_batch_request_throughput_bucket_rust(fault_client):
    run = await fault_client(throughput_bucket=2)
    result = await invoke(
        run.container.execute_item_batch,
        [("create", ({"id": "bucket", "pk": "p"},))],
        partition_key="p",
        throughput_bucket=3,
    )
    run.native.assert_called_once()
    prepared = run.native.call_args.args[1]
    assert prepared.settings.throughput_bucket == 3
    assert prepared.op == "execute_item_batch"
    assert result[0]["statusCode"] == 201


async def test_batch_same_name_container_recreation_rust(fault_client, batch_database):
    run = await fault_client()
    identifier = "batch_recreate_" + uuid.uuid4().hex
    container = run.client.get_database_client(batch_database.id).get_container_client(identifier)
    owned = False
    try:
        for field in ("PK", "partkey"):
            if owned:
                resources.retry_control_plane(batch_database.delete_container, identifier)
                owned = False
            resources.create_owned_container(
                batch_database, id=identifier, partition_key=PartitionKey(path="/" + field)
            )
            owned = True
            batch_operations = [
                ("create", ({"id": "item" + str(i), field: "Microsoft"},)) for i in range(100)
            ]
            batch_response = await invoke(
                container.execute_item_batch, batch_operations=batch_operations, partition_key="Microsoft"
            )
            assert len(batch_response) == 100
            assert all(item["statusCode"] == 201 for item in batch_response)
        assert run.native.call_count == 2
    finally:
        if owned:
            resources.retry_control_plane(batch_database.delete_container, identifier)


@pytest.mark.parametrize("version", [1, 2])
@pytest.mark.parametrize("variant", ["none", "null-sentinel", "undefined"])
async def test_batch_null_and_undefined_partition_keys_rust(
    fault_client, batch_database, version, variant
):
    run = await fault_client()
    identifier = "batch_keys_" + uuid.uuid4().hex
    resources.create_owned_container(
        batch_database,
        id=identifier,
        partition_key=PartitionKey(path="/pk", kind="Hash", version=version),
    )
    try:
        container = run.client.get_database_client(
            batch_database.id
        ).get_container_client(identifier)
        document = {"id": str(uuid.uuid4())}
        if variant == "undefined":
            key = partition_key.NonePartitionKeyValue
        else:
            document["pk"] = None
            key = None if variant == "none" else partition_key.NullPartitionKeyValue
        response = await invoke(
            container.execute_item_batch, [("upsert", (document,))], partition_key=key
        )
        run.native.assert_called_once()
        assert len(response) == 1
        item = response[0]["resourceBody"]
        if variant == "undefined":
            assert None not in item
            assert "pk" not in item
        else:
            assert item["pk"] is None
        stored = await invoke(container.read_item, document["id"], partition_key=key)
        assert stored["id"] == document["id"]
        assert ("pk" in stored, stored.get("pk")) == (
            "pk" in document,
            document.get("pk"),
        )
    finally:
        resources.retry_control_plane(batch_database.delete_container, identifier)
