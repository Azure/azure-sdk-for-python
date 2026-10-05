# The MIT License (MIT)
# Copyright (c) Microsoft Corporation. All rights reserved.

"""Live split-suite regression for incremental updates to already-split ranges.

Runs in the cosmosSplit and cosmosAADSplit lanes using TestConfig credentials.
Creates a temporary database and scales its `default` container from 400 to
20,000 to 40,000 RU/s. Async cleanup deletes the database on success or failure.

From the package directory with a provisioned-throughput test account configured:
    PYTHONPATH=.:tests python -m unittest tests.test_pk_range_child_update_live_async -v

This standalone runner avoids the package conftest's unrelated provisioning.
The first split has a ten-minute deadline; the second has fifteen minutes to
allow for slower physical splits and offer replacement. Missing the real
child-update transition fails the test rather than claiming that a split alone
validates the fix.
"""

import asyncio
import hashlib
import json
import time
import unittest
from collections import Counter, deque
from unittest.mock import patch

import pytest
import test_config

import azure.cosmos
from azure.cosmos import PartitionKey
from azure.cosmos._constants import _Constants
from azure.cosmos._routing.aio import routing_map_provider
from azure.cosmos.aio import CosmosClient
from azure.cosmos.exceptions import CosmosHttpResponseError
from azure.cosmos.http_constants import HttpHeaders


def _record(event, **fields):
    print(json.dumps({"event": event, "time": time.time(), **fields}), flush=True)


def _error_fields(error):
    headers = getattr(error, "headers", None) or {}
    return {
        "error_type": type(error).__name__,
        "status_code": getattr(error, "status_code", None),
        "sub_status": getattr(error, "sub_status", None),
        "activity_id": headers.get(HttpHeaders.ActivityId),
    }


def _range_state(routing_map):
    if routing_map is None:
        return None
    return [
        {"id": r.id, "parents": r.parents, "status": r.status}
        for r in routing_map.get_ordered_partition_key_ranges()
    ]


def _continuation_hash(token):
    return hashlib.sha256(token.encode("utf-8")).hexdigest()[:12] if token else None


def _observe_query_post(original_post, requests):
    request_count = 0

    async def observe_post(path, request_params, body, req_headers, **kwargs):
        nonlocal request_count
        if not path.rstrip("/").endswith("/docs") or req_headers.get(HttpHeaders.IsQuery) != "true":
            return await original_post(path, request_params, body, req_headers, **kwargs)
        request_count += 1
        entry = {
            "request": request_count,
            "range_id": req_headers.get(HttpHeaders.PartitionKeyRangeID),
            "request_continuation_hash": _continuation_hash(req_headers.get(HttpHeaders.Continuation)),
            "time": time.time(),
            "outcome": "pending",
        }
        requests.append(entry)
        start = time.monotonic()
        try:
            response = await original_post(path, request_params, body, req_headers, **kwargs)
        except (Exception, asyncio.CancelledError) as error:
            entry.update(outcome="error", **_error_fields(error))
            raise
        else:
            result, headers = response
            entry.update(
                outcome="page",
                ids=[item["id"] for item in result["Documents"]],
                response_continuation_hash=_continuation_hash(headers.get(HttpHeaders.Continuation)),
                activity_id=headers.get(HttpHeaders.ActivityId),
            )
            return response
        finally:
            entry["elapsed_seconds"] = round(time.monotonic() - start, 3)

    return observe_post


@pytest.mark.cosmosSplit
@pytest.mark.cosmosAADSplit
@pytest.mark.timeout(1800)
class TestPkRangeChildUpdateLiveAsync(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        configs = test_config.TestConfig
        self.key_client = CosmosClient(configs.host, configs.masterKey)
        self.addAsyncCleanup(self.key_client.close)
        await self.key_client.__aenter__()
        self.database = await test_config.retry_control_plane_async(
            self.key_client.create_database, test_config.unique_database_id("PKRangeChildUpdate")
        )
        self.addAsyncCleanup(self._delete_database)
        _record("database_created", database=self.database.id, sdk=azure.cosmos.__version__)
        self.key_container = await test_config.retry_control_plane_async(
            self.database.create_container, "default", partition_key=PartitionKey(path="/pk"), offer_throughput=400
        )
        self.client = configs.create_data_client_async(user_agent_suffix="habitat-migration-service")
        self.addAsyncCleanup(self.client.close)
        await self.client.__aenter__()
        self.container = self.client.get_database_client(self.database.id).get_container_client("default")
        properties = await self.container.read()
        self.feed_options = {_Constants.ContainerRID: properties["_rid"]}
        self.provider = self.client.client_connection._routing_map_provider
        self.routing_map = await self.provider.get_routing_map(self.container.container_link, self.feed_options)
        self.expected_ids = [f"item-{i:03d}" for i in range(50)]
        for item_id in self.expected_ids:
            await self.container.create_item({"id": item_id, "pk": item_id})
        self.scans = 0

    async def _delete_database(self):
        try:
            await asyncio.wait_for(
                test_config.retry_control_plane_async(self.key_client.delete_database, self.database.id), timeout=120
            )
        except Exception as error:
            _record("database_cleanup_failed", database=self.database.id, **_error_fields(error))
            raise
        _record("database_deleted", database=self.database.id)

    async def _scan(self):
        # Retain only this scan's last 50 backend requests; do not log raw tokens or ordinary successful scans.
        requests = deque(maxlen=50)
        connection = self.client.client_connection
        observe_post = _observe_query_post(connection._CosmosClientConnection__Post, requests)
        try:
            with patch.object(connection, "_CosmosClientConnection__Post", new=observe_post):
                items = self.container.query_items(
                    query="SELECT * FROM c",
                    feed_range={"Range": {"min": "", "max": "FF", "isMinInclusive": True, "isMaxInclusive": False}},
                    max_item_count=10,
                )
                ids = [item["id"] async for item in items]
        except (Exception, asyncio.CancelledError) as error:
            _record(
                "scan_failed", scans=self.scans, ranges=_range_state(self.routing_map),
                requests=list(requests), **_error_fields(error),
            )
            raise
        if sorted(ids) != self.expected_ids:
            _record(
                "scan_mismatch", scans=self.scans, ranges=_range_state(self.routing_map),
                expected_count=len(self.expected_ids), actual_count=len(ids),
                missing=sorted(set(self.expected_ids) - set(ids)),
                unexpected=sorted(set(ids) - set(self.expected_ids)),
                duplicate_count=len(ids) - len(set(ids)),
                duplicate_ids={item_id: count for item_id, count in Counter(ids).items() if count > 1},
                returned_ids=ids,
                requests=list(requests),
            )
        elif any(request.get("status_code") == 410 for request in requests):
            _record("scan_split_recovered", scans=self.scans, requests=list(requests))
        self.assertEqual(sorted(ids), self.expected_ids)
        self.scans += 1

    async def _split_to(self, throughput):
        old_ids = set(self.routing_map._rangeById)
        _record("scale_start", throughput=throughput, previous_ids=sorted(old_ids))
        start = time.monotonic()
        phase = "replace_throughput"
        polls = 0
        last_progress = start
        offer_pending = None
        complete = False
        try:
            while True:
                try:
                    await self.key_container.replace_throughput(throughput)
                    break
                except CosmosHttpResponseError as error:
                    if error.status_code != 423:
                        raise
                    _record("waiting_for_previous_scale", throughput=throughput, **_error_fields(error))
                    await asyncio.sleep(5)
            phase = "routing_refresh"
            while True:
                previous = self.routing_map
                self.routing_map = await self.provider.get_routing_map(
                    self.container.container_link,
                    self.feed_options,
                    force_refresh=True,
                    previous_routing_map=previous,
                )
                polls += 1
                if self.routing_map.change_feed_etag != previous.change_feed_etag:
                    _record("routing_map", throughput=throughput, etag=self.routing_map.change_feed_etag,
                            ranges=_range_state(self.routing_map))
                phase = "scan"
                await self._scan()
                phase = "routing_refresh"
                new_ids = set(self.routing_map._rangeById)
                if new_ids.isdisjoint(old_ids) and len(new_ids) > len(old_ids):
                    phase = "read_offer"
                    offer = await self.key_container.get_throughput()
                    offer_pending = offer.properties["content"].get("isOfferReplacePending", False)
                    if not offer_pending:
                        self.assertEqual(offer.offer_throughput, throughput)
                        _record(
                            "split_complete",
                            throughput=throughput,
                            elapsed_seconds=round(time.monotonic() - start, 1),
                            ids=sorted(new_ids),
                            scans=self.scans,
                        )
                        complete = True
                        return
                    phase = "routing_refresh"
                now = time.monotonic()
                if now - last_progress >= 30:
                    _record(
                        "split_progress", throughput=throughput, phase=phase, elapsed_seconds=round(now - start, 1),
                        polls=polls, scans=self.scans, offer_pending=offer_pending, ranges=_range_state(self.routing_map),
                    )
                    last_progress = now
                await asyncio.sleep(1)
        except Exception as error:
            _record("split_failed", throughput=throughput, phase=phase, **_error_fields(error))
            raise
        finally:
            if not complete:
                _record(
                    "split_incomplete", throughput=throughput, phase=phase,
                    elapsed_seconds=round(time.monotonic() - start, 1),
                    polls=polls, scans=self.scans, offer_pending=offer_pending, ranges=_range_state(self.routing_map),
                )

    async def test_existing_child_revision_does_not_full_reload(self):
        self.assertEqual(len(self.routing_map._rangeById), 1)
        await asyncio.wait_for(self._split_to(20000), timeout=600)
        _record("first_split_observations", ranges=_range_state(self.routing_map), scans=self.scans)
        self.assertTrue(all(r.parents for r in self.routing_map.get_ordered_partition_key_ranges()))

        original_read = self.client.client_connection._ReadPartitionKeyRanges
        original_process = routing_map_provider.process_fetched_ranges
        requested_etags = []
        child_updates = []
        observed_children = []

        def observe_read(link, options, **kwargs):
            requested_etags.append(kwargs["headers"].get(HttpHeaders.IfNoneMatch))
            if len(requested_etags) <= 5 or len(requested_etags) % 30 == 0:
                _record("metadata_request", number=len(requested_etags),
                        conditional=requested_etags[-1] is not None)
            return original_read(link, options, **kwargs)

        def observe_process(ranges, previous, collection_id, collection_link, new_etag):
            candidates = []
            if previous is not None:
                for raw in ranges:
                    cached = previous.get_range_by_partition_key_range_id(raw["id"])
                    parents = raw.get("parents") or []
                    if parents:
                        observation = {
                            "id": raw["id"], "parents": parents, "status": raw.get("status"),
                            "previous_status": cached.status if cached else None,
                            "was_cached": cached is not None,
                            "parent_was_cached": any(parent in previous._rangeById for parent in parents),
                        }
                        if observation not in observed_children and len(observed_children) < 30:
                            observed_children.append(observation)
                            _record("child_range_observed", **observation)
                    if (
                        cached is not None
                        and parents
                        and all(parent not in previous._rangeById for parent in parents)
                        and raw.get("status") == "splitting"
                        and cached.status != "splitting"
                    ):
                        candidates.append({"id": raw["id"], "parents": parents, "status": raw["status"]})
            result = original_process(ranges, previous, collection_id, collection_link, new_etag)
            for update in candidates:
                child_updates.append(update)
                _record("existing_child_update_merged", **update)
            return result

        # Observe real service payloads and production processing; neither wrapper changes them.
        try:
            with patch.object(self.client.client_connection, "_ReadPartitionKeyRanges", new=observe_read), patch.object(
                routing_map_provider, "process_fetched_ranges", new=observe_process
            ):
                await asyncio.wait_for(self._split_to(40000), timeout=900)
        finally:
            _record(
                "second_split_observations", child_updates=child_updates, observed_children=observed_children,
                metadata_requests=len(requested_etags), full_reloads=requested_etags.count(None),
                final_ranges=_range_state(self.routing_map), scans=self.scans,
            )
        self.assertTrue(
            child_updates, "No real existing-child status transition was observed; "
            "see child_range_observed and second_split_observations for raw vs cached range statuses.")
        self.assertTrue(requested_etags, "No partition range metadata requests were observed during second split.")
        self.assertNotIn(
            None, requested_etags, "A full routing-map reload occurred during the second split; "
            "see metadata_request and second_split_observations.")
        await asyncio.wait_for(self._scan(), timeout=60)
        _record(
            "validated",
            child_updates=child_updates,
            metadata_requests=len(requested_etags),
            full_reloads=requested_etags.count(None),
            scans=self.scans,
        )


if __name__ == "__main__":
    unittest.main()
