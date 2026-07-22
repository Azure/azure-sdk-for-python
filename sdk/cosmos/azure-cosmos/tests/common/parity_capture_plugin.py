# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# -------------------------------------------------------------------------
"""Pytest plugin that observes per-operation SDK calls and emits JSON
capture blocks for the legacy-folder parity reporter.

Activation
----------

The plugin is **dormant by default**. It activates only when the env
var ``COSMOS_PARITY_CAPTURE_OP`` is set to an operation name the
plugin knows how to patch (e.g. ``read_item``). When the env var is
unset the plugin's hooks return immediately and there is zero effect
on a normal ``pytest tests/`` run.

Two-track audit story
---------------------

The plugin powers track 1 of the two parity tracks the legacy-folder
workflow runs:

  * **Track 1 -- parity audit.** Run the *originals* once under
    ``COSMOS_PARITY_CAPTURE_OP=read_item`` (core-python column), then
    run the *legacy/ copies* once under the same env var (rust column,
    because the copies pin ``_backend="rust"``). The reporter parses
    both transcripts, pairs captures by ``(class name, method name)``,
    and renders the rich PARITY CALL block per test (REQUEST /
    CORE-PYTHON / RUST / DIFFS / VERDICT) using the same diff +
    verdict logic the in-process parity tests use.

  * **Track 2 -- legacy contract proof.** The same legacy/ copies are
    also runnable on rust without the env var; ``PASSED`` on every
    copy means no v4 customer contract regressed. The plugin is not
    involved in track 2.

How the patch works
-------------------

When active, the plugin replaces the unbound ``read_item`` method on
the relevant ``ContainerProxy`` class (sync at
``azure.cosmos.container.ContainerProxy`` and aio at
``azure.cosmos.aio._container.ContainerProxy``) with a wrapper that:

  1. Records the call's positional + keyword arguments.
  2. Invokes the original method (so the test sees the real return
     value / exception).
  3. Snapshots ``container.client_connection.last_response_headers``
     post-call.
  4. Reads the backend label from
     ``container.client_connection._backend`` (``None`` →
     ``core-python``, else → ``rust``).
  5. Emits one ``===PARITY-CAPTURE-START===\\n{json}\\n===PARITY-CAPTURE-END===``
     fenced block to ``sys.stdout``.
  6. Re-raises (if it raised) or returns the value (if it succeeded).

The patch is installed at ``pytest_sessionstart`` and reverted at
``pytest_sessionfinish``, so it has no effect outside the test
process.

Block format
------------

Single-line JSON wrapped in fixed sentinels. One-line because pytest
line-wraps multi-line stdout under some terminals; explicit sentinels
because the JSON body may itself contain ``}`` characters. The
reporter is the only consumer and uses the sentinels to slice.

Example block (whitespace added for readability — the real thing is
on one line)::

    ===PARITY-CAPTURE-START===
    {
      "nodeid": "tests/test_none_options.py::TestNoneOptions::test_container_read_item_none_options",
      "backend": "core-python",
      "surface": "sync",
      "op": "read_item",
      "ordinal": 0,
      "status": "ok",
      "request": {
        "args": ["a1b2c3..."],
        "kwargs": {"partition_key": "pk-value", ...}
      },
      "return_value": {"id": "...", "pk": "...", "value": 42, "_rid": "...", ...},
      "response_headers": {"x-ms-request-charge": "1.0", "etag": "\\"0x8DC...\\"", ...},
      "exception": null
    }
    ===PARITY-CAPTURE-END===

For an exception::

    ===PARITY-CAPTURE-START===
    {
      ...,
      "status": "raised",
      "return_value": null,
      "response_headers": {...},  // last_response_headers snapshot if available
      "exception": {
        "type": "CosmosResourceNotFoundError",
        "message": "(NotFound) ...",
        "status_code": 404,
        "sub_status": null
      }
    }
    ===PARITY-CAPTURE-END===
"""
from __future__ import annotations

import json
import inspect
import os
import re
import secrets
import sys
import threading
from typing import Any, Callable, Dict, List, Optional, Tuple

import pytest


# ---------------------------------------------------------------------------
# Plugin protocol version
# ---------------------------------------------------------------------------

#: Bumped whenever the JSON payload schema changes in a way the reporter
#: must know about (new required field, renamed field, semantics change
#: for an existing field). The reporter parses this and warns if the two
#: transcripts being diffed were produced by different plugin versions.
#: Schema history:
#:   v1 -- initial release (read_item op only).
#:   v2 -- (June 2026) added ``test_doc``; sentinels gained per-session
#:         random token (see ``SENTINEL_TOKEN`` below); ``response_headers``
#:         on the raised path is now guarded against the stale-headers
#:         carry-over bug (Bug 3 of the principal-engineer review).
#:   v3 -- records the Rust binding operation-count delta so backend selection
#:         cannot be mistaken for actual Rust execution.
PLUGIN_VERSION = "v3"


# ---------------------------------------------------------------------------
# Env-var gate
# ---------------------------------------------------------------------------

#: When this env var is set to a known operation name, the plugin
#: patches that operation's entry point on ``ContainerProxy`` and
#: emits a capture block per invocation. When unset, the plugin is
#: inert.
ENV_CAPTURE_OP = "COSMOS_PARITY_CAPTURE_OP"

#: Optional override for the backend label printed in the capture
#: block. Normally inferred from the live client; the override exists
#: so a custom test harness (or a CI runner spinning up a synthetic
#: client) can force a label without touching the SDK internals.
ENV_BACKEND_LABEL_OVERRIDE = "COSMOS_PARITY_CAPTURE_BACKEND_LABEL"

#: Optional override for the per-session sentinel token. Set by the
#: reporter's unit tests so they can predict the sentinel pattern in
#: synthetic transcripts. In normal use, a fresh 8-hex token is
#: generated at session start and embedded in the sentinels so any
#: stray ``===PARITY-CAPTURE-START===`` literal in test stdout cannot
#: confuse the reporter (Bug 6 of the principal-engineer review).
ENV_SENTINEL_TOKEN_OVERRIDE = "COSMOS_PARITY_CAPTURE_SENTINEL_TOKEN"

#: Per-session sentinel token. Built at first emit (or at
#: ``pytest_sessionstart`` time) so synthetic test runs can predict
#: it via the env override above. The reporter matches the sentinel
#: via the regex pattern in :data:`SENTINEL_REGEX` rather than a
#: literal string compare, so any well-formed token works.
SENTINEL_TOKEN: Optional[str] = None

#: Static sentinel prefix and suffix; the actual emitted sentinel is
#: ``{SENTINEL_PREFIX}{SENTINEL_TOKEN}{SENTINEL_SUFFIX_START}`` /
#: ``{SENTINEL_PREFIX}{SENTINEL_TOKEN}{SENTINEL_SUFFIX_END}``.
SENTINEL_PREFIX = "===PARITY-CAPTURE-"
SENTINEL_SUFFIX_START = "-START==="
SENTINEL_SUFFIX_END = "-END==="

_HEX_ADDR_RE = re.compile(r" at 0x[0-9a-fA-F]+")


def _ensure_sentinel_token() -> str:
    """Return the per-session sentinel token, building it on first use."""
    global SENTINEL_TOKEN  # noqa: PLW0603
    if SENTINEL_TOKEN is None:
        override = os.environ.get(ENV_SENTINEL_TOKEN_OVERRIDE)
        SENTINEL_TOKEN = override if override else secrets.token_hex(4)
    return SENTINEL_TOKEN


# ---------------------------------------------------------------------------
# Operation registry
# ---------------------------------------------------------------------------

# Each entry knows how to patch one operation's entry point on the
# sync + aio ``ContainerProxy``. Add a new entry when a new operation
# joins the parity audit.
#
# ``importer`` is a callable returning ``(module, class_name,
# method_name)`` for each surface. It's a callable (not a constant)
# so the SDK isn't imported at plugin-collection time -- only when
# the plugin actually activates.
_OP_REGISTRY: Dict[str, Dict[str, Callable[[], Tuple[Any, str, str]]]] = {}


def _register_op(op: str, *, sync: Callable[[], Tuple[Any, str, str]],
                 aio: Callable[[], Tuple[Any, str, str]]) -> None:
    _OP_REGISTRY[op] = {"sync": sync, "aio": aio}


# create_item ----------------------------------------------------------------

def _sync_create_item_target() -> Tuple[Any, str, str]:
    from azure.cosmos import container as _sync_container_mod
    return _sync_container_mod, "ContainerProxy", "create_item"


def _aio_create_item_target() -> Tuple[Any, str, str]:
    from azure.cosmos.aio import _container as _aio_container_mod
    return _aio_container_mod, "ContainerProxy", "create_item"


_register_op("create_item", sync=_sync_create_item_target, aio=_aio_create_item_target)


# create_database -------------------------------------------------------------

def _sync_create_database_target() -> Tuple[Any, str, str]:
    from azure.cosmos import cosmos_client as _sync_client_mod
    return _sync_client_mod, "CosmosClient", "create_database"


def _aio_create_database_target() -> Tuple[Any, str, str]:
    from azure.cosmos.aio import _cosmos_client as _aio_client_mod
    return _aio_client_mod, "CosmosClient", "create_database"


_register_op(
    "create_database",
    sync=_sync_create_database_target,
    aio=_aio_create_database_target,
)


# delete_item ----------------------------------------------------------------

def _sync_delete_item_target() -> Tuple[Any, str, str]:
    from azure.cosmos import container as _sync_container_mod
    return _sync_container_mod, "ContainerProxy", "delete_item"


def _aio_delete_item_target() -> Tuple[Any, str, str]:
    from azure.cosmos.aio import _container as _aio_container_mod
    return _aio_container_mod, "ContainerProxy", "delete_item"


_register_op("delete_item", sync=_sync_delete_item_target, aio=_aio_delete_item_target)


# read_item ------------------------------------------------------------------

def _sync_read_item_target() -> Tuple[Any, str, str]:
    from azure.cosmos import container as _sync_container_mod
    return _sync_container_mod, "ContainerProxy", "read_item"


def _aio_read_item_target() -> Tuple[Any, str, str]:
    from azure.cosmos.aio import _container as _aio_container_mod
    return _aio_container_mod, "ContainerProxy", "read_item"


_register_op("read_item", sync=_sync_read_item_target, aio=_aio_read_item_target)


# upsert_item ----------------------------------------------------------------

def _sync_upsert_item_target() -> Tuple[Any, str, str]:
    from azure.cosmos import container as _sync_container_mod
    return _sync_container_mod, "ContainerProxy", "upsert_item"


def _aio_upsert_item_target() -> Tuple[Any, str, str]:
    from azure.cosmos.aio import _container as _aio_container_mod
    return _aio_container_mod, "ContainerProxy", "upsert_item"


_register_op("upsert_item", sync=_sync_upsert_item_target, aio=_aio_upsert_item_target)


# replace_item ---------------------------------------------------------------

def _sync_replace_item_target() -> Tuple[Any, str, str]:
    from azure.cosmos import container as _sync_container_mod
    return _sync_container_mod, "ContainerProxy", "replace_item"


def _aio_replace_item_target() -> Tuple[Any, str, str]:
    from azure.cosmos.aio import _container as _aio_container_mod
    return _aio_container_mod, "ContainerProxy", "replace_item"


_register_op("replace_item", sync=_sync_replace_item_target, aio=_aio_replace_item_target)


# patch_item -----------------------------------------------------------------

def _sync_patch_item_target() -> Tuple[Any, str, str]:
    from azure.cosmos import container as _sync_container_mod
    return _sync_container_mod, "ContainerProxy", "patch_item"


def _aio_patch_item_target() -> Tuple[Any, str, str]:
    from azure.cosmos.aio import _container as _aio_container_mod
    return _aio_container_mod, "ContainerProxy", "patch_item"


_register_op("patch_item", sync=_sync_patch_item_target, aio=_aio_patch_item_target)


# query_items -----------------------------------------------------------------

def _sync_query_items_target() -> Tuple[Any, str, str]:
    from azure.cosmos import container as _sync_container_mod
    return _sync_container_mod, "ContainerProxy", "query_items"


def _aio_query_items_target() -> Tuple[Any, str, str]:
    from azure.cosmos.aio import _container as _aio_container_mod
    return _aio_container_mod, "ContainerProxy", "query_items"


_register_op("query_items", sync=_sync_query_items_target, aio=_aio_query_items_target)


# read_all_items --------------------------------------------------------------

def _sync_read_all_items_target() -> Tuple[Any, str, str]:
    from azure.cosmos import container as _sync_container_mod
    return _sync_container_mod, "ContainerProxy", "read_all_items"


def _aio_read_all_items_target() -> Tuple[Any, str, str]:
    from azure.cosmos.aio import _container as _aio_container_mod
    return _aio_container_mod, "ContainerProxy", "read_all_items"


_register_op("read_all_items", sync=_sync_read_all_items_target, aio=_aio_read_all_items_target)


# read_items ------------------------------------------------------------------
# Points the parity harness at the batched read-many call. read_items is a
# client-side orchestration built from point reads and per-partition queries, so
# the capture records the returned CosmosList (the merged result) for one call.
# Without this registration the harness could not intercept read_items, so the
# two-column read_items audit (core-python vs rust) could not be generated.

def _sync_read_items_target() -> Tuple[Any, str, str]:
    from azure.cosmos import container as _sync_container_mod
    return _sync_container_mod, "ContainerProxy", "read_items"


def _aio_read_items_target() -> Tuple[Any, str, str]:
    from azure.cosmos.aio import _container as _aio_container_mod
    return _aio_container_mod, "ContainerProxy", "read_items"


_register_op("read_items", sync=_sync_read_items_target, aio=_aio_read_items_target)


# read_feed_ranges -------------------------------------------------------------

def _sync_read_feed_ranges_target() -> Tuple[Any, str, str]:
    from azure.cosmos import container as _sync_container_mod
    return _sync_container_mod, "ContainerProxy", "read_feed_ranges"


def _aio_read_feed_ranges_target() -> Tuple[Any, str, str]:
    from azure.cosmos.aio import _container as _aio_container_mod
    return _aio_container_mod, "ContainerProxy", "read_feed_ranges"


_register_op("read_feed_ranges", sync=_sync_read_feed_ranges_target, aio=_aio_read_feed_ranges_target)


# feed_range_from_partition_key ------------------------------------------------

def _sync_feed_range_from_partition_key_target() -> Tuple[Any, str, str]:
    from azure.cosmos import container as _sync_container_mod
    return _sync_container_mod, "ContainerProxy", "feed_range_from_partition_key"


def _aio_feed_range_from_partition_key_target() -> Tuple[Any, str, str]:
    from azure.cosmos.aio import _container as _aio_container_mod
    return _aio_container_mod, "ContainerProxy", "feed_range_from_partition_key"


_register_op(
    "feed_range_from_partition_key",
    sync=_sync_feed_range_from_partition_key_target,
    aio=_aio_feed_range_from_partition_key_target,
)


# is_feed_range_subset ---------------------------------------------------------
# Points the parity harness at the customer call that checks whether one feed
# range sits entirely inside another. This is a pure client-side check (no
# network), so the capture records the returned yes/no rather than any wire
# response. Without this registration the harness would not know how to intercept
# the subset check, so the two-column is_feed_range_subset audit (core-python vs
# rust) could not be generated at all.

def _sync_is_feed_range_subset_target() -> Tuple[Any, str, str]:
    from azure.cosmos import container as _sync_container_mod
    return _sync_container_mod, "ContainerProxy", "is_feed_range_subset"


def _aio_is_feed_range_subset_target() -> Tuple[Any, str, str]:
    from azure.cosmos.aio import _container as _aio_container_mod
    return _aio_container_mod, "ContainerProxy", "is_feed_range_subset"


_register_op(
    "is_feed_range_subset",
    sync=_sync_is_feed_range_subset_target,
    aio=_aio_is_feed_range_subset_target,
)


# read_offer (get_throughput) --------------------------------------------------
# Points the parity harness at the customer call that reports provisioned RU/s
# and the autoscale ceiling. Without this registration the harness would not
# know how to intercept the throughput read, so the two-column read_offer audit
# (core-python vs rust) could not be generated at all.

def _sync_read_offer_target() -> Tuple[Any, str, str]:
    from azure.cosmos import container as _sync_container_mod
    return _sync_container_mod, "ContainerProxy", "get_throughput"


def _aio_read_offer_target() -> Tuple[Any, str, str]:
    from azure.cosmos.aio import _container as _aio_container_mod
    return _aio_container_mod, "ContainerProxy", "get_throughput"


_register_op("read_offer", sync=_sync_read_offer_target, aio=_aio_read_offer_target)


# replace_throughput --------------------------------------------------------
# Points the parity harness at the customer call that *changes* provisioned RU/s
# (the read-modify-write on the container's offer). Without this registration the
# harness would not know how to intercept the throughput change, so the two-column
# replace_throughput audit (core-python vs rust) could not be generated at all.

def _sync_replace_throughput_target() -> Tuple[Any, str, str]:
    from azure.cosmos import container as _sync_container_mod
    return _sync_container_mod, "ContainerProxy", "replace_throughput"


def _aio_replace_throughput_target() -> Tuple[Any, str, str]:
    from azure.cosmos.aio import _container as _aio_container_mod
    return _aio_container_mod, "ContainerProxy", "replace_throughput"


_register_op(
    "replace_throughput",
    sync=_sync_replace_throughput_target,
    aio=_aio_replace_throughput_target,
)


# ---------------------------------------------------------------------------
# Capture state (per pytest session)
# ---------------------------------------------------------------------------

class _CaptureState:
    """Mutable session-scoped state shared between hooks and patches."""

    def __init__(self) -> None:
        self.active_op: Optional[str] = None
        self.current_nodeid: Optional[str] = None
        # The first non-empty line of the currently-running test's
        # docstring, captured at ``pytest_runtest_protocol`` time and
        # re-attached to every emitted block. The reporter renders it
        # in the scoreboard's Description column. ``None`` when the
        # test method has no docstring (the reporter then falls back
        # to a humanised version of the method name).
        self.current_test_doc: Optional[str] = None
        self.ordinal_by_nodeid: Dict[str, int] = {}
        self._lock = threading.Lock()
        # ``patches`` is a list of (class, method_name,
        # original_callable, surface) tuples we use to revert at
        # session end.
        self.patches: List[Tuple[Any, str, Callable[..., Any], str]] = []

    def next_ordinal(self, nodeid: str) -> int:
        with self._lock:
            n = self.ordinal_by_nodeid.get(nodeid, 0)
            self.ordinal_by_nodeid[nodeid] = n + 1
            return n


_STATE = _CaptureState()


# ---------------------------------------------------------------------------
# Backend label inference
# ---------------------------------------------------------------------------

def _infer_backend_label(container_self: Any) -> str:
    """Read ``_backend`` off the live client_connection.

    ``None`` → ``"core-python"``, anything else → ``"rust"``. If the
    env-var override is set, it wins (used by integration tests of the
    plugin itself where there is no real SDK client involved)."""
    override = os.environ.get(ENV_BACKEND_LABEL_OVERRIDE)
    if override:
        return override
    try:
        cc = getattr(container_self, "client_connection", None)
        if cc is None:
            return "unknown"
        backend = getattr(cc, "_backend", None)
        return "rust" if backend is not None else "core-python"
    except Exception:  # pylint: disable=broad-except
        return "unknown"


# ---------------------------------------------------------------------------
# Serialisation helpers
# ---------------------------------------------------------------------------

def _coerce_json_safe(value: Any) -> Any:
    """Return a JSON-safe view of ``value``.

    Handles the types we actually capture: ``CosmosDict``,
    ``CaseInsensitiveDict``, sets, bytes, and anything else gets
    ``repr()``-folded so the block is never malformed.
    """
    if value is None or isinstance(value, (bool, int, float, str)):
        return value
    if isinstance(value, dict):
        return {str(k): _coerce_json_safe(v) for k, v in value.items()}
    # CaseInsensitiveDict + CosmosDict subclass dict but also implement
    # ``items()``; the dict branch above already handles them. Anything
    # ``Mapping``-like that does NOT subclass dict falls through to
    # the ``items``-or-iter walk below.
    if hasattr(value, "items") and callable(value.items):
        try:
            return {str(k): _coerce_json_safe(v) for k, v in value.items()}  # type: ignore[union-attr]
        except Exception:  # pylint: disable=broad-except
            pass
    if isinstance(value, (list, tuple, set, frozenset)):
        return [_coerce_json_safe(v) for v in value]
    if isinstance(value, bytes):
        try:
            return value.decode("utf-8")
        except UnicodeDecodeError:
            return value.decode("utf-8", errors="replace")
    # Object reprs often include memory addresses (``... at 0x...``), which
    # are process-local noise and create false parity diffs for iterator/pager
    # return values. Drop only the hex-address suffix, keep the type context.
    return _HEX_ADDR_RE.sub("", repr(value))


def _serialise_exception(exc: BaseException) -> Dict[str, Any]:
    return {
        "type": type(exc).__name__,
        "message": str(exc),
        "status_code": getattr(exc, "status_code", None),
        "sub_status": getattr(exc, "sub_status", None),
    }


def _snapshot_headers(container_self: Any) -> Dict[str, str]:
    try:
        cc = container_self.client_connection
        h = getattr(cc, "last_response_headers", None) or {}
        # Force into a plain dict of str→str so JSON serialisation is
        # deterministic and the reporter can rely on .lower() keys
        # later when bucketing into the three header populations.
        return {str(k): str(v) for k, v in h.items()}
    except Exception:  # pylint: disable=broad-except
        return {}


def _snapshot_result_headers(result: Any, container_self: Any) -> Dict[str, str]:
    getter = getattr(result, "get_response_headers", None)
    if callable(getter):
        try:
            return {str(k): str(v) for k, v in getter().items()}
        except Exception:  # pylint: disable=broad-except
            pass
    return _snapshot_headers(container_self)


def _rust_operation_count() -> Optional[int]:
    try:
        from azure.cosmos import _rust
        counter = getattr(_rust, "operation_count", None)
        if callable(counter):
            return int(counter())
    except (ImportError, TypeError, ValueError):
        pass
    return None


def _rust_fallback_count() -> int:
    from azure.cosmos._backend.base import rust_compatibility_fallback_count
    from azure.cosmos._query_rust_routing import rust_query_fallback_count
    return rust_compatibility_fallback_count() + rust_query_fallback_count()


def _execution_evidence(before: Optional[int], fallback_before: int) -> Dict[str, Any]:
    after = _rust_operation_count()
    fallback_delta = max(0, _rust_fallback_count() - fallback_before)
    if before is None or after is None:
        return {
            "executed_engine": "unknown",
            "rust_operation_delta": None,
            "rust_fallback_delta": fallback_delta,
        }
    delta = max(0, after - before)
    return {
        "executed_engine": (
            "rust"
            if delta > 0 and fallback_delta == 0
            else "core-python"
        ),
        "rust_operation_delta": delta,
        "rust_fallback_delta": fallback_delta,
    }


def _snapshot_headers_identity(container_self: Any) -> int:
    """Return the ``id()`` of the live ``last_response_headers`` dict.

    Used as a cheap "did the SDK swap in a new headers dict on this
    call?" check. The SDK's request path does
    ``headers = copy.copy(response.headers)`` and re-assigns
    ``client_connection.last_response_headers`` on every HTTP round-
    trip, so a fresh ``id()`` means a fresh response. Same ``id()``
    before and after means no HTTP call happened on this invocation
    -- e.g. the wrapper's input validation raised client-side and
    the headers we'd be about to snapshot are a stale carry-over
    from a previous call. (Bug 3 of the principal-engineer review.)
    """
    try:
        cc = container_self.client_connection
        h = getattr(cc, "last_response_headers", None)
        return id(h) if h is not None else 0
    except Exception:  # pylint: disable=broad-except
        return 0


def _emit_block(payload: Dict[str, Any]) -> None:
    """Write one capture block to stdout.

    Wrapped in a try/except so a serialisation bug in one capture
    cannot break the test under run.
    """
    token = _ensure_sentinel_token()
    sentinel_start = f"{SENTINEL_PREFIX}{token}{SENTINEL_SUFFIX_START}"
    sentinel_end = f"{SENTINEL_PREFIX}{token}{SENTINEL_SUFFIX_END}"
    try:
        line = json.dumps(payload, default=repr, ensure_ascii=False)
    except Exception as serialise_err:  # pylint: disable=broad-except
        # Fall back to a minimal block so the reporter still sees
        # *something* for this call -- better than silently dropping.
        line = json.dumps({
            "nodeid": payload.get("nodeid"),
            "backend": payload.get("backend"),
            "surface": payload.get("surface"),
            "op": payload.get("op"),
            "ordinal": payload.get("ordinal"),
            "plugin_version": PLUGIN_VERSION,
            "status": "capture-error",
            "exception": {
                "type": type(serialise_err).__name__,
                "message": str(serialise_err),
            },
        })
    sys.stdout.write("\n" + sentinel_start + "\n" + line + "\n" + sentinel_end + "\n")
    sys.stdout.flush()


# ---------------------------------------------------------------------------
# Wrapper builders
# ---------------------------------------------------------------------------
#
# Each wrapper monkey-patches **one** entry point per op (sync +
# aio). If a test ever routes through a *different* SDK callable
# that ultimately ends up doing the same work (e.g. an internal
# helper bypass, a different proxy method, or pagination internals
# that don't go back through the patched proxy), the capture will
# not fire. For ``read_item`` today every test goes through
# ``ContainerProxy.read_item`` directly so this is not a current
# issue; flag it as a known limitation for future ops with multiple
# entry points (Bug 9 of the principal-engineer review).
#
# Thread-safety note: ``_STATE`` is accessed without locking inside
# the wrappers. pytest-xdist multi-process is fine (each worker has
# its own process and its own ``_STATE``). Multi-threaded test runs
# inside a single pytest worker would race on
# ``_STATE.current_nodeid`` and the ordinal counter. The current
# cosmos test suite is single-threaded per worker so this is not a
# concrete issue (Bug 10 of the principal-engineer review).

def _build_sync_wrapper(op_name: str, surface: str,
                        original: Callable[..., Any]) -> Callable[..., Any]:
    def _wrapper(self_container, *args, **kwargs):
        nodeid = _STATE.current_nodeid
        if nodeid is None:
            return original(self_container, *args, **kwargs)
        ordinal = _STATE.next_ordinal(nodeid)
        backend = _infer_backend_label(self_container)
        rust_count_before = _rust_operation_count()
        fallback_count_before = _rust_fallback_count()
        test_doc = _STATE.current_test_doc
        request_view = {
            "args": [_coerce_json_safe(a) for a in args],
            "kwargs": {k: _coerce_json_safe(v) for k, v in kwargs.items()},
        }
        # Snapshot the headers-dict identity BEFORE the call so the
        # raised-path branch can tell whether this call actually
        # produced a fresh ``last_response_headers``. Without this
        # guard, a client-side validation error (e.g. negative
        # ``max_integrated_cache_staleness_in_ms``) leaves the
        # PREVIOUS call's headers in ``last_response_headers`` and
        # the audit doc misleadingly displays them as if they were
        # this test's. (Bug 3 of the principal-engineer review.)
        headers_id_before = _snapshot_headers_identity(self_container)
        try:
            result = original(self_container, *args, **kwargs)
            # ``read_feed_ranges`` is lazy on both sync and aio surfaces:
            # the method returns a pager, and the HTTP call happens when
            # the pager is drained. Capture at drain-time so request/headers
            # reflect the actual operation, not the pre-call account probe.
            if op_name == "read_feed_ranges" and hasattr(result, "__aiter__"):
                async def _captured_async_iterable():
                    try:
                        materialized = [item async for item in result]
                    except BaseException as iter_exc:  # pylint: disable=broad-except
                        headers_id_after = _snapshot_headers_identity(self_container)
                        if headers_id_after != headers_id_before and headers_id_after != 0:
                            response_headers = _snapshot_headers(self_container)
                        else:
                            response_headers = {}
                        payload = {
                            "nodeid": nodeid,
                            "backend": backend,
                            "surface": surface,
                            "op": op_name,
                            "ordinal": ordinal,
                            "plugin_version": PLUGIN_VERSION,
                            "status": "raised",
                            "test_doc": test_doc,
                            "request": request_view,
                            "return_value": None,
                            "response_headers": response_headers,
                            "exception": _serialise_exception(iter_exc),
                        }
                        payload.update(_execution_evidence(rust_count_before, fallback_count_before))
                        _emit_block(payload)
                        raise
                    payload = {
                        "nodeid": nodeid,
                        "backend": backend,
                        "surface": surface,
                        "op": op_name,
                        "ordinal": ordinal,
                        "plugin_version": PLUGIN_VERSION,
                        "status": "ok",
                        "test_doc": test_doc,
                        "request": request_view,
                        "return_value": _coerce_json_safe(materialized),
                        "response_headers": _snapshot_headers(self_container),
                        "exception": None,
                    }
                    payload.update(_execution_evidence(rust_count_before, fallback_count_before))
                    _emit_block(payload)
                    for item in materialized:
                        yield item

                return _captured_async_iterable()

            if op_name == "read_feed_ranges" and hasattr(result, "__iter__"):
                def _captured_sync_iterable():
                    try:
                        materialized = list(result)
                    except BaseException as iter_exc:  # pylint: disable=broad-except
                        headers_id_after = _snapshot_headers_identity(self_container)
                        if headers_id_after != headers_id_before and headers_id_after != 0:
                            response_headers = _snapshot_headers(self_container)
                        else:
                            response_headers = {}
                        payload = {
                            "nodeid": nodeid,
                            "backend": backend,
                            "surface": surface,
                            "op": op_name,
                            "ordinal": ordinal,
                            "plugin_version": PLUGIN_VERSION,
                            "status": "raised",
                            "test_doc": test_doc,
                            "request": request_view,
                            "return_value": None,
                            "response_headers": response_headers,
                            "exception": _serialise_exception(iter_exc),
                        }
                        payload.update(_execution_evidence(rust_count_before, fallback_count_before))
                        _emit_block(payload)
                        raise
                    payload = {
                        "nodeid": nodeid,
                        "backend": backend,
                        "surface": surface,
                        "op": op_name,
                        "ordinal": ordinal,
                        "plugin_version": PLUGIN_VERSION,
                        "status": "ok",
                        "test_doc": test_doc,
                        "request": request_view,
                        "return_value": _coerce_json_safe(materialized),
                        "response_headers": _snapshot_headers(self_container),
                        "exception": None,
                    }
                    payload.update(_execution_evidence(rust_count_before, fallback_count_before))
                    _emit_block(payload)
                    return iter(materialized)

                return _captured_sync_iterable()

            payload = {
                "nodeid": nodeid,
                "backend": backend,
                "surface": surface,
                "op": op_name,
                "ordinal": ordinal,
                "plugin_version": PLUGIN_VERSION,
                "status": "ok",
                "test_doc": test_doc,
                "request": request_view,
                "return_value": _coerce_json_safe(result),
                "response_headers": _snapshot_result_headers(result, self_container),
                "exception": None,
            }
            payload.update(_execution_evidence(rust_count_before, fallback_count_before))
            _emit_block(payload)
            return result
        except BaseException as exc:  # pylint: disable=broad-except
            headers_id_after = _snapshot_headers_identity(self_container)
            if headers_id_after != headers_id_before and headers_id_after != 0:
                response_headers = _snapshot_headers(self_container)
            else:
                # Client-side raise: no HTTP call happened, the SDK
                # did not refresh ``last_response_headers``, anything
                # there is a stale carry-over from a previous call.
                # Emit an empty dict so the audit doc doesn't display
                # stale headers (Bug 3).
                response_headers = {}
            payload = {
                "nodeid": nodeid,
                "backend": backend,
                "surface": surface,
                "op": op_name,
                "ordinal": ordinal,
                "plugin_version": PLUGIN_VERSION,
                "status": "raised",
                "test_doc": test_doc,
                "request": request_view,
                "return_value": None,
                "response_headers": response_headers,
                "exception": _serialise_exception(exc),
            }
            payload.update(_execution_evidence(rust_count_before, fallback_count_before))
            _emit_block(payload)
            raise

    _wrapper.__wrapped__ = original  # type: ignore[attr-defined]
    _wrapper.__name__ = getattr(original, "__name__", op_name)
    return _wrapper


def _build_aio_wrapper(op_name: str, surface: str,
                       original: Callable[..., Any]) -> Callable[..., Any]:
    async def _wrapper(self_container, *args, **kwargs):
        nodeid = _STATE.current_nodeid
        if nodeid is None:
            return await original(self_container, *args, **kwargs)
        ordinal = _STATE.next_ordinal(nodeid)
        backend = _infer_backend_label(self_container)
        rust_count_before = _rust_operation_count()
        fallback_count_before = _rust_fallback_count()
        test_doc = _STATE.current_test_doc
        request_view = {
            "args": [_coerce_json_safe(a) for a in args],
            "kwargs": {k: _coerce_json_safe(v) for k, v in kwargs.items()},
        }
        headers_id_before = _snapshot_headers_identity(self_container)
        try:
            result = await original(self_container, *args, **kwargs)
            payload = {
                "nodeid": nodeid,
                "backend": backend,
                "surface": surface,
                "op": op_name,
                "ordinal": ordinal,
                "plugin_version": PLUGIN_VERSION,
                "status": "ok",
                "test_doc": test_doc,
                "request": request_view,
                "return_value": _coerce_json_safe(result),
                "response_headers": _snapshot_result_headers(result, self_container),
                "exception": None,
            }
            payload.update(_execution_evidence(rust_count_before, fallback_count_before))
            _emit_block(payload)
            return result
        except BaseException as exc:  # pylint: disable=broad-except
            headers_id_after = _snapshot_headers_identity(self_container)
            if headers_id_after != headers_id_before and headers_id_after != 0:
                response_headers = _snapshot_headers(self_container)
            else:
                # See sync wrapper for the rationale; same logic.
                response_headers = {}
            payload = {
                "nodeid": nodeid,
                "backend": backend,
                "surface": surface,
                "op": op_name,
                "ordinal": ordinal,
                "plugin_version": PLUGIN_VERSION,
                "status": "raised",
                "test_doc": test_doc,
                "request": request_view,
                "return_value": None,
                "response_headers": response_headers,
                "exception": _serialise_exception(exc),
            }
            payload.update(_execution_evidence(rust_count_before, fallback_count_before))
            _emit_block(payload)
            raise

    _wrapper.__wrapped__ = original  # type: ignore[attr-defined]
    _wrapper.__name__ = getattr(original, "__name__", op_name)
    return _wrapper


# ---------------------------------------------------------------------------
# Patch install / revert
# ---------------------------------------------------------------------------

def _install_patches(op_name: str) -> None:
    """Patch sync + aio entry points for ``op_name``."""
    spec = _OP_REGISTRY.get(op_name)
    if spec is None:
        sys.stderr.write(
            "[parity_capture_plugin] unknown op {!r}; known ops: {}\n".format(
                op_name, sorted(_OP_REGISTRY.keys()),
            )
        )
        return
    for surface, importer in spec.items():
        try:
            module, class_name, method_name = importer()
            cls = getattr(module, class_name)
            original = getattr(cls, method_name)
        except Exception as import_err:  # pylint: disable=broad-except
            sys.stderr.write(
                "[parity_capture_plugin] failed to import {} target for op={}: {}\n"
                .format(surface, op_name, import_err)
            )
            continue
        if surface == "aio" and inspect.iscoroutinefunction(original):
            wrapper = _build_aio_wrapper(op_name, surface, original)
        else:
            wrapper = _build_sync_wrapper(op_name, surface, original)
        setattr(cls, method_name, wrapper)
        _STATE.patches.append((cls, method_name, original, surface))  # type: ignore[arg-type]


def _revert_patches() -> None:
    while _STATE.patches:
        cls, method_name, original, _surface = _STATE.patches.pop()
        try:
            setattr(cls, method_name, original)
        except Exception:  # pylint: disable=broad-except
            pass


# ---------------------------------------------------------------------------
# Pytest hooks
# ---------------------------------------------------------------------------

def pytest_sessionstart(session):  # pylint: disable=unused-argument
    op = os.environ.get(ENV_CAPTURE_OP, "").strip()
    if not op:
        return
    _STATE.active_op = op
    _install_patches(op)
    # NOTE: deliberately do not embed the literal SENTINEL strings
    # in this message -- the reporter's capture parser scans the
    # transcript for the sentinels, and a message containing them
    # would trip a spurious START + END match with non-JSON in
    # between. Describing them by name (rather than printing them
    # verbatim) keeps the transcript safe to feed to the reporter.
    sys.stdout.write(
        "\n[parity-capture-plugin] active for op={!r}; emitting one "
        "fenced JSON block per intercepted call (see "
        "tests/common/parity_capture_plugin.py for the block format).\n"
        .format(op)
    )


def pytest_sessionfinish(session, exitstatus):  # pylint: disable=unused-argument
    if _STATE.active_op is None:
        return
    _revert_patches()
    _STATE.active_op = None
    sys.stdout.write("\n[parity-capture-plugin] patches reverted.\n")


@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_protocol(item, nextitem):  # pylint: disable=unused-argument
    """Track which nodeid is currently running so emitted blocks
    carry the right ``nodeid``.

    Using ``pytest_runtest_protocol`` rather than ``runtest_setup``
    keeps the nodeid live across the setup → call → teardown phases,
    which matters for tests whose ``setUp`` itself triggers a capture
    (rare, but possible).

    Also stashes the first non-empty line of the test method's
    docstring (if any) so each emitted capture block can carry a
    human-readable description for the reporter's scoreboard. We do
    this once per test (not once per capture) so the description is
    stable across multi-call tests."""
    if _STATE.active_op is not None:
        _STATE.current_nodeid = item.nodeid
        _STATE.current_test_doc = _extract_test_doc(item)
    yield
    if _STATE.active_op is not None:
        _STATE.current_nodeid = None
        _STATE.current_test_doc = None


def _extract_test_doc(item: Any) -> Optional[str]:
    """Pull a one-line description from the test method's docstring.

    Strategy: take ``item.obj.__doc__`` (works for both function- and
    unittest-class-style tests under pytest), split on newline, and
    return the first stripped non-empty line. Returns ``None`` when
    the test has no docstring -- the reporter then falls back to a
    humanised version of the method name."""
    try:
        obj = getattr(item, "obj", None)
        doc = getattr(obj, "__doc__", None)
        if not doc:
            return None
        for line in doc.splitlines():
            stripped = line.strip()
            if stripped:
                return stripped
        return None
    except Exception:  # pylint: disable=broad-except
        return None
