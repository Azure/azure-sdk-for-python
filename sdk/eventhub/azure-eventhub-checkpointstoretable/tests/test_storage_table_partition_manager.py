# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

import pytest
import uuid
import warnings
import os

from azure.eventhub.extensions.checkpointstoretable._vendor.data.tables import TableServiceClient
from azure.eventhub.extensions.checkpointstoretable import TableCheckpointStore
from azure.eventhub.exceptions import OwnershipLostError

STORAGE_ENV_KEYS = [
    "AZURE_TABLES_CONN_STR",
    "AZURE_COSMOS_CONN_STR"
]


def get_live_storage_table_client(conn_str_env_key):
    try:
        storage_connection_str = os.environ[conn_str_env_key]
        table_name = "table{}".format(uuid.uuid4().hex)
        table_service_client = TableServiceClient.from_connection_string(
            storage_connection_str
        )
        table_service_client.create_table_if_not_exists(table_name)
        return storage_connection_str, table_name
    except:
        pytest.skip("Storage table client can't be created")


def remove_live_storage_table_client(storage_connection_str, table_name):
    try:
        table_service_client = TableServiceClient.from_connection_string(
            storage_connection_str
        )
        table_service_client.delete_table(table_name)
    except:
        warnings.warn(UserWarning("storage table teardown failed"))


def _create_checkpoint(partition_id, offset, sequence_number):
    return {
        "fully_qualified_namespace": "test_namespace",
        "eventhub_name": "eventhub",
        "consumer_group": "$default",
        "partition_id": str(partition_id),
        "offset": offset,
        "sequence_number": sequence_number,
    }


def _create_ownership(partition_id, owner_id, etag, last_modified_time):
    return {
        "fully_qualified_namespace": "test_namespace",
        "eventhub_name": "eventhub",
        "consumer_group": "$default",
        "partition_id": str(partition_id),
        "owner_id": owner_id,
        "etag": etag,
        "last_modified_time": last_modified_time,
    }


def _claim_ownership_exception_test(storage_connection_str, table_name):
    fully_qualified_namespace = "test_namespace"
    eventhub_name = "eventhub"
    consumer_group = "$default"
    ownership_cnt = 8

    checkpoint_store = TableCheckpointStore.from_connection_string(
        storage_connection_str, table_name
    )
    ownership_list = []
    for i in range(ownership_cnt):
        ownership = _create_ownership(str(i), "owner_id", None, None)
        ownership_list.append(ownership)
    result_ownership_list = checkpoint_store.claim_ownership(ownership_list)
    assert result_ownership_list[0]["owner_id"] == "owner_id"
    single_ownership = [result_ownership_list[0].copy()]
    single_ownership[0]["owner_id"] = "Bill"
    ownership_list = checkpoint_store.claim_ownership(single_ownership)
    assert ownership_list[0]["owner_id"] == "Bill"

    single_ownership = [result_ownership_list[0].copy()]
    single_ownership[0]["etag"] = "W/\"datetime'2021-08-02T00%3A46%3A51.7645424Z'\""
    single_ownership[0]["owner_id"] = "Jack"
    single_ownership[0]["partition_id"] = "10"
    result_ownership = checkpoint_store.claim_ownership(single_ownership)
    list_ownership = checkpoint_store.list_ownership(
        fully_qualified_namespace, eventhub_name, consumer_group
    )
    assert result_ownership[0] in list_ownership

    single_ownership = [result_ownership_list[0].copy()]
    single_ownership[0]["etag"] = "W/\"datetime'2021-08-02T00%3A46%3A51.7645424Z'\""
    with pytest.raises(OwnershipLostError) as e_info:
        checkpoint_store.claim_ownership(single_ownership)


def _claim_and_list_ownership(storage_connection_str, table_name):
    fully_qualified_namespace = "test_namespace"
    eventhub_name = "eventhub"
    consumer_group = "$default"
    ownership_cnt = 8

    checkpoint_store = TableCheckpointStore.from_connection_string(
        storage_connection_str, table_name
    )
    ownership_list = checkpoint_store.list_ownership(
        fully_qualified_namespace, eventhub_name, consumer_group
    )
    assert len(ownership_list) == 0

    ownership_list = []

    for i in range(ownership_cnt):
        ownership = _create_ownership(str(i), "owner_id", None, None)
        ownership_list.append(ownership)
    result_ownership_list = checkpoint_store.claim_ownership(ownership_list)
    assert ownership_list != result_ownership_list
    assert len(result_ownership_list) == len(ownership_list)
    for i in range(len(ownership_list)):
        assert ownership_list[i]["etag"] != result_ownership_list[i]["etag"]
        assert (
            ownership_list[i]["last_modified_time"]
            != result_ownership_list[i]["last_modified_time"]
        )

    ownership_list = checkpoint_store.list_ownership(
        fully_qualified_namespace, eventhub_name, consumer_group
    )
    assert len(ownership_list) == ownership_cnt
    assert len(ownership_list) == len(result_ownership_list)
    for i in range(len(result_ownership_list)):
        assert ownership_list[i]["etag"] == result_ownership_list[i]["etag"]
        assert (
            ownership_list[i]["last_modified_time"]
            == result_ownership_list[i]["last_modified_time"]
        )


def _update_and_list_checkpoint(storage_connection_str, table_name):
    fully_qualified_namespace = "test_namespace"
    eventhub_name = "eventhub"
    consumer_group = "$default"
    partition_cnt = 8

    checkpoint_store = TableCheckpointStore.from_connection_string(
        storage_connection_str, table_name
    )
    checkpoint_list = checkpoint_store.list_checkpoints(
        fully_qualified_namespace, eventhub_name, consumer_group
    )
    assert len(checkpoint_list) == 0
    for i in range(partition_cnt):
        checkpoint = _create_checkpoint(i, 2, 20)
        checkpoint_store.update_checkpoint(checkpoint)

    checkpoint_list = checkpoint_store.list_checkpoints(
        fully_qualified_namespace, eventhub_name, consumer_group
    )
    assert len(checkpoint_list) == partition_cnt
    for checkpoint in checkpoint_list:
        assert checkpoint["offset"] == "2"
        assert checkpoint["sequence_number"] == 20

    checkpoint = _create_checkpoint(0, "30", 42)
    checkpoint_store.update_checkpoint(checkpoint)
    checkpoint_list = checkpoint_store.list_checkpoints(
        fully_qualified_namespace, eventhub_name, consumer_group
    )
    assert len(checkpoint_list) == partition_cnt
    assert checkpoint_list[0]["offset"] == "30"


@pytest.mark.parametrize("conn_str_env_key", STORAGE_ENV_KEYS)
@pytest.mark.liveTest
def test_claim_ownership_exception(conn_str_env_key):
    storage_connection_str, table_name = get_live_storage_table_client(
        conn_str_env_key
    )
    try:
        _claim_ownership_exception_test(storage_connection_str, table_name)
    finally:
        remove_live_storage_table_client(storage_connection_str, table_name)


@pytest.mark.parametrize("conn_str_env_key", STORAGE_ENV_KEYS)
@pytest.mark.liveTest
def test_claim_and_list_ownership(conn_str_env_key):
    storage_connection_str, table_name = get_live_storage_table_client(
        conn_str_env_key
    )
    try:
        _claim_and_list_ownership(storage_connection_str, table_name)
    finally:
        remove_live_storage_table_client(storage_connection_str, table_name)


@pytest.mark.parametrize("conn_str_env_key", STORAGE_ENV_KEYS)
@pytest.mark.liveTest
def test_update_checkpoint(conn_str_env_key):
    storage_connection_str, table_name = get_live_storage_table_client(
        conn_str_env_key
    )
    try:
        _update_and_list_checkpoint(storage_connection_str, table_name)
    finally:
        remove_live_storage_table_client(storage_connection_str, table_name)
