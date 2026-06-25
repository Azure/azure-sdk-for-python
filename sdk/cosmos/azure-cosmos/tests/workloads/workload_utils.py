# The MIT License (MIT)
# Copyright (c) Microsoft Corporation. All rights reserved.
import asyncio
import logging
import os
import random
import time
import traceback
import uuid
from datetime import datetime
from logging.handlers import RotatingFileHandler
from aiohttp import ClientSession
from azure.monitor.opentelemetry import configure_azure_monitor
from azure.cosmos.exceptions import CosmosHttpResponseError

from custom_tcp_connector import ProxiedTCPConnector
from workload_configs import *

_NOISY_ERRORS = set([404, 409, 412])
_NOISY_SUB_STATUS_CODES = set([0, None])
_REQUIRED_ATTRIBUTES = [
    "resource_type",
    "verb",
    "operation_type",
    "status_code",
    "sub_status_code",
    "duration",
]


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _extra_kwargs(excluded_locations):
    """Build optional kwargs for excluded_locations."""
    return {"excluded_locations": excluded_locations} if excluded_locations else {}


def _record_error(stats, operation, error):
    """Extract Cosmos status codes and record the error in stats."""
    if not stats:
        return
    status_code = sub_status_code = None
    if isinstance(error, CosmosHttpResponseError):
        status_code = error.status_code
        sub_status_code = getattr(error, "sub_status", None)
    stats.record_error(
        operation, str(error), traceback.format_exc(), status_code, sub_status_code
    )


def _timed_call(op_name, stats, fn, *args, **kwargs):
    """Run *fn*, timing it and recording the result.

    On success it records the latency; on failure it records the error and
    returns None instead of raising, so one bad call cannot stop the rest
    of the batch the caller is looping over.
    """
    start = time.perf_counter_ns()
    try:
        result = fn(*args, **kwargs)
        if stats:
            stats.record(op_name, (time.perf_counter_ns() - start) / 1_000_000)
        return result
    except Exception as e:
        _record_error(stats, op_name, e)
        return None


async def _timed_call_async(op_name, stats, coroutine):
    """Await *coroutine*, timing it and recording the result.

    On success it records the latency; on failure it records the error and
    returns None instead of raising, so one bad call cannot stop the rest
    of the batch run together.
    """
    start = time.perf_counter_ns()
    try:
        result = await coroutine
        if stats:
            stats.record(op_name, (time.perf_counter_ns() - start) / 1_000_000)
        return result
    except Exception as e:
        _record_error(stats, op_name, e)
        return None


# ---------------------------------------------------------------------------
# Item generation
# ---------------------------------------------------------------------------

def get_user_agent(client_id):
    prefix = USER_AGENT_PREFIX + "-" if USER_AGENT_PREFIX else ""
    return prefix + str(client_id) + "-" + datetime.now().strftime("%Y%m%d-%H%M%S")


def get_existing_random_item():
    random_int = random.randint(0, NUMBER_OF_LOGICAL_PARTITIONS)
    item = create_random_item()
    item["id"] = "test-" + str(random_int)
    item["pk"] = "pk-" + str(random_int)
    return item


def create_random_item():
    paragraph1 = (
        "Lorem ipsum dolor sit amet, consectetur adipiscing elit. "
        "Sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. "
        "Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat. "
        f"Random ID: {uuid.uuid4()}"
    )
    paragraph2 = (
        "Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur. "
        "Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt mollit anim id est laborum. "
        f" Timestamp: {datetime.utcnow().isoformat()}"
    )
    return {
        "id": "test-" + str(uuid.uuid4()),
        "pk": "pk-" + str(uuid.uuid4()),
        "value": random.randint(1, 1000000000),
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "flag": random.choice([True, False]),
        "description": paragraph1 + "\n\n" + paragraph2,
    }


def _get_upsert_item():
    # 10 percent of the time, create a new item instead of updating an existing one
    return create_random_item() if random.random() < 0.1 else get_existing_random_item()


# ---------------------------------------------------------------------------
# Sync operations
# ---------------------------------------------------------------------------

def upsert_item(container, excluded_locations, num_upserts, stats=None):
    extra = _extra_kwargs(excluded_locations)
    for _ in range(num_upserts):
        item = _get_upsert_item()
        _timed_call(
            "UpsertItem", stats,
            container.upsert_item, item, etag=None, match_condition=None, **extra,
        )


def read_item(container, excluded_locations, num_reads, stats=None):
    extra = _extra_kwargs(excluded_locations)
    for _ in range(num_reads):
        item = get_existing_random_item()
        _timed_call(
            "ReadItem", stats,
            container.read_item, item["id"], item[PARTITION_KEY],
            etag=None, match_condition=None, **extra,
        )


def create_item(container, excluded_locations, num_creates, stats=None):
    extra = _extra_kwargs(excluded_locations)
    for _ in range(num_creates):
        item = create_random_item()
        _timed_call("CreateItem", stats, container.create_item, item, **extra)
        # Delete the new item again (not timed) so the container does not grow
        # without bound over a long run.
        try:
            container.delete_item(item["id"], item[PARTITION_KEY], **extra)
        except Exception:
            pass


def replace_item(container, excluded_locations, num_replaces, stats=None):
    extra = _extra_kwargs(excluded_locations)
    for _ in range(num_replaces):
        item = get_existing_random_item()
        _timed_call("ReplaceItem", stats, container.replace_item, item["id"], item, **extra)


def delete_item(container, excluded_locations, num_deletes, stats=None):
    extra = _extra_kwargs(excluded_locations)
    for _ in range(num_deletes):
        item = create_random_item()
        # Create the item first (not timed) so each delete has something to remove.
        try:
            container.create_item(item, **extra)
        except Exception:
            continue
        _timed_call("DeleteItem", stats, container.delete_item, item["id"], item[PARTITION_KEY], **extra)


def patch_item(container, excluded_locations, num_patches, stats=None):
    extra = _extra_kwargs(excluded_locations)
    for _ in range(num_patches):
        item = get_existing_random_item()
        operations = [{"op": "set", "path": "/value", "value": random.randint(1, 1000000000)}]
        _timed_call(
            "PatchItem", stats,
            container.patch_item, item["id"], item[PARTITION_KEY], operations, **extra,
        )


def query_items(container, excluded_locations, num_queries, stats=None):
    extra = _extra_kwargs(excluded_locations)
    for _ in range(num_queries):
        random_item = get_existing_random_item()

        def _do_query(ri=random_item):
            results = container.query_items(
                query="SELECT * FROM c where c.id=@id and c.pk=@pk",
                parameters=[
                    {"name": "@id", "value": ri["id"]},
                    {"name": "@pk", "value": ri["pk"]},
                ],
                partition_key=ri[PARTITION_KEY],
                **extra,
            )
            return [item for item in results]

        _timed_call("QueryItems", stats, _do_query)


# ---------------------------------------------------------------------------
# Async operations
# ---------------------------------------------------------------------------

async def upsert_item_concurrently(container, excluded_locations, num_upserts, stats=None):
    extra = _extra_kwargs(excluded_locations)
    tasks = []
    for _ in range(num_upserts):
        item = _get_upsert_item()
        awaitable = container.upsert_item(item, etag=None, match_condition=None, **extra)
        tasks.append(_timed_call_async("UpsertItem", stats, awaitable))
    await asyncio.gather(*tasks, return_exceptions=True)


async def read_item_concurrently(container, excluded_locations, num_reads, stats=None):
    extra = _extra_kwargs(excluded_locations)
    tasks = []
    for _ in range(num_reads):
        item = get_existing_random_item()
        awaitable = container.read_item(
            item["id"], item[PARTITION_KEY], etag=None, match_condition=None, **extra,
        )
        tasks.append(_timed_call_async("ReadItem", stats, awaitable))
    await asyncio.gather(*tasks, return_exceptions=True)


async def create_item_concurrently(container, excluded_locations, num_creates, stats=None):
    extra = _extra_kwargs(excluded_locations)
    created = []
    tasks = []
    for _ in range(num_creates):
        item = create_random_item()
        created.append(item)
        tasks.append(_timed_call_async("CreateItem", stats, container.create_item(item, **extra)))
    await asyncio.gather(*tasks, return_exceptions=True)
    # Delete the new items again (not timed) so the container does not grow
    # without bound over a long run.
    cleanup = [container.delete_item(it["id"], it[PARTITION_KEY], **extra) for it in created]
    await asyncio.gather(*cleanup, return_exceptions=True)


async def replace_item_concurrently(container, excluded_locations, num_replaces, stats=None):
    extra = _extra_kwargs(excluded_locations)
    tasks = []
    for _ in range(num_replaces):
        item = get_existing_random_item()
        tasks.append(
            _timed_call_async("ReplaceItem", stats, container.replace_item(item["id"], item, **extra))
        )
    await asyncio.gather(*tasks, return_exceptions=True)


async def delete_item_concurrently(container, excluded_locations, num_deletes, stats=None):
    extra = _extra_kwargs(excluded_locations)
    items = [create_random_item() for _ in range(num_deletes)]
    # Create the items first (not timed) so each delete has something to remove.
    setup = [container.create_item(it, **extra) for it in items]
    await asyncio.gather(*setup, return_exceptions=True)
    tasks = [
        _timed_call_async(
            "DeleteItem", stats, container.delete_item(it["id"], it[PARTITION_KEY], **extra)
        )
        for it in items
    ]
    await asyncio.gather(*tasks, return_exceptions=True)


async def patch_item_concurrently(container, excluded_locations, num_patches, stats=None):
    extra = _extra_kwargs(excluded_locations)
    tasks = []
    for _ in range(num_patches):
        item = get_existing_random_item()
        operations = [{"op": "set", "path": "/value", "value": random.randint(1, 1000000000)}]
        tasks.append(
            _timed_call_async(
                "PatchItem", stats,
                container.patch_item(item["id"], item[PARTITION_KEY], operations, **extra),
            )
        )
    await asyncio.gather(*tasks, return_exceptions=True)


async def query_items_concurrently(container, excluded_locations, num_queries, stats=None):
    extra = _extra_kwargs(excluded_locations)
    tasks = []
    for _ in range(num_queries):
        random_item = get_existing_random_item()

        async def _do_query(ri=random_item):
            results = container.query_items(
                query="SELECT * FROM c where c.id=@id and c.pk=@pk",
                parameters=[
                    {"name": "@id", "value": ri["id"]},
                    {"name": "@pk", "value": ri["pk"]},
                ],
                partition_key=ri[PARTITION_KEY],
                **extra,
            )
            return [item async for item in results]

        tasks.append(_timed_call_async("QueryItems", stats, _do_query()))
    await asyncio.gather(*tasks, return_exceptions=True)


# ---------------------------------------------------------------------------
# Session / logging
# ---------------------------------------------------------------------------

def create_custom_session():
    proxied_connector = ProxiedTCPConnector(
        proxy_host=COSMOS_PROXY_URI,
        proxy_port=5100,
        limit=100,
        limit_per_host=10,
        keepalive_timeout=30,
        enable_cleanup_closed=True,
    )
    return ClientSession(connector=proxied_connector)


def create_logger(file_name):
    logger = logging.getLogger()
    if APP_INSIGHTS_CONNECTION_STRING:
        configure_azure_monitor(
            logger_name="azure.cosmos",
            connection_string=APP_INSIGHTS_CONNECTION_STRING,
        )
    prefix = os.path.splitext(file_name)[0] + "-" + str(os.getpid())
    handler = RotatingFileHandler(
        "log-" + get_user_agent(prefix) + ".log",
        maxBytes=1024 * 1024 * 10,  # 10 mb
        backupCount=5,
    )
    logger.setLevel(LOG_LEVEL)
    workload_logger_filter = WorkloadLoggerFilter()
    handler.addFilter(workload_logger_filter)
    logger.addHandler(handler)
    return prefix, logger


def create_inner_logger(file_name="internal_logger_tues"):
    logger = logging.getLogger("internal_requests")
    prefix = os.path.splitext(file_name)[0] + "-" + str(os.getpid())
    handler = RotatingFileHandler(
        "log-" + file_name + ".log",
        maxBytes=1024 * 1024 * 10,  # 10 mb
        backupCount=5,
    )
    logger.setLevel(LOG_LEVEL)
    logger.addHandler(handler)


class WorkloadLoggerFilter(logging.Filter):
    def filter(self, record):
        if record.msg:
            if isinstance(record.msg, str):
                request_url_index = record.msg.find("Request URL:")
                response_status_index = record.msg.find("Response status:")
                if request_url_index == -1 and response_status_index == -1:
                    return True
        if all(hasattr(record, attr) for attr in _REQUIRED_ATTRIBUTES):
            if (
                record.resource_type == "databaseaccount"
                and record.verb == "GET"
                and record.operation_type == "Read"
            ):
                return True
            if record.status_code >= 400 and not (
                record.status_code in _NOISY_ERRORS
                and record.sub_status_code in _NOISY_SUB_STATUS_CODES
            ):
                return True
            if record.duration >= 1000:
                return True
        return False
