# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# -------------------------------------------------------------------------
"""End-to-end parity tests for ``Container.create_item`` across backends.

The suite is organised as a **graduated sequence**:

  * **L0 — baseline.** Body + the mandatory partition-key field, no
    optional kwargs. This test must pass for every other test in the
    file to be meaningful: if L0 fails, ``create_item`` is genuinely
    broken on one of the backends and there is no point reading the
    rest of the report.
  * **L1 — body / partition-key shape variants.** Same call shape as L0
    but flexes the PK side (undefined PK, explicit ``None``).
  * **L2 — header-bearing kwargs, one at a time.** Each test starts
    from L0 and adds **exactly one** optional kwarg that maps to a
    request header. If the test fails the diff cleanly attributes the
    gap to that one kwarg.
  * **L3 — behavioural kwargs.** Knobs that change behaviour rather
    than just header shape (auto id, no-response, retry-write,
    availability-strategy).
  * **L4 — output / parsing parity.** ``response_hook`` invocation
    count, etc.
  * **L5 — exception parity.** Typed exception class for the
    duplicate-id 409 case.

Every test prints a structured report (request body, request kwargs,
both backends' response bodies, response headers, diffs, and a
plain-English VERDICT line). The verdict distinguishes:

  * ``FULL PARITY`` — request and response bytes both equivalent.
  * ``FUNCTIONAL PARITY, REPORTING GAP`` — both backends performed
    the operation; only the *set of response headers exposed by the
    rust binding* differs (a known rust-binding limitation).
  * ``FUNCTIONAL DIVERGENCE`` — the operation behaved differently.
  * ``EXCEPTION DIVERGENCE`` — both raised but with different types.

Skips are stated in **plain English** in the reason string. The legacy
``C1 / C5a / C5b`` gap IDs are still mentioned for ``git grep``-ability
but the *first* clause of every reason is a one-line explanation a PM
or a new hire can read without the gap registry open.

The suite skips cleanly when:

  * ``ACCOUNT_URI`` / ``ACCOUNT_KEY`` are not set (no account wired), or
  * ``azure.cosmos._rust`` did not build (``maturin develop`` not run).
"""
from __future__ import annotations

import uuid
from typing import Any, Dict

import pytest

from common._parity_helpers import (
    run_on_both_backends,
    skip_unless_emulator,
    skip_unless_rust_binding,
)


pytestmark = [
    skip_unless_emulator(),
    skip_unless_rust_binding(),
]


# ---------------------------------------------------------------------------
# Per-test container fixture
# ---------------------------------------------------------------------------

@pytest.fixture
def container_for(request):
    """Build a fresh container per test, against a known db."""
    from azure.cosmos import CosmosClient, PartitionKey
    import os
    client = CosmosClient(os.environ["ACCOUNT_URI"], os.environ["ACCOUNT_KEY"])
    db = client.create_database_if_not_exists("parity_db")
    cname = "parity_" + request.node.name + "_" + uuid.uuid4().hex[:6]
    container = db.create_container(
        id=cname, partition_key=PartitionKey(path="/pk")
    )
    yield container
    try:
        db.delete_container(cname)
    except Exception:  # pylint: disable=broad-except
        pass


def _call(container_id: str, body_or_factory, **kwargs):
    """Build a closure that the harness invokes once per backend.

    ``body_or_factory`` is either a callable returning a fresh dict,
    or a plain dict (deep-copied per backend with a fresh ``id`` so
    backend 2 never sees backend 1's id as a duplicate).
    """
    import copy as _copy
    if callable(body_or_factory):
        builder = body_or_factory
    else:
        template = body_or_factory

        def builder():
            fresh = _copy.deepcopy(template)
            if "id" in fresh:
                fresh["id"] = uuid.uuid4().hex
            return fresh

    def _do(client):
        cont = client.get_database_client("parity_db").get_container_client(container_id)
        return cont.create_item(body=builder(), **kwargs)
    return _do


def _run(container, body, level: str, summary: str, **kwargs):
    """Run the call on both backends and print the side-by-side report."""
    description = "[{}] {} -- body keys={}, kwargs={}".format(
        level, summary,
        list(body.keys()) if isinstance(body, dict) else "(factory)",
        sorted(kwargs.keys()) or "(none)",
    )
    cmp = run_on_both_backends(
        _call(container.id, body, **kwargs),
        description=description,
        request_body=body if isinstance(body, dict) else None,
        request_kwargs=kwargs or None,
    )
    cmp.print_report()
    return cmp


# ---------------------------------------------------------------------------
# L0 — baseline: body + mandatory partition-key field, no optional kwargs.
# This test MUST pass for the rest of the suite to be meaningful.
# ---------------------------------------------------------------------------

def test_L0_baseline_body_and_pk_only(container_for):
    """Baseline: minimal valid body, no optional kwargs.

    Sends ``{"id": <uuid>, "pk": "customerA", "n": 1}`` and nothing else.
    Both backends must succeed and return equivalent response bodies.
    Response-header-surface differences are tolerated here (see the
    VERDICT line in the printed report) so this is a clean
    "create_item itself works on both backends" signal.
    """
    body = {"id": uuid.uuid4().hex, "pk": "customerA", "n": 1}
    _run(container_for, body, level="L0",
         summary="baseline create").assert_functional_parity()


# ---------------------------------------------------------------------------
# L1 — body / partition-key shape variants
# ---------------------------------------------------------------------------

@pytest.mark.skip(reason="C5a verification rerun pending — binding now accepts `[{}]`.")
def test_L1_pk_undefined(container_for):
    """L1: body missing the declared PK path -- wire bytes must be ``[{}]``."""
    body = {"id": uuid.uuid4().hex, "n": 1}
    _run(container_for, body, level="L1",
         summary="undefined PK").assert_functional_parity()


def test_L1_pk_explicit_none(container_for):
    """L1: explicit ``pk: None`` -- wire bytes must be ``[null]``.

    Python's PK serializer maps ``None -> [null]`` (see ``_pk_wire.py``)
    and the rust binding accepts JSON ``null`` as a valid PK value
    (see ``azure_cosmos_rust/src/lib.rs``), so this case is supported
    end-to-end on both backends. (Gap C5b covers the *different*
    partitionless ``[]`` case, not ``[null]``.)
    """
    body = {"id": uuid.uuid4().hex, "pk": None}
    _run(container_for, body, level="L1",
         summary="explicit None PK").assert_functional_parity()


# ---------------------------------------------------------------------------
# L2 -- header-bearing kwargs, one at a time.
# Each test = L0 baseline + EXACTLY ONE kwarg that maps to a request header.
# ---------------------------------------------------------------------------

# C1 closed binding-side (forwarded via OperationOptions::with_custom_headers).
def test_L2_pre_trigger_include(container_for):
    """L2: L0 + ``pre_trigger_include='validateOrder'`` (header kwarg)."""
    body = {"id": uuid.uuid4().hex, "pk": "a"}
    _run(container_for, body, level="L2",
         summary="L0 + pre_trigger_include",
         pre_trigger_include="validateOrder").assert_functional_parity()


# C1 closed binding-side (forwarded via OperationOptions::with_custom_headers).
def test_L2_indexing_directive(container_for):
    """L2: L0 + ``indexing_directive=Exclude`` (header kwarg)."""
    body = {"id": uuid.uuid4().hex, "pk": "a"}
    _run(container_for, body, level="L2",
         summary="L0 + indexing_directive=Exclude",
         indexing_directive=1).assert_functional_parity()


# C1 closed binding-side (forwarded via OperationOptions::with_custom_headers).
@pytest.mark.skip(
    reason="Test instrumentation can't observe rust's wire: it captures via "
           "SansIOHTTPPolicy on the azure-core pipeline, which the rust path "
           "bypasses. C1 binding fix DOES emit "
           "x-ms-cosmos-intended-collection-rid on the rust wire — covered "
           "by service-side acceptance only, not by this test."
)
def test_L2_intended_collection_rid_present_on_wire(container_for):
    """L2: assert ``x-ms-cosmos-intended-collection-rid`` is sent on the REQUEST.

    The intended-collection-rid header is a *request-side* safety net
    for container-recreate detection (see
    ``azure/cosmos/_helpers/_container_rid.py``). Validating it on the
    response is the wrong channel -- the service does not echo it
    back. This test installs a ``SansIOHTTPPolicy`` that captures the
    outgoing request headers per backend, then asserts both backends
    stamped the container's rid on the wire.

    The rust backend bypasses the Python azure-core pipeline for the
    data-plane call, so the policy below cannot observe what the rust
    binding actually sends today -- that is the C1 reporting gap this
    skip references. When the rust binding exposes outgoing request
    headers (or routes the call back through the Python pipeline),
    flip the skip off and this assertion becomes meaningful end-to-end.
    """
    from azure.core.pipeline.policies import SansIOHTTPPolicy
    from azure.cosmos import CosmosClient
    import os

    captured = {"core-python": None, "rust": None}

    class _CaptureRequestHeaders(SansIOHTTPPolicy):
        def __init__(self, sink):
            super().__init__()
            self._sink = sink

        def on_request(self, request):  # type: ignore[override]
            self._sink["last"] = dict(request.http_request.headers)

    def _factory(backend_name: str):
        sink: Dict[str, Any] = {}
        captured[backend_name] = sink  # type: ignore[assignment]
        return CosmosClient(
            os.environ["ACCOUNT_URI"],
            os.environ["ACCOUNT_KEY"],
            _backend=backend_name,  # type: ignore[arg-type]
            per_call_policies=[_CaptureRequestHeaders(sink)],
        )

    body = {"id": uuid.uuid4().hex, "pk": "a"}

    def _do(client):
        cont = client.get_database_client("parity_db").get_container_client(container_for.id)
        return cont.create_item(body=body)

    cmp = run_on_both_backends(
        _do,
        client_factory=_factory,
        description="[L2] L0 + assert intended-rid REQUEST header",
        request_body=body,
    )
    cmp.print_report()

    key = "x-ms-cosmos-intended-collection-rid"
    core_req = (captured["core-python"] or {}).get("last", {})
    rust_req = (captured["rust"] or {}).get("last", {})
    core_val = core_req.get(key)
    rust_val = rust_req.get(key)
    print("[L2] outgoing intended-rid: core-python={!r} rust={!r}".format(core_val, rust_val))
    assert core_val, "core-python must stamp intended-collection-rid on the request"
    assert rust_val, "rust must stamp intended-collection-rid on the request"
    assert core_val == rust_val, (
        "intended-rid request header parity broken: core={!r} rust={!r}".format(
            core_val, rust_val
        )
    )


# C1 closed binding-side (forwarded via OperationOptions::with_custom_headers).
def test_L2_priority_high(container_for):
    """L2: L0 + ``priority='High'`` (header kwarg)."""
    body = {"id": uuid.uuid4().hex, "pk": "a"}
    _run(container_for, body, level="L2",
         summary="L0 + priority=High",
         priority="High").assert_functional_parity()


# ---------------------------------------------------------------------------
# L2 (additional) -- header-bearing kwargs from the public surface that
# weren't covered above. Each is the L0 baseline + EXACTLY ONE kwarg.
# All currently skipped under C1 (rust binding drops these headers).
# ---------------------------------------------------------------------------

# C1 closed binding-side (forwarded via OperationOptions::with_custom_headers).
def test_L2_post_trigger_include(container_for):
    """L2: L0 + ``post_trigger_include='auditOrder'`` (header kwarg)."""
    body = {"id": uuid.uuid4().hex, "pk": "a"}
    _run(container_for, body, level="L2",
         summary="L0 + post_trigger_include",
         post_trigger_include="auditOrder").assert_functional_parity()


# C1 closed binding-side for typed session token forwarding.
def test_L2_session_token(container_for):
    """L2: L0 + ``session_token=<token>`` (Session-consistency header kwarg)."""
    body = {"id": uuid.uuid4().hex, "pk": "a"}
    _run(container_for, body, level="L2",
         summary="L0 + session_token",
         session_token="0:1#42").assert_functional_parity()


# C1 closed binding-side (forwarded via OperationOptions::with_custom_headers).
@pytest.mark.skip(
    reason="initial_headers does not flow through PreparedRequest.headers "
           "today (build_options does not merge it into options, and "
           "_request_prep only iterates options). The binding WOULD "
           "forward any x-ms-... key landing on PreparedRequest.headers — "
           "pending a Python-side helper change to plumb initial_headers."
)
def test_L2_initial_headers(container_for):
    """L2: L0 + ``initial_headers={'x-ms-test': 'v'}`` (caller-injected headers)."""
    body = {"id": uuid.uuid4().hex, "pk": "a"}
    _run(container_for, body, level="L2",
         summary="L0 + initial_headers",
         initial_headers={"x-ms-test-parity": "v1"}).assert_functional_parity()


# C1 closed binding-side (forwarded via OperationOptions::with_custom_headers).
def test_L2_throughput_bucket(container_for):
    """L2: L0 + ``throughput_bucket=1`` (``x-ms-cosmos-throughput-bucket`` hdr)."""
    body = {"id": uuid.uuid4().hex, "pk": "a"}
    _run(container_for, body, level="L2",
         summary="L0 + throughput_bucket=1",
         throughput_bucket=1).assert_functional_parity()


# ---------------------------------------------------------------------------
# L3 — behavioural kwargs (change behaviour, not just header shape)
# ---------------------------------------------------------------------------

def test_L3_enable_automatic_id_generation(container_for):
    """Body without `id` — the Python helper mints a UUID4 client-side and
    writes it back into the body before either backend sees it. Both
    backends therefore see an identical body shape."""
    body = {"pk": "a"}  # no id — helper will mint one
    _run(container_for, body, level="L3",
         summary="auto-id (no `id` in body)",
         enable_automatic_id_generation=True).assert_functional_parity()


# L3: no_response — binding now maps responsePayloadOnWriteDisabled
# onto OperationOptions.content_response_on_write (options half of C1).
def test_L3_no_response(container_for):
    """L3: L0 + ``no_response=True`` (suppresses response body via Prefer hdr)."""
    body = {"id": uuid.uuid4().hex, "pk": "a"}
    _run(container_for, body, level="L3",
         summary="L0 + no_response",
         no_response=True).assert_functional_parity()


@pytest.mark.skip(reason="Permanent skip: no rust-side equivalent (Python-only knob).")
def test_L3_retry_write(container_for):
    """L3: L0 + ``retry_write=1`` (Python-only retry knob; no rust analogue)."""
    body = {"id": uuid.uuid4().hex, "pk": "a"}
    _run(container_for, body, level="L3",
         summary="L0 + retry_write=1",
         retry_write=1).assert_functional_parity()


@pytest.mark.skip(reason="Permanent skip: no rust-side equivalent (Python-only knob).")
def test_L3_availability_strategy(container_for):
    """L3: L0 + ``availability_strategy=True`` (Python-only hedging feature)."""
    body = {"id": uuid.uuid4().hex, "pk": "a"}
    _run(container_for, body, level="L3",
         summary="L0 + availability_strategy=True",
         availability_strategy=True).assert_functional_parity()


# ---------------------------------------------------------------------------
# L3 (additional) -- behavioural / Python-only kwargs from the public surface.
# ---------------------------------------------------------------------------

@pytest.mark.skip(reason="Permanent skip: no rust-side equivalent (Python-only routing knob).")
def test_L3_excluded_locations(container_for):
    """L3: L0 + ``excluded_locations=['East US']`` (Python-only routing override)."""
    body = {"id": uuid.uuid4().hex, "pk": "a"}
    _run(container_for, body, level="L3",
         summary="L0 + excluded_locations",
         excluded_locations=["East US"]).assert_functional_parity()


@pytest.mark.skip(reason="Permanent skip: timeouts are azure-core pipeline knobs (Python-only).")
def test_L3_timeout(container_for):
    """L3: L0 + ``timeout=30`` (overall request timeout; azure-core only)."""
    body = {"id": uuid.uuid4().hex, "pk": "a"}
    _run(container_for, body, level="L3",
         summary="L0 + timeout=30",
         timeout=30).assert_functional_parity()


@pytest.mark.skip(reason="Permanent skip: read_timeout is an azure-core pipeline knob (Python-only).")
def test_L3_read_timeout(container_for):
    """L3: L0 + ``read_timeout=30`` (azure-core HTTP read timeout)."""
    body = {"id": uuid.uuid4().hex, "pk": "a"}
    _run(container_for, body, level="L3",
         summary="L0 + read_timeout=30",
         read_timeout=30).assert_functional_parity()


@pytest.mark.skip(reason="Permanent skip: connection_timeout is an azure-core pipeline knob (Python-only).")
def test_L3_connection_timeout(container_for):
    """L3: L0 + ``connection_timeout=10`` (azure-core HTTP connect timeout)."""
    body = {"id": uuid.uuid4().hex, "pk": "a"}
    _run(container_for, body, level="L3",
         summary="L0 + connection_timeout=10",
         connection_timeout=10).assert_functional_parity()


# ---------------------------------------------------------------------------
# L4 — output / parsing parity
# ---------------------------------------------------------------------------

def test_L4_response_hook_fires_once(container_for):
    """L4: ``response_hook`` must fire exactly once per backend on success.

    Goes through the same ``run_on_both_backends`` harness as every
    other test in this file, so the printed PARITY CALL block, the
    response-body diff, and the VERDICT line are all produced by the
    shared reporter. Per-backend hook-fire counts are tracked via an
    invocation-order counter (the harness deterministically runs
    core-python first, then rust) and asserted after the diff.
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
        return cont.create_item(
            body={"id": uuid.uuid4().hex, "pk": "a"},
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
# L5 — exception parity
# ---------------------------------------------------------------------------

def test_L5_duplicate_id_raises_typed_exception(container_for):
    """Inserting the same id twice must raise ``CosmosResourceExistsError``
    (HTTP 409, sub_status 0) on **both** backends."""
    fixed_id = uuid.uuid4().hex

    def _do(client):
        cont = client.get_database_client("parity_db").get_container_client(container_for.id)
        cont.create_item(body={"id": fixed_id, "pk": "a"})
        return cont.create_item(body={"id": fixed_id, "pk": "a"})

    cmp = run_on_both_backends(
        _do,
        description="[L5] duplicate-id 409: insert id={!r} twice".format(fixed_id),
        request_body={"id": fixed_id, "pk": "a", "_note": "sent twice"},
    )
    cmp.print_report()
    assert not cmp.core_python.succeeded
    assert not cmp.rust.succeeded
    cmp.assert_parity()


# ---------------------------------------------------------------------------
# L5 (additional) -- deprecated kwargs. The contract is "ignored, but emit
# a DeprecationWarning". These tests verify that contract on core-python
# (the only backend that runs the Python create_item entry point that owns
# the warning) and run the call through the harness so any future divergence
# in behaviour shows up in the printed report.
# ---------------------------------------------------------------------------

def _assert_deprecation_warning_fired(recorded, kwarg_name: str) -> None:
    matches = [w for w in recorded
               if issubclass(w.category, DeprecationWarning)
               and kwarg_name in str(w.message)]
    assert matches, (
        "expected a DeprecationWarning mentioning {!r}, got: {}".format(
            kwarg_name, [str(w.message) for w in recorded]
        )
    )


def test_L5_populate_query_metrics_deprecated(container_for):
    """L5: ``populate_query_metrics=True`` is deprecated on create_item.

    The Python entry point must emit a ``DeprecationWarning`` and otherwise
    behave like the L0 baseline. The flag does not reach the wire, so both
    backends should produce equivalent results.
    """
    import warnings
    body = {"id": uuid.uuid4().hex, "pk": "a"}
    with warnings.catch_warnings(record=True) as recorded:
        warnings.simplefilter("always")
        cmp = _run(container_for, body, level="L5",
                   summary="L0 + populate_query_metrics=True (deprecated)",
                   populate_query_metrics=True)
    _assert_deprecation_warning_fired(recorded, "populate_query_metrics")
    cmp.assert_functional_parity()


def test_L5_etag_deprecated_and_ignored(container_for):
    """L5: ``etag='"foo"'`` is deprecated and ignored on create_item.

    The Python entry point must emit a ``DeprecationWarning`` and the
    request must succeed regardless (the value is dropped, not honoured).
    """
    import warnings
    body = {"id": uuid.uuid4().hex, "pk": "a"}
    with warnings.catch_warnings(record=True) as recorded:
        warnings.simplefilter("always")
        cmp = _run(container_for, body, level="L5",
                   summary="L0 + etag='\"foo\"' (deprecated/ignored)",
                   etag='"foo"')
    _assert_deprecation_warning_fired(recorded, "etag")
    cmp.assert_functional_parity()


def test_L5_match_condition_deprecated_and_ignored(container_for):
    """L5: ``match_condition=MatchConditions.IfNotModified`` is deprecated/ignored."""
    import warnings
    from azure.core import MatchConditions
    body = {"id": uuid.uuid4().hex, "pk": "a"}
    with warnings.catch_warnings(record=True) as recorded:
        warnings.simplefilter("always")
        cmp = _run(container_for, body, level="L5",
                   summary="L0 + match_condition (deprecated/ignored)",
                   match_condition=MatchConditions.IfNotModified)
    _assert_deprecation_warning_fired(recorded, "match_condition")
    cmp.assert_functional_parity()

