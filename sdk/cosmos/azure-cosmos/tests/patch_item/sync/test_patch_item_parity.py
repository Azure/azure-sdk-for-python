# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# -------------------------------------------------------------------------
"""Live patch comparisons using explicitly selected backends and owned resources.

Body suppression, service-issued session tokens and invalid-path errors run
without historical skips. Numeric, SQL predicate, trigger and tracking-property
differences remain visible failures rather than being hidden by relaxed checks.
The copied-original runner adds strict stored-state and resource-address checks.
"""
from __future__ import annotations

import os
import uuid
from types import SimpleNamespace

import pytest

from azure.core import MatchConditions

from azure.cosmos import CosmosClient, PartitionKey
from azure.cosmos.exceptions import CosmosHttpResponseError, CosmosResourceNotFoundError
from common._parity_helpers import BackendComparison, run_on_both_backends, skip_unless_emulator, skip_unless_rust_binding

pytestmark = [skip_unless_emulator(), skip_unless_rust_binding()]


# ---------------------------------------------------------------------------
# Per-test container fixture
# ---------------------------------------------------------------------------

@pytest.fixture
def container_for():
    """Own the database and verify deletion even when a comparison fails."""
    with CosmosClient(
        os.environ["ACCOUNT_HOST"], os.environ["ACCOUNT_KEY"], _backend="core-python",
    ) as client:
        database = client.create_database("patch_parity_" + uuid.uuid4().hex)
        try:
            container = database.create_container(
                id="orders", partition_key=PartitionKey(path="/pk"),
            )
            yield SimpleNamespace(
                id=container.id, database_id=database.id, scripts=container.scripts,
            )
        finally:
            client.delete_database(database.id)
            with pytest.raises(CosmosResourceNotFoundError) as error:
                database.read()
            assert error.value.status_code == 404


@pytest.fixture
def container_with_trigger(container_for):
    """Add observable pre-trigger and post-trigger functions.

    Trigger tests are only meaningful against a trigger that actually exists.
    Naming a non-existent trigger merely proves both backends can produce *an*
    error, which passes even when the feature is entirely broken. This trigger
    writes a field onto the item the service is about to write, so its
    effect is visible in the stored item and the test can prove the trigger
    ran rather than that it was merely accepted.
    """
    container_for.scripts.create_trigger({
        "id": "stampTrigger",
        "triggerType": "Pre",
        "triggerOperation": "All",
        "body": """function stamp() {
            var ctx = getContext();
            var req = ctx.getRequest();
            var doc = req.getBody();
            doc['stampedBy'] = 'pre-trigger';
            req.setBody(doc);
        }""",
    })
    container_for.scripts.create_trigger({
        "id": "auditOrder", "triggerType": "Post", "triggerOperation": "All",
        "body": """function audit() {
            var response = getContext().getResponse();
            var body = response.getBody();
            body.stampedBy = 'post-trigger';
            response.setBody(body);
        }""",
    })
    return container_for


# ---------------------------------------------------------------------------
# Closure builders
# ---------------------------------------------------------------------------
#
# Each backend seeds and patches its OWN row (a fresh id under the same
# partition key) so the two runs never race and neither observes the other's
# writes. The reported parity contract is the *patch half*; the seed write only
# exists to give each backend an item to modify.

# The seed item carries one field per operator exercised below, so a single
# shape works for every test in the file and the patch programs stay readable.
_SEED_TEMPLATE = {
    "pk": "customerA",
    "n": 1,
    "label": "before",
    "doomed": "remove me",
    "nested": {"inner": 1},
}


def _seed_document(item_id: str) -> dict:
    """Build the item a test patches, with a caller-chosen id."""
    seeded = dict(_SEED_TEMPLATE)
    seeded["id"] = item_id
    return seeded


def _patch_call(container, patch_operations: list, *, use_session_token=False, **kwargs):
    """Build a seed-then-patch closure the harness runs once per backend."""
    def _do(client):
        cont = client.get_database_client(container.database_id).get_container_client(container.id)
        item_id = uuid.uuid4().hex
        created = cont.create_item(_seed_document(item_id))
        options = dict(kwargs)
        if use_session_token:
            options["session_token"] = created.get_response_headers()["x-ms-session-token"]
        result = cont.patch_item(
            item=item_id,
            partition_key="customerA",
            patch_operations=patch_operations,
            **options,
        )
        if options.get("no_response"):
            assert dict(result) == {}
        return result
    return _do

def _run_patch(container, patch_operations: list, summary: str,
               **kwargs) -> BackendComparison:
    """Run one patch on both backends and print the side-by-side report."""
    description = "sync {} -- ops={}, kwargs={}".format(
        summary,
        [op.get("op") for op in patch_operations],
        sorted(kwargs.keys()) or "(none)",
    )
    cmp = run_on_both_backends(
        _patch_call(container, patch_operations, **kwargs),
        description=description,
        request_body={"patch_operations": patch_operations},
        request_kwargs=kwargs or None,
    )
    cmp.print_report()
    return cmp


# ---------------------------------------------------------------------------
# Baseline
# ---------------------------------------------------------------------------

def test_baseline_set(container_for):
    """a single ``set`` on an existing field, no optional kwargs.

    If the baseline fails, sync ``patch_item`` is broken on one backend and no other
    result in this file is meaningful.
    """
    cmp = _run_patch(container_for, [{"op": "set", "path": "/n", "value": 99}],
                     summary="baseline set /n")
    cmp.assert_functional_parity()


# ---------------------------------------------------------------------------
# Patch operators.
#
# The patch body is a program, so each operator is its own wire shape. A binding
# that mishandled one operator while forwarding the rest would look healthy on
# the baseline and corrupt customer items in production, which is why these
# are pinned individually rather than as one combined program.
# ---------------------------------------------------------------------------

def test_op_add_new_field(container_for):
    """``add`` introduces a field the seed item does not have."""
    cmp = _run_patch(container_for, [{"op": "add", "path": "/added", "value": "x"}],
                     summary="add new field")
    cmp.assert_functional_parity()


def test_op_replace_existing_field(container_for):
    """``replace`` overwrites a field that already exists.

    Distinct from ``set``: ``replace`` requires the path to be present, so this
    also pins that both backends resolve the path the same way.
    """
    cmp = _run_patch(container_for, [{"op": "replace", "path": "/label", "value": "after"}],
                     summary="replace existing field")
    cmp.assert_functional_parity()


def test_op_remove_field(container_for):
    """``remove`` deletes a field -- the only operator carrying no value.

    Worth its own test because the absent ``value`` key is a different wire
    shape, and a binding that assumed every operation has a value would fail
    here and nowhere else.
    """
    cmp = _run_patch(container_for, [{"op": "remove", "path": "/doomed"}],
                     summary="remove field")
    cmp.assert_functional_parity()


def test_op_incr(container_for):
    """Compare an increment, including any extra returned tracking property."""
    cmp = _run_patch(container_for, [{"op": "incr", "path": "/n", "value": 5}],
                     summary="incr /n by 5")
    cmp.assert_functional_parity()


def test_op_nested_path(container_for):
    """a nested path (``/nested/inner``) must survive the trip intact."""
    cmp = _run_patch(container_for, [{"op": "set", "path": "/nested/inner", "value": 42}],
                     summary="set nested path")
    cmp.assert_functional_parity()


def test_multiple_operations_applied_in_order(container_for):
    """a multi-operation program applies atomically and in order.

    The program increments ``/n`` and then sets it, so the final value proves
    the operations were applied in the order given rather than reordered or
    partially dropped -- a failure mode a single-operation test cannot see.
    """
    operations = [
        {"op": "incr", "path": "/n", "value": 5},
        {"op": "set", "path": "/n", "value": 7},
        {"op": "add", "path": "/added", "value": "x"},
        {"op": "remove", "path": "/doomed"},
    ]
    cmp = _run_patch(container_for, operations,
                     summary="multi-op program")
    cmp.assert_functional_parity()
    if cmp.core_python.succeeded:
        assert cmp.core_python.return_value["n"] == 7, "later set must win over the earlier incr"


# ---------------------------------------------------------------------------
# Header-bearing kwargs, exactly one per test
# ---------------------------------------------------------------------------

def test_pre_trigger_include(container_with_trigger):
    """Baseline call plus ``pre_trigger_include`` naming a trigger that exists.

    Asserts more than header forwarding: the trigger writes a field onto the
    item, so a passing run proves the trigger actually executed rather than
    that the request was merely accepted.
    """
    cmp = _run_patch(container_with_trigger, [{"op": "incr", "path": "/n", "value": 1}],
                     summary="baseline + pre_trigger_include (real trigger)",
                     pre_trigger_include="stampTrigger")
    cmp.assert_functional_parity()
    if cmp.core_python.succeeded:
        assert cmp.core_python.return_value.get("stampedBy") == "pre-trigger", (
            "the pre-trigger must actually run, not just be accepted")

    assert cmp.core_python.succeeded and cmp.rust.succeeded
    for outcome in (cmp.core_python, cmp.rust):
        assert outcome.return_value["stampedBy"] == "pre-trigger"


def test_post_trigger_include(container_with_trigger):
    """Baseline call plus ``post_trigger_include`` -- forwarded as a request header."""
    cmp = _run_patch(container_with_trigger, [{"op": "incr", "path": "/n", "value": 1}],
                     summary="baseline + post_trigger_include",
                     post_trigger_include="auditOrder")
    cmp.assert_functional_parity()

    assert cmp.core_python.succeeded and cmp.rust.succeeded
    for outcome in (cmp.core_python, cmp.rust):
        assert outcome.return_value["stampedBy"] == "post-trigger"


def test_session_token(container_for):
    """Baseline call plus ``session_token`` -- forwarded as a request header."""
    cmp = _run_patch(container_for, [{"op": "set", "path": "/n", "value": 2}],
                     summary="baseline + session_token",
                     use_session_token=True)
    assert cmp.core_python.succeeded and cmp.rust.succeeded
    cmp.assert_functional_parity()


def test_priority(container_for):
    """Baseline call plus ``priority='High'`` -- the priority-based-throttling header."""
    cmp = _run_patch(container_for, [{"op": "set", "path": "/n", "value": 2}],
                     summary="baseline + priority=High",
                     priority="High")
    cmp.assert_functional_parity()


def test_throughput_bucket(container_for):
    """Baseline call plus ``throughput_bucket=1`` -- the throughput-bucket header."""
    cmp = _run_patch(container_for, [{"op": "set", "path": "/n", "value": 2}],
                     summary="baseline + throughput_bucket",
                     throughput_bucket=1)
    cmp.assert_functional_parity()


# ---------------------------------------------------------------------------
# Behavioural kwargs
# ---------------------------------------------------------------------------

def test_no_response(container_for):
    """``no_response=True`` -- the service must not echo the item back.

    Changes the shape of the return value rather than just a header, so it is
    the kwarg most likely to expose a helper divergence between sync and async.
    """
    cmp = _run_patch(container_for, [{"op": "set", "path": "/n", "value": 2}],
                     summary="baseline + no_response",
                     no_response=True)
    assert cmp.core_python.succeeded and cmp.rust.succeeded
    cmp.assert_functional_parity()


def test_retry_write(container_for):
    """``retry_write=1`` -- opts a non-idempotent write into retries."""
    cmp = _run_patch(container_for, [{"op": "set", "path": "/n", "value": 2}],
                     summary="baseline + retry_write",
                     retry_write=1)
    cmp.assert_functional_parity()


def test_availability_strategy(container_for):
    """``availability_strategy=True`` -- enables hedged cross-region requests."""
    cmp = _run_patch(container_for, [{"op": "set", "path": "/n", "value": 2}],
                     summary="baseline + availability_strategy",
                     availability_strategy=True)
    cmp.assert_functional_parity()


def test_timeout(container_for):
    """``timeout=30`` -- the overall per-request timeout.

    Honoured on both backends: core-python through azure-core's per-call
    timeout, rust by handing the value to the driver. 30 s sits well clear of
    the driver's 1 s clamp, so the call is expected to succeed normally.
    """
    cmp = _run_patch(container_for, [{"op": "set", "path": "/n", "value": 2}],
                     summary="baseline + timeout=30",
                     timeout=30)
    cmp.assert_functional_parity()


def test_filter_predicate_matching(container_for):
    """a ``filter_predicate`` whose condition holds lets the patch through.

    This is a conditional update expressed as SQL against the stored item,
    independent of the etag mechanism. The seed sets ``n = 1``, so the predicate
    matches and the patch must apply on both backends.
    """
    cmp = _run_patch(container_for, [{"op": "set", "path": "/n", "value": 2}],
                     summary="baseline + matching filter_predicate",
                     filter_predicate="FROM c WHERE c.n = 1")
    cmp.assert_functional_parity()


# ---------------------------------------------------------------------------
# Output / parsing parity
# ---------------------------------------------------------------------------

def test_response_hook_fires_once(container_for):
    """``response_hook`` must fire exactly once per backend on success.

    Counting invocations is the point: asserting only that the hook is accepted
    would pass even if it were never called, which is the failure mode worth
    guarding -- a hook that silently stops firing breaks customer telemetry
    without breaking any request. The harness runs core-python first and rust
    second, so an invocation counter attributes each call to the right backend.
    """
    fired = {"core-python": 0, "rust": 0}
    order = ["core-python", "rust"]
    call_idx = [0]

    def _do(client):
        backend = order[call_idx[0]]
        call_idx[0] += 1

        def _hook(_headers, _body):
            fired[backend] += 1

        cont = client.get_database_client(container_for.database_id).get_container_client(container_for.id)
        item_id = uuid.uuid4().hex
        cont.create_item(_seed_document(item_id))
        return cont.patch_item(
            item=item_id,
            partition_key="customerA",
            patch_operations=[{"op": "set", "path": "/n", "value": 2}],
            response_hook=_hook,
        )

    cmp = run_on_both_backends(
        _do,
        description="sync patch response_hook fires exactly once per backend",
        request_kwargs={"response_hook": "<callable>"},
    )
    cmp.print_report()
    print("sync patch response_hook fired: core-python={} rust={}".format(
        fired["core-python"], fired["rust"]))
    cmp.assert_functional_parity()
    assert fired["core-python"] == 1, "core-python should fire response_hook exactly once"
    assert fired["rust"] == 1, "rust should fire response_hook exactly once"


# ---------------------------------------------------------------------------
# Error and concurrency contracts
# ---------------------------------------------------------------------------

def test_patch_missing_id_raises_not_found(container_for):
    """patching an id that was never created raises a typed 404 on both.

    Uses the functional exception assertion: the rust binding exposes a smaller
    response-header surface on errors, a known and separately tracked gap, so
    demanding header-set equality would fail every run for a reason unrelated
    to the exception contract.
    """
    def _do(client):
        cont = client.get_database_client(container_for.database_id).get_container_client(container_for.id)
        return cont.patch_item(
            item="missing-" + uuid.uuid4().hex,
            partition_key="customerA",
            patch_operations=[{"op": "set", "path": "/n", "value": 1}],
        )

    cmp = run_on_both_backends(_do, description="sync patch missing id -> 404")
    cmp.print_report()
    assert not cmp.core_python.succeeded
    assert not cmp.rust.succeeded
    cmp.assert_functional_exception_parity()


def test_stale_etag_raises_precondition_failed(container_for):
    """a stale ``etag`` with ``IfNotModified`` must fail the patch on both.

    This is the optimistic-concurrency contract customers rely on for
    read-modify-write loops. The item is deliberately modified after its
    etag is captured, so the etag presented to ``patch_item`` no longer matches
    the stored one and the service must reject the write rather than silently
    overwrite a concurrent update.
    """
    def _do(client):
        cont = client.get_database_client(container_for.database_id).get_container_client(container_for.id)
        item_id = uuid.uuid4().hex
        created = cont.create_item(_seed_document(item_id))
        stale_etag = created["_etag"]
        # Second write moves the stored etag past the captured one.
        cont.patch_item(
            item=item_id, partition_key="customerA",
            patch_operations=[{"op": "set", "path": "/label", "value": "moved on"}],
        )
        return cont.patch_item(
            item=item_id, partition_key="customerA",
            patch_operations=[{"op": "set", "path": "/n", "value": 999}],
            etag=stale_etag, match_condition=MatchConditions.IfNotModified,
        )

    cmp = run_on_both_backends(_do, description="sync patch with stale etag -> 412")
    cmp.print_report()
    assert not cmp.core_python.succeeded
    assert not cmp.rust.succeeded
    cmp.assert_functional_exception_parity()


def test_current_etag_succeeds(container_for):
    """the *current* etag with ``IfNotModified`` must let the patch through.

    The other half of the concurrency contract. Without this, a backend that
    rejected every conditional patch would still pass the stale-etag test above
    while being completely broken for customers.
    """
    def _do(client):
        cont = client.get_database_client(container_for.database_id).get_container_client(container_for.id)
        item_id = uuid.uuid4().hex
        created = cont.create_item(_seed_document(item_id))
        return cont.patch_item(
            item=item_id, partition_key="customerA",
            patch_operations=[{"op": "set", "path": "/n", "value": 5}],
            etag=created["_etag"], match_condition=MatchConditions.IfNotModified,
        )

    cmp = run_on_both_backends(_do, description="sync patch with current etag -> success")
    cmp.print_report()
    cmp.assert_functional_parity()


def test_non_matching_filter_predicate_raises(container_for):
    """a ``filter_predicate`` whose condition fails must reject the patch.

    The negative half of the matching-predicate test above. The seed sets ``n = 1``
    so this predicate cannot hold, and the service must refuse the write on both
    backends rather than applying it regardless.
    """
    cmp = _run_patch(container_for, [{"op": "set", "path": "/n", "value": 2}],
                     summary="non-matching filter_predicate",
                     filter_predicate="FROM c WHERE c.n = 99999")
    assert not cmp.core_python.succeeded
    assert not cmp.rust.succeeded
    cmp.assert_functional_exception_parity()


def test_etag_without_match_condition_raises_value_error(container_for):
    """``etag`` without ``match_condition`` is rejected before any network call.

    The gate lives in the shared ``_base._get_match_headers``, so the error must
    be a local ``ValueError`` on both backends -- never a service round trip.
    """
    def _do(client):
        cont = client.get_database_client(container_for.database_id).get_container_client(container_for.id)
        item_id = uuid.uuid4().hex
        cont.create_item(_seed_document(item_id))
        return cont.patch_item(
            item=item_id, partition_key="customerA",
            patch_operations=[{"op": "set", "path": "/n", "value": 5}],
            etag='"some-etag"',
        )

    cmp = run_on_both_backends(
        _do, description="sync patch etag without match_condition -> ValueError")
    cmp.print_report()
    assert isinstance(cmp.core_python.raised, ValueError), (
        "core-python must reject etag-without-match_condition locally")
    assert isinstance(cmp.rust.raised, ValueError), (
        "rust must reject etag-without-match_condition locally, at the same shared gate")


def test_invalid_patch_path_raises(container_for):
    """a patch against a path that cannot be resolved must fail on both.

    An increment with a missing parent tests the Rust driver\'s local error
    mapping. Both backends must return CosmosHttpResponseError with status 400.
    """
    cmp = _run_patch(
        container_for,
        [{"op": "incr", "path": "/definitely/not/here", "value": 1}],
        summary="replace on a missing path")
    assert not cmp.core_python.succeeded
    assert not cmp.rust.succeeded
    for outcome in (cmp.core_python, cmp.rust):
        assert isinstance(outcome.raised, CosmosHttpResponseError)
        assert outcome.raised.status_code == 400
    cmp.assert_functional_exception_parity()
