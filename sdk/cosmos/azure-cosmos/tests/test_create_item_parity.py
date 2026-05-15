# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# -------------------------------------------------------------------------
"""End-to-end parity tests for ``Container.create_item`` across backends.

Each test runs the *same* call shape through ``run_on_both_backends``
and asserts the two outcomes are equivalent (return value,
``last_response_headers``, and — on failure — exception type and
sub_status).

Skips cleanly when:
  * ``ACCOUNT_URI`` / ``ACCOUNT_KEY`` are not set (no emulator wired), or
  * ``azure.cosmos._rust`` did not build (``maturin develop`` not run).

Known gaps where the rust backend doesn't yet match core-python are
tagged with ``xfail_on_backend("rust", reason="...")`` so:
  * the suite stays green today (gaps are expected to fail),
  * once a gap closes the strict xfail flips to a pass and forces the
    marker's removal, which surfaces the parity progress mechanically.

Test layout:

  - **Body / partition-key shape parity** (the wire-prep contract).
  - **Header-bearing kwargs** (pre/post triggers, indexing directive,
    intended-rid, priority).
  - **Behavioral kwargs** (no_response, enable_automatic_id_generation,
    retry_write, availability_strategy).
  - **Output / parsing parity** (CosmosDict shape, last_response_headers,
    response_hook fired once).
  - **Exception parity** (typed class for 409, sub_status surfaced).

Every test is intentionally small. The harness handles the diffing.
"""
from __future__ import annotations

import uuid

import pytest

from _parity_helpers import (
    have_emulator_or_account,
    have_rust_binding,
    run_on_both_backends,
    skip_unless_emulator,
    skip_unless_rust_binding,
    xfail_on_backend,
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


def _call(container_id: str, body: dict, **kwargs):
    """Build a closure that the harness invokes once per backend."""
    def _do(client):
        cont = client.get_database_client("parity_db").get_container_client(container_id)
        return cont.create_item(body=body, **kwargs)
    return _do


def _run(container, body, **kwargs):
    """Run the call on both backends and print the side-by-side report.

    ``pytest -s`` will show the report for every test; without ``-s``
    you only see it on failure (printed by ``assert_parity``).
    """
    description = "create_item(body={!r}, kwargs={!r})".format(body, kwargs)
    cmp = run_on_both_backends(
        _call(container.id, body, **kwargs),
        description=description,
    )
    cmp.print_report()
    return cmp


# ---------------------------------------------------------------------------
# Body / partition-key shape parity
# ---------------------------------------------------------------------------

def test_simple_string_partition_key(container_for):
    """Single-string PK — the baseline case both backends should agree on."""
    body = {"id": uuid.uuid4().hex, "pk": "customerA", "n": 1}
    _run(container_for, body).assert_parity()


@xfail_on_backend("rust", reason="_Undefined PK has no driver variant — wire bytes ``[{}]`` not produced")
def test_undefined_partition_key(container_for):
    """Body missing the declared PK path — wire bytes must be ``[{}]``.

    The rust driver's ``PartitionKeyValue`` enum has no ``Undefined``
    variant, so the rust path either silently writes to the wrong
    partition or raises — either way, parity fails.
    """
    body = {"id": uuid.uuid4().hex, "n": 1}  # no "pk"
    _run(container_for, body).assert_parity()


@xfail_on_backend("rust", reason="partitionless PK overloaded with cross-partition-query in driver")
def test_none_partition_key_value(container_for):
    """Explicit ``None`` PK value — ``[null]`` on the wire."""
    body = {"id": uuid.uuid4().hex, "pk": None}
    _run(container_for, body).assert_parity()


# ---------------------------------------------------------------------------
# Header-bearing kwargs (rust driver currently drops most extra headers)
# ---------------------------------------------------------------------------

@xfail_on_backend("rust", reason="pre_trigger_include header dropped by rust driver")
def test_pre_trigger_include(container_for):
    body = {"id": uuid.uuid4().hex, "pk": "a"}
    _run(container_for, body, pre_trigger_include="validateOrder").assert_parity()


@xfail_on_backend("rust", reason="indexing_directive header dropped by rust driver")
def test_indexing_directive(container_for):
    body = {"id": uuid.uuid4().hex, "pk": "a"}
    _run(container_for, body, indexing_directive=1).assert_parity()  # Exclude


@xfail_on_backend("rust", reason="x-ms-cosmos-intended-collection-rid header dropped by rust driver")
def test_intended_collection_rid_present_on_wire(container_for):
    """The recreate-retry safety net depends on this header reaching the
    service. Until the rust driver passes it through, expected to xfail."""
    body = {"id": uuid.uuid4().hex, "pk": "a"}
    cmp = _run(container_for, body)
    core_h = (cmp.core_python.response_headers or {})
    rust_h = (cmp.rust.response_headers or {})
    key = "x-ms-cosmos-intended-collection-rid"
    assert core_h.get(key) == rust_h.get(key), (
        "intended-rid header parity broken: core={!r} rust={!r}".format(
            core_h.get(key), rust_h.get(key)
        )
    )


@xfail_on_backend("rust", reason="priority header dropped by rust driver")
def test_priority_high(container_for):
    body = {"id": uuid.uuid4().hex, "pk": "a"}
    _run(container_for, body, priority="High").assert_parity()


# ---------------------------------------------------------------------------
# Behavioral kwargs
# ---------------------------------------------------------------------------

def test_enable_automatic_id_generation(container_for):
    """Body without an id — both backends mint one client-side and write
    it back into the body. Auto-id is a Python-side mutation, so the
    rust backend just sees the already-mutated body."""
    body = {"pk": "a"}  # no id
    _run(container_for, body, enable_automatic_id_generation=True).assert_parity()


@xfail_on_backend("rust", reason="Prefer: return=minimal header dropped by rust driver")
def test_no_response(container_for):
    """``no_response=True`` should produce a 204 with empty body. Both
    backends must surface ``CosmosDict({})``."""
    body = {"id": uuid.uuid4().hex, "pk": "a"}
    _run(container_for, body, no_response=True).assert_parity()


@xfail_on_backend("rust", reason="no rust equivalent for retry_write attempt-count knob")
def test_retry_write(container_for):
    """``retry_write`` has no rust equivalent. The diff will surface as a
    behavior delta on this kwarg — visible in the printed report."""
    body = {"id": uuid.uuid4().hex, "pk": "a"}
    _run(container_for, body, retry_write=1).assert_parity()


@xfail_on_backend("rust", reason="no rust equivalent for availability_strategy hedging")
def test_availability_strategy(container_for):
    body = {"id": uuid.uuid4().hex, "pk": "a"}
    _run(container_for, body, availability_strategy=True).assert_parity()


# ---------------------------------------------------------------------------
# Output / parsing parity
# ---------------------------------------------------------------------------

def test_response_hook_fires_once(container_for):
    """Both backends must invoke ``response_hook`` exactly once on success.
    The hook is implemented in the Python response parser, so this is a
    pure-Python parity property — should pass on rust today as long as
    the parser is wired into the rust path."""
    seen_core = []
    seen_rust = []

    def make_call(seen):
        def _do(client):
            cont = client.get_database_client("parity_db").get_container_client(container_for.id)
            return cont.create_item(
                body={"id": uuid.uuid4().hex, "pk": "a"},
                response_hook=lambda h, b: seen.append(1),
            )
        return _do

    from azure.cosmos import CosmosClient
    import os
    for backend_name, seen in (("core-python", seen_core), ("rust", seen_rust)):
        client = CosmosClient(
            os.environ["ACCOUNT_URI"],
            os.environ["ACCOUNT_KEY"],
            _backend=backend_name,  # type: ignore[arg-type]
        )
        make_call(seen)(client)
    print("response_hook fired: core-python={} rust={}".format(len(seen_core), len(seen_rust)))
    assert len(seen_core) == 1, "core-python should fire response_hook exactly once"
    assert len(seen_rust) == 1, "rust should fire response_hook exactly once"


# ---------------------------------------------------------------------------
# Exception parity
# ---------------------------------------------------------------------------

def test_duplicate_id_raises_typed_exception(container_for):
    """Inserting the same id twice should raise
    ``CosmosResourceExistsError`` (HTTP 409, sub_status 0) on *both*
    backends. The exception class, sub_status, and status_code must
    match."""
    fixed_id = uuid.uuid4().hex

    def _do(client):
        cont = client.get_database_client("parity_db").get_container_client(container_for.id)
        cont.create_item(body={"id": fixed_id, "pk": "a"})
        return cont.create_item(body={"id": fixed_id, "pk": "a"})

    cmp = run_on_both_backends(
        _do,
        description="test_duplicate_id_raises_typed_exception: insert id={!r} twice".format(fixed_id),
    )
    cmp.print_report()
    assert not cmp.core_python.succeeded
    assert not cmp.rust.succeeded
    cmp.assert_parity()

