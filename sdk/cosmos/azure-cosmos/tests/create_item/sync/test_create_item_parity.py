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

Skips are stated in **plain English** in the reason string -- the
first clause of every reason is a one-line explanation a PM or a new
hire can read without any internal tracker open.

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

# The binding accepts ``[{}]`` and maps it to the typed undefined
# partition-key value end-to-end; this test pins that round-trip.
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
    end-to-end on both backends. (The partitionless ``[]`` case is a
    separate, still-rejected shape -- see the partitionless-rejection
    test at the bottom of the file.)
    """
    body = {"id": uuid.uuid4().hex, "pk": None}
    _run(container_for, body, level="L1",
         summary="explicit None PK").assert_functional_parity()


# ---------------------------------------------------------------------------
# L2 -- header-bearing kwargs, one at a time.
# Each test = L0 baseline + EXACTLY ONE kwarg that maps to a request header.
# ---------------------------------------------------------------------------

# Binding forwards the per-request header through the driver's custom-headers channel.
def test_L2_pre_trigger_include(container_for):
    """L2: L0 + ``pre_trigger_include='validateOrder'`` (header kwarg)."""
    body = {"id": uuid.uuid4().hex, "pk": "a"}
    _run(container_for, body, level="L2",
         summary="L0 + pre_trigger_include",
         pre_trigger_include="validateOrder").assert_functional_parity()


# Binding forwards the per-request header through the driver's custom-headers channel.
def test_L2_indexing_directive(container_for):
    """L2: L0 + ``indexing_directive=Exclude`` (header kwarg)."""
    body = {"id": uuid.uuid4().hex, "pk": "a"}
    _run(container_for, body, level="L2",
         summary="L0 + indexing_directive=Exclude",
         indexing_directive=1).assert_functional_parity()


# Binding forwards the per-request header through the driver's custom-headers channel.
def test_L2_intended_collection_rid_present_on_wire(container_for):
    """L2: assert ``x-ms-cosmos-intended-collection-rid`` is sent on the REQUEST.

    The intended-collection-rid header is a *request-side* safety net
    for container-recreate detection (see
    ``azure/cosmos/_helpers/_container_rid.py``). The service does not
    echo it back, so validating it on the response is the wrong
    channel — we have to look at the outgoing request.

    The two backends are observed through different lenses because the
    rust path bypasses azure-core entirely:

      * **core-python** — a ``SansIOHTTPPolicy`` on the azure-core
        pipeline captures the outgoing HTTP request headers. The
        ``x-ms-cosmos-intended-collection-rid`` header must be present
        with the container's ``_rid`` as its value.
      * **rust** — the binding consumes a ``PreparedRequest`` whose
        ``headers`` map already carries the container rid under the
        ``containerRID`` option-key (see ``_Constants.ContainerRID``).
        The lib.rs header loop translates this exact key to the
        ``x-ms-cosmos-intended-collection-rid`` wire header before
        handing the call to the driver. We monkey-patch
        ``RustBackend.execute`` to capture the PreparedRequest the
        helper hands it and assert the key is populated. The
        Rust-side wire mapping itself is exercised by the binding's
        own unit tests and the service-side acceptance suite.

    A previous revision skipped this test because the
    ``SansIOHTTPPolicy`` cannot observe the rust wire. That skip was a
    test-instrumentation gap, not a missing binding feature — the
    binding has always emitted the header. This rewrite removes the
    skip by observing the binding's *input* instead of trying to
    observe its output.
    """
    from azure.core.pipeline.policies import SansIOHTTPPolicy
    from azure.cosmos import CosmosClient
    from azure.cosmos._backend import rust as _rust_backend_module
    from azure.cosmos._constants import _Constants
    import os

    intended_rid_header = "x-ms-cosmos-intended-collection-rid"

    core_request_headers: Dict[str, Any] = {}
    rust_prepared_headers: Dict[str, Any] = {}

    class _CaptureCoreRequestHeaders(SansIOHTTPPolicy):
        def on_request(self, request):  # type: ignore[override]
            # Only keep the last create_item request; trivia like
            # account-metadata pre-flight reads also flow through this
            # policy and would otherwise overwrite our capture.
            url = getattr(request.http_request, "url", "")
            if "/docs" in url:
                core_request_headers.update(dict(request.http_request.headers))

    # Monkey-patch RustBackend.execute for the duration of the call so
    # we can grab the PreparedRequest the helper handed it. We restore
    # the original method in a finally block so other tests in the
    # session see the unpatched class.
    original_execute = _rust_backend_module.RustBackend.execute

    def _capturing_execute(self, prepared):  # type: ignore[no-redef]
        if prepared is not None and getattr(prepared, "op", None) == "create_item":
            rust_prepared_headers.update(dict(prepared.headers))
        return original_execute(self, prepared)

    def _core_factory(_backend_name: str):
        return CosmosClient(
            os.environ["ACCOUNT_URI"],
            os.environ["ACCOUNT_KEY"],
            _backend="core-python",  # type: ignore[arg-type]
            per_call_policies=[_CaptureCoreRequestHeaders()],
        )

    def _rust_factory(_backend_name: str):
        return CosmosClient(
            os.environ["ACCOUNT_URI"],
            os.environ["ACCOUNT_KEY"],
            _backend="rust",  # type: ignore[arg-type]
        )

    body = {"id": uuid.uuid4().hex, "pk": "a"}

    def _do(client):
        cont = (
            client.get_database_client("parity_db").get_container_client(container_for.id)
        )
        return cont.create_item(body=body)

    _rust_backend_module.RustBackend.execute = _capturing_execute  # type: ignore[method-assign]
    try:
        # Run core-python and rust through ``run_on_both_backends`` so
        # the structured PARITY CALL report still lands in the
        # transcript. The wrapper picks the right factory per backend.
        def _factory(backend_name: str):
            return (
                _core_factory(backend_name)
                if backend_name == "core-python"
                else _rust_factory(backend_name)
            )

        cmp = run_on_both_backends(
            _do,
            client_factory=_factory,
            description="[L2] L0 + assert intended-rid on REQUEST (both backends)",
            request_body=body,
        )
        cmp.print_report()
    finally:
        _rust_backend_module.RustBackend.execute = original_execute  # type: ignore[method-assign]

    # core-python: the wire header itself.
    core_val = core_request_headers.get(intended_rid_header)
    assert core_val, (
        "core-python must stamp {!r} on the outgoing request; "
        "captured headers: {!r}".format(intended_rid_header, sorted(core_request_headers))
    )

    # rust: the PreparedRequest's option-key the binding translates to
    # the wire header. We assert *both* the option-key form (what the
    # helper writes) and the lowercase wire-name form (in case a
    # future helper revision writes the wire-name directly) — exactly
    # one of them must be present and equal to core-python's value.
    rust_val = (
        rust_prepared_headers.get(_Constants.ContainerRID)
        or rust_prepared_headers.get(intended_rid_header)
    )
    assert rust_val, (
        "rust PreparedRequest.headers must carry the container rid under "
        "{!r} (or the wire-name {!r}) for the binding to translate it to "
        "the {!r} header; captured: {!r}".format(
            _Constants.ContainerRID,
            intended_rid_header,
            intended_rid_header,
            sorted(rust_prepared_headers),
        )
    )
    assert core_val == rust_val, (
        "intended-rid parity broken: core-python wire value {!r} != "
        "rust PreparedRequest value {!r}".format(core_val, rust_val)
    )
    print(
        "[L2] intended-rid parity OK: core-wire={!r} rust-prepared={!r}".format(
            core_val, rust_val
        )
    )


# Binding forwards the per-request header through the driver's custom-headers channel.
def test_L2_priority_high(container_for):
    """L2: L0 + ``priority='High'`` (header kwarg)."""
    body = {"id": uuid.uuid4().hex, "pk": "a"}
    _run(container_for, body, level="L2",
         summary="L0 + priority=High",
         priority="High").assert_functional_parity()


# ---------------------------------------------------------------------------
# L2 (additional) -- header-bearing kwargs from the public surface that
# weren't covered above. Each is the L0 baseline + EXACTLY ONE kwarg.
# (Historical note: these all used to be skipped while the binding still dropped per-request headers; the binding now forwards them.)
# ---------------------------------------------------------------------------

# Binding forwards the per-request header through the driver's custom-headers channel.
def test_L2_post_trigger_include(container_for):
    """L2: L0 + ``post_trigger_include='auditOrder'`` (header kwarg)."""
    body = {"id": uuid.uuid4().hex, "pk": "a"}
    _run(container_for, body, level="L2",
         summary="L0 + post_trigger_include",
         post_trigger_include="auditOrder").assert_functional_parity()


# Binding routes the session token to the driver's typed setter.
def test_L2_session_token(container_for):
    """L2: L0 + ``session_token=<token>`` (Session-consistency header kwarg)."""
    body = {"id": uuid.uuid4().hex, "pk": "a"}
    _run(container_for, body, level="L2",
         summary="L0 + session_token",
         session_token="0:1#42").assert_functional_parity()


# Binding forwards the per-request header through the driver's custom-headers channel.
# Python side: ``_request_prep.py`` now flattens the ``initialHeaders`` dict
# into individual entries on ``PreparedRequest.headers`` so the binding's
# existing ``x-ms-…``/``prefer`` pass-through picks each one up.
def test_L2_initial_headers(container_for):
    """L2: L0 + ``initial_headers={'x-ms-test': 'v'}`` (caller-injected headers)."""
    body = {"id": uuid.uuid4().hex, "pk": "a"}
    _run(container_for, body, level="L2",
         summary="L0 + initial_headers",
         initial_headers={"x-ms-test-parity": "v1"}).assert_functional_parity()


# Binding forwards the per-request header through the driver's custom-headers channel.
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
# onto the driver's typed content_response_on_write option.
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
    """L3: L0 + ``excluded_locations=['East US']`` (Python-only routing override).

    Binding now translates this kwarg into the driver's typed
    ``OperationOptions::excluded_regions`` field (see
    ``azure_cosmos_rust/src/lib.rs`` -- the ``excludedlocations`` arm
    builds an ``ExcludedRegions`` from the supplied region names via
    ``Region::from`` and attaches it through
    ``OperationOptionsBuilder::with_excluded_regions``). The skip is
    kept *only* because the parity assertion is hard to make
    end-to-end against a single-region test account: ``["East US"]``
    on a westus2-only account exercises no routing decision the
    legacy path would diff against. Remove this skip once the parity
    harness gains a multi-region fixture (or a fault-injection
    transport that can observe the request-time region choice).
    """
    body = {"id": uuid.uuid4().hex, "pk": "a"}
    _run(container_for, body, level="L3",
         summary="L0 + excluded_locations",
         excluded_locations=["East US"]).assert_functional_parity()


def test_L3_timeout(container_for):
    """L3: L0 + ``timeout=30`` (overall request timeout).

    Both backends now honour this kwarg: legacy via the azure-core
    pipeline's per-call timeout policy, Rust via the binding lifting
    the value into the driver's typed
    ``EndToEndOperationLatencyPolicy`` (see lib.rs --
    ``__overall_timeout_seconds`` arm; ``_helpers/_request_prep.py``
    stamps the sentinel header). Sub-second values are clamped by
    the driver to its 1 s floor; the parity harness uses 30 s, well
    above that floor.
    """
    body = {"id": uuid.uuid4().hex, "pk": "a"}
    _run(container_for, body, level="L3",
         summary="L0 + timeout=30",
         timeout=30).assert_functional_parity()


@pytest.mark.skip(reason="Partial parity: the driver has client-level analogs via "
                          "ConnectionPoolOptions::{min,max}_dataplane_request_timeout "
                          "(reqwest's builder.timeout) and TransportRequest::timeout for the per-call "
                          "override, but `OperationOptions` doesn't yet expose a per-call hook and the "
                          "binding doesn't construct the pool options from Python's `read_timeout` "
                          "kwarg. Driver-level support exists; per-call parity is a binding follow-up.")
def test_L3_read_timeout(container_for):
    """L3: L0 + ``read_timeout=30`` (azure-core HTTP read timeout)."""
    body = {"id": uuid.uuid4().hex, "pk": "a"}
    _run(container_for, body, level="L3",
         summary="L0 + read_timeout=30",
         read_timeout=30).assert_functional_parity()


@pytest.mark.skip(reason="Partial parity: the driver has client-level analogs via "
                          "ConnectionPoolOptions::{min,max}_connect_timeout (reqwest's "
                          "builder.connect_timeout) and the env var "
                          "AZURE_COSMOS_CONNECTION_POOL_MAX_CONNECT_TIMEOUT_MS, but the binding "
                          "doesn't yet wire Python's `connection_timeout` kwarg into the pool config. "
                          "No per-call hook today; client-level parity is a binding follow-up.")
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


# ---------------------------------------------------------------------------
# L1 (gap) -- partitionless container / NonePartitionKey on the wire.
#
# ``_pk_wire.serialize_partition_key_to_wire`` maps
# ``_Empty()`` / ``NonePartitionKeyValue`` to the JSON literal ``"[]"``.
# Both legacy v4.x and the helper layer treat this as the wire shape
# for a partitionless container's create_item. The Rust binding's
# ``parse_partition_key_header`` (azure_cosmos_rust/src/lib.rs)
# explicitly rejects ``"[]"`` because the underlying driver currently
# overloads ``PartitionKey::EMPTY`` to mean "cross-partition query":
# emitting it would set the ``x-ms-documentdb-query-enablecrosspartition``
# header instead of ``x-ms-documentdb-partitionkey: []`` and silently
# route the write to the wrong code path. Until the driver splits the
# two concepts, the binding must keep failing fast.
#
# This test pins both halves of that contract end-to-end on the rust
# path so the gap is *exercised in CI* rather than only described in
# comments. It is intentionally binding-scoped (no live partitionless
# container required from the fixture) -- the moment the binding stops
# raising on ``"[]"`` (because the driver gap closed), this test will
# fail loudly and force a follow-up to either:
#   (a) flip it into a full live parity test against a partitionless
#       container fixture, or
#   (b) delete it together with the binding's rejection branch.
# ---------------------------------------------------------------------------

def test_L1_partitionless_container_rejected_by_rust_binding():
    """L1 gap: ``partition_key_header == "[]"`` is rejected by the binding.

    Build a ``PreparedRequest`` whose ``partition_key_header`` is the
    NonePartitionKey wire shape and hand it directly to ``RustBackend.execute``.
    The binding must raise ``ValueError`` with a message that names the
    partitionless-container limitation in plain English, so an engineer
    chasing a flaky partitionless write knows exactly what they hit and
    which backend to use as a workaround.
    """
    import os
    import pytest
    from azure.cosmos._backend.base import OP_CREATE_ITEM, PreparedRequest
    from azure.cosmos._backend.rust import RustBackend

    # The endpoint / key are only needed to build the driver handle on
    # the first call. The request itself fails *before* any network IO
    # because parse_partition_key_header rejects the wire shape during
    # PreparedRequest validation. We still need a backend instance to
    # exercise the rejection through the public dispatch surface.
    endpoint = os.environ.get("ACCOUNT_URI")
    master_key = os.environ.get("ACCOUNT_KEY")
    if not endpoint or not master_key:
        pytest.skip(
            "ACCOUNT_URI / ACCOUNT_KEY not set; this test needs a real "
            "endpoint to bootstrap the Rust driver before the binding "
            "ever inspects the partition-key header."
        )

    backend = RustBackend(endpoint=endpoint, master_key=master_key)
    body = {"id": uuid.uuid4().hex, "pk": "a"}
    import json as _json
    prepared = PreparedRequest(
        op=OP_CREATE_ITEM,
        container_link="dbs/parity_db/colls/does_not_matter",
        body_bytes=_json.dumps(body).encode("utf-8"),
        partition_key_header="[]",  # the NonePartitionKey wire shape
        headers={},
    )

    # The binding wraps every internal error as ``RuntimeError`` /
    # ``ValueError`` from PyO3. The rejection comes from
    # ``parse_partition_key_header`` (PyValueError on the Rust side ->
    # ``ValueError`` on the Python side). ``pytest.raises`` matches the
    # exception class plus a regex against the message so a future
    # rewording of the error has to be a deliberate test update.
    with pytest.raises((ValueError, RuntimeError)) as excinfo:
        backend.execute(prepared)

    message = str(excinfo.value)
    assert "partitionless" in message.lower(), (
        "Rust binding must reject partition_key_header='[]' with a message "
        "naming the partitionless-container limitation; got: {!r}".format(message)
    )
    print(
        "[L1] partitionless container rejection pinned: {}".format(message)
    )



