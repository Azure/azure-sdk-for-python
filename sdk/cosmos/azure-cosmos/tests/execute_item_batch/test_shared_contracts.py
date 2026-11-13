# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.
"""Batch portions of original composite tests, with configured key/AAD clients."""

import uuid
from unittest.mock import Mock

import pytest

from config import clients, resources
from execute_item_batch.test_service_failures import invoke, rule
from fault_injection._query_resume import set_rule

from azure.core import MatchConditions
from azure.cosmos import PartitionKey, _rust, exceptions, partition_key

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


@pytest.mark.cosmosLong
async def test_batch_unicode_write_read_delete_rust(fault_client):
    run = await fault_client(enable_compact_utf8_item_writes=True)
    key = "\u65e5\u672c"
    content = "batch \u0e44\u0e17\u0e22 \u65e5\u672c \U0001f389"
    identifier = "utf8-batch-" + key + "-" + str(uuid.uuid4())
    batch_result = await invoke(
        run.container.execute_item_batch,
        [("create", ({"id": identifier, "pk": key, "content": content},))],
        partition_key=key,
    )
    assert batch_result[0]["statusCode"] == 201
    body = run.native.call_args.args[1].body_bytes
    assert isinstance(body, bytes)
    assert content in body.decode("utf-8")
    assert "\\u65e5" not in body.decode("utf-8")
    read_batch_result = await invoke(
        run.container.execute_item_batch, [("read", (identifier,))], partition_key=key
    )
    assert read_batch_result[0]["statusCode"] == 200
    assert read_batch_result[0]["resourceBody"]["content"] == content
    body = run.native.call_args.args[1].body_bytes
    assert key not in body.decode("utf-8")
    assert "\\u65e5" in body.decode("utf-8")
    delete_batch_result = await invoke(
        run.container.execute_item_batch, [("delete", (identifier,))], partition_key=key
    )
    assert delete_batch_result[0]["statusCode"] == 204
    body = run.native.call_args.args[1].body_bytes
    assert key not in body.decode("utf-8")
    assert "\\u65e5" in body.decode("utf-8")
    assert run.native.call_count == 3


@pytest.mark.cosmosLong
async def test_batch_same_name_container_recreation_rust(fault_client, batch_database):
    run = await fault_client()
    identifier = "batch_recreate_" + uuid.uuid4().hex
    container = run.client.get_database_client(batch_database.id).get_container_client(
        identifier
    )
    owned = False
    try:
        for field in ("PK", "partkey"):
            if owned:
                resources.retry_control_plane(
                    batch_database.delete_container, identifier
                )
                owned = False
            resources.create_owned_container(
                batch_database,
                id=identifier,
                partition_key=PartitionKey(path="/" + field),
            )
            owned = True
            batch_operations = [
                ("create", ({"id": "item" + str(i), field: "Microsoft"},))
                for i in range(100)
            ]
            batch_response = await invoke(
                container.execute_item_batch,
                batch_operations=batch_operations,
                partition_key="Microsoft",
            )
            assert len(batch_response) == 100
            assert all(item["statusCode"] == 201 for item in batch_response)
        assert run.native.call_count == 2
    finally:
        if owned:
            resources.retry_control_plane(batch_database.delete_container, identifier)


@pytest.mark.parametrize("version", [1, 2])
@pytest.mark.parametrize("variant", ["none", "null-sentinel", "undefined"])
@pytest.mark.unittest
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


@pytest.mark.parametrize("arity,supplied", [(2, 1), (2, 3), (3, 1), (3, 2)])
async def test_batch_hierarchical_key_arity_rejection_and_recovery_rust(
    fault_client, batch_database, arity, supplied
):
    identifier = "batch_hpk_" + uuid.uuid4().hex
    observer = resources.create_owned_container(
        batch_database,
        id=identifier,
        partition_key=PartitionKey(
            path=["/state", "/city", "/zipcode"][:arity], kind="MultiHash"
        ),
    )
    try:
        fault = rule(observer, error_type="ConnectionError")
        run = await fault_client([fault])
        container = run.client.get_database_client(
            batch_database.id
        ).get_container_client(identifier)
        body = {
            "id": str(uuid.uuid4()),
            "state": "WA",
            "city": "Redmond",
            "zipcode": "98052",
        }
        values = ["WA", "Redmond", "98052"]
        hook = Mock()
        with pytest.raises(exceptions.CosmosHttpResponseError) as caught:
            await invoke(
                container.execute_item_batch,
                [("create", (body,))],
                partition_key=values[:supplied],
                response_hook=hook,
            )
        assert (caught.value.status_code, caught.value.sub_status) == (400, 1001)
        assert (
            "Partition key provided either doesn't correspond to definition in the collection "
            "or doesn't match partition key field values specified in the document."
        ) in caught.value.message
        run.native.assert_called_once()
        hook.assert_not_called()
        assert _rust._debug_fault_injection_rule_hit_count(run.handle, fault["id"]) == 0
        with pytest.raises(exceptions.CosmosResourceNotFoundError) as missing:
            await invoke(observer.read_item, body["id"], partition_key=values[:arity])
        assert missing.value.status_code == 404

        set_rule(run.handle, fault["id"], False)
        run.native.reset_mock()
        response = await invoke(
            container.execute_item_batch,
            [("create", (body,))],
            partition_key=values[:arity],
        )
        run.native.assert_called_once()
        assert [result["statusCode"] for result in response] == [201]
        stored = await invoke(
            observer.read_item, body["id"], partition_key=values[:arity]
        )
        assert all(stored[field] == value for field, value in body.items())
    finally:
        resources.retry_control_plane(batch_database.delete_container, identifier)


@pytest.mark.parametrize("arities", [(2, 3), (3, 2)])
async def test_batch_recreated_hierarchical_key_definition_rust(
    fault_client, batch_database, arities
):
    run = await fault_client()
    identifier = "batch_hpk_recreate_" + uuid.uuid4().hex
    container = run.client.get_database_client(batch_database.id).get_container_client(
        identifier
    )
    owned = False
    try:
        for arity in arities:
            if owned:
                resources.retry_control_plane(
                    batch_database.delete_container, identifier
                )
                owned = False
            resources.create_owned_container(
                batch_database,
                id=identifier,
                partition_key=PartitionKey(
                    path=["/state", "/city", "/zipcode"][:arity], kind="MultiHash"
                ),
            )
            owned = True
            body = {
                "id": str(uuid.uuid4()),
                "state": "WA",
                "city": "Redmond",
                "zipcode": "98052",
            }
            key = ["WA", "Redmond", "98052"][:arity]
            response = await invoke(
                container.execute_item_batch, [("create", (body,))], partition_key=key
            )
            assert [result["statusCode"] for result in response] == [201]
            # Keep the storage observer independent of old-container sessions.
            with clients.create_setup_client(_backend="core-python") as observer_client:
                observer = observer_client.get_database_client(
                    batch_database.id
                ).get_container_client(identifier)
                stored = await invoke(observer.read_item, body["id"], partition_key=key)
            assert all(stored[field] == value for field, value in body.items())
        assert run.native.call_count == 2
    finally:
        if owned:
            resources.retry_control_plane(batch_database.delete_container, identifier)
