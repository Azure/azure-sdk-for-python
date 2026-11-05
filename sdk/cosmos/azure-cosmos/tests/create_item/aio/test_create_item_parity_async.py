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
  cleanly:
  ``indexing_directive``, ``session_token``, ``initial_headers``,
  ``priority``, ``throughput_bucket``.
* **behavioural kwargs.** ``enable_automatic_id_generation``,
  ``no_response``, ``retry_write``, ``availability_strategy``, ``timeout``.
* **``response_hook`` fires exactly once per backend.**
* **409.** Inserting the same id twice raises
  ``CosmosResourceExistsError`` on both.
* **retired kwargs.** ``populate_query_metrics``, ``etag``, and
  ``match_condition`` are rejected by presence, including None/False.

Deliberately NOT mirrored from the sync suite:

* The partitionless-container (``"[]"``) binding-rejection test and the
  intended-collection-rid wire test. Both assert against the shared binding
  rather than the async entry point, so running them again here would diff the
  same code twice and add nothing.
"""

from __future__ import annotations

import copy
import os
import uuid

import pytest


from azure.cosmos import CosmosClient, PartitionKey, exceptions
from azure.cosmos.aio._backend import binding_adapter as _rust_backend_module
from common._parity_helpers import BackendComparison, run_on_both_backends_async, skip_unless_emulator, skip_unless_rust_binding

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
async def test_async_baseline_body_and_pk_only_rust(container_for):
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
async def test_async_pk_undefined_rust(container_for):
    """body omits the declared PK path -- the undefined-PK wire shape.

    The binding accepts this and treats it as the undefined partition-key
    value end to end; the async path must round-trip it exactly as sync does.
    """
    body = {"id": uuid.uuid4().hex, "n": 1}
    cmp = await _run_create(container_for, body, summary="undefined PK")
    cmp.assert_functional_parity()


@pytest.mark.asyncio
async def test_async_pk_explicit_none_rust(container_for):
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
async def test_async_indexing_directive_rust(container_for):
    """Baseline call plus ``indexing_directive=1`` (Exclude) -- forwarded as a header.

    The value is an enum member on the wire, so this also pins that the async
    path converts the int the same way sync does rather than passing it raw.
    """
    body = {"id": uuid.uuid4().hex, "pk": "a"}
    cmp = await _run_create(container_for, body, summary="baseline + indexing_directive=Exclude",
                            indexing_directive=1)
    cmp.assert_functional_parity()


@pytest.mark.asyncio
async def test_async_session_token_rust(container_for, monkeypatch):
    """Pass a service-issued token to fresh async clients for the same container and partition."""
    seed_body = {"id": uuid.uuid4().hex, "pk": "a"}
    seed = container_for.create_item(body=seed_body)
    assert seed["id"] == seed_body["id"] and seed["pk"] == "a"
    token = seed.get_response_headers()["x-ms-session-token"]
    assert token, "Seed create must return a service-issued token"

    select = _rust_backend_module._binding_function_for_op
    native_create = select("create_item")
    native_ids = []

    async def capture(handle, prepared, **kwargs):
        assert prepared.settings.session_token == token, "Rust must receive the unchanged token"
        native_ids.append(prepared.item_id)
        return await native_create(handle, prepared, **kwargs)

    monkeypatch.setattr(
        _rust_backend_module, "_binding_function_for_op",
        lambda operation: capture if operation == "create_item" else select(operation),
    )
    body = {"id": uuid.uuid4().hex, "pk": "a"}
    cmp = await _run_create(container_for, body, summary="service-issued session_token on fresh clients",
                            session_token=token)
    # Legacy may omit write tokens; successful parity alone does not prove forwarding.
    for outcome in (cmp.core_python, cmp.rust):
        assert outcome.raised is None, outcome
        assert outcome.return_value["pk"] == "a", outcome
    assert native_ids == [cmp.rust.return_value["id"]], "Expected one real native create"
    cmp.assert_functional_parity()


@pytest.mark.asyncio
async def test_async_initial_headers_rust(container_for):
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
async def test_async_priority_rust(container_for):
    """Baseline call plus ``priority='High'`` -- the priority-based-throttling header."""
    body = {"id": uuid.uuid4().hex, "pk": "a"}
    cmp = await _run_create(container_for, body, summary="baseline + priority=High",
                            priority="High")
    cmp.assert_functional_parity()


@pytest.mark.asyncio
async def test_async_throughput_bucket_rust(container_for):
    """Baseline call plus ``throughput_bucket=1`` -- the throughput-bucket header."""
    body = {"id": uuid.uuid4().hex, "pk": "a"}
    cmp = await _run_create(container_for, body, summary="baseline + throughput_bucket",
                            throughput_bucket=1)
    cmp.assert_functional_parity()


# ---------------------------------------------------------------------------
# Behavioural kwargs
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_async_enable_automatic_id_generation_rust(container_for):
    """``enable_automatic_id_generation=True`` with no ``id`` in the body.

    Both backends must generate an id rather than reject the insert. The generated
    ids differ between backends by definition, so the harness's functional
    comparison (which tolerates server-assigned identity fields) is the right
    assertion here.
    """
    body = {"pk": "a", "n": 1}
    cmp = await _run_create(container_for, body, summary="baseline + enable_automatic_id_generation",
                            enable_automatic_id_generation=True)
    cmp.assert_functional_parity()


@pytest.mark.asyncio
async def test_async_no_response_rust(container_for):
    """``no_response=True`` -- the service must not echo the document back.

    This changes the *shape of the return value*, not just a header, so it is
    the async kwarg most likely to expose a helper divergence.
    """
    body = {"id": uuid.uuid4().hex, "pk": "a", "n": 1}
    cmp = await _run_create(container_for, body, summary="baseline + no_response",
                            no_response=True)
    cmp.assert_functional_parity()


@pytest.mark.skip(reason=(
    "Accepted design exclusion: docs/V5/api-review/RUST_PARITY_PUSHBACKS.md#gap-13. "
    "Rust owns automatic write retries and rejects non-None per-call retry_write; "
    "retain this legacy parity test for reference."
))
@pytest.mark.asyncio
async def test_async_retry_write_rust(container_for):
    """Retained legacy ``retry_write=1`` parity case; excluded by pushback 13."""
    body = {"id": uuid.uuid4().hex, "pk": "a"}
    cmp = await _run_create(container_for, body, summary="baseline + retry_write",
                            retry_write=1)
    cmp.assert_functional_parity()


@pytest.mark.asyncio
async def test_async_availability_strategy_rust(container_for):
    """``availability_strategy=True`` -- enables hedged cross-region requests."""
    body = {"id": uuid.uuid4().hex, "pk": "a"}
    cmp = await _run_create(container_for, body, summary="baseline + availability_strategy",
                            availability_strategy=True)
    cmp.assert_functional_parity()


@pytest.mark.asyncio
async def test_async_timeout_rust(container_for):
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
async def test_async_excluded_locations_rust(container_for):
    """``excluded_locations`` -- a Python-only routing override."""
    body = {"id": uuid.uuid4().hex, "pk": "a"}
    cmp = await _run_create(container_for, body, summary="baseline + excluded_locations",
                            excluded_locations=["East US"])
    cmp.assert_functional_parity()




@pytest.mark.skip(reason="Partial parity: the binding does not wire Python's "
                         "connection_timeout into the driver's connection-pool config yet. "
                         "Mirrors the sync suite's skip.")
@pytest.mark.asyncio
async def test_async_connection_timeout_rust(container_for):
    """``connection_timeout=10`` -- the azure-core HTTP connect timeout."""
    body = {"id": uuid.uuid4().hex, "pk": "a"}
    cmp = await _run_create(container_for, body, summary="baseline + connection_timeout=10",
                            connection_timeout=10)
    cmp.assert_functional_parity()


# ---------------------------------------------------------------------------
# Output / parsing parity
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_async_response_hook_fires_once_rust(container_for):
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
async def test_async_duplicate_id_raises_typed_exception_rust(container_for):
    """Each backend creates its own item, then gets a plain 409 on duplication.

    Compare the exception type and codes, not service text or header surfaces.
    """
    created_ids = []

    async def _do(client):
        fixed_id = uuid.uuid4().hex
        cont = client.get_database_client("parity_db").get_container_client(container_for.id)
        created = await cont.create_item(body={"id": fixed_id, "pk": "a"})
        assert created["id"] == fixed_id and created["pk"] == "a"
        created_ids.append(fixed_id)
        return await cont.create_item(body={"id": fixed_id, "pk": "a"})

    cmp = await run_on_both_backends_async(
        _do,
        description="async duplicate-id 409: create a distinct item twice per backend",
    )
    assert len(set(created_ids)) == 2, "Each backend must first create its own distinct item successfully"
    for outcome in (cmp.core_python, cmp.rust):
        assert isinstance(outcome.raised, exceptions.CosmosResourceExistsError), outcome
        assert outcome.raised.status_code == 409, outcome
        assert outcome.raised.sub_status in (None, 0), outcome


# ---------------------------------------------------------------------------
# Retired arguments are rejected by presence on both backends.
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
@pytest.mark.parametrize("name", ["populate_query_metrics", "etag", "match_condition"])
@pytest.mark.parametrize("value", [None, False, True])
async def test_async_retired_create_arguments_are_rejected_rust(container_for, name, value):
    body = {"id": uuid.uuid4().hex, "pk": "a"}
    comparison = await _run_create(container_for, body, summary=f"create rejects {name}", **{name: value})
    for outcome in (comparison.core_python, comparison.rust):
        assert isinstance(outcome.raised, TypeError)
