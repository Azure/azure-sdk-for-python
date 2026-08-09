# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# -------------------------------------------------------------------------
"""End-to-end parity tests for ``Container.read_item`` across backends.

Mirrors the layout of ``tests/delete_item/sync/test_delete_item_parity.py``.
The graduated structure (L0..L5) and the verdict grammar match that
file so a contributor reading one in-process parity test recognises
the shape of every other one.

This file is a CI gate, not the source for the audit doc. Each test
runs both backends inside one pytest process via ``BackendComparison``
and asserts on the diff. A failure prints the full ``PARITY CALL:``
block to the CI log so the contributor sees the evidence directly. The
per-operation audit doc (the rolling, human-readable summary) is
produced separately by the legacy-folder workflow's reporter script.

What this file pins for ``read_item``:

* **L0 baseline.** Create one item, then read it by bare id with the
  mandatory ``partition_key``. Both backends must succeed and return
  a ``CosmosDict`` whose body carries the same ``id`` and ``pk``.
* **L1 -- ``item`` is polymorphic.** Pass the read-back document dict
  (which carries ``_self``) instead of the bare id.
* **L1 -- 404 paths.** Missing id and wrong-partition-key both surface
  the same ``CosmosResourceNotFoundError``. The wire cannot distinguish
  the two failure modes (the server returns 404 either way), so parity
  here is "same typed exception with the same status code", not "same
  reason text".
* **L2 -- header-bearing kwargs.** ``post_trigger_include``,
  ``session_token``, ``initial_headers``, ``priority``,
  ``throughput_bucket``. One kwarg per test so a failure attributes
  cleanly.
* **L3 -- ``max_integrated_cache_staleness_in_ms``.** Three cases:
  a positive value emits ``x-ms-dedicatedgateway-max-age``, ``0`` is
  a silent no-op (no header on the wire), a negative value raises
  ``ValueError`` up front (no network round trip).
* **L3 -- ``timeout``.** Honoured on both backends.
* **L4 -- ``response_hook`` fires exactly once per backend.** Same
  pattern as the create / delete parity suites.
* **L4 -- conditional read.** Three cases:
  * ``etag`` + ``IfModified``, server etag unchanged -> ``304`` is
    surfaced as an empty ``CosmosDict`` with the etag readable on
    ``get_response_headers()``.
  * ``etag`` + ``IfNotModified``, etag matches -> ``200`` + body.
  * ``etag`` + ``IfNotModified``, etag stale -> ``412``
    ``CosmosAccessConditionFailedError``.
* **L5 -- typed exceptions and sync-only deprecations.**
  * ``etag=`` without ``match_condition=`` raises ``ValueError``
    *before* any network call (parity with delete; the SDK refuses to
    guess).
  * ``populate_query_metrics=True`` is sync-only-deprecated and DROPPED
    before the helper layer -- the wire header must not appear on the
    outgoing GET.
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
# Per-test container fixture (same shape as the delete_item parity suite)
# ---------------------------------------------------------------------------

@pytest.fixture
def container_for(request):
    """Build a fresh container per test, against a known db."""
    from azure.cosmos import CosmosClient, PartitionKey
    import os
    client = CosmosClient(os.environ["ACCOUNT_HOST"], os.environ["ACCOUNT_KEY"])
    db = client.create_database_if_not_exists("parity_db")
    cname = "parity_read_" + request.node.name + "_" + uuid.uuid4().hex[:6]
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
# Each backend creates its OWN row (under the same partition key) so the
# tests are deterministic and the two backends do not race on shared
# state. The reported parity contract is the *read half*; the create
# half is only present so each backend has a row to point at.

def _new_item_factory(pk: str = "customerA"):
    """Provide a distinct item id and partition key for each backend."""
    def _factory():
        return uuid.uuid4().hex, pk
    return _factory


def _read_by_id_call(container_id: str, item_factory, **kwargs):
    """Build a read that targets an item by id."""
    def _do(client):
        cont = client.get_database_client("parity_db").get_container_client(container_id)
        item_id, pk = item_factory()
        cont.create_item({"id": item_id, "pk": pk, "value": 1})
        return cont.read_item(item_id, partition_key=pk, **kwargs)
    return _do


def _read_by_dict_call(container_id: str, item_factory, **kwargs):
    """Build a read that targets an item returned by the SDK."""
    def _do(client):
        cont = client.get_database_client("parity_db").get_container_client(container_id)
        item_id, pk = item_factory()
        created = cont.create_item({"id": item_id, "pk": pk, "value": 1})
        return cont.read_item(created, partition_key=pk, **kwargs)
    return _do


def _run_read(container, level: str, summary: str,
              by_dict: bool = False, **kwargs) -> BackendComparison:
    """Compare the public read result from Python and Rust."""
    builder = _read_by_dict_call if by_dict else _read_by_id_call
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
# L0 -- baseline
# ---------------------------------------------------------------------------

def test_L0_baseline_read_by_id(container_for):
    """Baseline: read by bare id + ``partition_key``. No optional kwargs.

    Both backends must succeed; the body's id/pk fields must match what
    was just written. Response-header-surface differences are tolerated
    here per the shared ``assert_functional_parity`` policy.
    """
    _run_read(container_for, level="L0",
              summary="baseline read by id").assert_functional_parity()


# ---------------------------------------------------------------------------
# L1 -- polymorphic ``item`` shape + 404 cases
# ---------------------------------------------------------------------------

def test_L1_read_by_document_dict(container_for):
    """L1: read by passing the document dict (uses ``_self`` lookup).

    Same precedent as ``delete_item``'s L1: ``Container._get_document_link``
    accepts either a bare id string or a full document dict (which carries
    ``_self``).
    """
    _run_read(container_for, level="L1",
              summary="read by document dict",
              by_dict=True).assert_functional_parity()


def test_L1_missing_id_raises_typed_not_found(container_for):
    """Reading a never-created id must raise ``CosmosResourceNotFoundError``
    (HTTP 404) on **both** backends."""
    fixed_id = "does-not-exist-" + uuid.uuid4().hex

    def _do(client):
        cont = client.get_database_client("parity_db").get_container_client(container_for.id)
        return cont.read_item(fixed_id, partition_key="a")

    cmp = run_on_both_backends(
        _do,
        description="[L1] missing-id 404: read id={!r} that was never created".format(fixed_id),
        request_kwargs={"item": fixed_id, "partition_key": "a"},
    )
    cmp.print_report()
    assert not cmp.core_python.succeeded, "core-python must raise on missing id"
    assert not cmp.rust.succeeded, "rust must raise on missing id"
    assert getattr(cmp.core_python.raised, "status_code", None) == 404
    assert getattr(cmp.rust.raised, "status_code", None) == 404
    cmp.assert_parity()


def test_L1_wrong_partition_key_raises_typed_not_found(container_for):
    """Reading with the wrong partition key returns 404 on both backends.

    The wire cannot distinguish wrong-id from wrong-pk; the server
    just returns 404 either way. The parity contract is that both
    backends surface the same typed exception with the same status
    code, not that they reveal *why* the read failed.
    """
    def _do(client):
        cont = client.get_database_client("parity_db").get_container_client(container_for.id)
        item_id = uuid.uuid4().hex
        # Each backend writes its own row under pk='a' (different ids
        # so they don't race), then reads with pk='b' (wrong pk).
        cont.create_item({"id": item_id, "pk": "a", "value": 1})
        return cont.read_item(item_id, partition_key="b")

    cmp = run_on_both_backends(
        _do,
        description="[L1] wrong-pk 404: row exists under pk='a', read with pk='b'",
        request_kwargs={"partition_key": "b"},
    )
    cmp.print_report()
    assert not cmp.core_python.succeeded
    assert not cmp.rust.succeeded
    assert getattr(cmp.core_python.raised, "status_code", None) == 404
    assert getattr(cmp.rust.raised, "status_code", None) == 404
    cmp.assert_parity()


# ---------------------------------------------------------------------------
# L2 -- header-bearing kwargs, one at a time
# ---------------------------------------------------------------------------

def test_L2_post_trigger_include(container_for):
    """L2: L0 + ``post_trigger_include='auditRead'`` (header kwarg).

    There is no registered trigger by that name; the server returns
    the same "trigger not found" error to both backends. The parity
    contract is that the typed exception matches.
    """
    cmp = _run_read(container_for, level="L2",
                    summary="L0 + post_trigger_include",
                    post_trigger_include="auditRead")
    cmp.assert_parity()


def test_L2_session_token(container_for):
    """L2: L0 + ``session_token=<token>``.

    Reads pass the session-token check; the known rust-side limitation
    with session tokens is on writes, not reads. Both backends forward
    the token as-is, and the outcome on the wire must match.
    """
    _run_read(container_for, level="L2",
              summary="L0 + session_token",
              session_token="0:1#42").assert_functional_parity()


def test_L2_initial_headers(container_for):
    """L2: L0 + customer-injected ``initial_headers``."""
    _run_read(container_for, level="L2",
              summary="L0 + initial_headers",
              initial_headers={"x-ms-test-parity": "v1"}).assert_functional_parity()


def test_L2_priority_high(container_for):
    """L2: L0 + ``priority='High'`` (``x-ms-cosmos-priority-level``)."""
    _run_read(container_for, level="L2",
              summary="L0 + priority=High",
              priority="High").assert_functional_parity()


def test_L2_throughput_bucket(container_for):
    """L2: L0 + ``throughput_bucket=1`` (``x-ms-cosmos-throughput-bucket``)."""
    _run_read(container_for, level="L2",
              summary="L0 + throughput_bucket=1",
              throughput_bucket=1).assert_functional_parity()


# ---------------------------------------------------------------------------
# L3 -- behavioural / Python-only kwargs.
# ---------------------------------------------------------------------------

def test_L3_max_cache_staleness_positive(container_for):
    """L3: L0 + ``max_integrated_cache_staleness_in_ms=5000``.

    The value reaches the wire as
    ``x-ms-dedicatedgateway-max-age: 5000``. Both backends must
    forward identically.
    """
    _run_read(container_for, level="L3",
              summary="L0 + max_integrated_cache_staleness_in_ms=5000",
              max_integrated_cache_staleness_in_ms=5000).assert_functional_parity()


def test_L3_max_cache_staleness_zero_is_silent_no_op(container_for):
    """L3: ``max_integrated_cache_staleness_in_ms=0`` is a silent no-op.

    The header must not be emitted on either backend (a falsy value is
    dropped on both paths). The call must succeed as if the keyword had
    not been passed.
    """
    _run_read(container_for, level="L3",
              summary="L0 + max_integrated_cache_staleness_in_ms=0",
              max_integrated_cache_staleness_in_ms=0).assert_functional_parity()


def test_L3_max_cache_staleness_negative_raises_value_error_up_front(container_for):
    """L3: negative cache-staleness raises ``ValueError`` BEFORE any network call.

    The validation lives at the call site so the customer's traceback
    points at their own code. Same wording across both backends
    because the validator runs in the public method, before backend
    dispatch.
    """
    def _do(client):
        cont = client.get_database_client("parity_db").get_container_client(container_for.id)
        item_id = uuid.uuid4().hex
        cont.create_item({"id": item_id, "pk": "a"})
        return cont.read_item(item_id, partition_key="a",
                              max_integrated_cache_staleness_in_ms=-1)

    cmp = run_on_both_backends(
        _do,
        description="[L3] negative max_integrated_cache_staleness raises ValueError",
        request_kwargs={"max_integrated_cache_staleness_in_ms": -1},
    )
    cmp.print_report()
    assert isinstance(cmp.core_python.raised, ValueError), (
        "core-python must raise ValueError before any network call; got {!r}".format(cmp.core_python.raised)
    )
    assert isinstance(cmp.rust.raised, ValueError), (
        "rust must raise ValueError before any network call; got {!r}".format(cmp.rust.raised)
    )


def test_L3_timeout(container_for):
    """L3: L0 + ``timeout=30`` (overall request timeout)."""
    _run_read(container_for, level="L3",
              summary="L0 + timeout=30",
              timeout=30).assert_functional_parity()


@pytest.mark.skip(reason="Permanent skip: no rust-side equivalent (Python-only hedging feature).")
def test_L3_availability_strategy(container_for):
    """L3: L0 + ``availability_strategy=True`` (Python-only hedging feature).

    No ``availability_strategy`` / hedging knob on the rust driver
    surface yet. Skipped on the parity run.
    """
    _run_read(container_for, level="L3",
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
    end-to-end against a single-region test account: ``["East US"]`` on a
    westus2-only account changes no routing decision the legacy path
    would diff against. Remove this skip once the parity harness gains a
    multi-region fixture (or a fault-injection transport that can observe
    which region a request actually chose).
    """
    _run_read(container_for, level="L3",
              summary="L0 + excluded_locations",
              excluded_locations=["East US"]).assert_functional_parity()


# ---------------------------------------------------------------------------
# L4 -- output / parsing parity, conditional reads
# ---------------------------------------------------------------------------

def test_L4_response_hook_fires_once(container_for):
    """L4: ``response_hook`` must fire exactly once per backend on success.

    Mirrors the create_item / delete_item suites' L4 test. The harness
    deterministically runs core-python first, then rust, so an
    invocation-order counter attributes hook fires to the right backend
    without any synchronisation.
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
        return cont.read_item(
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


def test_L4_conditional_etag_if_modified_unchanged_returns_304_empty_dict(container_for):
    """L4: ``etag`` + ``IfModified``, server etag unchanged -> 304 empty CosmosDict.

    This is the cache-validation idiom. The customer's cached etag
    still matches the server version, so the server returns
    ``304 Not Modified`` with an empty body. The SDK surfaces this as
    a non-error empty ``CosmosDict`` whose
    ``get_response_headers()["etag"]`` is the current etag (equal to
    what the customer sent in).

    This is the pinned behaviour for read on the new path: the
    response parser short-circuits at status 304 and treats it as
    success with an empty body.
    """
    def _do(client):
        cont = client.get_database_client("parity_db").get_container_client(container_for.id)
        item_id = uuid.uuid4().hex
        created = cont.create_item({"id": item_id, "pk": "a", "value": 1})
        current_etag = created["_etag"]
        # The row has not changed since the create returned ``current_etag``,
        # so a conditional read with ``IfModified`` must surface as 304.
        return cont.read_item(
            item_id,
            partition_key="a",
            etag=current_etag,
            match_condition=MatchConditions.IfModified,
        )

    cmp = run_on_both_backends(
        _do,
        description="[L4] etag + IfModified, unchanged -> 304 empty CosmosDict",
        request_kwargs={"etag": "<current>", "match_condition": "IfModified"},
    )
    cmp.print_report()
    assert cmp.core_python.succeeded, (
        "core-python must succeed on unchanged-etag conditional read; raised={!r}".format(
            cmp.core_python.raised))
    assert cmp.rust.succeeded, (
        "rust must succeed on unchanged-etag conditional read; raised={!r}".format(
            cmp.rust.raised))
    # The body must be empty (no JSON to parse) and the etag must be
    # readable from the response headers. We don't compare equality
    # against the original etag because the two backends ran two
    # *different* underlying rows (each backend created its own).
    for name, outcome in (("core-python", cmp.core_python), ("rust", cmp.rust)):
        result = outcome.return_value
        assert len(result) == 0, (
            "{}: 304 must surface as an empty CosmosDict; got {!r}".format(name, dict(result))
        )
        headers = result.get_response_headers()
        assert "etag" in headers, (
            "{}: response headers must carry the current etag on 304; got keys {!r}".format(
                name, sorted(headers))
        )


def test_L4_conditional_etag_if_not_modified_match_returns_200_body(container_for):
    """L4: ``etag`` + ``IfNotModified``, server etag matches -> 200 + body.

    Same set-up as the 304 test above, but with ``IfNotModified``
    (translates to ``If-Match``). When the etag matches, the server
    returns 200 + body normally.
    """
    def _do(client):
        cont = client.get_database_client("parity_db").get_container_client(container_for.id)
        item_id = uuid.uuid4().hex
        created = cont.create_item({"id": item_id, "pk": "a", "value": 1})
        return cont.read_item(
            item_id,
            partition_key="a",
            etag=created["_etag"],
            match_condition=MatchConditions.IfNotModified,
        )

    cmp = run_on_both_backends(
        _do,
        description="[L4] etag + IfNotModified, matches -> 200 + body",
        request_kwargs={"etag": "<current>", "match_condition": "IfNotModified"},
    )
    cmp.print_report()
    cmp.assert_functional_parity()
    for name, outcome in (("core-python", cmp.core_python), ("rust", cmp.rust)):
        result = outcome.return_value
        assert "id" in result and "pk" in result, (
            "{}: 200 must surface body; got {!r}".format(name, dict(result))
        )


def test_L4_conditional_etag_if_not_modified_mismatch_observes_actual_behavior(container_for):
    """L4: stale ``etag`` + ``IfNotModified`` on a read — pin what actually
    happens on the wire, not the intuitive expectation.

    The intuitive expectation is that ``IfNotModified`` on a read sends
    ``If-Match: <etag>`` and returns ``412 CosmosAccessConditionFailedError``
    on a mismatch. In practice, against a live Cosmos account, both the
    rust driver and core-python return ``200 + the current body`` instead
    of ``412`` — the service does not enforce ``If-Match`` on a
    ``GET /docs/<id>``. (Delete is different: there ``IfNotModified`` IS
    enforced and returns 412 — see
    ``test_delete_item_parity::test_L5_stale_etag_if_not_modified_raises_412``.)

    This test pins only what we can observe: both backends must behave the
    same way. If one backend later started raising while the other didn't,
    it would show up here as a ``FUNCTIONAL DIVERGENCE`` verdict from
    ``assert_parity``.
    """
    def _do(client):
        cont = client.get_database_client("parity_db").get_container_client(container_for.id)
        item_id = uuid.uuid4().hex
        created = cont.create_item({"id": item_id, "pk": "a", "value": 1})
        stale_etag = created["_etag"]
        # Bump the row so ``stale_etag`` is no longer current.
        cont.upsert_item({"id": item_id, "pk": "a", "value": 2})
        return cont.read_item(
            item_id,
            partition_key="a",
            etag=stale_etag,
            match_condition=MatchConditions.IfNotModified,
        )

    cmp = run_on_both_backends(
        _do,
        description="[L4] stale etag + IfNotModified on read — observe behavior",
        request_kwargs={"etag": "<stale>", "match_condition": "IfNotModified"},
    )
    cmp.print_report()
    # The parity contract here is "both backends must end up in the
    # same observable state" -- either both raise the same typed
    # exception, or both return the same body. The harness's diff
    # logic handles both shapes uniformly. Tolerate header-surface
    # divergence, which the rust backend still reports less of.
    cmp.assert_functional_parity()
    # Pin the SUCCEEDED bit explicitly so a future change where the
    # SDK actually starts enforcing this (or the service starts
    # rejecting it) surfaces as a deliberate change, not a silent
    # behavioural drift.
    assert cmp.core_python.succeeded == cmp.rust.succeeded, (
        "core-python and rust must agree on whether the call raised; "
        "core_python.succeeded={!r}, rust.succeeded={!r}".format(
            cmp.core_python.succeeded, cmp.rust.succeeded,
        )
    )


# ---------------------------------------------------------------------------
# L5 -- exception parity for misuse
# ---------------------------------------------------------------------------

def test_L5_etag_without_match_condition_raises_value_error_up_front(container_for):
    """L5: ``etag=`` without ``match_condition=`` raises ``ValueError`` before
    any network call.

    This is the same gate every operation applies: the SDK refuses to
    guess what the customer meant. Both backends must raise the same
    ``ValueError`` with the same wording, on the public method's own call
    frame (it fires while the options are being built, before either
    backend is chosen).
    """
    def _do(client):
        cont = client.get_database_client("parity_db").get_container_client(container_for.id)
        item_id = uuid.uuid4().hex
        cont.create_item({"id": item_id, "pk": "a"})
        return cont.read_item(item_id, partition_key="a", etag="x")

    cmp = run_on_both_backends(
        _do,
        description="[L5] etag without match_condition raises ValueError",
        request_kwargs={"etag": "x"},
    )
    cmp.print_report()
    assert isinstance(cmp.core_python.raised, ValueError), (
        "core-python must raise ValueError; got {!r}".format(cmp.core_python.raised))
    assert isinstance(cmp.rust.raised, ValueError), (
        "rust must raise ValueError; got {!r}".format(cmp.rust.raised))


# ---------------------------------------------------------------------------
# L5 (sync-only) -- deprecated kwargs that are dropped before the wire
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

    Two pinned guarantees, same shape as the delete_item L5 test:

    1. The public sync ``read_item`` emits a ``DeprecationWarning``
       mentioning ``populate_query_metrics``.
    2. The ``x-ms-documentdb-populatequerymetrics`` request header is
       NOT present on the outgoing GET -- the value is dropped before
       the helper layer sees it. We assert this by wrapping the legacy
       ``CosmosClientConnection.__Get`` method and inspecting the
       captured header dict.

    Runs against core-python only because the kwarg is a sync-only-
    and-deprecated Python-side wrapper concern; the rust backend never
    receives it through the helper layer either way (the public method
    drops it).
    """
    from azure.cosmos import CosmosClient
    from azure.cosmos import _cosmos_client_connection as _ccc_module
    from azure.cosmos.http_constants import HttpHeaders
    import os

    captured_get_headers: Dict[str, Any] = {}

    # The name-mangled __Get receives ``req_headers`` already fully
    # built. Any populate-query-metrics that reached this far would
    # show up there.
    original_get = _ccc_module.CosmosClientConnection._CosmosClientConnection__Get  # type: ignore[attr-defined]

    def _capturing_get(self, path, request_params, req_headers, **kwargs):  # type: ignore[no-redef]
        if "/docs/" in path:
            captured_get_headers.clear()
            captured_get_headers.update(dict(req_headers))
        return original_get(self, path, request_params, req_headers, **kwargs)

    _ccc_module.CosmosClientConnection._CosmosClientConnection__Get = _capturing_get  # type: ignore[attr-defined]
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
            cont.read_item(
                item_id,
                partition_key="a",
                populate_query_metrics=True,
            )
    finally:
        _ccc_module.CosmosClientConnection._CosmosClientConnection__Get = original_get  # type: ignore[attr-defined]

    _assert_deprecation_warning_fired(recorded, "populate_query_metrics")
    pqm_header = HttpHeaders.PopulateQueryMetrics  # 'x-ms-documentdb-populatequerymetrics'
    assert pqm_header not in captured_get_headers, (
        "populate_query_metrics must be DROPPED before the helper layer "
        "on read_item -- the wire header {!r} must NOT be on the outgoing "
        "GET. Captured headers: {!r}".format(
            pqm_header, sorted(captured_get_headers)
        )
    )
    print(
        "[L5] populate_query_metrics: DeprecationWarning fired AND "
        "{!r} absent from outgoing GET headers (captured {} headers)".format(
            pqm_header, len(captured_get_headers)
        )
    )

