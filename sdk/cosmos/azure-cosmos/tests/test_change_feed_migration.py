# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.
"""Rust checkpoint/create/resume scenarios adapted from test_change_feed.py."""

import asyncio
import base64
import json
from copy import deepcopy

import pytest

from azure.cosmos import PartitionKey
from azure.cosmos.partition_key import _build_partition_key_from_properties
from common.change_feed_samples import load_change_feed_sample
from config.clients import create_data_client, create_data_client_async
from config.settings import unique_database_id


def _pages(container, token, channel, size, **kwargs):
    kwargs.update(max_item_count=size, timeout=30)
    if channel == "keyword":
        return container.query_items_change_feed(continuation=token, **kwargs).by_page()
    return container.query_items_change_feed(**kwargs).by_page(continuation_token=token)


def _assert_ids(rows, expected):
    ids = [row["id"] for row in rows]
    assert len(ids) == len(set(ids)) and set(ids) == expected


@pytest.mark.cosmosEmulator
@pytest.mark.cosmosAADLong
@pytest.mark.parametrize("asynchronous", [False, True], ids=["sync", "async"])
@pytest.mark.parametrize("conflicting_scope", [False, True], ids=["matching-scope", "conflicting-scope"])
def test_change_feed_custom_header_precedence_rust(asynchronous, conflicting_scope):
    """Adapt the original empty/checkpoint/write/resume scenario with header conflicts."""
    database_id = unique_database_id("ChangeFeedHeaders")
    headers = {
        "x-app-check": "alpha-bank",
        "If-None-Match": "*",
        "A-IM": "customer-mode",
        "x-ms-max-item-count": "99",
    }
    if conflicting_scope:
        headers["x-ms-documentdb-partitionkey"] = '["other"]'
    original = deepcopy(headers)
    with create_data_client(_backend="core-python", timeout=30) as setup:
        database = setup.create_database(database_id)
        try:
            writer = database.create_container("orders", PartitionKey(path="/pk"), offer_throughput=400)

            async def exercise(target):
                async def collect(pages):
                    rows = []
                    if asynchronous:
                        async for page in pages:
                            batch = [row async for row in page]
                            assert len(batch) <= 1
                            rows.extend(batch)
                    else:
                        for page in pages:
                            batch = list(page)
                            assert len(batch) <= 1
                            rows.extend(batch)
                    return rows

                def pages(**kwargs):
                    return target.query_items_change_feed(
                        partition_key="customer", max_item_count=1,
                        initial_headers=kwargs.pop("initial_headers", headers), timeout=30, **kwargs,
                    ).by_page()

                initial = pages()
                assert await collect(initial) == []
                checkpoint = initial.continuation_token
                assert checkpoint
                for item_id in ("one", "two"):
                    writer.create_item({"id": item_id, "pk": "customer"})
                writer.create_item({"id": "outside", "pk": "other"})
                resumed = pages(continuation=checkpoint)
                rows = await collect(resumed)
                _assert_ids(rows, {"one", "two"})
                assert resumed.continuation_token
                assert await collect(pages(continuation=resumed.continuation_token)) == []
                assert headers == original

            if asynchronous:
                async def run():
                    async with create_data_client_async(_backend="rust") as client:
                        await asyncio.wait_for(
                            exercise(client.get_database_client(database_id).get_container_client("orders")),
                            timeout=90,
                        )
                asyncio.run(run())
            else:
                with create_data_client(_backend="rust") as client:
                    asyncio.run(exercise(client.get_database_client(database_id).get_container_client("orders")))
        finally:
            setup.delete_database(database_id)


@pytest.mark.cosmosEmulator
@pytest.mark.cosmosAADLong
@pytest.mark.parametrize("asynchronous", [False, True], ids=["sync", "async"])
@pytest.mark.parametrize("partition_count", [1, 2], ids=["single-range", "multiple-ranges"])
def test_change_feed_continuation_sample_rust(asynchronous, partition_count, monkeypatch):
    """Run the shipped sample's create/checkpoint/resume scenario on Rust."""
    database_id = unique_database_id("ChangeFeedSample")
    sample = load_change_feed_sample(asynchronous, monkeypatch)
    printed, created = [], []
    monkeypatch.setattr(sample, "print", lambda value: printed.append(value), raising=False)
    with create_data_client(_backend="core-python") as setup:
        database = setup.create_database(database_id)
        try:
            writer = database.create_container(
                "orders", PartitionKey(path="/address/state"),
                offer_throughput=400 if partition_count == 1 else 12000,
            )
            ranges = list(writer.client_connection._ReadPartitionKeyRanges(writer.container_link))
            assert len(ranges) == partition_count
            definition = _build_partition_key_from_properties(writer.read())
            keys = {}
            for index in range(100):
                key = f"customer-{index}"
                epk = definition._get_effective_partition_key_string([key])
                for interval in ranges:
                    if interval["minInclusive"] <= epk < interval["maxExclusive"]:
                        keys.setdefault(interval["id"], key)
            assert len(keys) == partition_count
            states = {"WA": keys[ranges[0]["id"]], "CA": keys[ranges[0]["id"]],
                      "OR": keys[ranges[-1]["id"]]}

            def observe(target):
                create = target.create_item
                query = target.query_items_change_feed

                def prepare(body):
                    body["address"]["state"] = states[body["address"]["state"]]
                    created.append(body["id"])
                    return body

                def create_sync(*, body):
                    return create(body=prepare(body))

                async def create_async(*, body):
                    return await create(body=prepare(body))

                def query_pages(**kwargs):
                    return query(max_item_count=3, timeout=30, **kwargs)

                monkeypatch.setattr(target, "create_item", create_async if asynchronous else create_sync)
                monkeypatch.setattr(target, "query_items_change_feed", query_pages)
                return target

            def run_sample():
                if asynchronous:
                    async def run():
                        async with create_data_client_async(_backend="rust") as client:
                            target = observe(client.get_database_client(database_id).get_container_client("orders"))
                            await asyncio.wait_for(sample.read_change_feed_with_continuation(target), timeout=90)
                    asyncio.run(run())
                else:
                    with create_data_client(_backend="rust") as client:
                        target = observe(client.get_database_client(database_id).get_container_client("orders"))
                        sample.read_change_feed_with_continuation(target)

            if partition_count > 1:
                with pytest.raises(NotImplementedError, match="multi-partition change-feed scopes"):
                    run_sample()
                assert len(created) == 10
                assert not any(isinstance(value, dict) for value in printed)
                return
            run_sample()
            rows = [value for value in printed if isinstance(value, dict)]
            assert len(created) == 20
            _assert_ids(rows[:10], set(created[:10]))
            _assert_ids(rows[10:], set(created[10:]))
        finally:
            setup.delete_database(database_id)


@pytest.mark.cosmosEmulator
@pytest.mark.cosmosAADLong
@pytest.mark.parametrize("asynchronous", [False, True], ids=["sync", "async"])
@pytest.mark.parametrize("partition_count", [1, 2], ids=["single-range", "multiple-ranges"])
def test_change_feed_partition_range_id_rust(asynchronous, partition_count):
    """Copy the range-ID scenario from TestChangeFeed.test_query_change_feed_with_different_filter."""
    database_id = unique_database_id("ChangeFeedRangeId")
    with create_data_client(_backend="core-python") as setup:
        database = setup.create_database(database_id)
        try:
            writer = database.create_container(
                "orders", PartitionKey(path="/pk"),
                offer_throughput=400 if partition_count == 1 else 12000,
            )
            ranges = list(writer.client_connection._ReadPartitionKeyRanges(writer.container_link))
            assert len(ranges) == partition_count
            selected = ranges[0]
            definition = _build_partition_key_from_properties(writer.read())
            keys, outside = [], []
            for index in range(100):
                key = f"customer-{index}"
                epk = definition._get_effective_partition_key_string([key])
                bucket = keys if selected["minInclusive"] <= epk < selected["maxExclusive"] else outside
                bucket.append(key)
            assert len(keys) >= 2
            if partition_count > 1:
                assert outside

            async def exercise(target):
                hooks = []

                def inspect_page(headers, body):
                    hooks.append((headers, body.get_response_headers()))

                def check_page(pages):
                    headers, body_headers = hooks[-1]
                    assert headers["etag"] == body_headers["etag"]
                    assert headers["etag"] != pages.continuation_token
                    assert headers["x-ms-continuation"] == pages.continuation_token

                async def collect(pages):
                    rows = []
                    previous_hooks = len(hooks)
                    if asynchronous:
                        async for page in pages:
                            assert len(hooks) == previous_hooks + 1
                            check_page(pages)
                            rows.extend([row async for row in page])
                            previous_hooks = len(hooks)
                    else:
                        for page in pages:
                            assert len(hooks) == previous_hooks + 1
                            check_page(pages)
                            rows.extend(page)
                            previous_hooks = len(hooks)
                    return rows

                def pages(**kwargs):
                    with pytest.warns(DeprecationWarning, match="partition_key_range_id"):
                        return target.query_items_change_feed(
                            partition_key_range_id=selected["id"], timeout=30, response_hook=inspect_page, **kwargs
                        ).by_page()

                current = pages()
                assert await collect(current) == []
                assert current.continuation_token
                beginning = pages(start_time="Beginning")
                assert await collect(beginning) == []
                empty_token = beginning.continuation_token
                assert empty_token
                writer.create_item({"pk": keys[0], "id": "doc1"})
                if outside:
                    writer.create_item({"pk": outside[0], "id": "not-in-selected-range"})
                beginning = pages(start_time="Beginning")
                _assert_ids(await collect(beginning), {"doc1"})
                token = beginning.continuation_token
                assert token != empty_token
                writer.create_item({"pk": keys[0], "id": "doc2"})
                writer.create_item({"pk": keys[1], "id": "doc3"})
                for size in (1, 100):
                    for channel in ("keyword", "by_page"):
                        with pytest.warns(DeprecationWarning, match="partition_key_range_id"):
                            resumed = _pages(
                                target, token, channel, size, partition_key_range_id=selected["id"],
                                response_hook=inspect_page,
                            )
                        _assert_ids(await collect(resumed), {"doc2", "doc3"})
                # The wrapper bookmark must also restore the ID without a new scope argument.
                resumed = _pages(target, token, "keyword", 1, response_hook=inspect_page)
                _assert_ids(await collect(resumed), {"doc2", "doc3"})
                beginning = pages(start_time="Beginning")
                _assert_ids(await collect(beginning), {"doc1", "doc2", "doc3"})
                caught_up = pages(continuation=beginning.continuation_token)
                assert await collect(caught_up) == []

            if asynchronous:
                async def run():
                    async with create_data_client_async(_backend="rust") as client:
                        await asyncio.wait_for(
                            exercise(client.get_database_client(database_id).get_container_client("orders")),
                            timeout=45,
                        )
                asyncio.run(run())
            else:
                with create_data_client(_backend="rust") as client:
                    asyncio.run(exercise(client.get_database_client(database_id).get_container_client("orders")))
        finally:
            setup.delete_database(database_id)


# NOTE: Retained for reference; requires retired legacy change-feed execution/modules and cannot run after legacy retirement.
# @pytest.mark.cosmosEmulator
# @pytest.mark.cosmosAADLong
# @pytest.mark.parametrize("backend", ["core-python", "rust"])
# @pytest.mark.parametrize("asynchronous", [False, True], ids=["sync", "async"])
# @pytest.mark.parametrize("conflicting_scope", [False, True], ids=["matching-scope", "conflicting-scope"])
# def test_change_feed_custom_header_precedence_comparison(backend, asynchronous, conflicting_scope):
#     """Adapt the original empty/checkpoint/write/resume scenario with header conflicts."""
#     database_id = unique_database_id("ChangeFeedHeaders")
#     headers = {
#         "x-app-check": "alpha-bank",
#         "If-None-Match": "*",
#         "A-IM": "customer-mode",
#         "x-ms-max-item-count": "99",
#     }
#     if conflicting_scope:
#         headers["x-ms-documentdb-partitionkey"] = '["other"]'
#     original = deepcopy(headers)
#     with create_data_client(_backend="core-python", timeout=30) as setup:
#         database = setup.create_database(database_id)
#         try:
#             writer = database.create_container("orders", PartitionKey(path="/pk"), offer_throughput=400)
#
#             async def exercise(target):
#                 async def collect(pages):
#                     rows = []
#                     if asynchronous:
#                         async for page in pages:
#                             batch = [row async for row in page]
#                             assert len(batch) <= 1
#                             rows.extend(batch)
#                     else:
#                         for page in pages:
#                             batch = list(page)
#                             assert len(batch) <= 1
#                             rows.extend(batch)
#                     return rows
#
#                 def pages(**kwargs):
#                     return target.query_items_change_feed(
#                         partition_key="customer", max_item_count=1,
#                         initial_headers=kwargs.pop("initial_headers", headers), timeout=30, **kwargs,
#                     ).by_page()
#
#                 initial = pages()
#                 assert await collect(initial) == []
#                 checkpoint = initial.continuation_token
#                 assert checkpoint
#                 for item_id in ("one", "two"):
#                     writer.create_item({"id": item_id, "pk": "customer"})
#                 writer.create_item({"id": "outside", "pk": "other"})
#                 resumed = pages(continuation=checkpoint)
#                 rows = await collect(resumed)
#                 if backend == "core-python" and conflicting_scope:
#                     _assert_ids(rows, set())
#                     # Legacy retains the conflicting raw key; retry the original
#                     # checkpoint without that header to recover the selected scope.
#                     resumed = pages(
#                         continuation=checkpoint,
#                         initial_headers={
#                             name: value for name, value in headers.items()
#                             if name != "x-ms-documentdb-partitionkey"
#                         },
#                     )
#                     rows = await collect(resumed)
#                 _assert_ids(rows, {"one", "two"})
#                 assert resumed.continuation_token
#                 assert await collect(pages(continuation=resumed.continuation_token)) == []
#                 assert headers == original
#
#             if asynchronous:
#                 async def run():
#                     async with create_data_client_async(_backend=backend) as client:
#                         await asyncio.wait_for(
#                             exercise(client.get_database_client(database_id).get_container_client("orders")),
#                             timeout=90,
#                         )
#                 asyncio.run(run())
#             else:
#                 with create_data_client(_backend=backend) as client:
#                     asyncio.run(exercise(client.get_database_client(database_id).get_container_client("orders")))
#         finally:
#             setup.delete_database(database_id)
# NOTE: Retained for reference; requires retired legacy change-feed execution/modules and cannot run after legacy retirement.
# @pytest.mark.cosmosEmulator
# @pytest.mark.cosmosAADLong
# @pytest.mark.parametrize("backend", ["core-python", "rust"])
# @pytest.mark.parametrize("asynchronous", [False, True], ids=["sync", "async"])
# @pytest.mark.parametrize("partition_count", [1, 2], ids=["single-range", "multiple-ranges"])
# def test_change_feed_continuation_sample_parity(backend, asynchronous, partition_count, monkeypatch):
#     """Run the shipped sample's create/checkpoint/resume scenario on both backends."""
#     database_id = unique_database_id("ChangeFeedSample")
#     sample = load_change_feed_sample(asynchronous, monkeypatch)
#     printed, created = [], []
#     monkeypatch.setattr(sample, "print", lambda value: printed.append(value), raising=False)
#     with create_data_client(_backend="core-python") as setup:
#         database = setup.create_database(database_id)
#         try:
#             writer = database.create_container(
#                 "orders", PartitionKey(path="/address/state"),
#                 offer_throughput=400 if partition_count == 1 else 12000,
#             )
#             ranges = list(writer.client_connection._ReadPartitionKeyRanges(writer.container_link))
#             assert len(ranges) == partition_count
#             definition = _build_partition_key_from_properties(writer.read())
#             keys = {}
#             for index in range(100):
#                 key = f"customer-{index}"
#                 epk = definition._get_effective_partition_key_string([key])
#                 for interval in ranges:
#                     if interval["minInclusive"] <= epk < interval["maxExclusive"]:
#                         keys.setdefault(interval["id"], key)
#             assert len(keys) == partition_count
#             states = {"WA": keys[ranges[0]["id"]], "CA": keys[ranges[0]["id"]],
#                       "OR": keys[ranges[-1]["id"]]}
#
#             def observe(target):
#                 create = target.create_item
#                 query = target.query_items_change_feed
#
#                 def prepare(body):
#                     body["address"]["state"] = states[body["address"]["state"]]
#                     created.append(body["id"])
#                     return body
#
#                 def create_sync(*, body):
#                     return create(body=prepare(body))
#
#                 async def create_async(*, body):
#                     return await create(body=prepare(body))
#
#                 def query_pages(**kwargs):
#                     return query(max_item_count=3, timeout=30, **kwargs)
#
#                 monkeypatch.setattr(target, "create_item", create_async if asynchronous else create_sync)
#                 monkeypatch.setattr(target, "query_items_change_feed", query_pages)
#                 return target
#
#             def run_sample():
#                 if asynchronous:
#                     async def run():
#                         async with create_data_client_async(_backend=backend) as client:
#                             target = observe(client.get_database_client(database_id).get_container_client("orders"))
#                             await asyncio.wait_for(sample.read_change_feed_with_continuation(target), timeout=90)
#                     asyncio.run(run())
#                 else:
#                     with create_data_client(_backend=backend) as client:
#                         target = observe(client.get_database_client(database_id).get_container_client("orders"))
#                         sample.read_change_feed_with_continuation(target)
#
#             if backend == "rust" and partition_count > 1:
#                 with pytest.raises(NotImplementedError, match="multi-partition change-feed scopes"):
#                     run_sample()
#                 assert len(created) == 10
#                 assert not any(isinstance(value, dict) for value in printed)
#                 return
#             run_sample()
#             rows = [value for value in printed if isinstance(value, dict)]
#             assert len(created) == 20
#             _assert_ids(rows[:10], set(created[:10]))
#             _assert_ids(rows[10:], set(created[10:]))
#         finally:
#             setup.delete_database(database_id)
# NOTE: Retained for reference; requires retired legacy change-feed execution/modules and cannot run after legacy retirement.
# @pytest.mark.cosmosEmulator
# @pytest.mark.cosmosAADLong
# @pytest.mark.parametrize("backend", ["core-python", "rust"])
# @pytest.mark.parametrize("asynchronous", [False, True], ids=["sync", "async"])
# @pytest.mark.parametrize("partition_count", [1, 2], ids=["single-range", "multiple-ranges"])
# def test_change_feed_partition_range_id_parity(backend, asynchronous, partition_count):
#     """Copy the range-ID scenario from TestChangeFeed.test_query_change_feed_with_different_filter."""
#     database_id = unique_database_id("ChangeFeedRangeId")
#     with create_data_client(_backend="core-python") as setup:
#         database = setup.create_database(database_id)
#         try:
#             writer = database.create_container(
#                 "orders", PartitionKey(path="/pk"),
#                 offer_throughput=400 if partition_count == 1 else 12000,
#             )
#             ranges = list(writer.client_connection._ReadPartitionKeyRanges(writer.container_link))
#             assert len(ranges) == partition_count
#             selected = ranges[0]
#             definition = _build_partition_key_from_properties(writer.read())
#             keys, outside = [], []
#             for index in range(100):
#                 key = f"customer-{index}"
#                 epk = definition._get_effective_partition_key_string([key])
#                 bucket = keys if selected["minInclusive"] <= epk < selected["maxExclusive"] else outside
#                 bucket.append(key)
#             assert len(keys) >= 2
#             if partition_count > 1:
#                 assert outside
#
#             async def exercise(target):
#                 hooks = []
#
#                 def inspect_page(headers, body):
#                     hooks.append((headers, body.get_response_headers()))
#
#                 def check_page(pages):
#                     headers, body_headers = hooks[-1]
#                     assert headers["etag"] == body_headers["etag"]
#                     assert headers["etag"] != pages.continuation_token
#                     assert headers["x-ms-continuation"] == pages.continuation_token
#
#                 async def collect(pages):
#                     rows = []
#                     previous_hooks = len(hooks)
#                     if asynchronous:
#                         async for page in pages:
#                             assert len(hooks) == previous_hooks + 1
#                             check_page(pages)
#                             rows.extend([row async for row in page])
#                             previous_hooks = len(hooks)
#                     else:
#                         for page in pages:
#                             assert len(hooks) == previous_hooks + 1
#                             check_page(pages)
#                             rows.extend(page)
#                             previous_hooks = len(hooks)
#                     return rows
#
#                 def pages(**kwargs):
#                     with pytest.warns(DeprecationWarning, match="partition_key_range_id"):
#                         return target.query_items_change_feed(
#                             partition_key_range_id=selected["id"], timeout=30, response_hook=inspect_page, **kwargs
#                         ).by_page()
#
#                 current = pages()
#                 assert await collect(current) == []
#                 assert current.continuation_token
#                 beginning = pages(start_time="Beginning")
#                 assert await collect(beginning) == []
#                 empty_token = beginning.continuation_token
#                 assert empty_token
#                 writer.create_item({"pk": keys[0], "id": "doc1"})
#                 if outside:
#                     writer.create_item({"pk": outside[0], "id": "not-in-selected-range"})
#                 beginning = pages(start_time="Beginning")
#                 _assert_ids(await collect(beginning), {"doc1"})
#                 token = beginning.continuation_token
#                 assert token != empty_token
#                 writer.create_item({"pk": keys[0], "id": "doc2"})
#                 writer.create_item({"pk": keys[1], "id": "doc3"})
#                 for size in (1, 100):
#                     for channel in ("keyword", "by_page"):
#                         with pytest.warns(DeprecationWarning, match="partition_key_range_id"):
#                             resumed = _pages(
#                                 target, token, channel, size, partition_key_range_id=selected["id"],
#                                 response_hook=inspect_page,
#                             )
#                         _assert_ids(await collect(resumed), {"doc2", "doc3"})
#                 # The wrapper bookmark must also restore the ID without a new scope argument.
#                 resumed = _pages(target, token, "keyword", 1, response_hook=inspect_page)
#                 _assert_ids(await collect(resumed), {"doc2", "doc3"})
#                 beginning = pages(start_time="Beginning")
#                 _assert_ids(await collect(beginning), {"doc1", "doc2", "doc3"})
#                 caught_up = pages(continuation=beginning.continuation_token)
#                 assert await collect(caught_up) == []
#
#             if asynchronous:
#                 async def run():
#                     async with create_data_client_async(_backend=backend) as client:
#                         await asyncio.wait_for(
#                             exercise(client.get_database_client(database_id).get_container_client("orders")),
#                             timeout=45,
#                         )
#                 asyncio.run(run())
#             else:
#                 with create_data_client(_backend=backend) as client:
#                     asyncio.run(exercise(client.get_database_client(database_id).get_container_client("orders")))
#         finally:
#             setup.delete_database(database_id)
# NOTE: Original legacy comparison body retained for reference; it requires retired legacy change-feed execution/modules and cannot run after legacy retirement.
# @pytest.mark.cosmosEmulator
# @pytest.mark.cosmosAADLong
# @pytest.mark.parametrize("asynchronous", [False, True], ids=["sync", "async"])
# def test_change_feed_point_range_matches_partition_key(asynchronous):
#     """Adapt test_query_change_feed_with_different_filter for legacy/Rust parity."""
#     database_id = unique_database_id("ChangeFeedPointRange")
#     expected = {"old0", "old1", "old2"}
#     with create_data_client(_backend="core-python") as setup:
#         database = setup.create_database(database_id)
#         try:
#             container = database.create_container("orders", PartitionKey(path="/pk"), offer_throughput=400)
#             for item_id in sorted(expected):
#                 container.create_item({"id": item_id, "pk": "customer"})
#             container.create_item({"id": "out-of-scope", "pk": "other"})
#             legacy_point = container.feed_range_from_partition_key("customer")
#             legacy_pages = container.query_items_change_feed(
#                 feed_range=legacy_point, start_time="Beginning", max_item_count=1, timeout=30
#             ).by_page()
#             _assert_ids([row for page in legacy_pages for row in page], expected)
#             legacy_token = legacy_pages.continuation_token
#
#             async def run_async():
#                 async with create_data_client_async(_backend="rust") as client:
#                     target = client.get_database_client(database_id).get_container_client("orders")
#                     point = await target.feed_range_from_partition_key("customer")
#                     assert point == legacy_point
#                     original = deepcopy(point)
#                     baseline = [
#                         row async for row in target.query_items_change_feed(
#                             partition_key="customer", start_time="Beginning", timeout=30
#                         )
#                     ]
#                     _assert_ids(baseline, expected)
#                     pages = target.query_items_change_feed(
#                         feed_range=point, start_time="Beginning", max_item_count=1, timeout=30
#                     ).by_page()
#                     _assert_ids([row async for page in pages async for row in page], expected)
#                     token = pages.continuation_token
#                     await target.create_item({"id": "later", "pk": "customer"})
#                     await target.create_item({"id": "later-out-of-scope", "pk": "other"})
#                     _assert_ids([
#                         row async for row in target.query_items_change_feed(continuation=token, timeout=30)
#                     ], {"later"})
#                     assert point == original
#
#             if asynchronous:
#                 asyncio.run(run_async())
#             else:
#                 with create_data_client(_backend="rust") as client:
#                     target = client.get_database_client(database_id).get_container_client("orders")
#                     point = target.feed_range_from_partition_key("customer")
#                     assert point == legacy_point
#                     original = deepcopy(point)
#                     _assert_ids(list(target.query_items_change_feed(
#                         partition_key="customer", start_time="Beginning", timeout=30
#                     )), expected)
#                     pages = target.query_items_change_feed(
#                         feed_range=point, start_time="Beginning", max_item_count=1, timeout=30
#                     ).by_page()
#                     _assert_ids([row for page in pages for row in page], expected)
#                     token = pages.continuation_token
#                     target.create_item({"id": "later", "pk": "customer"})
#                     target.create_item({"id": "later-out-of-scope", "pk": "other"})
#                     _assert_ids(list(target.query_items_change_feed(
#                         continuation=token, timeout=30
#                     )), {"later"})
#                     assert point == original
#             _assert_ids(list(container.query_items_change_feed(
#                 continuation=legacy_token, timeout=30
#             )), {"later"})
#         finally:
#             setup.delete_database(database_id)

@pytest.mark.cosmosEmulator
@pytest.mark.cosmosAADLong
@pytest.mark.parametrize("asynchronous", [False, True], ids=["sync", "async"])
@pytest.mark.parametrize("hierarchical", [False, True], ids=["single-key", "complete-hpk"])
def test_change_feed_point_range_matches_partition_key(asynchronous, hierarchical):
    """Preserve query/change-feed point scope and resume without mutating the range."""
    database_id = unique_database_id("ChangeFeedPointRange")
    expected = {"old0", "old1", "old2"}
    key = ["tenant", "customer"] if hierarchical else "customer"
    definition = (
        PartitionKey(path=["/tenant", "/pk"], kind="MultiHash")
        if hierarchical else PartitionKey(path="/pk")
    )
    with create_data_client(_backend="core-python") as setup:
        database = setup.create_database(database_id)
        try:
            container = database.create_container("orders", definition, offer_throughput=400)
            for item_id in sorted(expected):
                container.create_item({"id": item_id, "tenant": "tenant", "pk": "customer"})
            container.create_item({"id": "out-of-scope", "tenant": "tenant", "pk": "other"})
            setup_point = container.feed_range_from_partition_key(key)
            assert setup_point["Range"]["min"] == setup_point["Range"]["max"]
            assert setup_point["Range"]["isMaxInclusive"] is True

            async def run_async():
                async with create_data_client_async(_backend="rust") as client:
                    target = client.get_database_client(database_id).get_container_client("orders")
                    point = await target.feed_range_from_partition_key(key)
                    assert point == setup_point
                    original = deepcopy(point)
                    _assert_ids([
                        row async for row in target.query_items("SELECT * FROM c", feed_range=point)
                    ], expected)
                    baseline = [
                        row async for row in target.query_items_change_feed(
                            partition_key=key, start_time="Beginning", timeout=30
                        )
                    ]
                    _assert_ids(baseline, expected)
                    pages = target.query_items_change_feed(
                        feed_range=point, start_time="Beginning", max_item_count=1, timeout=30
                    ).by_page()
                    _assert_ids([row async for page in pages async for row in page], expected)
                    token = pages.continuation_token
                    await target.create_item({"id": "later", "tenant": "tenant", "pk": "customer"})
                    await target.create_item({"id": "later-out-of-scope", "tenant": "tenant", "pk": "other"})
                    _assert_ids([
                        row async for row in target.query_items_change_feed(continuation=token, timeout=30)
                    ], {"later"})
                    assert point == original

            if asynchronous:
                asyncio.run(run_async())
            else:
                with create_data_client(_backend="rust") as client:
                    target = client.get_database_client(database_id).get_container_client("orders")
                    point = target.feed_range_from_partition_key(key)
                    assert point == setup_point
                    original = deepcopy(point)
                    _assert_ids(list(target.query_items("SELECT * FROM c", feed_range=point)), expected)
                    _assert_ids(list(target.query_items_change_feed(
                        partition_key=key, start_time="Beginning", timeout=30
                    )), expected)
                    pages = target.query_items_change_feed(
                        feed_range=point, start_time="Beginning", max_item_count=1, timeout=30
                    ).by_page()
                    _assert_ids([row for page in pages for row in page], expected)
                    token = pages.continuation_token
                    target.create_item({"id": "later", "tenant": "tenant", "pk": "customer"})
                    target.create_item({"id": "later-out-of-scope", "tenant": "tenant", "pk": "other"})
                    _assert_ids(list(target.query_items_change_feed(
                        continuation=token, timeout=30
                    )), {"later"})
                    assert point == original
        finally:
            setup.delete_database(database_id)


# NOTE: Original legacy comparison body retained for reference; it requires retired legacy change-feed execution/modules and cannot run after legacy retirement.
# @pytest.mark.cosmosEmulator
# @pytest.mark.cosmosAADLong
# @pytest.mark.parametrize("asynchronous", [False, True], ids=["sync", "async"])
# @pytest.mark.parametrize("hierarchical", [False, True], ids=["single-key", "complete-hpk"])
# def test_legacy_checkpoints_rejected_and_native_resume_preserved_rust(asynchronous, hierarchical):
#     database_id = unique_database_id("ChangeFeedMigration")
#     key = ["tenant", "customer"] if hierarchical else "customer"
#     definition = (
#         PartitionKey(path=["/tenant", "/pk"], kind="MultiHash")
#         if hierarchical else PartitionKey(path="/pk")
#     )
#     with create_data_client(_backend="core-python") as legacy:
#         database = legacy.create_database(database_id)
#         try:
#             container = database.create_container("orders", definition)
#             database.create_container("other", definition)
#             for index in range(6):
#                 container.create_item({"id": f"old{index}", "tenant": "tenant", "pk": "customer"})
#             container.create_item({"id": "out-of-scope", "tenant": "tenant", "pk": "other"})
#             pages = container.query_items_change_feed(
#                 partition_key=key, start_time="Beginning", max_item_count=2, timeout=30
#             ).by_page()
#             consumed = {row["id"] for row in next(pages)}
#             partial = pages.continuation_token
#             assert json.loads(base64.b64decode(partial))["v"] == "v2"
#             for page in pages:
#                 list(page)
#             caught_up = pages.continuation_token
#             etag = json.loads(base64.b64decode(partial))["continuation"]["continuation"][0]["token"]
#             for index in range(2):
#                 container.create_item({"id": f"new{index}", "tenant": "tenant", "pk": "customer"})
#             expected_new = {"new0", "new1"}
#             expected_partial = ({f"old{index}" for index in range(6)} - consumed) | expected_new
#             checkpoints = [
#                 (partial, {}, expected_partial),
#                 (caught_up, {}, expected_new),
#                 (etag, {"partition_key": key}, expected_partial),
#             ]
#             for token, options, expected in checkpoints:
#                 for channel in ("keyword", "by_page"):
#                     for size in (1, 100):
#                         rows = [row for page in _pages(container, token, channel, size, **options) for row in page]
#                         _assert_ids(rows, expected)
#
#             async def run_async():
#                 async with create_data_client_async(_backend="rust") as client:
#                     native = client.get_database_client(database_id).get_container_client("orders")
#                     for token, options, _ in checkpoints:
#                         for channel in ("keyword", "by_page"):
#                             for size in (1, 100):
#                                 with pytest.raises(ValueError, match="Use a token returned by the Rust-backed change feed"):
#                                     resumed = _pages(native, token, channel, size, **options)
#                                     async for page in resumed:
#                                         async for _ in page:
#                                             pass
#                     resumed = _pages(native, None, "keyword", 2, partition_key=key, start_time="Beginning")
#                     _assert_ids(
#                         [row async for page in resumed async for row in page],
#                         {f"old{index}" for index in range(6)} | expected_new,
#                     )
#                     saved = resumed.continuation_token
#                     assert saved.startswith("cf1.")
#                     await native.create_item({"id": "later", "tenant": "tenant", "pk": "customer"})
#                     rows = [row async for row in native.query_items_change_feed(continuation=saved, timeout=30)]
#                     _assert_ids(rows, {"later"})
#                     other = client.get_database_client(database_id).get_container_client("other")
#                     with pytest.raises(ValueError, match="incompatible backend or container"):
#                         async for _ in other.query_items_change_feed(continuation=saved, timeout=30):
#                             pass
#
#             if asynchronous:
#                 asyncio.run(run_async())
#             else:
#                 with create_data_client(_backend="rust") as client:
#                     native = client.get_database_client(database_id).get_container_client("orders")
#                     for token, options, _ in checkpoints:
#                         for channel in ("keyword", "by_page"):
#                             for size in (1, 100):
#                                 with pytest.raises(ValueError, match="Use a token returned by the Rust-backed change feed"):
#                                     resumed = _pages(native, token, channel, size, **options)
#                                     list(resumed)
#                     resumed = _pages(native, None, "keyword", 2, partition_key=key, start_time="Beginning")
#                     _assert_ids(
#                         [row for page in resumed for row in page],
#                         {f"old{index}" for index in range(6)} | expected_new,
#                     )
#                     saved = resumed.continuation_token
#                     assert saved.startswith("cf1.")
#                     native.create_item({"id": "later", "tenant": "tenant", "pk": "customer"})
#                     _assert_ids(list(native.query_items_change_feed(continuation=saved, timeout=30)), {"later"})
#                     other = client.get_database_client(database_id).get_container_client("other")
#                     with pytest.raises(ValueError, match="incompatible backend or container"):
#                         list(other.query_items_change_feed(continuation=saved, timeout=30))
#         finally:
#             legacy.delete_database(database_id)

@pytest.mark.cosmosEmulator
@pytest.mark.cosmosAADLong
@pytest.mark.parametrize("asynchronous", [False, True], ids=["sync", "async"])
@pytest.mark.parametrize("hierarchical", [False, True], ids=["single-key", "complete-hpk"])
def test_legacy_checkpoints_rejected_and_native_resume_preserved_rust(asynchronous, hierarchical):
    database_id = unique_database_id("ChangeFeedMigration")
    key = ["tenant", "customer"] if hierarchical else "customer"
    definition = (
        PartitionKey(path=["/tenant", "/pk"], kind="MultiHash")
        if hierarchical else PartitionKey(path="/pk")
    )
    with create_data_client(_backend="rust") as setup:
        database = setup.create_database(database_id)
        try:
            container = database.create_container("orders", definition)
            database.create_container("other", definition)
            for index in range(6):
                container.create_item({"id": f"old{index}", "tenant": "tenant", "pk": "customer"})
            container.create_item({"id": "out-of-scope", "tenant": "tenant", "pk": "other"})
            for index in range(2):
                container.create_item({"id": f"new{index}", "tenant": "tenant", "pk": "customer"})
            expected_new = {"new0", "new1"}
            # V4's serialized checkpoint shape is rejected before any legacy execution.
            legacy_checkpoint = {
                "v": "v2", "containerRid": container.read()["_rid"], "mode": "LatestVersion",
                "startFrom": {"Type": "Beginning"},
                "continuation": {
                    "v": "v2", "rid": container.read()["_rid"], "PK": key,
                    "continuation": [{
                        "token": '"1"',
                        "range": definition._get_epk_range_for_partition_key(key).to_dict(),
                    }],
                },
            }
            checkpoints = [
                (base64.b64encode(json.dumps(legacy_checkpoint).encode()).decode(), {}),
                ('"1"', {"partition_key": key}),
            ]

            async def run_async():
                async with create_data_client_async(_backend="rust") as client:
                    native = client.get_database_client(database_id).get_container_client("orders")
                    for token, options in checkpoints:
                        for channel in ("keyword", "by_page"):
                            for size in (1, 100):
                                with pytest.raises(ValueError, match="Use a token returned by the Rust-backed change feed"):
                                    resumed = _pages(native, token, channel, size, **options)
                                    async for page in resumed:
                                        async for _ in page:
                                            pass
                    resumed = _pages(native, None, "keyword", 2, partition_key=key, start_time="Beginning")
                    _assert_ids(
                        [row async for page in resumed async for row in page],
                        {f"old{index}" for index in range(6)} | expected_new,
                    )
                    saved = resumed.continuation_token
                    assert saved.startswith("cf1.")
                    await native.create_item({"id": "later", "tenant": "tenant", "pk": "customer"})
                    rows = [row async for row in native.query_items_change_feed(continuation=saved, timeout=30)]
                    _assert_ids(rows, {"later"})
                    other = client.get_database_client(database_id).get_container_client("other")
                    with pytest.raises(ValueError, match="incompatible backend or container"):
                        async for _ in other.query_items_change_feed(continuation=saved, timeout=30):
                            pass

            if asynchronous:
                asyncio.run(run_async())
            else:
                with create_data_client(_backend="rust") as client:
                    native = client.get_database_client(database_id).get_container_client("orders")
                    for token, options in checkpoints:
                        for channel in ("keyword", "by_page"):
                            for size in (1, 100):
                                with pytest.raises(ValueError, match="Use a token returned by the Rust-backed change feed"):
                                    resumed = _pages(native, token, channel, size, **options)
                                    list(resumed)
                    resumed = _pages(native, None, "keyword", 2, partition_key=key, start_time="Beginning")
                    _assert_ids(
                        [row for page in resumed for row in page],
                        {f"old{index}" for index in range(6)} | expected_new,
                    )
                    saved = resumed.continuation_token
                    assert saved.startswith("cf1.")
                    native.create_item({"id": "later", "tenant": "tenant", "pk": "customer"})
                    _assert_ids(list(native.query_items_change_feed(continuation=saved, timeout=30)), {"later"})
                    other = client.get_database_client(database_id).get_container_client("other")
                    with pytest.raises(ValueError, match="incompatible backend or container"):
                        list(other.query_items_change_feed(continuation=saved, timeout=30))
        finally:
            setup.delete_database(database_id)
