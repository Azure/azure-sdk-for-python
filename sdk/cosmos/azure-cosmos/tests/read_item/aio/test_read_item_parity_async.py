# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# -------------------------------------------------------------------------
"""End-to-end parity tests for ``aio.Container.read_item`` across backends.

Async twin of ``tests/read_item/sync/test_read_item_parity.py``. The
graduated structure and the verdict grammar match that file, so a
contributor who has read the sync suite recognises every test here.

Why this file exists at full strength rather than as a smoke test: the sync
and async containers are *separate* implementations that happen to share the
option-merge helpers. ``read_item`` reaches the wire through ``ItemHelper``
on sync and ``AsyncItemHelper`` on async, and only the async path awaits
``_set_partition_key``. A divergence between those two helpers is invisible
to the sync suite no matter how thorough it is, and this package has already
shipped one such bug (the ``_closing`` flag that existed on the async backend
but not the sync one). Every option the sync suite pins is therefore pinned
again here, against the async surface.

What this file pins for async ``read_item``:

* **Baseline.** Create one item, read it by bare id with the mandatory
  ``partition_key``. Both backends succeed and return a ``CosmosDict``
  carrying the same ``id`` / ``pk``.
* **``item`` is polymorphic.** Pass the read-back document dict
  (which carries ``_self``) instead of the bare id.
* **404 paths.** Missing id and wrong-partition-key both surface the
  same ``CosmosResourceNotFoundError``. The wire cannot tell the two apart
  (the service answers 404 either way), so the contract is "same typed
  exception with the same status code", not "same reason text".
* **header-bearing kwargs**, one per test so a failure attributes
  cleanly: ``post_trigger_include``, ``session_token``, ``initial_headers``,
  ``priority``, ``throughput_bucket``.
* **``max_integrated_cache_staleness_in_ms``.** Positive emits
  ``x-ms-dedicatedgateway-max-age``; ``0`` is a silent no-op; negative raises
  ``ValueError`` up front with no network round trip.
* **``timeout``.** Honoured on both backends.
* **``response_hook`` fires exactly once per backend.**
* **conditional read.** ``etag`` + ``IfModified`` with an unchanged
  server etag surfaces 304 as an empty ``CosmosDict``; ``etag`` +
  ``IfNotModified`` on a match returns 200 + body.
* **``etag=`` without ``match_condition=``** raises ``ValueError``
  before any network call. The gate lives in ``_base._get_match_headers``,
  which sync and async share -- this test is what proves the async path
  actually reaches it.

Deliberately NOT mirrored from the sync suite: the ``populate_query_metrics``
deprecation test. That keyword is a sync-only positional parameter; the async
``read_item`` signature does not accept it, so there is no async behaviour to
pin.
"""
from __future__ import annotations

import os
import uuid

import pytest

from azure.core import MatchConditions

from azure.cosmos import CosmosClient, PartitionKey
from common._parity_helpers import (
    BackendComparison,
    run_on_both_backends_async,
    skip_unless_emulator,
    skip_unless_rust_binding,
)

pytestmark = [skip_unless_emulator(), skip_unless_rust_binding()]


# ---------------------------------------------------------------------------
# Per-test container fixture
# ---------------------------------------------------------------------------

@pytest.fixture
def container_for(request):
    """Provide an isolated container so each test reads only its own items.

    Built with the *sync* client on purpose: the fixture is plain setup, not
    the behaviour under test, and a sync client keeps the fixture free of
    event-loop lifetime concerns. The reads under test all run on the async
    client created inside ``run_on_both_backends_async``.
    """
    client = CosmosClient(os.environ["ACCOUNT_HOST"], os.environ["ACCOUNT_KEY"])
    db = client.create_database_if_not_exists("parity_db")
    cname = "rda_" + request.node.name + "_" + uuid.uuid4().hex[:6]
    container = db.create_container(id=cname, partition_key=PartitionKey(path="/pk"))
    yield container
    try:
        db.delete_container(cname)
    except Exception:  # pylint: disable=broad-except
        pass


# ---------------------------------------------------------------------------
# Closure builders
# ---------------------------------------------------------------------------
#
# Each backend creates its OWN row (under the same partition key, with a
# fresh id) so the two runs never race on shared state. The parity contract
# being reported is the *read half*; the create half exists only so each
# backend has a row to point at.

def _async_read_by_id_call(container_id: str, **kwargs):
    """Build an async read that targets an item by its bare id."""
    async def _do(client):
        cont = client.get_database_client("parity_db").get_container_client(container_id)
        item_id = uuid.uuid4().hex
        await cont.create_item({"id": item_id, "pk": "customerA", "value": 1})
        return await cont.read_item(item_id, partition_key="customerA", **kwargs)
    return _do


def _async_read_by_dict_call(container_id: str, **kwargs):
    """Build an async read that targets the document dict the SDK returned."""
    async def _do(client):
        cont = client.get_database_client("parity_db").get_container_client(container_id)
        item_id = uuid.uuid4().hex
        created = await cont.create_item({"id": item_id, "pk": "customerA", "value": 1})
        return await cont.read_item(created, partition_key="customerA", **kwargs)
    return _do


async def _run_read(container, summary: str,
                    by_dict: bool = False, **kwargs) -> BackendComparison:
    """Compare the public async read result from Python and Rust."""
    builder = _async_read_by_dict_call if by_dict else _async_read_by_id_call
    description = "{} -- mode={}, kwargs={}".format(
        summary,
        "by-dict" if by_dict else "by-id",
        sorted(kwargs.keys()) or "(none)",
    )
    cmp = await run_on_both_backends_async(
        builder(container.id, **kwargs),
        description=description,
        request_kwargs=kwargs or None,
    )
    cmp.print_report()
    return cmp


# ---------------------------------------------------------------------------
# Baseline
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_baseline_read_by_id(container_for):
    """Baseline: async read by bare id + ``partition_key``, no optional kwargs.

    Both backends must succeed and the body's id/pk must match what was just
    written. Response-header-surface differences are tolerated here, per the
    shared ``assert_functional_parity`` policy.
    """
    cmp = await _run_read(container_for, summary="baseline read by id")
    cmp.assert_functional_parity()


# ---------------------------------------------------------------------------
# Polymorphic ``item`` shape + 404 cases
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_read_by_document_dict(container_for):
    """async read by passing the document dict (uses ``_self`` lookup).

    ``Container._get_document_link`` accepts either a bare id string or a
    full document dict; both shapes must land on the same request.
    """
    cmp = await _run_read(container_for, summary="read by document dict", by_dict=True)
    cmp.assert_functional_parity()


@pytest.mark.asyncio
async def test_missing_id_raises_typed_not_found(container_for):
    """Reading a never-created id raises ``CosmosResourceNotFoundError`` (404)
    on both backends."""
    fixed_id = "does-not-exist-" + uuid.uuid4().hex

    async def _do(client):
        cont = client.get_database_client("parity_db").get_container_client(container_for.id)
        return await cont.read_item(fixed_id, partition_key="a")

    cmp = await run_on_both_backends_async(
        _do,
        description="missing-id 404: read id={!r} that was never created".format(fixed_id),
        request_kwargs={"item": fixed_id, "partition_key": "a"},
    )
    cmp.print_report()
    assert not cmp.core_python.succeeded, "core-python must raise on missing id"
    assert not cmp.rust.succeeded, "rust must raise on missing id"
    assert getattr(cmp.core_python.raised, "status_code", None) == 404
    assert getattr(cmp.rust.raised, "status_code", None) == 404
    cmp.assert_functional_exception_parity()


@pytest.mark.asyncio
async def test_wrong_partition_key_raises_typed_not_found(container_for):
    """Reading with the wrong partition key returns 404 on both backends.

    The wire cannot distinguish wrong-id from wrong-pk -- the service answers
    404 either way. The contract is that both backends surface the same typed
    exception with the same status code, not that they explain *why*.
    """
    async def _do(client):
        cont = client.get_database_client("parity_db").get_container_client(container_for.id)
        item_id = uuid.uuid4().hex
        # Each backend writes its own row under pk='a' (distinct ids, so they
        # cannot race), then reads it back with the wrong pk='b'.
        await cont.create_item({"id": item_id, "pk": "a", "value": 1})
        return await cont.read_item(item_id, partition_key="b")

    cmp = await run_on_both_backends_async(
        _do,
        description="wrong-pk 404: row exists under pk='a', read with pk='b'",
        request_kwargs={"partition_key": "b"},
    )
    cmp.print_report()
    assert not cmp.core_python.succeeded
    assert not cmp.rust.succeeded
    assert getattr(cmp.core_python.raised, "status_code", None) == 404
    assert getattr(cmp.rust.raised, "status_code", None) == 404
    cmp.assert_functional_exception_parity()


# ---------------------------------------------------------------------------
# Header-bearing kwargs, one at a time
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_post_trigger_include(container_for):
    """Baseline call plus ``post_trigger_include='auditRead'``.

    No trigger by that name is registered, so the service returns the same
    "trigger not found" error to both backends. The parity contract is that
    the typed exception matches -- which still proves the keyword reached
    the wire on the async path.
    """
    cmp = await _run_read(container_for, summary="baseline + post_trigger_include",
                          post_trigger_include="auditRead")
    cmp.assert_functional_exception_parity()


@pytest.mark.asyncio
async def test_session_token(container_for):
    """Baseline call plus ``session_token=<token>``.

    Reads pass the session-token check; the known rust-side session-token
    limitation is on writes. Both backends forward the token as-is.
    """
    cmp = await _run_read(container_for, summary="baseline + session_token",
                          session_token="0:1#42")
    cmp.assert_functional_parity()


@pytest.mark.asyncio
async def test_initial_headers(container_for):
    """Baseline call plus customer-injected ``initial_headers``."""
    cmp = await _run_read(container_for, summary="baseline + initial_headers",
                          initial_headers={"x-ms-test-parity": "v1"})
    cmp.assert_functional_parity()


@pytest.mark.asyncio
async def test_priority_high(container_for):
    """Baseline call plus ``priority='High'`` (``x-ms-cosmos-priority-level``)."""
    cmp = await _run_read(container_for, summary="baseline + priority=High", priority="High")
    cmp.assert_functional_parity()


@pytest.mark.asyncio
async def test_throughput_bucket(container_for):
    """Baseline call plus ``throughput_bucket=1`` (``x-ms-cosmos-throughput-bucket``)."""
    cmp = await _run_read(container_for, summary="baseline + throughput_bucket=1", throughput_bucket=1)
    cmp.assert_functional_parity()


# ---------------------------------------------------------------------------
# Behavioural / Python-only kwargs
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_max_cache_staleness_positive(container_for):
    """Baseline call plus ``max_integrated_cache_staleness_in_ms=5000``.

    Reaches the wire as ``x-ms-dedicatedgateway-max-age: 5000``; both
    backends must forward it identically.
    """
    cmp = await _run_read(container_for, summary="baseline + max_integrated_cache_staleness_in_ms=5000",
                          max_integrated_cache_staleness_in_ms=5000)
    cmp.assert_functional_parity()


@pytest.mark.asyncio
async def test_max_cache_staleness_zero_is_silent_no_op(container_for):
    """``max_integrated_cache_staleness_in_ms=0`` is a silent no-op.

    Zero is falsy, so neither backend emits the header; the call must
    succeed exactly as if the keyword had not been passed.
    """
    cmp = await _run_read(container_for, summary="baseline + max_integrated_cache_staleness_in_ms=0",
                          max_integrated_cache_staleness_in_ms=0)
    cmp.assert_functional_parity()


@pytest.mark.asyncio
async def test_max_cache_staleness_negative_raises_value_error_up_front(container_for):
    """a negative cache-staleness raises ``ValueError`` BEFORE any network
    call.

    The validator runs in the public async method, before backend dispatch,
    so the customer's traceback points at their own call line and the wording
    is identical on both backends.
    """
    async def _do(client):
        cont = client.get_database_client("parity_db").get_container_client(container_for.id)
        item_id = uuid.uuid4().hex
        await cont.create_item({"id": item_id, "pk": "a"})
        return await cont.read_item(item_id, partition_key="a",
                                    max_integrated_cache_staleness_in_ms=-1)

    cmp = await run_on_both_backends_async(
        _do,
        description="negative max_integrated_cache_staleness raises ValueError",
        request_kwargs={"max_integrated_cache_staleness_in_ms": -1},
    )
    cmp.print_report()
    assert isinstance(cmp.core_python.raised, ValueError), (
        "core-python must raise ValueError before any network call; got {!r}".format(
            cmp.core_python.raised))
    assert isinstance(cmp.rust.raised, ValueError), (
        "rust must raise ValueError before any network call; got {!r}".format(
            cmp.rust.raised))


@pytest.mark.asyncio
async def test_timeout(container_for):
    """Baseline call plus ``timeout=30`` (overall request timeout)."""
    cmp = await _run_read(container_for, summary="baseline + timeout=30", timeout=30)
    cmp.assert_functional_parity()


@pytest.mark.skip(reason="Permanent skip: no rust-side equivalent (Python-only hedging feature). "
                         "Same rationale as the sync suite's L3_availability_strategy.")
@pytest.mark.asyncio
async def test_availability_strategy(container_for):
    """Baseline call plus ``availability_strategy=True`` (Python-only hedging feature).

    The rust driver surface has no hedging knob, so there is nothing to
    compare against. Skipped for the same reason as its sync twin.
    """
    cmp = await _run_read(container_for, summary="baseline + availability_strategy=True",
                          availability_strategy=True)
    cmp.assert_functional_parity()


@pytest.mark.skip(reason="Skipped: binding forwards excluded_locations to the driver's typed "
                         "ExcludedRegions field, but the parity assertion is hard to make "
                         "end-to-end against a single-region test account. Same skip rationale "
                         "as the sync suite's L3_excluded_locations.")
@pytest.mark.asyncio
async def test_excluded_locations(container_for):
    """Baseline call plus ``excluded_locations=['East US']``.

    The binding forwards this to the driver as an excluded-regions setting.
    Skipped only because the assertion is not meaningful on a single-region
    account: excluding a region the account does not use changes no routing
    decision the legacy path would diff against. Remove this skip once the
    harness gains a multi-region fixture.
    """
    cmp = await _run_read(container_for, summary="baseline + excluded_locations",
                          excluded_locations=["East US"])
    cmp.assert_functional_parity()


# ---------------------------------------------------------------------------
# Output / parsing parity, conditional reads
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_response_hook_fires_once(container_for):
    """``response_hook`` must fire exactly once per backend on success.

    The harness runs core-python first and rust second, deterministically, so
    an invocation-order counter attributes each hook fire to the right backend
    without any synchronisation. This asserts the callback actually *runs* --
    not merely that the keyword was accepted.
    """
    fired = {"core-python": 0, "rust": 0}
    order = ["core-python", "rust"]
    call_idx = [0]

    async def _do(client):
        backend = order[call_idx[0]]
        call_idx[0] += 1

        def _hook(_headers, _body):
            fired[backend] += 1

        cont = client.get_database_client("parity_db").get_container_client(container_for.id)
        item_id = uuid.uuid4().hex
        await cont.create_item({"id": item_id, "pk": "a"})
        return await cont.read_item(item_id, partition_key="a", response_hook=_hook)

    cmp = await run_on_both_backends_async(
        _do,
        description="response_hook fires exactly once per backend",
        request_kwargs={"response_hook": "<callable>"},
    )
    cmp.print_report()
    print("response_hook fired: core-python={} rust={}".format(
        fired["core-python"], fired["rust"]))
    cmp.assert_functional_parity()
    assert fired["core-python"] == 1, "core-python should fire response_hook exactly once"
    assert fired["rust"] == 1, "rust should fire response_hook exactly once"


@pytest.mark.asyncio
async def test_conditional_etag_if_modified_unchanged_returns_304_empty_dict(container_for):
    """``etag`` + ``IfModified``, server etag unchanged -> 304 empty dict.

    This is the cache-validation idiom: the caller's etag still matches the
    stored version, so the service answers ``304 Not Modified`` with no body.
    The SDK surfaces that as a *successful* empty ``CosmosDict`` whose
    ``get_response_headers()["etag"]`` carries the current etag.
    """
    async def _do(client):
        cont = client.get_database_client("parity_db").get_container_client(container_for.id)
        item_id = uuid.uuid4().hex
        created = await cont.create_item({"id": item_id, "pk": "a", "value": 1})
        # The row has not changed since create returned this etag, so a
        # conditional read with IfModified must surface as 304.
        return await cont.read_item(
            item_id,
            partition_key="a",
            etag=created["_etag"],
            match_condition=MatchConditions.IfModified,
        )

    cmp = await run_on_both_backends_async(
        _do,
        description="etag + IfModified, unchanged -> 304 empty CosmosDict",
        request_kwargs={"etag": "<current>", "match_condition": "IfModified"},
    )
    cmp.print_report()
    assert cmp.core_python.succeeded, (
        "core-python must succeed on unchanged-etag conditional read; raised={!r}".format(
            cmp.core_python.raised))
    assert cmp.rust.succeeded, (
        "rust must succeed on unchanged-etag conditional read; raised={!r}".format(
            cmp.rust.raised))
    # The body must be empty (nothing to parse) and the etag must be readable
    # from the response headers. We do not compare the two etags to each other
    # because each backend read its own row.
    for name, outcome in (("core-python", cmp.core_python), ("rust", cmp.rust)):
        result = outcome.return_value
        assert len(result) == 0, (
            "{}: 304 must surface as an empty CosmosDict; got {!r}".format(name, dict(result)))
        headers = result.get_response_headers()
        assert "etag" in headers, (
            "{}: response headers must carry the current etag on 304; got keys {!r}".format(
                name, sorted(headers)))


@pytest.mark.asyncio
async def test_conditional_etag_if_not_modified_match_returns_200_body(container_for):
    """``etag`` + ``IfNotModified``, server etag matches -> 200 + body.

    Same set-up as the 304 case above but with ``IfNotModified`` (which
    translates to ``If-Match``). On a match the service returns the document
    normally, so both backends must produce a populated body.
    """
    async def _do(client):
        cont = client.get_database_client("parity_db").get_container_client(container_for.id)
        item_id = uuid.uuid4().hex
        created = await cont.create_item({"id": item_id, "pk": "a", "value": 1})
        return await cont.read_item(
            item_id,
            partition_key="a",
            etag=created["_etag"],
            match_condition=MatchConditions.IfNotModified,
        )

    cmp = await run_on_both_backends_async(
        _do,
        description="etag + IfNotModified, matches -> 200 + body",
        request_kwargs={"etag": "<current>", "match_condition": "IfNotModified"},
    )
    cmp.print_report()
    cmp.assert_functional_parity()
    for name, outcome in (("core-python", cmp.core_python), ("rust", cmp.rust)):
        result = outcome.return_value
        assert "id" in result and "pk" in result, (
            "{}: 200 must surface the body; got {!r}".format(name, dict(result)))


# ---------------------------------------------------------------------------
# Exception parity for misuse
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_etag_without_match_condition_raises_value_error_up_front(container_for):
    """``etag=`` without ``match_condition=`` raises ``ValueError`` before
    any network call.

    The SDK refuses to guess what the caller meant. The gate itself lives in
    ``_base._get_match_headers``, which the sync and async paths share -- so
    what this test actually proves is that the *async* option-build path
    reaches that gate, on both backends, before dispatching a request.
    """
    async def _do(client):
        cont = client.get_database_client("parity_db").get_container_client(container_for.id)
        item_id = uuid.uuid4().hex
        await cont.create_item({"id": item_id, "pk": "a"})
        return await cont.read_item(item_id, partition_key="a", etag="x")

    cmp = await run_on_both_backends_async(
        _do,
        description="etag without match_condition raises ValueError",
        request_kwargs={"etag": "x"},
    )
    cmp.print_report()
    assert isinstance(cmp.core_python.raised, ValueError), (
        "core-python must raise ValueError; got {!r}".format(cmp.core_python.raised))
    assert isinstance(cmp.rust.raised, ValueError), (
        "rust must raise ValueError; got {!r}".format(cmp.rust.raised))
