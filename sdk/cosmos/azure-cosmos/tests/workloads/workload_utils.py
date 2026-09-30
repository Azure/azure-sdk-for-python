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
    """Call *fn* synchronously with timing and error recording."""
    start = time.perf_counter_ns()
    try:
        result = fn(*args, **kwargs)
        if stats:
            stats.record(op_name, (time.perf_counter_ns() - start) / 1_000_000)
        return result
    except Exception as e:
        _record_error(stats, op_name, e)
        raise


async def _timed_call_async(op_name, stats, coroutine):
    """Await *coroutine* with timing and error recording."""
    start = time.perf_counter_ns()
    try:
        result = await coroutine
        if stats:
            stats.record(op_name, (time.perf_counter_ns() - start) / 1_000_000)
        return result
    except Exception as e:
        _record_error(stats, op_name, e)
        raise


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
    await asyncio.gather(*tasks)


async def read_item_concurrently(container, excluded_locations, num_reads, stats=None):
    extra = _extra_kwargs(excluded_locations)
    tasks = []
    for _ in range(num_reads):
        item = get_existing_random_item()
        awaitable = container.read_item(
            item["id"], item[PARTITION_KEY], etag=None, match_condition=None, **extra,
        )
        tasks.append(_timed_call_async("ReadItem", stats, awaitable))
    await asyncio.gather(*tasks)


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
    await asyncio.gather(*tasks)


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
