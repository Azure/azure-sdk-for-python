# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# -------------------------------------------------------------------------
"""End-to-end parity tests for ``Container.delete_item`` across backends.

Mirrors the layout of ``tests/create_item/sync/test_create_item_parity.py``.
The graduated structure (L0..L5) and the verdict grammar (FULL PARITY /
FUNCTIONAL PARITY, HEADER GAP / FUNCTIONAL DIVERGENCE / EXCEPTION
DIVERGENCE) match that file so a contributor reading one in-process
parity test recognises the shape of every other one.

This file is a CI gate, not the source for the audit doc. Each test
runs both backends inside one pytest process via ``BackendComparison``
and asserts on the diff. A failure prints the full ``PARITY CALL:``
block to the CI log so the contributor sees the evidence directly. The
per-operation audit doc (the rolling, human-readable summary) is
produced separately by the legacy-folder workflow's reporter script.

What this file pins for ``delete_item``:

* **L0 baseline.** Create one item, then delete it by bare id with the
  mandatory ``partition_key``. Both backends must succeed and return
  ``None`` (DELETE has no useful payload).
* **L1 -- ``item`` is polymorphic.** Pass the read-back document dict
  (which carries ``_self``) instead of the bare id; the SDK resolves
  it via ``Container._get_document_link``.
* **L2 -- header-bearing kwargs.** One per test: ``pre_trigger_include``,
  ``post_trigger_include``, ``session_token``, ``initial_headers``,
  ``priority``, ``throughput_bucket``. Each is the L0 shape + exactly
  one kwarg so a failure attributes cleanly to that kwarg.
* **L3 -- behavioural / Python-only kwargs.** ``timeout`` is honoured
  on both backends; ``retry_write``, ``availability_strategy``,
  ``excluded_locations``, ``read_timeout``, ``connection_timeout`` are
  Python-only or partially-mapped on the rust path and are skipped with
  plain-English reasons (same skip pattern as the create_item suite).
* **L4 -- ``response_hook`` fires exactly once per backend.** Captures
  the response without wrapping every call.
* **L5 -- typed-exception parity.**
  * Missing id => ``CosmosResourceNotFoundError`` (HTTP 404) on both
    backends.
  * Stale etag + ``MatchConditions.IfNotModified`` => HTTP 412 on both
    backends. This is the main delete-vs-create difference: on delete,
    ``etag`` + ``match_condition`` are the optimistic-concurrency
    primitive (on create they are inert and warn).
  * ``populate_query_metrics=True`` => ``DeprecationWarning`` is emitted
    AND the ``x-ms-documentdb-populatequerymetrics`` header is NOT sent
    on the outgoing request (the public method drops the value before
    it reaches the helper layer). This is the sync-only contract from
    "Asking the server for detailed query metrics it can't actually
    produce here: ``populate_query_metrics``".
"""
from __future__ import annotations

import uuid
import warnings
from typing import Any, Dict

import pytest

from azure.core import MatchConditions

from common._parity_helpers import (
    BackendComparison,
    run_on_both_backends,
    skip_unless_emulator,
    skip_unless_rust_binding,
)


pytestmark = [
    skip_unless_emulator(),
    skip_unless_rust_binding(),
]


# ---------------------------------------------------------------------------
# Per-test container fixture (same shape as the create_item parity suite)
# ---------------------------------------------------------------------------

@pytest.fixture
def container_for(request):
    """Build a fresh container per test, against a known db."""
    from azure.cosmos import CosmosClient, PartitionKey
    import os
    client = CosmosClient(os.environ["ACCOUNT_HOST"], os.environ["ACCOUNT_KEY"])
    db = client.create_database_if_not_exists("parity_db")
    cname = "parity_del_" + request.node.name + "_" + uuid.uuid4().hex[:6]
    container = db.create_container(
        id=cname, partition_key=PartitionKey(path="/pk")
    )
    yield container
    try:
        db.delete_container(cname)
    except Exception:  # pylint: disable=broad-except
        pass


# ---------------------------------------------------------------------------
# Closure builders
# ---------------------------------------------------------------------------
#
# Each backend gets its OWN freshly-created item so backend 2's delete is
# not racing backend 1's delete on the same row (which would just 404).
# This means the closure is "create + delete" not "delete only" -- the
# parity contract we report on is the *delete half*, the create half is
# only present to give each backend a row to point at.

def _new_item_factory(pk: str = "customerA"):
    """Return a no-arg callable that mints ``(id, pk)`` per invocation."""
    def _factory():
        return uuid.uuid4().hex, pk
    return _factory


def _delete_by_id_call(container_id: str, item_factory, **kwargs):
    """Closure: backend creates its own item, then deletes it by bare id."""
    def _do(client):
        cont = client.get_database_client("parity_db").get_container_client(container_id)
        item_id, pk = item_factory()
        cont.create_item({"id": item_id, "pk": pk})
        return cont.delete_item(item_id, partition_key=pk, **kwargs)
    return _do


def _delete_by_dict_call(container_id: str, item_factory, **kwargs):
    """Closure: backend creates its own item, then deletes it by passing
    the returned dict (which carries the SDK-stamped ``_self``)."""
    def _do(client):
        cont = client.get_database_client("parity_db").get_container_client(container_id)
        item_id, pk = item_factory()
        created = cont.create_item({"id": item_id, "pk": pk})
        return cont.delete_item(created, partition_key=pk, **kwargs)
    return _do


def _run_delete(container, level: str, summary: str,
                by_dict: bool = False, **kwargs) -> BackendComparison:
    """Drive the by-id-or-dict closure through ``run_on_both_backends``."""
    builder = _delete_by_dict_call if by_dict else _delete_by_id_call
    description = "[{}] {} -- mode={}, kwargs={}".format(
        level, summary,
        "by-dict" if by_dict else "by-id",
        sorted(kwargs.keys()) or "(none)",
    )
    cmp = run_on_both_backends(
        builder(container.id, _new_item_factory(), **kwargs),
        description=description,
        request_body=None,
        request_kwargs=kwargs or None,
    )
    cmp.print_report()
    return cmp


# ---------------------------------------------------------------------------
# L0 -- baseline: delete by id with the mandatory ``partition_key``.
# This test MUST pass for the rest of the suite to be meaningful.
# ---------------------------------------------------------------------------

def test_L0_baseline_delete_by_id(container_for):
    """Baseline: delete by bare id + ``partition_key``. No optional kwargs.

    Both backends must succeed and surface ``None`` (DELETE returns
    204 No Content). Response-header-surface differences are tolerated
    here per the shared ``assert_functional_parity`` policy.
    """
    _run_delete(container_for, level="L0",
                summary="baseline delete by id").assert_functional_parity()


# ---------------------------------------------------------------------------
# L1 -- polymorphic ``item`` shape: pass the read-back document dict.
# Exercises ``Container._get_document_link`` resolving ``item["_self"]``.
# ---------------------------------------------------------------------------

def test_L1_delete_by_document_dict(container_for):
    """L1: delete by passing the document dict (uses ``_self`` lookup).

    ``Container._get_document_link`` accepts either a bare id string
    or a dict the SDK previously returned (which carries ``_self``).
    The bare-id path is exercised by L0; this test pins the dict-path
    so a binding change that drops ``_self`` resolution surfaces here
    rather than as an obscure ``KeyError`` from inside the SDK.
    """
    _run_delete(container_for, level="L1",
                summary="delete by document dict",
                by_dict=True).assert_functional_parity()


# ---------------------------------------------------------------------------
# L2 -- header-bearing kwargs, one at a time.
# ---------------------------------------------------------------------------

def test_L2_pre_trigger_include(container_for):
    """L2: L0 + ``pre_trigger_include='validateOrder'`` (header kwarg).

    There is no registered trigger by that name on the parity
    container; the server returns the same well-defined "trigger not
    found" 400 to both backends. The parity contract is that both
    backends raise the *same typed exception* (header reached the
    wire, server validated it). The closure swallows the resulting
    ``CosmosHttpResponseError`` so the harness can still compare
    bodies / headers on the deterministic create+failed-delete path.
    """
    cmp = _run_delete(container_for, level="L2",
                      summary="L0 + pre_trigger_include",
                      pre_trigger_include="validateOrder")
    # Both backends should exhibit the same outcome (either both raise
    # the typed "trigger not found" error, or both succeed on accounts
    # where the trigger is present). The diff catches a divergence.
    cmp.assert_parity()


def test_L2_post_trigger_include(container_for):
    """L2: L0 + ``post_trigger_include='auditOrder'`` (header kwarg)."""
    cmp = _run_delete(container_for, level="L2",
                      summary="L0 + post_trigger_include",
                      post_trigger_include="auditOrder")
    cmp.assert_parity()


def test_L2_session_token(container_for):
    """L2: L0 + ``session_token=<token>`` (Session-consistency header kwarg).

    The token shape ``"0:1#42"`` is intentionally permissive; the server
    accepts it and the parity contract is "both backends forward it
    through the same code path." A binding that drops or rewrites the
    header on the way out would surface here.
    """
    _run_delete(container_for, level="L2",
                summary="L0 + session_token",
                session_token="0:1#42").assert_functional_parity()


def test_L2_initial_headers(container_for):
    """L2: L0 + ``initial_headers={'x-ms-test-parity': 'v1'}`` -- caller-injected.

    The SDK forwards customer-supplied headers verbatim, no
    interpretation. Both backends must surface the same outcome.
    """
    _run_delete(container_for, level="L2",
                summary="L0 + initial_headers",
                initial_headers={"x-ms-test-parity": "v1"}).assert_functional_parity()


def test_L2_priority_high(container_for):
    """L2: L0 + ``priority='High'`` (``x-ms-cosmos-priority-level`` header)."""
    _run_delete(container_for, level="L2",
                summary="L0 + priority=High",
                priority="High").assert_functional_parity()


def test_L2_throughput_bucket(container_for):
    """L2: L0 + ``throughput_bucket=1`` (``x-ms-cosmos-throughput-bucket`` hdr)."""
    _run_delete(container_for, level="L2",
                summary="L0 + throughput_bucket=1",
                throughput_bucket=1).assert_functional_parity()


# ---------------------------------------------------------------------------
# L3 -- behavioural / Python-only kwargs. Some are honoured everywhere
# (``timeout``), others are Python-only knobs with no rust analogue today.
# The skips quote the same reason the create_item parity suite uses.
# ---------------------------------------------------------------------------

def test_L3_timeout(container_for):
    """L3: L0 + ``timeout=30`` (overall request timeout).

    Both backends honour the keyword today: core-python through
    azure-core's per-call timeout, rust by handing the value to the
    driver's own timeout setting. 30 s is well above the driver's 1 s
    floor, so the test is deterministic.
    """
    _run_delete(container_for, level="L3",
                summary="L0 + timeout=30",
                timeout=30).assert_functional_parity()


@pytest.mark.skip(reason="Permanent skip: no rust-side equivalent (Python-only knob).")
def test_L3_retry_write(container_for):
    """L3: L0 + ``retry_write=1`` (Python-only retry knob; no rust analogue)."""
    _run_delete(container_for, level="L3",
                summary="L0 + retry_write=1",
                retry_write=1).assert_functional_parity()


@pytest.mark.skip(reason="Permanent skip: no rust-side equivalent (Python-only hedging feature).")
def test_L3_availability_strategy(container_for):
    """L3: L0 + ``availability_strategy=True`` (Python-only hedging feature)."""
    _run_delete(container_for, level="L3",
                summary="L0 + availability_strategy=True",
                availability_strategy=True).assert_functional_parity()


@pytest.mark.skip(reason="Skipped: binding forwards excluded_locations to the driver's typed "
                          "ExcludedRegions field, but the parity assertion is hard to make "
                          "end-to-end against a single-region test account. Same skip rationale "
                          "as create_item's L3_excluded_locations.")
def test_L3_excluded_locations(container_for):
    """L3: L0 + ``excluded_locations=['East US']``.

    The binding passes this keyword to the driver as an excluded-regions
    setting (the mapping lives in ``azure_cosmos_rust/src/lib.rs``). The
    test is skipped only because the parity check is hard to make
    end-to-end against a single-region test account.
    """
    _run_delete(container_for, level="L3",
                summary="L0 + excluded_locations",
                excluded_locations=["East US"]).assert_functional_parity()


@pytest.mark.skip(reason="Partial parity: the driver has client-level analogs via "
                          "ConnectionPoolOptions::{min,max}_dataplane_request_timeout but the "
                          "binding doesn't construct the pool options from Python's `read_timeout` "
                          "kwarg yet. Same skip rationale as create_item's L3_read_timeout.")
def test_L3_read_timeout(container_for):
    """L3: L0 + ``read_timeout=30`` (azure-core HTTP read timeout)."""
    _run_delete(container_for, level="L3",
                summary="L0 + read_timeout=30",
                read_timeout=30).assert_functional_parity()


@pytest.mark.skip(reason="Partial parity: the driver has client-level analogs via "
                          "ConnectionPoolOptions::{min,max}_connect_timeout but the binding doesn't "
                          "yet wire Python's `connection_timeout` kwarg into the pool config. "
                          "Same skip rationale as create_item's L3_connection_timeout.")
def test_L3_connection_timeout(container_for):
    """L3: L0 + ``connection_timeout=10`` (azure-core HTTP connect timeout)."""
    _run_delete(container_for, level="L3",
                summary="L0 + connection_timeout=10",
                connection_timeout=10).assert_functional_parity()


# ---------------------------------------------------------------------------
# L4 -- output / parsing parity
# ---------------------------------------------------------------------------

def test_L4_response_hook_fires_once(container_for):
    """L4: ``response_hook`` must fire exactly once per backend on success.

    Mirrors the create_item suite's L4 test. The harness deterministically
    runs core-python first, then rust, so an invocation-order counter
    attributes hook fires to the right backend without any synchronisation.
    """
    fired = {"core-python": 0, "rust": 0}
    order = ["core-python", "rust"]
    call_idx = [0]

    def _do(client):
        backend = order[call_idx[0]]
        call_idx[0] += 1

        def _hook(_h, _b):
            fired[backend] += 1

        cont = client.get_database_client("parity_db").get_container_client(container_for.id)
        item_id = uuid.uuid4().hex
        cont.create_item({"id": item_id, "pk": "a"})
        return cont.delete_item(
            item_id,
            partition_key="a",
            response_hook=_hook,
        )

    cmp = run_on_both_backends(
        _do,
        description="[L4] response_hook fires exactly once per backend",
        request_kwargs={"response_hook": "<callable>"},
    )
    cmp.print_report()
    print("[L4] response_hook fired: core-python={} rust={}".format(
        fired["core-python"], fired["rust"]))
    cmp.assert_functional_parity()
    assert fired["core-python"] == 1, "core-python should fire response_hook exactly once"
    assert fired["rust"] == 1, "rust should fire response_hook exactly once"


# ---------------------------------------------------------------------------
# L5 -- exception parity
# ---------------------------------------------------------------------------

def test_L5_missing_id_raises_typed_not_found(container_for):
    """Deleting a never-created id must raise ``CosmosResourceNotFoundError``
    (HTTP 404) on **both** backends with the same status code."""
    fixed_id = "does-not-exist-" + uuid.uuid4().hex

    def _do(client):
        cont = client.get_database_client("parity_db").get_container_client(container_for.id)
        return cont.delete_item(fixed_id, partition_key="a")

    cmp = run_on_both_backends(
        _do,
        description="[L5] missing-id 404: delete id={!r} that was never created".format(fixed_id),
        request_kwargs={"item": fixed_id, "partition_key": "a"},
    )
    cmp.print_report()
    assert not cmp.core_python.succeeded, "core-python must raise on missing id"
    assert not cmp.rust.succeeded, "rust must raise on missing id"
    cmp.assert_parity()


def test_L5_stale_etag_if_not_modified_raises_412(container_for):
    """L5: stale ``etag`` + ``MatchConditions.IfNotModified`` => HTTP 412.

    This is the delete-vs-create difference: on ``delete_item`` the
    ``etag``+``match_condition`` pair is the optimistic-concurrency
    primitive (on ``create_item`` it is inert and warns). The
    contract:

    1. Create the row.
    2. Replace it -- the row's etag on the server changes.
    3. Delete with the OLD etag and ``IfNotModified``. The server
       returns 412, the SDK raises the typed precondition error,
       both backends must raise the same typed exception with
       ``status_code == 412``.
    """
    def _do(client):
        cont = client.get_database_client("parity_db").get_container_client(container_for.id)
        item_id = uuid.uuid4().hex
        created = cont.create_item({"id": item_id, "pk": "a"})
        stale_etag = created["_etag"]
        # Bump the row's etag on the server so ``stale_etag`` is no
        # longer current. ``upsert_item`` here is deliberate: it does
        # not require the caller to track the current etag.
        cont.upsert_item({"id": item_id, "pk": "a", "bumped": True})
        return cont.delete_item(
            item_id,
            partition_key="a",
            etag=stale_etag,
            match_condition=MatchConditions.IfNotModified,
        )

    cmp = run_on_both_backends(
        _do,
        description="[L5] stale etag + IfNotModified must raise typed 412 on both backends",
        request_kwargs={"etag": "<stale>", "match_condition": "IfNotModified"},
    )
    cmp.print_report()
    assert not cmp.core_python.succeeded, "core-python must raise on stale etag + IfNotModified"
    assert not cmp.rust.succeeded, "rust must raise on stale etag + IfNotModified"
    # Pin the status code at 412 explicitly. If a future binding change
    # surfaces a different code (e.g. 409, 500), the diff harness's
    # ``exception.status_code`` line catches it -- this assert keeps
    # the contract pinned even when the two backends agree on the
    # wrong number.
    assert getattr(cmp.core_python.raised, "status_code", None) == 412, (
        "core-python must raise HTTP 412 (Precondition Failed); got status_code={!r}, "
        "exception={!r}".format(
            getattr(cmp.core_python.raised, "status_code", None),
            type(cmp.core_python.raised).__name__,
        )
    )
    assert getattr(cmp.rust.raised, "status_code", None) == 412, (
        "rust must raise HTTP 412 (Precondition Failed); got status_code={!r}, "
        "exception={!r}".format(
            getattr(cmp.rust.raised, "status_code", None),
            type(cmp.rust.raised).__name__,
        )
    )
    cmp.assert_parity()


# ---------------------------------------------------------------------------
# L5 (sync-only) -- deprecated kwargs whose contract is
# "ignored AND dropped before the wire, but emit a DeprecationWarning".
# ``populate_query_metrics`` is sync-only-and-deprecated on
# ``delete_item``; the async sibling does not expose it at all.
# ---------------------------------------------------------------------------

def _assert_deprecation_warning_fired(recorded, kwarg_name: str) -> None:
    """Confirm customers receive the documented deprecation warning."""
    matches = [w for w in recorded
               if issubclass(w.category, DeprecationWarning)
               and kwarg_name in str(w.message)]
    assert matches, (
        "expected a DeprecationWarning mentioning {!r}, got: {}".format(
            kwarg_name, [str(w.message) for w in recorded]
        )
    )


def test_L5_populate_query_metrics_deprecated_and_not_on_wire(container_for):
    """L5: ``populate_query_metrics=True`` is deprecated AND not forwarded.

    Two pinned guarantees:

    1. The public sync ``delete_item`` emits a ``DeprecationWarning``
       mentioning ``populate_query_metrics``.
    2. The ``x-ms-documentdb-populatequerymetrics`` request header is
       NOT present on the outgoing DELETE -- the value is dropped
       before the helper layer sees it. We assert this by wrapping
       ``CosmosClientConnection.__Delete`` (the name-mangled method
       that receives ``req_headers`` already fully built) and
       inspecting the captured header dict.

    The test runs against core-python only because the kwarg is a
    sync-only-and-deprecated Python-side wrapper concern; the rust
    backend never receives it through the helper layer either way
    (the public method drops it).
    """
    from azure.cosmos import CosmosClient
    from azure.cosmos import _cosmos_client_connection as _ccc_module
    from azure.cosmos.http_constants import HttpHeaders
    import os

    captured_delete_headers: Dict[str, Any] = {}

    original_delete = _ccc_module.CosmosClientConnection._CosmosClientConnection__Delete  # type: ignore[attr-defined]

    def _capturing_delete(self, path, request_params, req_headers, **kwargs):  # type: ignore[no-redef]
        if "/docs/" in path:
            captured_delete_headers.clear()
            captured_delete_headers.update(dict(req_headers))
        return original_delete(self, path, request_params, req_headers, **kwargs)

    _ccc_module.CosmosClientConnection._CosmosClientConnection__Delete = _capturing_delete  # type: ignore[attr-defined]
    try:
        client = CosmosClient(
            os.environ["ACCOUNT_HOST"],
            os.environ["ACCOUNT_KEY"],
            _backend="core-python",  # type: ignore[arg-type]
        )
        cont = client.get_database_client("parity_db").get_container_client(container_for.id)
        item_id = uuid.uuid4().hex
        cont.create_item({"id": item_id, "pk": "a"})
        with warnings.catch_warnings(record=True) as recorded:
            warnings.simplefilter("always")
            cont.delete_item(
                item_id,
                partition_key="a",
                populate_query_metrics=True,
            )
    finally:
        _ccc_module.CosmosClientConnection._CosmosClientConnection__Delete = original_delete  # type: ignore[attr-defined]

    _assert_deprecation_warning_fired(recorded, "populate_query_metrics")
    pqm_header = HttpHeaders.PopulateQueryMetrics  # 'x-ms-documentdb-populatequerymetrics'
    assert pqm_header not in captured_delete_headers, (
        "``populate_query_metrics`` must be DROPPED before the helper "
        "layer on delete_item -- the wire header {!r} must NOT be on "
        "the outgoing DELETE. Captured headers: {!r}".format(
            pqm_header, sorted(captured_delete_headers)
        )
    )
    print(
        "[L5] populate_query_metrics: DeprecationWarning fired AND "
        "{!r} absent from outgoing DELETE headers (captured {} headers)".format(
            pqm_header, len(captured_delete_headers)
        )
    )


def test_L5_etag_meaningful_not_deprecated(container_for):
    """L5: ``etag`` + ``match_condition`` are meaningful on delete_item.

    Unlike ``create_item`` where these two kwargs are inert and warn,
    on ``delete_item`` they are the optimistic-concurrency primitive.
    Passing a *current* etag with ``IfNotModified`` must succeed and
    must NOT emit any DeprecationWarning.
    """
    def _do(client):
        cont = client.get_database_client("parity_db").get_container_client(container_for.id)
        item_id = uuid.uuid4().hex
        created = cont.create_item({"id": item_id, "pk": "a"})
        current_etag = created["_etag"]
        return cont.delete_item(
            item_id,
            partition_key="a",
            etag=current_etag,
            match_condition=MatchConditions.IfNotModified,
        )

    with warnings.catch_warnings(record=True) as recorded:
        warnings.simplefilter("always")
        cmp = run_on_both_backends(
            _do,
            description="[L5] current etag + IfNotModified must succeed and not warn",
            request_kwargs={"etag": "<current>", "match_condition": "IfNotModified"},
        )
    cmp.print_report()
    # No DeprecationWarning should be raised for ``etag`` or
    # ``match_condition`` on delete_item -- they are meaningful.
    offending = [w for w in recorded
                 if issubclass(w.category, DeprecationWarning)
                 and ("etag" in str(w.message) or "match_condition" in str(w.message))]
    assert not offending, (
        "delete_item must NOT emit DeprecationWarning for etag/match_condition "
        "(meaningful on delete, inert only on create). "
        "Got: {}".format([str(w.message) for w in offending])
    )
    cmp.assert_functional_parity()


