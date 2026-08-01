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

_NOISY_ERRORS = {404, 409, 412}
_NOISY_SUB_STATUS_CODES = {0, None}
_REQUIRED_ATTRIBUTES = [
    "resource_type",
    "verb",
    "operation_type",
    "status_code",
    "sub_status_code",
    "duration",
]

# Response header carrying the RU charge. The SDK sets it on every successful op
# on both backends, so reading it per call is the reliable RU source.
_REQUEST_CHARGE_HEADER = "x-ms-request-charge"

# Response header carrying the service-reported processing time in milliseconds.
# Both the core-python and the Rust backend surface it (the Rust binding copies
# the driver's server_duration_ms field to this wire name), so reading it per
# call gives a client-vs-server latency split that is comparable across backends.
_SERVER_DURATION_HEADER = "x-ms-request-duration-ms"

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _extra_kwargs(excluded_locations):
    """Build the optional per-call kwargs shared by every operation.

    Adds ``excluded_locations`` when set, and a ``timeout`` (seconds) when
    COSMOS_REQUEST_TIMEOUT > 0 so both runs use the same timeout.
    """
    extra = {}
    if excluded_locations:
        extra["excluded_locations"] = excluded_locations
    if REQUEST_TIMEOUT and REQUEST_TIMEOUT > 0:
        extra["timeout"] = REQUEST_TIMEOUT
    return extra


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


def _make_ru_hook(op_name, stats):
    """Build a ``response_hook`` that records *op_name*'s RU charge and the
    service-reported processing time into *stats*.

    The SDK calls the hook once per successful operation on both backends with the
    ``x-ms-request-charge`` header set, which makes RU per operation readable from
    the result row. When the response also carries ``x-ms-request-duration-ms``
    (both backends surface it), the hook records that into the parallel server
    histogram for the client-vs-server latency split. Returns ``None`` when there
    is no ``stats`` to record into.
    """
    if stats is None:
        return None

    def _hook(headers, _body):
        if not headers:
            return
        charge = headers.get(_REQUEST_CHARGE_HEADER)
        if charge is not None:
            try:
                stats.record_ru(op_name, float(charge))
            except (TypeError, ValueError):
                pass
        server_ms = headers.get(_SERVER_DURATION_HEADER)
        if server_ms is not None:
            try:
                stats.record_server_ms(op_name, float(server_ms))
            except (TypeError, ValueError):
                pass

    return _hook


def _with_ru_hook(op_name, stats, kwargs):
    """Inject the RU-capturing ``response_hook`` into *kwargs* if absent."""
    if stats is not None and "response_hook" not in kwargs:
        hook = _make_ru_hook(op_name, stats)
        if hook is not None:
            kwargs["response_hook"] = hook
    return kwargs


def _timed_call(op_name, stats, fn, *args, **kwargs):
    """Run *fn*, timing it and recording the result.

    On success it records the latency and RU charge; on failure it records the
    error and returns None instead of raising, so one bad call does not stop the
    batch the caller is looping over.
    """
    _with_ru_hook(op_name, stats, kwargs)
    start = time.perf_counter_ns()
    try:
        result = fn(*args, **kwargs)
        if stats:
            stats.record(op_name, (time.perf_counter_ns() - start) / 1_000_000)
        return result
    except Exception as e:
        _record_error(stats, op_name, e)
        return None


async def _timed_call_async(op_name, stats, fn, *args, **kwargs):
    """Await ``fn(*args, **kwargs)``, timing it and recording the result.

    Takes the callable plus its args (not a pre-built coroutine) so it can inject
    the RU-capturing ``response_hook``. On success it records the latency and RU
    charge; on failure it records the error and returns None instead of raising.
    """
    _with_ru_hook(op_name, stats, kwargs)
    start = time.perf_counter_ns()
    try:
        result = await fn(*args, **kwargs)
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
    random_int = random.randint(0, MAX_ITEM_INDEX)
    item = create_random_item()
    item["id"] = "test-" + str(random_int)
    item["pk"] = "pk-" + str(random_int)
    return item


def create_random_item():
    # "default" serializes to about 732 bytes of JSON (a single fixed flat shape).
    # "large" grows the body and adds nested objects/arrays (about 4,670 bytes,
    # roughly 6.4x the default) so a run can check whether conclusions hold for a
    # bigger, deeper document. Selected by WORKLOAD_DOC_PROFILE. Both sizes are
    # means over 200,000 generated documents; individual documents vary by a byte
    # or two because the random integer fields differ in digit count.
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
    item = {
        "id": "test-" + str(uuid.uuid4()),
        "pk": "pk-" + str(uuid.uuid4()),
        "value": random.randint(1, 1000000000),
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "flag": random.choice([True, False]),
        "description": paragraph1 + "\n\n" + paragraph2,
    }
    if WORKLOAD_DOC_PROFILE in ("large", "nested"):
        filler = (paragraph1 + " " + paragraph2) * 6
        item["description"] = filler
        item["details"] = {
            "attributes": {f"k{i}": i for i in range(20)},
            "tags": [f"tag-{i}" for i in range(20)],
            "nested": {"level2": {"level3": {"note": filler[:512]}}},
        }
        item["history"] = [
            {"seq": i, "v": random.randint(1, 1000000000)} for i in range(10)
        ]
    return item


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
        except Exception as e:
            # A failed cleanup delete leaves synthetic documents behind and can
            # contaminate later runs on shared containers, so surface it explicitly.
            _record_error(stats, "CreateCleanupDelete", e)


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

        def _do_query(ri=random_item, **call_kwargs):
            results = container.query_items(
                query="SELECT * FROM c where c.id=@id and c.pk=@pk",
                parameters=[
                    {"name": "@id", "value": ri["id"]},
                    {"name": "@pk", "value": ri["pk"]},
                ],
                partition_key=ri[PARTITION_KEY],
                **call_kwargs,
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
        tasks.append(_timed_call_async(
            "UpsertItem", stats,
            container.upsert_item, item, etag=None, match_condition=None, **extra,
        ))
    await asyncio.gather(*tasks, return_exceptions=True)


async def read_item_concurrently(container, excluded_locations, num_reads, stats=None):
    extra = _extra_kwargs(excluded_locations)
    tasks = []
    for _ in range(num_reads):
        item = get_existing_random_item()
        tasks.append(_timed_call_async(
            "ReadItem", stats,
            container.read_item, item["id"], item[PARTITION_KEY],
            etag=None, match_condition=None, **extra,
        ))
    await asyncio.gather(*tasks, return_exceptions=True)


async def create_item_concurrently(container, excluded_locations, num_creates, stats=None):
    extra = _extra_kwargs(excluded_locations)
    created = []
    tasks = []
    for _ in range(num_creates):
        item = create_random_item()
        created.append(item)
        tasks.append(_timed_call_async("CreateItem", stats, container.create_item, item, **extra))
    await asyncio.gather(*tasks, return_exceptions=True)
    # Delete the new items again (not timed) so the container does not grow
    # without bound over a long run.
    cleanup = [container.delete_item(it["id"], it[PARTITION_KEY], **extra) for it in created]
    cleanup_results = await asyncio.gather(*cleanup, return_exceptions=True)
    for err in cleanup_results:
        if isinstance(err, Exception):
            _record_error(stats, "CreateCleanupDelete", err)


async def replace_item_concurrently(container, excluded_locations, num_replaces, stats=None):
    extra = _extra_kwargs(excluded_locations)
    tasks = []
    for _ in range(num_replaces):
        item = get_existing_random_item()
        tasks.append(
            _timed_call_async("ReplaceItem", stats, container.replace_item, item["id"], item, **extra)
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
            "DeleteItem", stats, container.delete_item, it["id"], it[PARTITION_KEY], **extra
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
                container.patch_item, item["id"], item[PARTITION_KEY], operations, **extra,
            )
        )
    await asyncio.gather(*tasks, return_exceptions=True)


async def query_items_concurrently(container, excluded_locations, num_queries, stats=None):
    extra = _extra_kwargs(excluded_locations)
    tasks = []
    for _ in range(num_queries):
        random_item = get_existing_random_item()

        async def _do_query(ri=random_item, **call_kwargs):
            results = container.query_items(
                query="SELECT * FROM c where c.id=@id and c.pk=@pk",
                parameters=[
                    {"name": "@id", "value": ri["id"]},
                    {"name": "@pk", "value": ri["pk"]},
                ],
                partition_key=ri[PARTITION_KEY],
                **call_kwargs,
                **extra,
            )
            return [item async for item in results]

        tasks.append(_timed_call_async("QueryItems", stats, _do_query))
    await asyncio.gather(*tasks, return_exceptions=True)


# ---------------------------------------------------------------------------
# Blended (mixed) traffic — one process issues a weighted mix of operations
# ---------------------------------------------------------------------------

_ASYNC_OP_FUNCS = {
    "read": read_item_concurrently,
    "create": create_item_concurrently,
    "upsert": upsert_item_concurrently,
    "replace": replace_item_concurrently,
    "delete": delete_item_concurrently,
    "patch": patch_item_concurrently,
}


def _mix_counts(weights, concurrency):
    """Split ``concurrency`` op-slots across weighted ops (largest-remainder), so a
    wave's op proportions match ``weights`` as closely as an integer split allows.
    ``query`` is not part of a latency blend and is ignored.
    """
    w = {op: v for op, v in weights.items() if op in _ASYNC_OP_FUNCS and v > 0}
    total = sum(w.values())
    if total <= 0 or concurrency <= 0:
        return {}
    raw = {op: concurrency * v / total for op, v in w.items()}
    counts = {op: int(x) for op, x in raw.items()}
    rem = concurrency - sum(counts.values())
    for op, _frac in sorted(raw.items(), key=lambda kv: kv[1] - int(kv[1]), reverse=True):
        if rem <= 0:
            break
        counts[op] += 1
        rem -= 1
    return {op: c for op, c in counts.items() if c > 0}


async def mixed_wave_concurrently(container, excluded_locations, concurrency, weights, stats=None):
    """One blended wave: issue ``concurrency`` operations split across ``weights``,
    all in flight together, so a process models realistic mixed traffic instead of
    one operation type at a time. Each op keeps its own label, so per-op AND pooled
    (blended) percentiles are both available from the stored rows.
    """
    counts = _mix_counts(weights, concurrency)
    if not counts:
        return
    await asyncio.gather(
        *[_ASYNC_OP_FUNCS[op](container, excluded_locations, n, stats)
          for op, n in counts.items()],
        return_exceptions=True,
    )


# ---------------------------------------------------------------------------
# Event-loop lag monitor (async)
# ---------------------------------------------------------------------------

async def _loop_lag_monitor(stats, interval_s=0.05):
    """Sample event-loop scheduling delay and feed the worst per-window into stats.

    Sleeps ``interval_s`` then measures how much longer than that the wake-up took.
    That excess is time the loop thread was busy and could not service the timer on
    schedule. A large value means the loop is the bottleneck, not the SDK. Runs
    until cancelled; a no-op when there is no ``stats`` to record into.
    """
    if stats is None:
        return
    loop = asyncio.get_running_loop()
    try:
        while True:
            t0 = loop.time()
            await asyncio.sleep(interval_s)
            lag_ms = max(0.0, (loop.time() - t0 - interval_s) * 1000.0)
            stats.record_loop_lag(lag_ms)
    except asyncio.CancelledError:
        return


# ---------------------------------------------------------------------------
# Open-loop (constant-arrival) async driver
# ---------------------------------------------------------------------------
#
# The default driver is closed-loop: it fires a wave and waits for it before the
# next. When the system stalls it stops issuing requests, so the stall is under-
# sampled and the measured tail looks better than a real client would see. This
# driver issues at a fixed rate and times each operation from its intended start,
# so time spent waiting to be issued lands in the latency. Only the single-call
# point ops are supported; run create/delete closed-loop.

_OPEN_LOOP_SUPPORTED = ("read", "upsert", "replace", "patch")


def _build_open_loop_call(container, op, extra):
    """Return ``(op_label, fn, args, kwargs)`` for ONE operation of kind ``op``."""
    if op == "read":
        item = get_existing_random_item()
        return (
            "ReadItem", container.read_item,
            (item["id"], item[PARTITION_KEY]),
            dict(etag=None, match_condition=None, **extra),
        )
    if op == "upsert":
        item = _get_upsert_item()
        return (
            "UpsertItem", container.upsert_item, (item,),
            dict(etag=None, match_condition=None, **extra),
        )
    if op == "replace":
        item = get_existing_random_item()
        return ("ReplaceItem", container.replace_item, (item["id"], item), dict(extra))
    if op == "patch":
        item = get_existing_random_item()
        operations = [{"op": "set", "path": "/value", "value": random.randint(1, 1000000000)}]
        return (
            "PatchItem", container.patch_item,
            (item["id"], item[PARTITION_KEY], operations), dict(extra),
        )
    raise ValueError(
        "Open-loop mode (WORKLOAD_ARRIVAL_RATE>0) supports only "
        f"{_OPEN_LOOP_SUPPORTED}; got {op!r}. Run create/delete closed-loop."
    )


async def _open_loop_call_async(op_name, stats, scheduled_ns, fn, *args, **kwargs):
    """Like ``_timed_call_async`` but times from ``scheduled_ns`` (the intended
    arrival), so the recorded latency includes any time the op waited to be issued.
    """
    _with_ru_hook(op_name, stats, kwargs)
    try:
        result = await fn(*args, **kwargs)
        if stats:
            stats.record(op_name, (time.perf_counter_ns() - scheduled_ns) / 1_000_000)
        return result
    except Exception as e:
        _record_error(stats, op_name, e)
        return None


async def run_open_loop(container, excluded_locations, stats, ops, rate, max_inflight, stop_event=None):
    """Constant-arrival async driver. Fires ``ops`` round-robin at ``rate`` ops/sec
    without waiting for each wave, timing each from its intended start. Runs until
    ``stop_event`` is set or the task is cancelled; a semaphore bounds in-flight
    work so a stall cannot run the process out of memory. On stop it drains the
    in-flight tasks so their latencies are recorded and the client closes cleanly.
    """
    op_list = [o for o in sorted(ops) if o != "query"]  # query has no latency target
    if WORKLOAD_MIX:
        # Weighted round-robin: expand each op to an integer number of slots
        # proportional to its weight, so open-loop arrivals follow the blend.
        weighted = []
        for o, wv in sorted(WORKLOAD_MIX.items()):
            if o == "query":
                continue
            weighted.extend([o] * max(1, int(round(wv))))
        if weighted:
            op_list = weighted
    if not op_list:
        return
    for o in op_list:
        if o not in _OPEN_LOOP_SUPPORTED:
            raise ValueError(
                "Open-loop mode supports only "
                f"{_OPEN_LOOP_SUPPORTED}; got {o!r}. Run create/delete closed-loop."
            )
    extra = _extra_kwargs(excluded_locations)
    sem = asyncio.Semaphore(max_inflight)
    interval_ns = max(1, int(1_000_000_000 / rate))
    loop = asyncio.get_running_loop()
    start_ns = time.perf_counter_ns()
    seq = 0
    inflight = set()

    async def _one(op_label, scheduled_ns, fn, args, kwargs):
        try:
            await _open_loop_call_async(op_label, stats, scheduled_ns, fn, *args, **kwargs)
        finally:
            sem.release()

    try:
        while stop_event is None or not stop_event.is_set():
            scheduled_ns = start_ns + seq * interval_ns
            now_ns = time.perf_counter_ns()
            if scheduled_ns > now_ns:
                await asyncio.sleep((scheduled_ns - now_ns) / 1_000_000_000)
            elif now_ns - scheduled_ns > 5_000_000_000:
                # More than 5 s behind: rebase the schedule so the backlog cannot
                # grow forever. The lateness was already recorded as latency.
                start_ns = now_ns - seq * interval_ns
                scheduled_ns = now_ns
            op = op_list[seq % len(op_list)]
            op_label, fn, args, kwargs = _build_open_loop_call(container, op, extra)
            await sem.acquire()
            task = loop.create_task(_one(op_label, scheduled_ns, fn, args, kwargs))
            inflight.add(task)
            task.add_done_callback(inflight.discard)
            seq += 1
    except asyncio.CancelledError:
        raise
    finally:
        # Drain whatever is still in flight so their latencies are recorded and
        # nothing is left pending when the client closes.
        if inflight:
            await asyncio.gather(*inflight, return_exceptions=True)


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
