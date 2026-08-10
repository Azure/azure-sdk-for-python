# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# -------------------------------------------------------------------------
"""End-to-end parity tests for ``aio.Container.delete_item`` across backends.

Async twin of ``tests/delete_item/sync/test_delete_item_parity.py``. The
graduated structure and the verdict grammar match that file, so a
contributor who has read the sync suite recognises every test here.

Why this file exists at full strength rather than as a smoke test: sync and
async are *separate* container implementations that share only the
option-merge helpers. ``delete_item`` reaches the wire through ``ItemHelper``
on sync and ``AsyncItemHelper`` on async, and only the async path awaits
``_set_partition_key``. A divergence between those two helpers cannot be seen
by the sync suite however thorough it is, and this package has already shipped
one such bug (the ``_closing`` flag present on the async backend but missing
on the sync one). Every option the sync suite pins is therefore pinned again
here against the async surface.

What this file pins for async ``delete_item``:

* **Baseline.** Create a row, delete it by bare id with the mandatory
  ``partition_key``. Both backends return ``None``.
* **``item`` is polymorphic.** Delete by passing the document dict
  (which carries ``_self``) rather than the bare id.
* **header-bearing kwargs**, one per test so a failure attributes
  cleanly: ``pre_trigger_include``, ``post_trigger_include``,
  ``session_token``, ``initial_headers``, ``priority``, ``throughput_bucket``.
* **``timeout``.** Honoured on both backends.
* **``response_hook`` fires exactly once per backend.**
* **404.** Deleting a never-created id raises
  ``CosmosResourceNotFoundError`` on both.
* **optimistic concurrency.** A *stale* ``etag`` with
  ``IfNotModified`` must raise a typed 412 on both backends; a *current*
  etag with ``IfNotModified`` must succeed and must not warn. This is the
  delete-specific contract -- on ``create_item`` the same pair is inert.
* **``etag=`` without ``match_condition=``** raises ``ValueError``
  before any network call, from the shared ``_base._get_match_headers`` gate.

Deliberately NOT mirrored from the sync suite: the ``populate_query_metrics``
deprecation test. That keyword is sync-only; the async ``delete_item``
signature does not expose it, so there is no async behaviour to pin.
"""
from __future__ import annotations

import os
import uuid
import warnings

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
    """Provide an isolated container so each test targets only its own items.

    Built with the *sync* client on purpose: the fixture is setup, not the
    behaviour under test, and a sync client keeps it free of event-loop
    lifetime concerns. The deletes under test all run on the async client
    created inside ``run_on_both_backends_async``.
    """
    client = CosmosClient(os.environ["ACCOUNT_HOST"], os.environ["ACCOUNT_KEY"])
    db = client.create_database_if_not_exists("parity_db")
    cname = "dla_" + request.node.name + "_" + uuid.uuid4().hex[:6]
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
# Each backend creates and deletes its OWN row (fresh id under the same
# partition key) so the two runs never race. The reported parity contract is
# the *delete half*; the create half only exists to give each backend a row
# to remove.

def _async_delete_by_id_call(container_id: str, **kwargs):
    """Build an async delete that targets an item by its bare id."""
    async def _do(client):
        cont = client.get_database_client("parity_db").get_container_client(container_id)
        item_id = uuid.uuid4().hex
        await cont.create_item({"id": item_id, "pk": "customerA", "value": 1})
        return await cont.delete_item(item_id, partition_key="customerA", **kwargs)
    return _do


def _async_delete_by_dict_call(container_id: str, **kwargs):
    """Build an async delete that targets the document dict the SDK returned."""
    async def _do(client):
        cont = client.get_database_client("parity_db").get_container_client(container_id)
        item_id = uuid.uuid4().hex
        created = await cont.create_item({"id": item_id, "pk": "customerA", "value": 1})
        return await cont.delete_item(created, partition_key="customerA", **kwargs)
    return _do


async def _run_delete(container, summary: str,
                      by_dict: bool = False, **kwargs) -> BackendComparison:
    """Compare the public async delete result from Python and Rust."""
    builder = _async_delete_by_dict_call if by_dict else _async_delete_by_id_call
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
async def test_baseline_delete_by_id(container_for):
    """Baseline: async delete by bare id + ``partition_key``, no optional kwargs.

    ``delete_item`` returns ``None`` on success, so the parity contract here
    is "both backends succeeded and returned nothing".
    """
    cmp = await _run_delete(container_for, summary="baseline delete by id")
    cmp.assert_functional_parity()
    assert cmp.core_python.return_value is None
    assert cmp.rust.return_value is None


# ---------------------------------------------------------------------------
# Polymorphic ``item`` shape
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_delete_by_document_dict(container_for):
    """async delete by passing the document dict (uses ``_self`` lookup).

    ``Container._get_document_link`` accepts a bare id string or a full
    document dict; both shapes must land on the same request.
    """
    cmp = await _run_delete(container_for, summary="delete by document dict", by_dict=True)
    cmp.assert_functional_parity()


# ---------------------------------------------------------------------------
# Header-bearing kwargs, one at a time
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_pre_trigger_include(container_for):
    """Baseline call plus ``pre_trigger_include='auditDelete'``.

    No trigger by that name is registered, so the service returns the same
    "trigger not found" error to both backends -- which still proves the
    keyword reached the wire on the async path.
    """
    cmp = await _run_delete(container_for, summary="baseline + pre_trigger_include",
                            pre_trigger_include="auditDelete")
    cmp.assert_functional_exception_parity()


@pytest.mark.asyncio
async def test_post_trigger_include(container_for):
    """Baseline call plus ``post_trigger_include='auditDelete'``.

    Same contract as the pre-trigger case above: the typed exception must
    match across backends.
    """
    cmp = await _run_delete(container_for, summary="baseline + post_trigger_include",
                            post_trigger_include="auditDelete")
    cmp.assert_functional_exception_parity()


@pytest.mark.asyncio
async def test_session_token(container_for):
    """Baseline call plus ``session_token=<token>``.

    Both backends forward the token as-is; the outcome on the wire must
    match.
    """
    cmp = await _run_delete(container_for, summary="baseline + session_token",
                            session_token="0:1#42")
    cmp.assert_functional_parity()


@pytest.mark.asyncio
async def test_initial_headers(container_for):
    """Baseline call plus customer-injected ``initial_headers``."""
    cmp = await _run_delete(container_for, summary="baseline + initial_headers",
                            initial_headers={"x-ms-test-parity": "v1"})
    cmp.assert_functional_parity()


@pytest.mark.asyncio
async def test_priority_high(container_for):
    """Baseline call plus ``priority='High'`` (``x-ms-cosmos-priority-level``)."""
    cmp = await _run_delete(container_for, summary="baseline + priority=High", priority="High")
    cmp.assert_functional_parity()


@pytest.mark.asyncio
async def test_throughput_bucket(container_for):
    """Baseline call plus ``throughput_bucket=1`` (``x-ms-cosmos-throughput-bucket``)."""
    cmp = await _run_delete(container_for, summary="baseline + throughput_bucket=1", throughput_bucket=1)
    cmp.assert_functional_parity()


# ---------------------------------------------------------------------------
# Behavioural / Python-only kwargs
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_timeout(container_for):
    """Baseline call plus ``timeout=30`` (overall request timeout)."""
    cmp = await _run_delete(container_for, summary="baseline + timeout=30", timeout=30)
    cmp.assert_functional_parity()


@pytest.mark.skip(reason="Permanent skip: no rust-side equivalent (Python-only knob). "
                         "Same rationale as the sync suite's L3_retry_write.")
@pytest.mark.asyncio
async def test_retry_write(container_for):
    """Baseline call plus ``retry_write=1`` (Python-only retry knob).

    The rust driver owns its own retry policy and exposes no per-request
    write-retry override, so there is nothing to compare against.
    """
    cmp = await _run_delete(container_for, summary="baseline + retry_write", retry_write=1)
    cmp.assert_functional_parity()


@pytest.mark.skip(reason="Permanent skip: no rust-side equivalent (Python-only hedging feature). "
                         "Same rationale as the sync suite's L3_availability_strategy.")
@pytest.mark.asyncio
async def test_availability_strategy(container_for):
    """Baseline call plus ``availability_strategy=True`` (Python-only hedging feature).

    The rust driver surface has no hedging knob, so there is nothing to
    compare against.
    """
    cmp = await _run_delete(container_for, summary="baseline + availability_strategy=True",
                            availability_strategy=True)
    cmp.assert_functional_parity()


@pytest.mark.skip(reason="Skipped: binding forwards excluded_locations to the driver's typed "
                         "ExcludedRegions field, but the parity assertion is hard to make "
                         "end-to-end against a single-region test account. Same skip rationale "
                         "as the sync suite's L3_excluded_locations.")
@pytest.mark.asyncio
async def test_excluded_locations(container_for):
    """Baseline call plus ``excluded_locations=['East US']``.

    Skipped only because the assertion is not meaningful on a single-region
    account: excluding a region the account does not use changes no routing
    decision the legacy path would diff against.
    """
    cmp = await _run_delete(container_for, summary="baseline + excluded_locations",
                            excluded_locations=["East US"])
    cmp.assert_functional_parity()


# ---------------------------------------------------------------------------
# Callback parity
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_response_hook_fires_once(container_for):
    """``response_hook`` must fire exactly once per backend on success.

    The harness runs core-python first and rust second, deterministically, so
    an invocation-order counter attributes each hook fire to the right backend
    without synchronisation. This asserts the callback actually *runs* -- not
    merely that the keyword was accepted.
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
        return await cont.delete_item(item_id, partition_key="a", response_hook=_hook)

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


# ---------------------------------------------------------------------------
# Exception parity
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_missing_id_raises_typed_not_found(container_for):
    """Deleting a never-created id raises ``CosmosResourceNotFoundError``
    (HTTP 404) on both backends with the same status code."""
    fixed_id = "does-not-exist-" + uuid.uuid4().hex

    async def _do(client):
        cont = client.get_database_client("parity_db").get_container_client(container_for.id)
        return await cont.delete_item(fixed_id, partition_key="a")

    cmp = await run_on_both_backends_async(
        _do,
        description="missing-id 404: delete id={!r} that was never created".format(fixed_id),
        request_kwargs={"item": fixed_id, "partition_key": "a"},
    )
    cmp.print_report()
    assert not cmp.core_python.succeeded, "core-python must raise on missing id"
    assert not cmp.rust.succeeded, "rust must raise on missing id"
    assert getattr(cmp.core_python.raised, "status_code", None) == 404
    assert getattr(cmp.rust.raised, "status_code", None) == 404
    cmp.assert_functional_exception_parity()


@pytest.mark.asyncio
async def test_stale_etag_if_not_modified_raises_412(container_for):
    """stale ``etag`` + ``MatchConditions.IfNotModified`` => HTTP 412.

    This is the delete-specific contract: on ``delete_item`` the
    ``etag``/``match_condition`` pair is the optimistic-concurrency
    primitive (on ``create_item`` it is inert and warns). The sequence:

    1. Create the row.
    2. Bump it, so the server-side etag changes.
    3. Delete with the OLD etag and ``IfNotModified``.

    The service answers 412 and the SDK must raise the typed precondition
    error with ``status_code == 412`` on both backends.
    """
    async def _do(client):
        cont = client.get_database_client("parity_db").get_container_client(container_for.id)
        item_id = uuid.uuid4().hex
        created = await cont.create_item({"id": item_id, "pk": "a"})
        stale_etag = created["_etag"]
        # Bump the row so ``stale_etag`` is no longer current. ``upsert_item``
        # is deliberate: it does not require tracking the current etag.
        await cont.upsert_item({"id": item_id, "pk": "a", "bumped": True})
        return await cont.delete_item(
            item_id,
            partition_key="a",
            etag=stale_etag,
            match_condition=MatchConditions.IfNotModified,
        )

    cmp = await run_on_both_backends_async(
        _do,
        description="stale etag + IfNotModified must raise typed 412 on both backends",
        request_kwargs={"etag": "<stale>", "match_condition": "IfNotModified"},
    )
    cmp.print_report()
    assert not cmp.core_python.succeeded, "core-python must raise on stale etag + IfNotModified"
    assert not cmp.rust.succeeded, "rust must raise on stale etag + IfNotModified"
    # Pin the status code explicitly. The harness's diff would catch the two
    # backends *disagreeing*; this assert also catches them agreeing on the
    # wrong number (e.g. both drifting to 409).
    assert getattr(cmp.core_python.raised, "status_code", None) == 412, (
        "core-python must raise HTTP 412 (Precondition Failed); got status_code={!r}, "
        "exception={!r}".format(
            getattr(cmp.core_python.raised, "status_code", None),
            type(cmp.core_python.raised).__name__))
    assert getattr(cmp.rust.raised, "status_code", None) == 412, (
        "rust must raise HTTP 412 (Precondition Failed); got status_code={!r}, "
        "exception={!r}".format(
            getattr(cmp.rust.raised, "status_code", None),
            type(cmp.rust.raised).__name__))
    cmp.assert_functional_exception_parity()


@pytest.mark.asyncio
async def test_current_etag_if_not_modified_succeeds_without_warning(container_for):
    """a *current* ``etag`` + ``IfNotModified`` succeeds and does not warn.

    The mirror of the 412 case: when the etag is still current the delete
    goes through. ``etag``/``match_condition`` are meaningful on delete (inert
    only on create), so no ``DeprecationWarning`` may be emitted for them.
    """
    async def _do(client):
        cont = client.get_database_client("parity_db").get_container_client(container_for.id)
        item_id = uuid.uuid4().hex
        created = await cont.create_item({"id": item_id, "pk": "a"})
        return await cont.delete_item(
            item_id,
            partition_key="a",
            etag=created["_etag"],
            match_condition=MatchConditions.IfNotModified,
        )

    with warnings.catch_warnings(record=True) as recorded:
        warnings.simplefilter("always")
        cmp = await run_on_both_backends_async(
            _do,
            description="current etag + IfNotModified must succeed and not warn",
            request_kwargs={"etag": "<current>", "match_condition": "IfNotModified"},
        )
    cmp.print_report()
    offending = [w for w in recorded
                 if issubclass(w.category, DeprecationWarning)
                 and ("etag" in str(w.message) or "match_condition" in str(w.message))]
    assert not offending, (
        "delete_item must NOT emit DeprecationWarning for etag/match_condition "
        "(meaningful on delete, inert only on create). Got: {}".format(
            [str(w.message) for w in offending]))
    cmp.assert_functional_parity()


@pytest.mark.asyncio
async def test_etag_without_match_condition_raises_value_error_up_front(container_for):
    """``etag=`` without ``match_condition=`` raises ``ValueError`` before
    any network call.

    The SDK refuses to guess what the caller meant. The gate lives in
    ``_base._get_match_headers``, shared by sync and async -- so what this
    test proves is that the *async* option-build path reaches that gate, on
    both backends, before dispatching a request.
    """
    async def _do(client):
        cont = client.get_database_client("parity_db").get_container_client(container_for.id)
        item_id = uuid.uuid4().hex
        await cont.create_item({"id": item_id, "pk": "a"})
        return await cont.delete_item(item_id, partition_key="a", etag="x")

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
