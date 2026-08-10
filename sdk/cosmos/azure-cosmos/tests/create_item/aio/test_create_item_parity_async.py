# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# -------------------------------------------------------------------------
"""End-to-end parity tests for ``aio.Container.create_item`` across backends.

Async twin of ``tests/create_item/sync/test_create_item_parity.py``. The
graduated structure and the verdict grammar match that file, so a
contributor who has read the sync suite recognises every test here.

Why this file exists at full strength rather than as a smoke test: sync and
async are *separate* container implementations that share only the
option-merge helpers. ``create_item`` reaches the wire through ``ItemHelper``
on sync and ``AsyncItemHelper`` on async, and only the async path awaits
``_set_partition_key``. A divergence between those two helpers cannot be seen
by the sync suite however thorough it is, and this package has already shipped
one such bug (the ``_closing`` flag present on the async backend but missing
on the sync one). Every option the sync suite pins is therefore pinned again
here against the async surface.

What this file pins for async ``create_item``:

* **Baseline.** Body plus the mandatory partition-key field, no optional
  kwargs. If the baseline fails, ``create_item`` is broken on one backend and no other
  result in the file means anything.
* **partition-key shape variants.** A body missing the declared PK path
  (the undefined-PK wire shape) and an explicit ``pk: None`` (the JSON-null
  wire shape).
* **header-bearing kwargs**, one per test so a failure attributes
  cleanly: ``pre_trigger_include``, ``post_trigger_include``,
  ``indexing_directive``, ``session_token``, ``initial_headers``,
  ``priority``, ``throughput_bucket``.
* **behavioural kwargs.** ``enable_automatic_id_generation``,
  ``no_response``, ``retry_write``, ``availability_strategy``, ``timeout``.
* **``response_hook`` fires exactly once per backend.**
* **409.** Inserting the same id twice raises
  ``CosmosResourceExistsError`` on both.
* **deprecated-but-ignored kwargs.** ``etag`` and ``match_condition``
  carry no meaning on an insert; the contract is that they warn and are then
  dropped rather than honoured. Note this is the *opposite* of the
  ``delete_item`` contract, where the same pair drives optimistic
  concurrency -- which is precisely why it is worth pinning per operation.

Deliberately NOT mirrored from the sync suite:

* The ``populate_query_metrics`` deprecation test. That keyword is a sync-only
  positional parameter; the async ``create_item`` signature does not expose it,
  so there is no async behaviour to pin.
* The partitionless-container (``"[]"``) binding-rejection test and the
  intended-collection-rid wire test. Both assert against the shared binding
  rather than the async entry point, so running them again here would diff the
  same code twice and add nothing.
"""
from __future__ import annotations

import copy
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
    lifetime concerns. The creates under test all run on the async client
    created inside ``run_on_both_backends_async``.
    """
    client = CosmosClient(os.environ["ACCOUNT_HOST"], os.environ["ACCOUNT_KEY"])
    db = client.create_database_if_not_exists("parity_db")
    cname = "cra_" + request.node.name + "_" + uuid.uuid4().hex[:6]
    container = db.create_container(id=cname, partition_key=PartitionKey(path="/pk"))
    yield container
    try:
        db.delete_container(cname)
    except Exception:  # pylint: disable=broad-except
        pass


# ---------------------------------------------------------------------------
# Closure builder
# ---------------------------------------------------------------------------

def _async_create_call(container_id: str, body: dict, **kwargs):
    """Build an async create that gives each backend its own fresh row.

    The id is regenerated per backend so the second run never collides with the
    first one's insert and reports a spurious 409. Everything else in the body
    is deep-copied, so a test that mutates its template cannot leak into the
    other backend's request.
    """
    async def _do(client):
        fresh = copy.deepcopy(body)
        if "id" in fresh:
            fresh["id"] = uuid.uuid4().hex
        cont = client.get_database_client("parity_db").get_container_client(container_id)
        return await cont.create_item(body=fresh, **kwargs)
    return _do


async def _run_create(container, body: dict, summary: str,
                      **kwargs) -> BackendComparison:
    """Run one async create on both backends and print the side-by-side report."""
    description = "async {} -- body keys={}, kwargs={}".format(
        summary, list(body.keys()), sorted(kwargs.keys()) or "(none)",
    )
    cmp = await run_on_both_backends_async(
        _async_create_call(container.id, body, **kwargs),
        description=description,
        request_body=body,
        request_kwargs=kwargs or None,
    )
    cmp.print_report()
    return cmp


# ---------------------------------------------------------------------------
# Baseline
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_async_baseline_body_and_pk_only(container_for):
    """minimal valid body, no optional kwargs.

    Both backends must accept the insert and return equivalent documents.
    Response-header-surface differences are tolerated (the rust binding exposes
    a smaller header set), so this is a clean "async create_item itself works"
    signal.
    """
    body = {"id": uuid.uuid4().hex, "pk": "customerA", "n": 1}
    cmp = await _run_create(container_for, body, summary="baseline create")
    cmp.assert_functional_parity()


# ---------------------------------------------------------------------------
# Partition-key shape variants
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_async_pk_undefined(container_for):
    """body omits the declared PK path -- the undefined-PK wire shape.

    The binding accepts this and treats it as the undefined partition-key
    value end to end; the async path must round-trip it exactly as sync does.
    """
    body = {"id": uuid.uuid4().hex, "n": 1}
    cmp = await _run_create(container_for, body, summary="undefined PK")
    cmp.assert_functional_parity()


@pytest.mark.asyncio
async def test_async_pk_explicit_none(container_for):
    """explicit ``pk: None`` -- the JSON-null partition-key wire shape.

    Distinct from the undefined case above: this sends a real ``null`` value
    rather than omitting the field, and both backends accept it.
    """
    body = {"id": uuid.uuid4().hex, "pk": None}
    cmp = await _run_create(container_for, body, summary="explicit None PK")
    cmp.assert_functional_parity()


# ---------------------------------------------------------------------------
# Header-bearing kwargs, exactly one per test
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_async_pre_trigger_include(container_for):
    """Baseline call plus ``pre_trigger_include`` -- forwarded as a request header."""
    body = {"id": uuid.uuid4().hex, "pk": "a"}
    cmp = await _run_create(container_for, body, summary="baseline + pre_trigger_include",
                            pre_trigger_include="validateOrder")
    cmp.assert_functional_parity()


@pytest.mark.asyncio
async def test_async_post_trigger_include(container_for):
    """Baseline call plus ``post_trigger_include`` -- forwarded as a request header."""
    body = {"id": uuid.uuid4().hex, "pk": "a"}
    cmp = await _run_create(container_for, body, summary="baseline + post_trigger_include",
                            post_trigger_include="auditOrder")
    cmp.assert_functional_parity()


@pytest.mark.asyncio
async def test_async_indexing_directive(container_for):
    """Baseline call plus ``indexing_directive=1`` (Exclude) -- forwarded as a header.

    The value is an enum member on the wire, so this also pins that the async
    path converts the int the same way sync does rather than passing it raw.
    """
    body = {"id": uuid.uuid4().hex, "pk": "a"}
    cmp = await _run_create(container_for, body, summary="baseline + indexing_directive=Exclude",
                            indexing_directive=1)
    cmp.assert_functional_parity()


@pytest.mark.asyncio
async def test_async_session_token(container_for):
    """Baseline call plus ``session_token`` -- forwarded as a request header."""
    body = {"id": uuid.uuid4().hex, "pk": "a"}
    cmp = await _run_create(container_for, body, summary="baseline + session_token",
                            session_token="0:1#42")
    cmp.assert_functional_parity()


@pytest.mark.asyncio
async def test_async_initial_headers(container_for):
    """Baseline call plus ``initial_headers`` -- a caller-supplied custom header.

    Worth pinning on the async path specifically: custom headers ride a
    different channel through the binding than the SDK's own headers, and a
    header dropped here would be invisible in the response.
    """
    body = {"id": uuid.uuid4().hex, "pk": "a"}
    cmp = await _run_create(container_for, body, summary="baseline + initial_headers",
                            initial_headers={"x-ms-test-parity": "v1"})
    cmp.assert_functional_parity()


@pytest.mark.asyncio
async def test_async_priority(container_for):
    """Baseline call plus ``priority='High'`` -- the priority-based-throttling header."""
    body = {"id": uuid.uuid4().hex, "pk": "a"}
    cmp = await _run_create(container_for, body, summary="baseline + priority=High",
                            priority="High")
    cmp.assert_functional_parity()


@pytest.mark.asyncio
async def test_async_throughput_bucket(container_for):
    """Baseline call plus ``throughput_bucket=1`` -- the throughput-bucket header."""
    body = {"id": uuid.uuid4().hex, "pk": "a"}
    cmp = await _run_create(container_for, body, summary="baseline + throughput_bucket",
                            throughput_bucket=1)
    cmp.assert_functional_parity()


# ---------------------------------------------------------------------------
# Behavioural kwargs
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_async_enable_automatic_id_generation(container_for):
    """``enable_automatic_id_generation=True`` with no ``id`` in the body.

    Both backends must mint an id rather than reject the insert. The generated
    ids differ between backends by definition, so the harness's functional
    comparison (which tolerates server-assigned identity fields) is the right
    assertion here.
    """
    body = {"pk": "a", "n": 1}
    cmp = await _run_create(container_for, body, summary="baseline + enable_automatic_id_generation",
                            enable_automatic_id_generation=True)
    cmp.assert_functional_parity()


@pytest.mark.asyncio
async def test_async_no_response(container_for):
    """``no_response=True`` -- the service must not echo the document back.

    This changes the *shape of the return value*, not just a header, so it is
    the async kwarg most likely to expose a helper divergence.
    """
    body = {"id": uuid.uuid4().hex, "pk": "a", "n": 1}
    cmp = await _run_create(container_for, body, summary="baseline + no_response",
                            no_response=True)
    cmp.assert_functional_parity()


@pytest.mark.asyncio
async def test_async_retry_write(container_for):
    """``retry_write=1`` -- opts a non-idempotent write into retries."""
    body = {"id": uuid.uuid4().hex, "pk": "a"}
    cmp = await _run_create(container_for, body, summary="baseline + retry_write",
                            retry_write=1)
    cmp.assert_functional_parity()


@pytest.mark.asyncio
async def test_async_availability_strategy(container_for):
    """``availability_strategy=True`` -- enables hedged cross-region requests."""
    body = {"id": uuid.uuid4().hex, "pk": "a"}
    cmp = await _run_create(container_for, body, summary="baseline + availability_strategy",
                            availability_strategy=True)
    cmp.assert_functional_parity()


@pytest.mark.asyncio
async def test_async_timeout(container_for):
    """``timeout=30`` -- the overall per-request timeout.

    Honoured on both backends: core-python through azure-core's per-call
    timeout, rust by handing the value to the driver. The driver clamps
    sub-second values to a 1 s floor, so 30 s sits well clear of the clamp and
    the call is expected to succeed normally.
    """
    body = {"id": uuid.uuid4().hex, "pk": "a"}
    cmp = await _run_create(container_for, body, summary="baseline + timeout=30",
                            timeout=30)
    cmp.assert_functional_parity()


@pytest.mark.skip(reason="Permanent skip: no rust-side equivalent (Python-only routing knob). "
                         "Mirrors the same skip in the sync suite -- a single-region test "
                         "account cannot show a routing difference either way.")
@pytest.mark.asyncio
async def test_async_excluded_locations(container_for):
    """``excluded_locations`` -- a Python-only routing override."""
    body = {"id": uuid.uuid4().hex, "pk": "a"}
    cmp = await _run_create(container_for, body, summary="baseline + excluded_locations",
                            excluded_locations=["East US"])
    cmp.assert_functional_parity()


@pytest.mark.skip(reason="Partial parity: the driver has client-level connect/read timeout "
                         "analogs but the binding does not wire Python's per-call "
                         "read_timeout into them yet. Mirrors the sync suite's skip.")
@pytest.mark.asyncio
async def test_async_read_timeout(container_for):
    """``read_timeout=30`` -- the azure-core HTTP read timeout."""
    body = {"id": uuid.uuid4().hex, "pk": "a"}
    cmp = await _run_create(container_for, body, summary="baseline + read_timeout=30",
                            read_timeout=30)
    cmp.assert_functional_parity()


@pytest.mark.skip(reason="Partial parity: the binding does not wire Python's "
                         "connection_timeout into the driver's connection-pool config yet. "
                         "Mirrors the sync suite's skip.")
@pytest.mark.asyncio
async def test_async_connection_timeout(container_for):
    """``connection_timeout=10`` -- the azure-core HTTP connect timeout."""
    body = {"id": uuid.uuid4().hex, "pk": "a"}
    cmp = await _run_create(container_for, body, summary="baseline + connection_timeout=10",
                            connection_timeout=10)
    cmp.assert_functional_parity()


# ---------------------------------------------------------------------------
# Output / parsing parity
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_async_response_hook_fires_once(container_for):
    """``response_hook`` must fire exactly once per backend on success.

    Counting the invocations is the point. Asserting only that the hook is
    accepted would pass even if it were never called, which is the failure mode
    worth guarding: a hook that silently stops firing breaks customer telemetry
    without breaking any request. The harness runs core-python first and rust
    second, so an invocation counter attributes each call to the right backend.
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
        return await cont.create_item(
            body={"id": uuid.uuid4().hex, "pk": "a"},
            response_hook=_hook,
        )

    cmp = await run_on_both_backends_async(
        _do,
        description="async response_hook fires exactly once per backend",
        request_kwargs={"response_hook": "<callable>"},
    )
    cmp.print_report()
    print("async response_hook fired: core-python={} rust={}".format(
        fired["core-python"], fired["rust"]))
    cmp.assert_functional_parity()
    assert fired["core-python"] == 1, "core-python should fire response_hook exactly once"
    assert fired["rust"] == 1, "rust should fire response_hook exactly once"


# ---------------------------------------------------------------------------
# Exception parity
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_async_duplicate_id_raises_typed_exception(container_for):
    """inserting the same id twice raises ``CosmosResourceExistsError``.

    Uses the functional exception assertion rather than the strict one: the
    rust binding exposes a smaller response-header surface on errors, which is
    a known and separately tracked gap, so demanding header-set equality here
    would fail every run for a reason unrelated to the exception contract.
    """
    fixed_id = uuid.uuid4().hex

    async def _do(client):
        cont = client.get_database_client("parity_db").get_container_client(container_for.id)
        await cont.create_item(body={"id": fixed_id, "pk": "a"})
        return await cont.create_item(body={"id": fixed_id, "pk": "a"})

    cmp = await run_on_both_backends_async(
        _do,
        description="async duplicate-id 409: insert id={!r} twice".format(fixed_id),
        request_body={"id": fixed_id, "pk": "a", "_note": "sent twice"},
    )
    cmp.print_report()
    assert not cmp.core_python.succeeded
    assert not cmp.rust.succeeded
    cmp.assert_functional_exception_parity()


# ---------------------------------------------------------------------------
# (additional) deprecated-but-ignored kwargs.
#
# ``etag`` and ``match_condition`` describe a precondition on an *existing*
# document, which an insert has none of. The documented contract is therefore
# "warn, then ignore" -- the call must still succeed. Pinning this per
# operation matters because the same two kwargs are load-bearing on
# ``delete_item`` and ``patch_item``, where they drive optimistic concurrency.
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


@pytest.mark.asyncio
async def test_async_etag_deprecated_and_ignored(container_for):
    """``etag`` on an async insert warns and is then dropped, not honoured.

    A backend that started *honouring* it would turn this success into a 412,
    so the assertion covers both halves: the warning fires and the insert still
    succeeds on both backends.
    """
    body = {"id": uuid.uuid4().hex, "pk": "a"}
    with warnings.catch_warnings(record=True) as recorded:
        warnings.simplefilter("always")
        cmp = await _run_create(container_for, body, summary="baseline + etag (deprecated/ignored)",
                                etag='"foo"')
    _assert_deprecation_warning_fired(recorded, "etag")
    cmp.assert_functional_parity()


@pytest.mark.asyncio
async def test_async_match_condition_deprecated_and_ignored(container_for):
    """``match_condition`` on an async insert warns and is then dropped."""
    body = {"id": uuid.uuid4().hex, "pk": "a"}
    with warnings.catch_warnings(record=True) as recorded:
        warnings.simplefilter("always")
        cmp = await _run_create(container_for, body, summary="baseline + match_condition (deprecated/ignored)",
                                match_condition=MatchConditions.IfNotModified)
    _assert_deprecation_warning_fired(recorded, "match_condition")
    cmp.assert_functional_parity()
