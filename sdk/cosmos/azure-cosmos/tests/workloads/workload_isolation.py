# The MIT License (MIT)
# Copyright (c) Microsoft Corporation. All rights reserved.
"""Owned item preparation and cleanup outside bounded point-operation measurements.

Writes require a manifest from profiling_restore_orders.py --initialize and its
namespace in WORKLOAD_ITEM_NAMESPACE. Retain the manifest for recovery after a
crash; no per-operation ownership journal is written during measurement.
"""

import asyncio
import os
from pathlib import Path
import random

from azure.core import MatchConditions
from azure.cosmos.aio import CosmosClient

from perf_results import OPERATIONS
from profiling_restore_orders import load_manifest, restoration_config, validate_owned_order
import workload_configs as config
import workload_utils as utils


async def _run_maintenance(items, operation):
    concurrency = config.WORKLOAD_MAINTENANCE_CONCURRENCY
    if concurrency == 1:
        for item in items:
            await operation(item)
        return
    pending = iter(items)
    failed = False

    async def worker():
        nonlocal failed
        try:
            while not failed:
                try:
                    item = next(pending)
                except StopIteration:
                    return
                await operation(item)
        except BaseException:
            failed = True
            raise

    workers = [asyncio.create_task(worker()) for _ in range(concurrency)]
    try:
        await asyncio.gather(*workers)
    finally:
        await asyncio.gather(*workers, return_exceptions=True)


class PointMeasurement:
    def __init__(self, container, operation):
        if operation not in {"read", "create", "upsert", "replace", "delete", "patch"}:
            raise ValueError("Unsupported bounded point operation")
        self.container = container
        self.operation = operation
        self.label = OPERATIONS[operation]
        self.namespace = config.WORKLOAD_ITEM_NAMESPACE
        self.prefix = f"order-{self.namespace}-"
        self.items = []
        self.existing_ids = set()
        self.expected_items = 0
        self.delete_index = 0
        self.owns_namespace = False

    def _maintenance_client(self):
        return CosmosClient(
            config.COSMOS_URI, config.COSMOS_CREDENTIAL, _backend="core-python",
            preferred_locations=config.PREFERRED_LOCATIONS,
            excluded_locations=config.CLIENT_EXCLUDED_LOCATIONS,
        )

    @staticmethod
    def _container(client):
        return client.get_database_client(config.COSMOS_DATABASE).get_container_client(config.COSMOS_CONTAINER)

    def _owned_items(self, container):
        return container.query_items(
            "SELECT * FROM c WHERE STARTSWITH(c.id, @prefix)",
            parameters=[{"name": "@prefix", "value": self.prefix}],
            enable_cross_partition_query=True, **utils._extra_kwargs(config.REQUEST_EXCLUDED_LOCATIONS),
        )

    def _new_item(self):
        item = utils.create_random_item()
        if not item["id"].startswith(self.prefix):
            raise ValueError("Generated item does not belong to the measurement namespace")
        return item

    def _existing_item(self):
        item = self._new_item()
        item["id"] = random.choice(self.items)
        item["customerId"] = "customer-" + item["id"].removeprefix("order-")
        return item

    async def prepare(self, stop_event):
        if self.operation == "read":
            return
        selected = restoration_config(os.environ, (
            config.COSMOS_URI, config.COSMOS_DATABASE, config.COSMOS_CONTAINER,
        ))
        manifest = load_manifest(Path(config.WORKLOAD_MEASUREMENT_MANIFEST), selected)
        if manifest["namespace"] != self.namespace:
            raise ValueError("Measurement namespace differs from the saved ownership manifest")
        extra = utils._extra_kwargs(config.REQUEST_EXCLUDED_LOCATIONS)
        async with self._maintenance_client() as client:
            container = self._container(client)
            properties = await container.read(**extra)
            if (properties.get("partitionKey", {}).get("paths") != ["/id"]
                    or properties.get("defaultTtl") is not None):
                raise ValueError("Bounded writes require partition key /id and no container TTL")
            async for _ in self._owned_items(container):
                raise ValueError("Measurement namespace is not empty; recover it explicitly before a new run")
            self.owns_namespace = True
            count = (
                config.WORKLOAD_DELETE_ITEM_COUNT if self.operation == "delete"
                else config.MAX_ITEM_INDEX + 1 if self.operation in ("upsert", "replace", "patch")
                else 0
            )
            async def create_owned(_):
                if stop_event.is_set():
                    raise RuntimeError("Measurement interrupted during item preparation")
                item = self._new_item()
                item["quantity"] = 2
                await container.create_item(item, **extra)
                self.items.append(item["id"])
                self.existing_ids.add(item["id"])
                self.expected_items += 1
            await _run_maintenance(range(count), create_owned)

    async def run(self, stats):
        if self.operation == "read":
            await utils.read_item_concurrently(self.container, config.REQUEST_EXCLUDED_LOCATIONS, 1, stats)
            return
        extra = utils._extra_kwargs(config.REQUEST_EXCLUDED_LOCATIONS)
        creates_item = self.operation == "create"
        if self.operation == "create":
            call, args = self.container.create_item, (self._new_item(),)
        elif self.operation == "upsert":
            item = utils._get_upsert_item(self._existing_item)
            if not item["id"].startswith(self.prefix):
                raise ValueError("Upsert item does not belong to the measurement namespace")
            call, args = self.container.upsert_item, (item,)
            creates_item = item["id"] not in self.existing_ids
            extra.update(etag=None, match_condition=None)
        elif self.operation == "replace":
            item = self._existing_item()
            call, args = self.container.replace_item, (item["id"], item)
        elif self.operation == "patch":
            item_id = random.choice(self.items)
            call, args = self.container.patch_item, (item_id, item_id, utils._patch_operations())
        else:
            if self.delete_index >= len(self.items):
                raise RuntimeError("Prepared delete pool exhausted; measurement is incomplete")
            item_id = self.items[self.delete_index]
            self.delete_index += 1
            call, args = self.container.delete_item, (item_id, item_id)
        succeeded, _ = await utils._timed_call_async(
            self.label, stats, call, *args, _return_outcome=True, **extra,
        )
        if succeeded:
            if creates_item:
                self.expected_items += 1
            elif self.operation == "delete":
                self.expected_items -= 1
        return succeeded

    async def cleanup(self):
        if not self.owns_namespace:
            return
        extra = utils._extra_kwargs(config.REQUEST_EXCLUDED_LOCATIONS)
        async with self._maintenance_client() as client:
            container = self._container(client)
            items = [item async for item in self._owned_items(container)]
            complete_inventory = len(items) >= self.expected_items
            for item in items:
                validate_owned_order(item, self.namespace)
            # Validate the full inventory before deleting; never touch baseline orders.
            async def delete_owned(item):
                await container.delete_item(
                    item["id"], partition_key=item["id"], etag=item["_etag"],
                    match_condition=MatchConditions.IfNotModified, **extra,
                )
            await _run_maintenance(items, delete_owned)
            async for _ in self._owned_items(container):
                raise RuntimeError("Owned measurement items remain after cleanup")
            if not complete_inventory:
                raise RuntimeError("Cleanup inventory did not cover all acknowledged items; explicit recovery required")
