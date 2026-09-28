# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# -------------------------------------------------------------------------
"""End-to-end parity tests for ``Container.create_item`` across backends.

The suite is organised as a **graduated sequence**:

  * **baseline.** Body + the mandatory partition-key field, no
    optional kwargs. This test must pass for every other test in the
    file to be meaningful: if the baseline fails, ``create_item`` is genuinely
    broken on one of the backends and there is no point reading the
    rest of the report.
  * **body / partition-key shape variants.** Same call shape as the baseline
    but flexes the PK side (undefined PK, explicit ``None``).
  * **header-bearing kwargs, one at a time.** Each test starts
    from the baseline and adds **exactly one** optional kwarg that maps to a
    request header. If the test fails the diff cleanly attributes the
    gap to that one kwarg.
  * **behavioural kwargs.** Options that change behaviour rather
    than just header shape (auto id, no-response, retry-write,
    availability-strategy).
  * **output / parsing parity.** ``response_hook`` invocation
    count, etc.
  * **exception parity.** Typed exception class for the
    duplicate-id 409 case.

Every test prints a structured report (request body, request kwargs,
both backends' response bodies, response headers, diffs, and a
plain-English VERDICT line). The verdict distinguishes:

  * ``FULL PARITY`` -- request and response bytes both equivalent.
  * ``FUNCTIONAL PARITY, HEADER GAP`` -- both backends performed
    the operation; only the *set of response headers exposed by the
    rust binding* differs (a known rust-binding limitation).
  * ``FUNCTIONAL DIVERGENCE`` -- the operation behaved differently.
  * ``EXCEPTION DIVERGENCE`` -- both raised but with different types.

Skips are stated in **plain English** in the reason string -- the
first clause of every reason is a one-line explanation a PM or a new
hire can read without any internal tracker open.

The suite skips cleanly when:

  * ``ACCOUNT_HOST`` / ``ACCOUNT_KEY`` are not set (no account wired), or
  * ``azure.cosmos._rust`` did not build (``maturin develop`` not run).
"""
from __future__ import annotations
import copy
import json
import os
import uuid
from typing import Any, Dict

import pytest

from azure.cosmos import CosmosClient, PartitionKey, exceptions
from azure.cosmos import _cosmos_client_connection as _ccc_module
from azure.cosmos._backend import binding_adapter as _rust_backend_module
from azure.cosmos._backend.operations import OP_CREATE_ITEM
from azure.cosmos._backend.contracts import PreparedRequest
from azure.cosmos._backend.partition_key_input import BindingPartitionKey
from azure.cosmos._backend.binding_adapter import BindingAdapter
from azure.cosmos._constants import _Constants

from common._parity_helpers import run_on_both_backends, skip_unless_emulator, skip_unless_rust_binding
from common.parity_provisioning import create_owned_container


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
    cname = "parity_" + request.node.name + "_" + uuid.uuid4().hex[:6]
    with CosmosClient(os.environ["ACCOUNT_HOST"], os.environ["ACCOUNT_KEY"]) as client:
        db = client.create_database_if_not_exists("parity_db")
        try:
            container = create_owned_container(db, id=cname, partition_key=PartitionKey(path="/pk"))
            yield container
        finally:
            try:
                db.delete_container(cname)
            except exceptions.CosmosResourceNotFoundError:
                pass


def _call(container_id: str, body_or_factory, **kwargs):
    """Build a closure that the harness invokes once per backend.

    ``body_or_factory`` is either a callable returning a fresh dict,
    or a plain dict (deep-copied per backend with a fresh ``id`` so
    backend 2 never sees backend 1's id as a duplicate).
    """
    if callable(body_or_factory):
        builder = body_or_factory
    else:
        template = body_or_factory

        def builder():
            fresh = copy.deepcopy(template)
            if "id" in fresh:
                fresh["id"] = uuid.uuid4().hex
            return fresh

    def _do(client):
        cont = client.get_database_client("parity_db").get_container_client(container_id)
        return cont.create_item(body=builder(), **kwargs)
    return _do


def _run(container, body, summary: str, **kwargs):
    """Run the call on both backends and print the side-by-side report."""
    description = "{} -- body keys={}, kwargs={}".format(
        summary,
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
# Baseline: body + mandatory partition-key field, no optional kwargs.
# This test MUST pass for the rest of the suite to be meaningful.
# ---------------------------------------------------------------------------

def test_baseline_body_and_pk_only(container_for):
    """Baseline: minimal valid body, no optional kwargs.

    Sends ``{"id": <uuid>, "pk": "customerA", "n": 1}`` and nothing else.
    Both backends must succeed and return equivalent response bodies.
    Response-header-surface differences are tolerated here (see the
    VERDICT line in the printed report) so this is a clean
    "create_item itself works on both backends" signal.
    """
    body = {"id": uuid.uuid4().hex, "pk": "customerA", "n": 1}
    _run(container_for, body, summary="baseline create").assert_functional_parity()


# ---------------------------------------------------------------------------
# Body / partition-key shape variants
# ---------------------------------------------------------------------------

# Compare the omitted-key case through the public clients.
def test_pk_undefined(container_for):
    """Compare outcomes when the body omits the declared partition-key path.

    The comparison filters headers and selected body fields; it does not capture
    native partition-key header bytes.
    """
    body = {"id": uuid.uuid4().hex, "n": 1}
    _run(container_for, body, summary="undefined PK").assert_functional_parity()


def test_pk_explicit_none(container_for):
    """Compare outcomes when the body explicitly contains a null partition key.

    This differs from an absent path. No native header bytes are inspected.
    """
    body = {"id": uuid.uuid4().hex, "pk": None}
    _run(container_for, body, summary="explicit None PK").assert_functional_parity()


# ---------------------------------------------------------------------------
# Header-bearing kwargs, one at a time.
# Each test = baseline + EXACTLY ONE kwarg that maps to a request header.
# ---------------------------------------------------------------------------

# Binding forwards the per-request header through the driver's custom-headers channel.
def test_pre_trigger_include(container_for):
    """Baseline call plus ``pre_trigger_include='validateOrder'`` (header kwarg)."""
    body = {"id": uuid.uuid4().hex, "pk": "a"}
    _run(container_for, body, summary="baseline + pre_trigger_include",
         pre_trigger_include="validateOrder").assert_functional_parity()


# Binding forwards the per-request header through the driver's custom-headers channel.
def test_indexing_directive(container_for):
    """Baseline call plus ``indexing_directive=Exclude`` (header kwarg)."""
    body = {"id": uuid.uuid4().hex, "pk": "a"}
    _run(container_for, body, summary="baseline + indexing_directive=Exclude",
         indexing_directive=1).assert_functional_parity()


def test_create_item_resolves_container_after_python_preparation(container_for, monkeypatch):
    """Create in the same container without requiring Python to stamp Rust's RID.

    Legacy resolves the container before __Post. Rust receives its name and
    resolves it below the Python preparation boundary. Use distinct item IDs
    so the second create is not a duplicate, then check each returned resource
    address belongs to the expected container. This does not inspect native
    HTTP request headers.
    """

    intended_rid_header = "x-ms-cosmos-intended-collection-rid"
    properties = container_for.read()
    core_request_headers: Dict[str, Any] = {}
    rust_requests: list[PreparedRequest] = []

    original_post = _ccc_module.CosmosClientConnection._CosmosClientConnection__Post  # type: ignore[attr-defined]

    def _capturing_post(self, path, request_params, body, req_headers, **kwargs):  # type: ignore[no-redef]
        if "/docs" in path:
            core_request_headers.clear()
            core_request_headers.update(dict(req_headers))
        return original_post(self, path, request_params, body, req_headers, **kwargs)

    original_execute = _rust_backend_module.BindingAdapter.execute

    def _capturing_execute(self, prepared, *, deadline=None):  # type: ignore[no-redef]
        if prepared.op == "create_item":
            rust_requests.append(prepared)
        return original_execute(self, prepared, deadline=deadline)

    def _do(client):
        cont = (
            client.get_database_client("parity_db").get_container_client(container_for.id)
        )
        result = cont.create_item(body={"id": uuid.uuid4().hex, "pk": "a"})
        assert result["_self"].rsplit("docs/", 1)[0] == properties["_self"]
        return result

    with monkeypatch.context() as capture:
        capture.setattr(
            _ccc_module.CosmosClientConnection, "_CosmosClientConnection__Post", _capturing_post
        )
        capture.setattr(_rust_backend_module.BindingAdapter, "execute", _capturing_execute)
        cmp = run_on_both_backends(
            _do, description="create_item resolves the same container on both paths",
        )

    assert cmp.core_python.raised is None and cmp.rust.raised is None
    cmp.assert_functional_parity()
    assert cmp.core_python.return_value["id"] != cmp.rust.return_value["id"]
    assert core_request_headers[intended_rid_header] == properties["_rid"]
    assert len(rust_requests) == 1
    assert rust_requests[0].container_link == container_for.container_link
    assert _Constants.ContainerRID not in rust_requests[0].headers
    assert intended_rid_header not in rust_requests[0].headers


# Binding forwards the per-request header through the driver's custom-headers channel.
def test_priority_high(container_for):
    """Baseline call plus ``priority='High'`` (header kwarg)."""
    body = {"id": uuid.uuid4().hex, "pk": "a"}
    _run(container_for, body, summary="baseline + priority=High",
         priority="High").assert_functional_parity()


# ---------------------------------------------------------------------------
# (additional) header-bearing kwargs from the public surface that
# weren't covered above. Each is the baseline + EXACTLY ONE kwarg.
# (Historical note: these all used to be skipped while the binding still dropped per-request headers; the binding now forwards them.)
# ---------------------------------------------------------------------------

# Binding forwards the per-request header through the driver's custom-headers channel.
def test_post_trigger_include(container_for):
    """Baseline call plus ``post_trigger_include='auditOrder'`` (header kwarg)."""
    body = {"id": uuid.uuid4().hex, "pk": "a"}
    _run(container_for, body, summary="baseline + post_trigger_include",
         post_trigger_include="auditOrder").assert_functional_parity()


# Binding routes the session token to the driver's typed setter.
def test_session_token(container_for):
    """Baseline call plus ``session_token=<token>`` (Session-consistency header kwarg)."""
    body = {"id": uuid.uuid4().hex, "pk": "a"}
    _run(container_for, body, summary="baseline + session_token",
         session_token="0:1#42").assert_functional_parity()


# Binding forwards the per-request header through the driver's custom-headers channel.
# Python side: ``_request_headers.py`` now flattens the ``initialHeaders`` dict
# into individual entries on ``PreparedRequest.headers`` so the binding's
# existing ``x-ms-...``/``prefer`` pass-through picks each one up.
def test_initial_headers(container_for):
    """Baseline call plus ``initial_headers={'x-ms-test': 'v'}`` (caller-injected headers)."""
    body = {"id": uuid.uuid4().hex, "pk": "a"}
    _run(container_for, body, summary="baseline + initial_headers",
         initial_headers={"x-ms-test-parity": "v1"}).assert_functional_parity()


# Binding forwards the per-request header through the driver's custom-headers channel.
def test_throughput_bucket(container_for):
    """Baseline call plus ``throughput_bucket=1`` (``x-ms-cosmos-throughput-bucket`` hdr)."""
    body = {"id": uuid.uuid4().hex, "pk": "a"}
    _run(container_for, body, summary="baseline + throughput_bucket=1",
         throughput_bucket=1).assert_functional_parity()


# ---------------------------------------------------------------------------
# Behavioural kwargs (change behaviour, not just header shape)
# ---------------------------------------------------------------------------

def test_enable_automatic_id_generation(container_for):
    """Compare create outcomes with automatic id generation requested.

    This comparison excludes returned ids by default; it does not establish
    identical generated ids or mutation of the caller's original dictionary.
    """
    body = {"pk": "a"}  # no id -- the helper generates one
    _run(container_for, body, summary="auto-id (no `id` in body)",
         enable_automatic_id_generation=True).assert_functional_parity()


# No_response -- binding now maps responsePayloadOnWriteDisabled
# onto the driver's typed content_response_on_write option.
def test_no_response(container_for):
    """Baseline call plus ``no_response=True`` (suppresses response body via Prefer hdr)."""
    body = {"id": uuid.uuid4().hex, "pk": "a"}
    _run(container_for, body, summary="baseline + no_response",
         no_response=True).assert_functional_parity()


@pytest.mark.skip(reason="Permanent skip: no rust-side equivalent (Python-only knob).")
def test_retry_write(container_for):
    """Baseline call plus ``retry_write=1`` (Python-only retry option; no rust analogue)."""
    body = {"id": uuid.uuid4().hex, "pk": "a"}
    _run(container_for, body, summary="baseline + retry_write=1",
         retry_write=1).assert_functional_parity()


@pytest.mark.skip(reason="Permanent skip: no rust-side equivalent (Python-only knob).")
def test_availability_strategy(container_for):
    """Baseline call plus ``availability_strategy=True`` (Python-only hedging feature)."""
    body = {"id": uuid.uuid4().hex, "pk": "a"}
    _run(container_for, body, summary="baseline + availability_strategy=True",
         availability_strategy=True).assert_functional_parity()


# ---------------------------------------------------------------------------
# (additional) behavioural / Python-only kwargs from the public surface.
# ---------------------------------------------------------------------------

@pytest.mark.skip(reason="Permanent skip: no rust-side equivalent (Python-only routing knob).")
def test_excluded_locations(container_for):
    """Baseline call plus ``excluded_locations=['East US']`` (a Python-only routing override).

    The binding passes this keyword to the driver as an excluded-regions
    setting (the mapping lives in ``azure_cosmos_rust/src/lib.rs``). The
    test is skipped only because the parity check is hard to make
    end-to-end against a single-region test account: ``["East US"]`` on a
    westus2-only account changes no routing decision the legacy path
    would diff against. Remove this skip once the parity harness gains a
    multi-region fixture (or a fault-injection transport that can observe
    which region a request actually chose).
    """
    body = {"id": uuid.uuid4().hex, "pk": "a"}
    _run(container_for, body, summary="baseline + excluded_locations",
         excluded_locations=["East US"]).assert_functional_parity()


def test_timeout(container_for):
    """Baseline call plus ``timeout=30`` (overall request timeout).

    Both backends honour this keyword now: core-python through
    azure-core's per-call timeout, rust by handing the value to the
    driver's own timeout setting (the prep sets an internal marker header the
    binding reads). The driver clamps sub-second values to its 1 s floor;
    the parity harness uses 30 s, well above it.
    """
    body = {"id": uuid.uuid4().hex, "pk": "a"}
    _run(container_for, body, summary="baseline + timeout=30",
         timeout=30).assert_functional_parity()


@pytest.mark.skip(reason="Partial parity: the driver has client-level analogs via "
                          "ConnectionPoolOptions::{min,max}_dataplane_request_timeout "
                          "(reqwest's builder.timeout) and TransportRequest::timeout for the per-call "
                          "override, but `OperationOptions` doesn't yet expose a per-call hook and the "
                          "binding doesn't construct the pool options from Python's `read_timeout` "
                          "kwarg. Driver-level support exists; per-call parity is a binding follow-up.")
def test_read_timeout(container_for):
    """Baseline call plus ``read_timeout=30`` (azure-core HTTP read timeout)."""
    body = {"id": uuid.uuid4().hex, "pk": "a"}
    _run(container_for, body, summary="baseline + read_timeout=30",
         read_timeout=30).assert_functional_parity()


@pytest.mark.skip(reason="Partial parity: the driver has client-level analogs via "
                          "ConnectionPoolOptions::{min,max}_connect_timeout (reqwest's "
                          "builder.connect_timeout) and the env var "
                          "AZURE_COSMOS_CONNECTION_POOL_MAX_CONNECT_TIMEOUT_MS, but the binding "
                          "doesn't yet wire Python's `connection_timeout` kwarg into the pool config. "
                          "No per-call hook today; client-level parity is a binding follow-up.")
def test_connection_timeout(container_for):
    """Baseline call plus ``connection_timeout=10`` (azure-core HTTP connect timeout)."""
    body = {"id": uuid.uuid4().hex, "pk": "a"}
    _run(container_for, body, summary="baseline + connection_timeout=10",
         connection_timeout=10).assert_functional_parity()


# ---------------------------------------------------------------------------
# Output / parsing parity
# ---------------------------------------------------------------------------

def test_response_hook_fires_once(container_for):
    """``response_hook`` must fire exactly once per backend on success.

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

def test_duplicate_id_raises_typed_exception(container_for):
    """Inserting the same id twice must raise ``CosmosResourceExistsError``
    (HTTP 409, sub_status 0) on **both** backends."""
    fixed_id = uuid.uuid4().hex

    def _do(client):
        cont = client.get_database_client("parity_db").get_container_client(container_for.id)
        cont.create_item(body={"id": fixed_id, "pk": "a"})
        return cont.create_item(body={"id": fixed_id, "pk": "a"})

    cmp = run_on_both_backends(
        _do,
        description="duplicate-id 409: insert id={!r} twice".format(fixed_id),
        request_body={"id": fixed_id, "pk": "a", "_note": "sent twice"},
    )
    cmp.print_report()
    assert not cmp.core_python.succeeded
    assert not cmp.rust.succeeded
    cmp.assert_parity()


# ---------------------------------------------------------------------------
# Retired arguments are rejected by presence on both backends.
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("name", ["populate_query_metrics", "etag", "match_condition"])
@pytest.mark.parametrize("value", [None, False, True])
def test_retired_create_arguments_are_rejected(container_for, name, value):
    body = {"id": uuid.uuid4().hex, "pk": "a"}
    comparison = _run(container_for, body, summary=f"create rejects {name}", **{name: value})
    for outcome in (comparison.core_python, comparison.rust):
        assert isinstance(outcome.raised, TypeError)


# ---------------------------------------------------------------------------
# Typed partitionless-key rejection. This does not establish the external
# driver's routing behavior or replace a test against a partitionless container.
# ---------------------------------------------------------------------------

def test_partitionless_container_rejected_by_rust_binding():
    """Check rejection of the explicit typed partitionless-key sentinel.

    Accept ValueError or RuntimeError and require 'partitionless' in its message.
    A cross-partition query scope is not this sentinel. This test does not
    independently detect whether initialization performed network I/O.
    """

    # Real configuration is required by this test's lazy driver initialization.
    # No network recorder or prohibition is installed here.
    endpoint = os.environ.get("ACCOUNT_HOST")
    master_key = os.environ.get("ACCOUNT_KEY")
    if not endpoint or not master_key:
        pytest.skip(
            "ACCOUNT_HOST / ACCOUNT_KEY not set; this test needs a real "
            "endpoint to bootstrap the Rust driver before the binding "
            "ever inspects the typed partition key."
        )

    backend = BindingAdapter(endpoint=endpoint, master_key=master_key)
    body = {"id": uuid.uuid4().hex, "pk": "a"}
    prepared = PreparedRequest(
        op=OP_CREATE_ITEM,
        container_link="dbs/parity_db/colls/does_not_matter",
        body_bytes=json.dumps(body).encode("utf-8"),
        partition_key=BindingPartitionKey("empty_sentinel"),
        headers={},
    )

    # Accept either exception type, then check the message substring separately.
    try:
        with pytest.raises((ValueError, RuntimeError)) as excinfo:
            backend.execute(prepared)
    finally:
        backend.close()

    message = str(excinfo.value)
    assert "partitionless" in message.lower(), (
        "Rust binding must reject the empty_sentinel partition key with a message "
        "naming the partitionless-container limitation; got: {!r}".format(message)
    )
    print(
        "partitionless container rejection pinned: {}".format(message)
    )
