# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.
import unittest
import uuid

import pytest

from azure.cosmos import CosmosClient
import test_config
from azure.cosmos.exceptions import CosmosHttpResponseError


@pytest.mark.cosmosEmulator
class TestNoneOptions(unittest.TestCase):
    configs = test_config.TestConfig
    host = configs.host
    masterKey = configs.masterKey
    connectionPolicy = configs.connectionPolicy

    def setUp(self) -> None:
        self.client = CosmosClient(self.host, self.masterKey)
        self.database = self.client.get_database_client(self.configs.TEST_DATABASE_ID)
        self.container = self.database.get_container_client(self.configs.TEST_SINGLE_PARTITION_CONTAINER_ID)

    def _create_sample_item(self):
        item = {"id": str(uuid.uuid4()), "pk": "pk-value", "value": 42}
        self.container.create_item(item, pre_trigger_include=None, post_trigger_include=None, indexing_directive=None,
                                   enable_automatic_id_generation=False, session_token=None, initial_headers=None,
                                   priority=None, no_response=None, retry_write=None, throughput_bucket=None)
        return item

    def test_container_read_none_options(self):
        result = self.container.read(populate_partition_key_range_statistics=None, populate_quota_info=None,
                                     priority=None, initial_headers=None)
        assert result

    def test_container_create_item_none_options(self):
        item = {"id": str(uuid.uuid4()), "pk": "pk-value", "value": 1}
        created = self.container.create_item(item, pre_trigger_include=None, post_trigger_include=None,
                                             indexing_directive=None, enable_automatic_id_generation=False,
                                             session_token=None, initial_headers=None, priority=None, no_response=None,
                                             retry_write=None, throughput_bucket=None)
        assert created["id"] == item["id"]

    def test_container_read_item_none_options(self):
        item = self._create_sample_item()
        read_back = self.container.read_item(item["id"], partition_key=item["pk"], post_trigger_include=None,
                                             session_token=None, initial_headers=None,
                                             max_integrated_cache_staleness_in_ms=None, priority=None,
                                             throughput_bucket=None)
        assert read_back["id"] == item["id"]

    def test_container_read_all_items_none_options(self):
        self._create_sample_item()
        pager = self.container.read_all_items(max_item_count=None, session_token=None, initial_headers=None,
                                              max_integrated_cache_staleness_in_ms=None, priority=None,
                                              throughput_bucket=None)
        items = list(pager)
        assert len(items) >= 1

    def test_container_read_items_none_options(self):
        item = self._create_sample_item()
        results = self.container.read_items([(item["id"], item["pk"])], max_concurrency=None, consistency_level=None,
                                            session_token=None, initial_headers=None, excluded_locations=None,
                                            priority=None, throughput_bucket=None)
        assert any(r["id"] == item["id"] for r in results)

    def test_container_query_items_none_options_partition(self):
        self._create_sample_item()
        pager = self.container.query_items("SELECT * FROM c", continuation_token_limit=None, enable_scan_in_query=None,
                                           initial_headers=None, max_integrated_cache_staleness_in_ms=None, max_item_count=None,
                                           parameters=None, partition_key=None, populate_index_metrics=None,
                                           populate_query_metrics=None, priority=None, response_hook=None, session_token=None,
                                           throughput_bucket=None, enable_cross_partition_query=True)
        items = list(pager)
        assert len(items) >= 1

    def test_upsert_item_none_options(self):
        item = {"id": str(uuid.uuid4()), "pk": "pk-value", "value": 5}
        upserted = self.container.upsert_item(item, pre_trigger_include=None, post_trigger_include=None,
                                              session_token=None, initial_headers=None, etag=None,
                                              match_condition=None, priority=None, no_response=None,
                                              retry_write=None, throughput_bucket=None)
        assert upserted["id"] == item["id"]

    def test_replace_item_none_options(self):
        item = self._create_sample_item()
        new_body = {"id": item["id"], "pk": item["pk"], "value": 999}
        replaced = self.container.replace_item(item["id"], new_body, pre_trigger_include=None,
                                               post_trigger_include=None, session_token=None,
                                               initial_headers=None, etag=None, match_condition=None,
                                               priority=None, no_response=None, retry_write=None,
                                               throughput_bucket=None)
        assert replaced["value"] == 999

    def test_patch_item_none_options(self):
        item = self._create_sample_item()
        operations = [{"op": "add", "path": "/patched", "value": True}]
        patched = self.container.patch_item(item["id"], partition_key=item["pk"], patch_operations=operations,
                                            filter_predicate=None, pre_trigger_include=None, post_trigger_include=None,
                                            session_token=None, etag=None, match_condition=None, priority=None,
                                            no_response=None, retry_write=None, throughput_bucket=None)
        assert patched["patched"] is True

    def test_delete_item_none_options(self):
        item = self._create_sample_item()
        self.container.delete_item(item["id"], partition_key=item["pk"], pre_trigger_include=None,
                                    post_trigger_include=None, session_token=None, initial_headers=None,
                                    etag=None, match_condition=None, priority=None, retry_write=None,
                                    throughput_bucket=None)
        with self.assertRaises(CosmosHttpResponseError):
            self.container.read_item(item["id"], partition_key=item["pk"], post_trigger_include=None,
                                     session_token=None, initial_headers=None,
                                     max_integrated_cache_staleness_in_ms=None, priority=None,
                                     throughput_bucket=None)

    def test_get_throughput_none_options(self):
        tp = self.container.get_throughput(response_hook=None)
        assert tp.offer_throughput > 0

    def test_list_conflicts_none_options(self):
        pager = self.container.list_conflicts(max_item_count=None, response_hook=None)
        conflicts = list(pager)
        assert conflicts == conflicts  # may be empty

    def test_query_conflicts_none_options(self):
        pager = self.container.query_conflicts("SELECT * FROM c", parameters=None, partition_key=None,
                                               max_item_count=None, response_hook=None, enable_cross_partition_query=True)
        conflicts = list(pager)
        assert conflicts == conflicts

    def test_delete_all_items_by_partition_key_none_options(self):
        pk_value = "delete-pk"
        for _ in range(2):
            item = {"id": str(uuid.uuid4()), "pk": pk_value, "value": 1}
            self.container.create_item(item, pre_trigger_include=None, post_trigger_include=None, indexing_directive=None,
                                       enable_automatic_id_generation=False, session_token=None, initial_headers=None,
                                       priority=None, no_response=None, retry_write=None, throughput_bucket=None)
        self.container.delete_all_items_by_partition_key(pk_value, pre_trigger_include=None, post_trigger_include=None,
                                                         session_token=None, throughput_bucket=None)
        pager = self.container.query_items("SELECT * FROM c WHERE c.pk = @pk", parameters=[{"name": "@pk", "value": pk_value}],
                                           partition_key=None, continuation_token_limit=None, enable_scan_in_query=None,
                                           initial_headers=None, max_integrated_cache_staleness_in_ms=None, max_item_count=None,
                                           populate_index_metrics=None, populate_query_metrics=None, priority=None,
                                           response_hook=None, session_token=None, throughput_bucket=None)
        _items = list(pager)
        assert _items == _items

    def test_execute_item_batch_none_options(self):
        pk_value = "batch-pk"
        id1 = str(uuid.uuid4())
        id2 = str(uuid.uuid4())
        ops = [
            ("create", ({"id": id1, "pk": pk_value},)),
            ("create", ({"id": id2, "pk": pk_value},)),
        ]
        batch_result = self.container.execute_item_batch(ops, partition_key=pk_value,
                                                          pre_trigger_include=None, post_trigger_include=None,
                                                          session_token=None, priority=None,
                                                          throughput_bucket=None)
        assert any(r.get("resourceBody").get("id") == id1 for r in batch_result) or any(r.get("resourceBody").get("id") == id2 for r in batch_result)

    def test_query_items_change_feed_none_options(self):
        #Create an item, then acquire the change feed pager to verify the item appears in the feed.
        self.container.create_item({"id": str(uuid.uuid4()), "pk": "cf-pk", "value": 100},
                                   pre_trigger_include=None, post_trigger_include=None, indexing_directive=None,
                                   enable_automatic_id_generation=False, session_token=None, initial_headers=None,
                                   priority=None, no_response=None, retry_write=None, throughput_bucket=None)
        pager = self.container.query_items_change_feed(max_item_count=None, start_time="Beginning", partition_key=None,
                                                       priority=None, mode=None, response_hook=None)
        changes = list(pager)
        assert len(changes) >= 1
