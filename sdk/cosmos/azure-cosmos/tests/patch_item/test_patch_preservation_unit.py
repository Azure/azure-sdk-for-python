# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.
"""Patch comparisons must verify their setup, returned fields, and stored state."""

import asyncio
import copy
import importlib.util
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock

import pytest


ROOT = Path(__file__).resolve().parents[2]


def _load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


@pytest.fixture
def runner(monkeypatch, tmp_path):
    monkeypatch.setenv("PATCH_REVIEW_OUTPUT", str(tmp_path / "evidence"))
    monkeypatch.delenv("PATCH_REVIEW_NONE_OPTIONS", raising=False)
    monkeypatch.delenv("PATCH_REVIEW_SUPPLEMENTAL", raising=False)
    return _load("patch_review_runner", ROOT / "scripts" / "v5" / "run_patch_item_parity.py")


@pytest.mark.parametrize("execution", ["original", "copied"])
@pytest.mark.parametrize(
    "scenario",
    ["correct", "returned_value_changed", "stored_value_changed", "not_stored",
     "returned_id_changed", "stored_pk_changed", "stored_value_missing"],
)
def test_patch_checks_returned_and_stored_fields(scenario, execution, runner, monkeypatch):
    module = _load("original_patch_none_options", ROOT / "tests" / "test_none_options.py")
    case = module.TestNoneOptions("test_patch_item_none_options")
    container = MagicMock()
    case.container = container
    stored = {}
    events = []

    def create(body, **kwargs):
        stored.update(copy.deepcopy(body))
        events.append("create")
        return dict(body)

    def patch(item_id, partition_key, patch_operations, **kwargs):
        assert item_id == stored["id"]
        assert partition_key == stored["pk"]
        assert patch_operations == [{"op": "add", "path": "/patched", "value": True}]
        assert all(value is None for value in kwargs.values())
        events.append("patch")
        returned = dict(stored, patched=True)
        if scenario != "not_stored":
            stored["patched"] = True
        if scenario == "returned_value_changed":
            returned["value"] = 0
        if scenario == "returned_id_changed":
            returned["id"] = "wrong"
        if scenario == "stored_value_changed":
            stored["value"] = 0
        if scenario == "stored_pk_changed":
            stored["pk"] = "wrong"
        if scenario == "stored_value_missing":
            del stored["value"]
        return returned

    def read(item_id, partition_key, **kwargs):
        events.append("read")
        assert item_id == stored["id"]
        assert partition_key == "pk-value"
        return dict(stored)

    container.create_item.side_effect = create
    container.patch_item.side_effect = patch
    container.read_item.side_effect = read
    runner.CURRENT.update(backend="core-python", surface="sync")
    monkeypatch.setattr(runner, "_binding_operation_count", lambda: 0)
    monkeypatch.setattr(runner, "_rust_fallback_count", lambda: 0)
    invoke = case.test_patch_item_none_options if execution == "original" else lambda: runner.run_none_options(container)
    if scenario == "correct":
        invoke()
        assert events == ["create", "patch", "read"]
        if execution == "copied":
            observation = runner.REPORT["patch_calls"][0]
            assert observation["returned_fields"] == observation["stored_fields"] == stored
            assert observation["binding_delta"] == observation["fallback_delta"] == 0
    else:
        error = KeyError if scenario in ("not_stored", "stored_value_missing") else AssertionError
        with pytest.raises(error):
            invoke()


@pytest.mark.parametrize("mode", ["default", "supplemental", "none_options"])
@pytest.mark.parametrize("asynchronous", [False, True])
def test_runner_preserves_selections_and_closes_client(runner, monkeypatch, mode, asynchronous):
    monkeypatch.setenv("ACCOUNT_HOST", "https://unused.invalid")
    monkeypatch.setenv("ACCOUNT_KEY", "unused")
    monkeypatch.setattr(runner, "NONE_OPTIONS_ONLY", mode == "none_options")
    if mode == "supplemental":
        monkeypatch.setenv("PATCH_REVIEW_SUPPLEMENTAL", "1")
    client = MagicMock()
    client.__aenter__ = AsyncMock()
    client.close = AsyncMock() if asynchronous else MagicMock(return_value=None)
    monkeypatch.setattr(runner, "AsyncCosmosClient" if asynchronous else "CosmosClient", MagicMock(return_value=client))
    names = []

    async def record(name, function):
        names.append(name)

    monkeypatch.setattr(runner, "record", record)
    asyncio.run(runner.run_backend("rust", asynchronous, "owned-database"))
    client.close.assert_called_once()
    if mode == "none_options":
        assert names == ([] if asynchronous else ["test_patch_item_none_options"])
    elif mode == "supplemental":
        assert names == ["integer_increment_on_fraction", "pre_trigger", "post_trigger"]
    else:
        assert len(names) == (31 if asynchronous else 32)
        assert ("test_patch_item_none_options" in names) is not asynchronous
        assert {"filter_false", "filter_true", "if_none_match", "invalid_path"} <= set(names)
        assert {"filter_etag_current", "filter_etag_stale"} <= set(names)
        assert {"filter_false_etag_current", "filter_false_etag_stale"} <= set(names)
        assert {"if_none_match", "if_none_match_stale"} <= set(names)
        assert {"ten_operations", "eleven_operations"} <= set(names)
        assert {"atomic_patch_control", "atomic_patch_rejection"} <= set(names)
        assert {"integer_increment_on_integer", "integer_increment_on_fraction"} <= set(names)
        assert {"array_add", "array_set"} <= set(names)
        assert {"array_add_then_remove", "array_remove_then_add"} <= set(names)
        assert {"no_response", "no_response_rejection"} <= set(names)
        originals = runner.ASYNC if asynchronous else runner.SYNC
        assert {method.__name__ for method in originals} <= set(names)


@pytest.mark.parametrize("focused,expected_calls", [(False, 4), (True, 2)])
def test_runner_owns_and_verifies_database_cleanup(runner, monkeypatch, focused, expected_calls):
    monkeypatch.setenv("ACCOUNT_HOST", "https://unused.invalid")
    monkeypatch.setenv("ACCOUNT_KEY", "unused")
    monkeypatch.setattr(runner, "NONE_OPTIONS_ONLY", focused)
    client = MagicMock()
    owner = client.return_value.__enter__.return_value
    database = owner.create_database.return_value
    database.id = "owned-database"
    database.read.side_effect = runner.exceptions.CosmosResourceNotFoundError(status_code=404)
    monkeypatch.setattr(runner, "CosmosClient", client)
    execute = AsyncMock()
    monkeypatch.setattr(runner, "run_backend", execute)
    asyncio.run(runner.main())
    assert execute.await_count == expected_calls
    assert owner.delete_database.call_count == database.read.call_count == expected_calls
    assert len(runner.REPORT["cleanup"]) == expected_calls
    assert {call.args[0] for call in execute.await_args_list} == {"core-python", "rust"}
    if focused:
        assert all(call.args[1] is False for call in execute.await_args_list)


def test_runner_rejects_conflicting_selections(monkeypatch, tmp_path):
    output = tmp_path / "not_created"
    monkeypatch.setenv("PATCH_REVIEW_OUTPUT", str(output))
    monkeypatch.setenv("PATCH_REVIEW_NONE_OPTIONS", "1")
    monkeypatch.setenv("PATCH_REVIEW_SUPPLEMENTAL", "1")
    with pytest.raises(ValueError, match="mutually exclusive"):
        _load("invalid_patch_selection", ROOT / "scripts" / "v5" / "run_patch_item_parity.py")
    assert not output.exists()


@pytest.mark.parametrize("delta,fallback", [(0, 0), (1, 1)])
def test_runner_rejects_wrong_rust_execution_evidence(runner, monkeypatch, delta, fallback):
    runner.CURRENT.update(backend="rust", surface="sync")
    monkeypatch.setattr(runner, "_binding_operation_count", MagicMock(side_effect=[0, delta]))
    monkeypatch.setattr(runner, "_rust_fallback_count", MagicMock(side_effect=[0, fallback]))
    container = MagicMock()
    container.patch_item.return_value = {"id": "any", "pk": "pk-value", "value": 42, "patched": True}
    with pytest.raises(AssertionError):
        runner.run_none_options(container)
    assert runner.REPORT["patch_calls"][0]["binding_delta"] == delta
    assert runner.REPORT["patch_calls"][0]["fallback_delta"] == fallback


@pytest.mark.parametrize("backend", ["core-python", "rust"])
@pytest.mark.parametrize("asynchronous", [False, True], ids=["sync", "async"])
@pytest.mark.parametrize("outcome", [
    "correct", "returned_operation_missing", "stored_operation_missing",
    "not_stored", "original_field_changed", "unexpected_rejection",
])
def test_ten_operations_checks_every_returned_and_stored_change(
    runner, monkeypatch, backend, asynchronous, outcome,
):
    runner.CURRENT.update(backend=backend, surface="async" if asynchronous else "sync")
    monkeypatch.setattr(runner, "_binding_operation_count", MagicMock(side_effect=[0, int(backend == "rust")]))
    monkeypatch.setattr(runner, "_rust_fallback_count", lambda: 0)
    stored = {}
    events = []
    observed_operations = []
    expected_operations = [{"op": "set", "path": f"/field{i}", "value": i} for i in range(10)]

    def create(body):
        events.append("create")
        stored.update(copy.deepcopy(body))
        return copy.deepcopy(stored)

    def patch(item, partition_key, patch_operations):
        events.append("patch")
        observed_operations.append(copy.deepcopy(patch_operations))
        assert item == stored["id"] and partition_key == stored["pk"]
        assert patch_operations == expected_operations
        if outcome == "unexpected_rejection":
            raise runner.exceptions.CosmosHttpResponseError(status_code=400)
        returned = {**stored, **{f"field{i}": i for i in range(10)}}
        if outcome != "not_stored":
            stored.update(returned)
        if outcome == "returned_operation_missing":
            del returned["field0"]
        if outcome == "stored_operation_missing":
            del stored["field0"]
        if outcome == "original_field_changed":
            stored["status"] = "wrong"
        return returned

    def read(item, partition_key):
        events.append("read")
        assert item == stored["id"] and partition_key == stored["pk"]
        return copy.deepcopy(stored)

    mock = AsyncMock if asynchronous else MagicMock
    container = MagicMock()
    container.create_item = mock(side_effect=create)
    container.patch_item = mock(side_effect=patch)
    container.read_item = mock(side_effect=read)
    if outcome == "correct":
        asyncio.run(runner.scenario(container, "ten_operations"))
        assert events == ["create", "patch", "read"]
        record = runner.REPORT["patch_calls"][0]
        assert record["operation_count"] == 10
        assert record["returned_fields"] == record["stored_fields"] == stored
    else:
        with pytest.raises(AssertionError):
            asyncio.run(runner.scenario(container, "ten_operations"))
    assert observed_operations == [expected_operations]


@pytest.mark.parametrize("backend", ["core-python", "rust"])
@pytest.mark.parametrize("asynchronous", [False, True], ids=["sync", "async"])
@pytest.mark.parametrize("changed", [False, True], ids=["same_version", "changed_version"])
@pytest.mark.parametrize("outcome", [
    "success", "not_stored", "wrong_returned_n", "wrong_returned_id",
    "wrong_stored_pk", "wrong_stored_status", "fallback", "unsupported",
    "http_412", "http_503", "rejected_but_changed", "rejected_but_version_changed",
])
def test_if_none_match_records_version_states_and_checks_outcomes(
    runner, monkeypatch, backend, asynchronous, changed, outcome,
):
    runner.CURRENT.update(backend=backend, surface="async" if asynchronous else "sync")
    rejects = outcome in {
        "unsupported", "http_412", "http_503", "rejected_but_changed", "rejected_but_version_changed",
    }
    unsupported = rejects and outcome not in {"http_412", "http_503"}
    binding_delta = int(backend == "rust" and not unsupported)
    monkeypatch.setattr(runner, "_binding_operation_count", MagicMock(side_effect=[0, binding_delta]))
    monkeypatch.setattr(runner, "_rust_fallback_count", MagicMock(side_effect=[0, int(outcome == "fallback")]))
    stored, requests, events = {}, [], []
    before_n = 8 if changed else 5
    before_etag = "E2" if changed else "E1"

    def create(body):
        events.append("create")
        stored.update(copy.deepcopy(body), _etag="E1")
        return copy.deepcopy(stored)

    def replace(item, body):
        events.append("replace")
        stored.update(copy.deepcopy(body), _etag="E2")
        return copy.deepcopy(stored)

    def patch(item, **kwargs):
        events.append("patch")
        requests.append((item, copy.deepcopy(kwargs)))
        if rejects:
            if outcome == "rejected_but_changed":
                stored["status"] = "wrong"
            if outcome == "rejected_but_version_changed":
                stored["_etag"] = "E3"
            if outcome in {"http_412", "http_503"}:
                raise runner.exceptions.CosmosHttpResponseError(status_code=int(outcome[-3:]))
            raise NotImplementedError("If-None-Match is unsupported")
        returned = dict(stored, n=before_n + 1, _etag="E3")
        if outcome != "not_stored":
            stored.update(returned)
        if outcome == "wrong_returned_n":
            returned["n"] = -1
        if outcome == "wrong_returned_id":
            returned["id"] = "wrong"
        if outcome == "wrong_stored_pk":
            stored["pk"] = "wrong"
        if outcome == "wrong_stored_status":
            stored["status"] = "wrong"
        return returned

    def read(item, partition_key):
        events.append("read")
        return copy.deepcopy(stored)

    mock = AsyncMock if asynchronous else MagicMock
    container = MagicMock()
    container.create_item = mock(side_effect=create)
    container.replace_item = mock(side_effect=replace)
    container.patch_item = mock(side_effect=patch)
    container.read_item = mock(side_effect=read)
    name = "if_none_match_stale" if changed else "if_none_match"
    asyncio.run(runner.record(name, lambda: runner.scenario(container, name)))

    assert events == ["create", *(["replace"] if changed else []), "read", "patch", "read"]
    item = container.create_item.call_args.args[0]["id"]
    assert requests == [(item, {
        "partition_key": item, "patch_operations": [{"op": "incr", "path": "/n", "value": 1}],
        "etag": "E1", "match_condition": runner.MatchConditions.IfModified,
    })]
    assert container.read_item.call_count == 2
    assert all(call.args == (item,) and call.kwargs == {"partition_key": item}
               for call in container.read_item.call_args_list)
    if changed:
        assert container.replace_item.call_args.args == (
            item, {"id": item, "pk": item, "n": 8, "status": "active", "_etag": "E1"},
        )
    observation = runner.REPORT["patch_calls"][0]
    assert observation["saved_etag"] == "E1"
    assert observation["before_etag"] == before_etag
    assert observation["version_changed"] is changed
    assert observation["before_fields"] == {"id": item, "pk": item, "n": before_n, "status": "active"}
    assert observation["stored_fields"] == {key: stored[key] for key in ("id", "pk", "n", "status")}
    assert observation["stored_etag"] == stored["_etag"]
    assert observation["binding_delta"] == binding_delta
    assert observation["fallback_delta"] == int(outcome == "fallback")
    assert observation["error"] == (
        "NotImplementedError" if unsupported else "CosmosHttpResponseError" if rejects else None
    )
    assert observation["status"] == (int(outcome[-3:]) if outcome in {"http_412", "http_503"} else None)
    case = runner.REPORT["cases"][0]
    assert case["outcome"] == ("PASS" if outcome == "success" else "FAIL")
    if outcome == "success":
        assert observation["returned_fields"] == observation["stored_fields"]
        assert observation["stored_n"] == before_n + 1
        assert observation["returned_etag"] == "E3"
    elif rejects:
        assert observation["returned_fields"] is None
        assert observation["returned_etag"] is None
        if outcome == "rejected_but_changed":
            assert "Rejected patch changed stored customer fields" in case["detail"]
        elif outcome == "rejected_but_version_changed":
            assert "Rejected patch changed stored ETag" in case["detail"]
        else:
            assert observation["stored_fields"] == observation["before_fields"]
            assert observation["stored_etag"] == observation["before_etag"]
            assert observation["error"] in case["detail"]


@pytest.mark.parametrize("asynchronous", [False, True], ids=["sync", "async"])
@pytest.mark.parametrize("changed", [False, True], ids=["same_version", "changed_version"])
@pytest.mark.parametrize("invalid", ["wrong_version", "wrong_fields", "missing_etag"])
def test_if_none_match_requires_verified_starting_state(runner, asynchronous, changed, invalid):
    runner.CURRENT.update(backend="core-python", surface="async" if asynchronous else "sync")
    stored = {}

    def create(body):
        stored.update(body, _etag="E1")
        return dict(stored)

    def replace(item, body):
        stored.update(body, _etag="E2")
        return dict(stored)

    def read(item, partition_key):
        result = dict(stored)
        if invalid == "wrong_version":
            result["_etag"] = "E1" if changed else "E2"
        elif invalid == "wrong_fields":
            result["n"] = -1
        else:
            del result["_etag"]
        return result

    mock = AsyncMock if asynchronous else MagicMock
    container = MagicMock()
    container.create_item = mock(side_effect=create)
    container.replace_item = mock(side_effect=replace)
    container.read_item = mock(side_effect=read)
    container.patch_item = mock()
    name = "if_none_match_stale" if changed else "if_none_match"
    asyncio.run(runner.record(name, lambda: runner.scenario(container, name)))
    assert runner.REPORT["cases"][0]["outcome"] == "FAIL"
    container.read_item.assert_called_once()
    container.patch_item.assert_not_called()
    assert not runner.REPORT["patch_calls"]


@pytest.mark.parametrize("backend", ["core-python", "rust"])
@pytest.mark.parametrize("asynchronous", [False, True], ids=["sync", "async"])
@pytest.mark.parametrize("reject,outcome", [
    (False, "correct"), (False, "not_stored"), (False, "wrong_return"),
    (False, "wrong_status"), (False, "unexpected_error"),
    (True, "correct"), (True, "increment_saved"), (True, "status_saved"),
    (True, "pk_changed"), (True, "unexpected_success"), (True, "wrong_error"),
    (True, "field_added"),
])
def test_atomic_patch_checks_valid_prefix_and_rejected_state(
    runner, monkeypatch, backend, asynchronous, reject, outcome,
):
    runner.CURRENT.update(backend=backend, surface="async" if asynchronous else "sync")
    monkeypatch.setattr(runner, "_binding_operation_count", MagicMock(side_effect=[0, int(backend == "rust")]))
    monkeypatch.setattr(runner, "_rust_fallback_count", lambda: 0)
    stored, events, requests = {}, [], []
    operations = [
        {"op": "incr", "path": "/n", "value": 1},
        {"op": "set", "path": "/status", "value": "reviewed"},
    ]
    if reject:
        operations.append({"op": "remove", "path": "/missing_field"})

    def create(body):
        events.append("create")
        stored.update(copy.deepcopy(body))
        return dict(stored)

    def read(item, partition_key):
        events.append("read")
        return dict(stored)

    def patch(item, **kwargs):
        events.append("patch")
        requests.append((item, copy.deepcopy(kwargs)))
        if reject:
            if outcome == "increment_saved":
                stored["n"] = 6
            elif outcome == "status_saved":
                stored["status"] = "reviewed"
            elif outcome == "pk_changed":
                stored["pk"] = "wrong"
            elif outcome == "field_added":
                stored["missing_field"] = True
            elif outcome == "unexpected_success":
                return dict(stored)
            raise runner.exceptions.CosmosHttpResponseError(status_code=503 if outcome == "wrong_error" else 400)
        if outcome == "unexpected_error":
            raise runner.exceptions.CosmosHttpResponseError(status_code=400)
        returned = dict(stored, n=6, status="reviewed")
        if outcome != "not_stored":
            stored.update(returned)
        if outcome == "wrong_return":
            returned["id"] = "wrong"
        elif outcome == "wrong_status":
            stored["status"] = "active"
        return returned

    mock = AsyncMock if asynchronous else MagicMock
    container = MagicMock()
    container.create_item = mock(side_effect=create)
    container.read_item = mock(side_effect=read)
    container.patch_item = mock(side_effect=patch)
    name = "atomic_patch_rejection" if reject else "atomic_patch_control"
    asyncio.run(runner.record(name, lambda: runner.scenario(container, name)))
    item = container.create_item.call_args.args[0]["id"]
    assert events == ["create", "read", "patch", "read"]
    assert requests == [(item, {"partition_key": item, "patch_operations": operations})]
    assert all(call.args == (item,) and call.kwargs == {"partition_key": item}
               for call in container.read_item.call_args_list)
    observation = runner.REPORT["patch_calls"][0]
    assert observation["patch_operations"] == operations
    assert observation["before_fields"] == {"id": item, "pk": item, "n": 5, "status": "active"}
    assert observation["missing_field_before"] is False
    assert observation["missing_field_after"] == ("missing_field" in stored)
    assert observation["stored_fields"] == {key: stored[key] for key in ("id", "pk", "n", "status")}
    assert observation["operation_count"] == len(operations)
    assert observation["binding_delta"] == int(backend == "rust")
    assert observation["fallback_delta"] == 0
    assert runner.REPORT["cases"][0]["outcome"] == ("PASS" if outcome == "correct" else "FAIL")
    if outcome == "correct":
        if reject:
            assert observation["status"] == 400
            assert observation["returned_fields"] is None
            assert observation["stored_fields"] == observation["before_fields"]
        else:
            assert observation["error"] is None
            assert observation["returned_fields"] == observation["stored_fields"] == dict(
                observation["before_fields"], n=6, status="reviewed",
            )


@pytest.mark.parametrize("asynchronous", [False, True], ids=["sync", "async"])
@pytest.mark.parametrize("name", ["atomic_patch_control", "atomic_patch_rejection"])
@pytest.mark.parametrize("invalid", ["wrong_fields", "field_exists"])
def test_atomic_patch_requires_verified_starting_state(runner, asynchronous, name, invalid):
    runner.CURRENT.update(backend="core-python", surface="async" if asynchronous else "sync")
    stored = {}

    def create(body):
        stored.update(body)
        return dict(stored)

    def read(item, partition_key):
        return dict(stored, **({"n": -1} if invalid == "wrong_fields" else {"missing_field": True}))

    mock = AsyncMock if asynchronous else MagicMock
    container = MagicMock()
    container.create_item = mock(side_effect=create)
    container.read_item = mock(side_effect=read)
    container.patch_item = mock()
    asyncio.run(runner.record(name, lambda: runner.scenario(container, name)))
    assert runner.REPORT["cases"][0]["outcome"] == "FAIL"
    container.read_item.assert_called_once()
    container.patch_item.assert_not_called()
    assert not runner.REPORT["patch_calls"]


@pytest.mark.parametrize("backend", ["core-python", "rust"])
@pytest.mark.parametrize("asynchronous", [False, True], ids=["sync", "async"])
@pytest.mark.parametrize("fractional", [False, True], ids=["integer", "fraction"])
@pytest.mark.parametrize("outcome", [
    "correct", "returned_wrong_number", "stored_wrong_number", "not_stored",
    "returned_id_changed", "stored_status_changed", "rejected_400", "rejected_503",
    "rejected_but_changed", "fallback",
])
def test_integer_increment_checks_numeric_states(
    runner, monkeypatch, backend, asynchronous, fractional, outcome,
):
    runner.CURRENT.update(backend=backend, surface="async" if asynchronous else "sync")
    monkeypatch.setattr(runner, "_binding_operation_count", MagicMock(side_effect=[0, int(backend == "rust")]))
    monkeypatch.setattr(runner, "_rust_fallback_count", MagicMock(side_effect=[0, int(outcome == "fallback")]))
    stored, events, requests = {}, [], []
    initial_n = 5.5 if fractional else 5
    operations = [{"op": "incr", "path": "/n", "value": 1}]
    rejects = outcome.startswith("rejected")

    def create(body):
        events.append("create")
        stored.update(copy.deepcopy(body))
        return dict(stored)

    def replace(item, body):
        events.append("replace")
        stored.update(copy.deepcopy(body))
        return dict(stored)

    def read(item, partition_key):
        events.append("read")
        return dict(stored)

    def patch(item, **kwargs):
        events.append("patch")
        requests.append((item, copy.deepcopy(kwargs)))
        if rejects:
            if outcome == "rejected_but_changed":
                stored["n"] = initial_n + 1
            raise runner.exceptions.CosmosHttpResponseError(
                status_code=503 if outcome == "rejected_503" else 400,
            )
        returned = dict(stored, n=initial_n + 1)
        if outcome != "not_stored":
            stored.update(returned)
        wrong_n = 6 if fractional else 7
        if outcome == "returned_wrong_number":
            returned["n"] = wrong_n
        elif outcome == "stored_wrong_number":
            stored["n"] = wrong_n
        elif outcome == "returned_id_changed":
            returned["id"] = "wrong"
        elif outcome == "stored_status_changed":
            stored["status"] = "wrong"
        return returned

    mock = AsyncMock if asynchronous else MagicMock
    container = MagicMock()
    container.create_item = mock(side_effect=create)
    container.replace_item = mock(side_effect=replace)
    container.read_item = mock(side_effect=read)
    container.patch_item = mock(side_effect=patch)
    name = "integer_increment_on_fraction" if fractional else "integer_increment_on_integer"
    asyncio.run(runner.record(name, lambda: runner.scenario(container, name)))
    item = container.create_item.call_args.args[0]["id"]
    assert events == ["create", *(["replace"] if fractional else []), "read", "patch", "read"]
    assert requests == [(item, {"partition_key": item, "patch_operations": operations})]
    assert type(requests[0][1]["patch_operations"][0]["value"]) is int
    assert all(call.args == (item,) and call.kwargs == {"partition_key": item}
               for call in container.read_item.call_args_list)
    observation = runner.REPORT["patch_calls"][0]
    assert observation["patch_operations"] == operations
    assert observation["before_fields"] == {"id": item, "pk": item, "n": initial_n, "status": "active"}
    assert observation["stored_fields"] == {key: stored[key] for key in ("id", "pk", "n", "status")}
    assert observation["operation_count"] == 1
    assert observation["binding_delta"] == int(backend == "rust")
    assert observation["fallback_delta"] == int(outcome == "fallback")
    case = runner.REPORT["cases"][0]
    assert case["outcome"] == ("PASS" if outcome == "correct" else "FAIL")
    if outcome == "correct":
        assert observation["error"] is None
        assert observation["returned_fields"] == observation["stored_fields"] == dict(
            observation["before_fields"], n=initial_n + 1,
        )
    elif rejects:
        assert observation["error"] == "CosmosHttpResponseError"
        assert observation["status"] == (503 if outcome == "rejected_503" else 400)
        assert observation["returned_fields"] is None
        if outcome == "rejected_but_changed":
            assert "Rejected patch changed stored customer fields" in case["detail"]
        else:
            assert observation["stored_fields"] == observation["before_fields"]
            assert "CosmosHttpResponseError" in case["detail"]


@pytest.mark.parametrize("asynchronous", [False, True], ids=["sync", "async"])
@pytest.mark.parametrize("fractional", [False, True], ids=["integer", "fraction"])
@pytest.mark.parametrize("invalid", ["wrong_number", "wrong_status"])
def test_integer_increment_requires_verified_starting_state(runner, asynchronous, fractional, invalid):
    runner.CURRENT.update(backend="core-python", surface="async" if asynchronous else "sync")
    stored = {}

    def create(body):
        stored.update(body)
        return dict(stored)

    def replace(item, body):
        stored.update(body)
        return dict(stored)

    def read(item, partition_key):
        return dict(stored, **({"n": -1} if invalid == "wrong_number" else {"status": "wrong"}))

    mock = AsyncMock if asynchronous else MagicMock
    container = MagicMock()
    container.create_item = mock(side_effect=create)
    container.replace_item = mock(side_effect=replace)
    container.read_item = mock(side_effect=read)
    container.patch_item = mock()
    name = "integer_increment_on_fraction" if fractional else "integer_increment_on_integer"
    asyncio.run(runner.record(name, lambda: runner.scenario(container, name)))
    assert runner.REPORT["cases"][0]["outcome"] == "FAIL"
    container.read_item.assert_called_once()
    container.patch_item.assert_not_called()
    assert not runner.REPORT["patch_calls"]


@pytest.mark.parametrize("backend", ["core-python", "rust"])
@pytest.mark.parametrize("asynchronous", [False, True], ids=["sync", "async"])
@pytest.mark.parametrize("operation", ["add", "set"])
@pytest.mark.parametrize("outcome", [
    "correct", "returned_wrong_semantics", "stored_wrong_semantics",
    "returned_reordered", "stored_reordered", "returned_truncated", "stored_truncated",
    "not_stored", "returned_id_changed", "stored_status_changed",
    "unexpected_rejection", "rejected_but_changed", "fallback",
])
def test_array_patch_checks_complete_returned_and_stored_arrays(
    runner, monkeypatch, backend, asynchronous, operation, outcome,
):
    runner.CURRENT.update(backend=backend, surface="async" if asynchronous else "sync")
    monkeypatch.setattr(runner, "_binding_operation_count", MagicMock(side_effect=[0, int(backend == "rust")]))
    monkeypatch.setattr(runner, "_rust_fallback_count", MagicMock(side_effect=[0, int(outcome == "fallback")]))
    stored, events, requests = {}, [], []
    initial_labels = ["received", "approved"]
    inserted_labels = ["received", "reviewed", "approved"]
    updated_labels = ["received", "reviewed"]
    expected_labels = inserted_labels if operation == "add" else updated_labels
    wrong_labels = updated_labels if operation == "add" else inserted_labels
    operations = [{"op": operation, "path": "/labels/1", "value": "reviewed"}]
    rejects = outcome in ("unexpected_rejection", "rejected_but_changed")

    def create(body):
        events.append("create")
        stored.update(copy.deepcopy(body))
        return copy.deepcopy(stored)

    def read(item, partition_key):
        events.append("read")
        return copy.deepcopy(stored)

    def patch(item, **kwargs):
        events.append("patch")
        requests.append((item, copy.deepcopy(kwargs)))
        if rejects:
            if outcome == "rejected_but_changed":
                stored["labels"] = list(expected_labels)
            raise runner.exceptions.CosmosHttpResponseError(status_code=400)
        returned = copy.deepcopy(stored)
        returned["labels"] = list(expected_labels)
        if outcome != "not_stored":
            stored.update(copy.deepcopy(returned))
        if outcome == "returned_wrong_semantics":
            returned["labels"] = list(wrong_labels)
        elif outcome == "stored_wrong_semantics":
            stored["labels"] = list(wrong_labels)
        elif outcome == "returned_reordered":
            returned["labels"].reverse()
        elif outcome == "stored_reordered":
            stored["labels"].reverse()
        elif outcome == "returned_truncated":
            returned["labels"].pop()
        elif outcome == "stored_truncated":
            stored["labels"].pop()
        elif outcome == "returned_id_changed":
            returned["id"] = "wrong"
        elif outcome == "stored_status_changed":
            stored["status"] = "wrong"
        return returned

    mock = AsyncMock if asynchronous else MagicMock
    container = MagicMock()
    container.create_item = mock(side_effect=create)
    container.read_item = mock(side_effect=read)
    container.patch_item = mock(side_effect=patch)
    name = "array_" + operation
    asyncio.run(runner.record(name, lambda: runner.scenario(container, name)))
    item = container.create_item.call_args.args[0]["id"]
    before = {"id": item, "pk": item, "n": 5, "status": "active", "labels": initial_labels}
    assert container.create_item.call_args.args == (before,)
    assert events == ["create", "read", "patch", "read"]
    assert requests == [(item, {"partition_key": item, "patch_operations": operations})]
    assert all(call.args == (item,) and call.kwargs == {"partition_key": item}
               for call in container.read_item.call_args_list)
    observation = runner.REPORT["patch_calls"][0]
    assert observation["patch_operations"] == operations
    assert observation["before_fields"] == before
    assert observation["stored_fields"] == stored
    assert observation["operation_count"] == 1
    assert observation["binding_delta"] == int(backend == "rust")
    assert observation["fallback_delta"] == int(outcome == "fallback")
    case = runner.REPORT["cases"][0]
    assert case["outcome"] == ("PASS" if outcome == "correct" else "FAIL")
    if outcome == "correct":
        assert observation["error"] is None
        assert observation["returned_fields"] == observation["stored_fields"] == dict(
            before, labels=expected_labels,
        )
    elif rejects:
        assert observation["error"] == "CosmosHttpResponseError"
        assert observation["status"] == 400
        assert observation["returned_fields"] is None
        if outcome == "rejected_but_changed":
            assert "Rejected patch changed stored customer fields" in case["detail"]
        else:
            assert observation["stored_fields"] == before
            assert "CosmosHttpResponseError" in case["detail"]


@pytest.mark.parametrize("asynchronous", [False, True], ids=["sync", "async"])
@pytest.mark.parametrize("operation", ["add", "set", "add_then_remove", "remove_then_add"])
@pytest.mark.parametrize("invalid", ["wrong_order", "missing_labels", "wrong_status"])
def test_array_patch_requires_verified_starting_state(runner, asynchronous, operation, invalid):
    runner.CURRENT.update(backend="core-python", surface="async" if asynchronous else "sync")
    stored = {}

    def create(body):
        stored.update(copy.deepcopy(body))
        return copy.deepcopy(stored)

    def read(item, partition_key):
        result = copy.deepcopy(stored)
        if invalid == "wrong_order":
            result["labels"] = ["approved", "received"]
        elif invalid == "missing_labels":
            result.pop("labels", None)
        else:
            result["status"] = "wrong"
        return result

    mock = AsyncMock if asynchronous else MagicMock
    container = MagicMock()
    container.create_item = mock(side_effect=create)
    container.read_item = mock(side_effect=read)
    container.patch_item = mock()
    name = "array_" + operation
    asyncio.run(runner.record(name, lambda: runner.scenario(container, name)))
    assert runner.REPORT["cases"][0]["outcome"] == "FAIL"
    container.read_item.assert_called_once()
    container.patch_item.assert_not_called()
    assert not runner.REPORT["patch_calls"]


@pytest.mark.parametrize("backend", ["core-python", "rust"])
@pytest.mark.parametrize("asynchronous", [False, True], ids=["sync", "async"])
@pytest.mark.parametrize("reverse", [False, True], ids=["add_then_remove", "remove_then_add"])
@pytest.mark.parametrize("outcome", [
    "correct", "opposite_order", "skip_remove", "skip_add", "not_stored",
    "wrong_return", "wrong_stored_field", "wrong_error", "fallback",
])
def test_array_patch_order_uses_updated_indexes(
    runner, monkeypatch, backend, asynchronous, reverse, outcome,
):
    runner.CURRENT.update(backend=backend, surface="async" if asynchronous else "sync")
    monkeypatch.setattr(runner, "_binding_operation_count", MagicMock(side_effect=[0, int(backend == "rust")]))
    monkeypatch.setattr(runner, "_rust_fallback_count", MagicMock(side_effect=[0, int(outcome == "fallback")]))
    stored, events, requests = {}, [], []
    operations = [
        {"op": "add", "path": "/labels/1", "value": "reviewed"},
        {"op": "remove", "path": "/labels/2"},
    ]
    if reverse:
        operations.reverse()

    def create(body):
        events.append("create")
        stored.update(copy.deepcopy(body))
        return copy.deepcopy(stored)

    def read(item, partition_key):
        events.append("read")
        return copy.deepcopy(stored)

    def patch(item, **kwargs):
        events.append("patch")
        requests.append((item, copy.deepcopy(kwargs)))
        if outcome == "wrong_error":
            raise runner.exceptions.CosmosHttpResponseError(status_code=503)
        if not reverse and outcome in ("opposite_order", "skip_add"):
            raise runner.exceptions.CosmosHttpResponseError(status_code=400)
        if reverse and outcome in ("correct", "fallback", "wrong_stored_field"):
            if outcome == "wrong_stored_field":
                stored["status"] = "wrong"
            raise runner.exceptions.CosmosHttpResponseError(status_code=400)
        returned = copy.deepcopy(stored)
        returned["labels"] = ["received", "reviewed"]
        if outcome == "skip_remove":
            returned["labels"] = ["received", "reviewed", "approved"]
        elif outcome == "skip_add":
            returned["labels"] = ["received", "approved"]
        if outcome != "not_stored":
            stored.update(copy.deepcopy(returned))
        if outcome == "wrong_return":
            returned["labels"] = ["reviewed", "received"]
        elif outcome == "wrong_stored_field":
            stored["pk"] = "wrong"
        return returned

    mock = AsyncMock if asynchronous else MagicMock
    container = MagicMock()
    container.create_item = mock(side_effect=create)
    container.read_item = mock(side_effect=read)
    container.patch_item = mock(side_effect=patch)
    name = "array_remove_then_add" if reverse else "array_add_then_remove"
    asyncio.run(runner.record(name, lambda: runner.scenario(container, name)))
    item = container.create_item.call_args.args[0]["id"]
    before = {"id": item, "pk": item, "n": 5, "status": "active", "labels": ["received", "approved"]}
    assert container.create_item.call_args.args == (before,)
    assert events == ["create", "read", "patch", "read"]
    assert requests == [(item, {"partition_key": item, "patch_operations": operations})]
    assert all(call.args == (item,) and call.kwargs == {"partition_key": item}
               for call in container.read_item.call_args_list)
    observation = runner.REPORT["patch_calls"][0]
    assert observation["before_fields"] == before
    assert observation["patch_operations"] == operations
    assert observation["operation_count"] == 2
    assert observation["stored_fields"] == stored
    assert observation["binding_delta"] == int(backend == "rust")
    assert observation["fallback_delta"] == int(outcome == "fallback")
    case = runner.REPORT["cases"][0]
    assert case["outcome"] == ("PASS" if outcome == "correct" else "FAIL")
    if outcome == "correct":
        if reverse:
            assert observation["error"] == "CosmosHttpResponseError" and observation["status"] == 400
            assert observation["returned_fields"] is None
            assert observation["stored_fields"] == before
        else:
            assert observation["error"] is None
            assert observation["returned_fields"] == observation["stored_fields"] == dict(
                before, labels=["received", "reviewed"],
            )
    if reverse and outcome == "wrong_stored_field":
        assert "Rejected patch changed stored customer fields" in case["detail"]


@pytest.mark.parametrize("backend", ["core-python", "rust"])
@pytest.mark.parametrize("asynchronous", [False, True], ids=["sync", "async"])
@pytest.mark.parametrize("reject,outcome", [
    (False, "correct"), (False, "not_stored"), (False, "returned_body"),
    (False, "returned_none"), (False, "wrong_fields"), (False, "unexpected_error"),
    (True, "correct"), (True, "swallowed_error"), (True, "wrong_error"),
    (True, "changed_after_error"), (True, "missing_field_added"),
])
def test_no_response_checks_public_result_and_stored_state(
    runner, monkeypatch, backend, asynchronous, reject, outcome,
):
    runner.CURRENT.update(backend=backend, surface="async" if asynchronous else "sync")
    monkeypatch.setattr(runner, "_binding_operation_count", MagicMock(side_effect=[0, int(backend == "rust")]))
    monkeypatch.setattr(runner, "_rust_fallback_count", lambda: 0)
    stored, events, requests = {}, [], []
    operations = ([{"op": "remove", "path": "/missing_field"}] if reject else
                  [{"op": "incr", "path": "/n", "value": 1}])

    def create(body):
        events.append("create")
        stored.update(copy.deepcopy(body))
        return dict(stored)

    def read(item, partition_key):
        events.append("read")
        return dict(stored)

    def patch(item, **kwargs):
        events.append("patch")
        requests.append((item, copy.deepcopy(kwargs)))
        if reject:
            if outcome == "swallowed_error":
                return {}
            if outcome == "changed_after_error":
                stored["status"] = "wrong"
            if outcome == "missing_field_added":
                stored["missing_field"] = True
            raise runner.exceptions.CosmosHttpResponseError(
                status_code=503 if outcome == "wrong_error" else 400,
            )
        if outcome == "unexpected_error":
            raise runner.exceptions.CosmosHttpResponseError(status_code=400)
        if outcome != "not_stored":
            stored["n"] = 6
        if outcome == "wrong_fields":
            stored["status"] = "wrong"
        if outcome == "returned_body":
            return dict(stored)
        return None if outcome == "returned_none" else {}

    mock = AsyncMock if asynchronous else MagicMock
    container = MagicMock()
    container.create_item = mock(side_effect=create)
    container.read_item = mock(side_effect=read)
    container.patch_item = mock(side_effect=patch)
    name = "no_response_rejection" if reject else "no_response"
    asyncio.run(runner.record(name, lambda: runner.scenario(container, name)))
    item = container.create_item.call_args.args[0]["id"]
    before = {"id": item, "pk": item, "n": 5, "status": "active"}
    assert events == ["create", "read", "patch", "read"]
    assert requests == [(item, {"partition_key": item, "patch_operations": operations, "no_response": True})]
    assert all(call.args == (item,) and call.kwargs == {"partition_key": item}
               for call in container.read_item.call_args_list)
    observation = runner.REPORT["patch_calls"][0]
    assert observation["before_fields"] == before
    assert observation["patch_operations"] == operations
    assert observation["no_response"] is True
    assert observation["operation_count"] == 1
    assert observation["stored_fields"] == {key: stored[key] for key in before}
    assert observation["missing_field_before"] is False
    assert observation["missing_field_after"] == ("missing_field" in stored)
    assert observation["binding_delta"] == int(backend == "rust")
    assert observation["fallback_delta"] == 0
    case = runner.REPORT["cases"][0]
    assert case["outcome"] == ("PASS" if outcome == "correct" else "FAIL")
    if outcome == "correct":
        if reject:
            assert observation["error"] == "CosmosHttpResponseError" and observation["status"] == 400
            assert observation["returned_body"] is None
            assert observation["stored_fields"] == before
        else:
            assert observation["error"] is None and observation["returned_body"] == {}
            assert observation["stored_fields"] == dict(before, n=6)
    if outcome == "changed_after_error":
        assert "Rejected patch changed stored customer fields" in case["detail"]


@pytest.mark.parametrize("asynchronous", [False, True], ids=["sync", "async"])
@pytest.mark.parametrize("name", ["no_response", "no_response_rejection"])
@pytest.mark.parametrize("invalid", ["wrong_fields", "field_exists"])
def test_no_response_requires_verified_starting_state(runner, asynchronous, name, invalid):
    runner.CURRENT.update(backend="core-python", surface="async" if asynchronous else "sync")
    stored = {}

    def create(body):
        stored.update(body)
        return dict(stored)

    def read(item, partition_key):
        return dict(stored, **({"n": -1} if invalid == "wrong_fields" else {"missing_field": True}))

    mock = AsyncMock if asynchronous else MagicMock
    container = MagicMock()
    container.create_item = mock(side_effect=create)
    container.read_item = mock(side_effect=read)
    container.patch_item = mock()
    asyncio.run(runner.record(name, lambda: runner.scenario(container, name)))
    assert runner.REPORT["cases"][0]["outcome"] == "FAIL"
    container.read_item.assert_called_once()
    container.patch_item.assert_not_called()
    assert not runner.REPORT["patch_calls"]


@pytest.mark.parametrize("backend", ["core-python", "rust"])
@pytest.mark.parametrize("asynchronous", [False, True], ids=["sync", "async"])
@pytest.mark.parametrize("outcome", [
    "correct", "missing_hook", "duplicate_hook", "stale_hook",
    "wrong_hook_id", "missing_hook_pk", "wrong_hook_status",
    "corrected_after_callback", "mutated_after_callback",
    "wrong_returned_id", "not_stored", "wrong_stored_status",
])
def test_response_hook_checks_expected_customer_fields(runner, monkeypatch, backend, asynchronous, outcome):
    runner.CURRENT.update(backend=backend, surface="async" if asynchronous else "sync")
    monkeypatch.setattr(runner, "_binding_operation_count", MagicMock(side_effect=[0, int(backend == "rust")]))
    monkeypatch.setattr(runner, "_rust_fallback_count", lambda: 0)
    stored, events, requests, delivered = {}, [], [], []
    operations = [{"op": "incr", "path": "/n", "value": 1}]

    def create(body):
        events.append("create")
        stored.update(copy.deepcopy(body))
        return dict(stored)

    def read(item, partition_key):
        events.append("read")
        return dict(stored)

    def patch(item, *, partition_key, patch_operations, response_hook):
        events.append("patch")
        requests.append((item, partition_key, copy.deepcopy(patch_operations)))
        returned = dict(stored, n=6)
        if outcome != "not_stored":
            stored.update(returned)
        body = dict(returned)
        if outcome == "stale_hook":
            body["n"] = 5
        elif outcome in ("wrong_hook_id", "corrected_after_callback"):
            body["id"] = "wrong"
        elif outcome == "missing_hook_pk":
            del body["pk"]
        elif outcome == "wrong_hook_status":
            body["status"] = "wrong"
        count = 0 if outcome == "missing_hook" else 2 if outcome == "duplicate_hook" else 1
        for _ in range(count):
            events.append("hook")
            delivered.append(dict(body))
            assert response_hook({"x-test-header": "controlled"}, body) is None
        if outcome == "corrected_after_callback":
            body["id"] = returned["id"]
        elif outcome == "mutated_after_callback":
            body["n"] = -1
        if outcome == "wrong_returned_id":
            returned["id"] = "wrong"
        elif outcome == "wrong_stored_status":
            stored["status"] = "wrong"
        return returned

    mock = AsyncMock if asynchronous else MagicMock
    container = MagicMock()
    container.create_item = mock(side_effect=create)
    container.read_item = mock(side_effect=read)
    container.patch_item = mock(side_effect=patch)
    asyncio.run(runner.record("response_hook", lambda: runner.scenario(container, "response_hook")))
    item = container.create_item.call_args.args[0]["id"]
    before = {"id": item, "pk": item, "n": 5, "status": "active"}
    assert requests == [(item, item, operations)]
    assert events == ["create", "read", "patch", *(["hook"] * len(delivered)), "read"]
    assert all(call.args == (item,) and call.kwargs == {"partition_key": item}
               for call in container.read_item.call_args_list)
    observation = runner.REPORT["patch_calls"][0]
    assert observation["before_fields"] == before
    assert observation["hook_fields"] == delivered
    assert observation["hooks"] == len(delivered)
    assert observation["patch_operations"] == operations
    assert observation["operation_count"] == 1
    assert observation["stored_fields"] == stored
    assert observation["binding_delta"] == int(backend == "rust")
    assert observation["fallback_delta"] == 0
    correct = outcome in ("correct", "mutated_after_callback")
    assert runner.REPORT["cases"][0]["outcome"] == ("PASS" if correct else "FAIL")
    if correct:
        expected = dict(before, n=6)
        assert observation["hook_fields"] == [expected]
        assert observation["returned_fields"] == observation["stored_fields"] == expected


@pytest.mark.parametrize("asynchronous", [False, True], ids=["sync", "async"])
@pytest.mark.parametrize("invalid", ["wrong_number", "wrong_id"])
def test_response_hook_requires_verified_starting_state(runner, asynchronous, invalid):
    runner.CURRENT.update(backend="core-python", surface="async" if asynchronous else "sync")
    stored = {}

    def create(body):
        stored.update(body)
        return dict(stored)

    def read(item, partition_key):
        return dict(stored, **({"n": -1} if invalid == "wrong_number" else {"id": "wrong"}))

    mock = AsyncMock if asynchronous else MagicMock
    container = MagicMock()
    container.create_item = mock(side_effect=create)
    container.read_item = mock(side_effect=read)
    container.patch_item = mock()
    asyncio.run(runner.record("response_hook", lambda: runner.scenario(container, "response_hook")))
    assert runner.REPORT["cases"][0]["outcome"] == "FAIL"
    container.read_item.assert_called_once()
    container.patch_item.assert_not_called()
    assert not runner.REPORT["patch_calls"]


@pytest.mark.parametrize("backend", ["core-python", "rust"])
@pytest.mark.parametrize("asynchronous", [False, True], ids=["sync", "async"])
@pytest.mark.parametrize("name,outcome", [
    ("etag_current", outcome) for outcome in (
        "correct", "wrong_returned_id", "missing_returned_pk", "wrong_returned_status",
        "not_stored", "wrong_stored_status", "unexpected_rejection",
    )
] + [
    ("etag_stale", outcome) for outcome in (
        "correct", "wrong_stored_status", "wrong_stored_id", "missing_stored_pk",
        "changed_etag", "missing_etag", "wrong_status", "unexpected_success", "changed_number",
    )
])
def test_if_match_checks_customer_fields_and_rejected_version(
    runner, monkeypatch, backend, asynchronous, name, outcome,
):
    runner.CURRENT.update(backend=backend, surface="async" if asynchronous else "sync")
    monkeypatch.setattr(runner, "_binding_operation_count", MagicMock(side_effect=[0, int(backend == "rust")]))
    monkeypatch.setattr(runner, "_rust_fallback_count", lambda: 0)
    stale = name == "etag_stale"
    stored, events, requests = {}, [], []

    def create(body):
        events.append("create")
        stored.update(body, _etag="E1")
        return dict(stored)

    def replace(item, body):
        events.append("replace")
        stored.update(body, _etag="E2")
        return dict(stored)

    def read(item, partition_key):
        events.append("read")
        return dict(stored)

    def patch(item, **kwargs):
        events.append("patch")
        requests.append((item, copy.deepcopy(kwargs)))
        if not stale:
            returned = dict(stored, n=6, _etag="E3")
            if outcome != "not_stored":
                stored.update(returned)
            if outcome == "wrong_returned_id":
                returned["id"] = "wrong"
            elif outcome == "missing_returned_pk":
                del returned["pk"]
            elif outcome == "wrong_returned_status":
                returned["status"] = "wrong"
            elif outcome == "wrong_stored_status":
                stored["status"] = "wrong"
            elif outcome == "unexpected_rejection":
                raise runner.exceptions.CosmosHttpResponseError(status_code=412, message="controlled")
            return returned
        if outcome == "wrong_stored_status":
            stored["status"] = "wrong"
        elif outcome == "wrong_stored_id":
            stored["id"] = "wrong"
        elif outcome == "missing_stored_pk":
            del stored["pk"]
        elif outcome == "changed_etag":
            stored["_etag"] = "E3"
        elif outcome == "missing_etag":
            del stored["_etag"]
        elif outcome == "changed_number":
            stored["n"] = 9
        elif outcome == "unexpected_success":
            return dict(stored)
        raise runner.exceptions.CosmosHttpResponseError(
            status_code=400 if outcome == "wrong_status" else 412, message="controlled",
        )

    mock = AsyncMock if asynchronous else MagicMock
    container = MagicMock()
    for method, callback in (("create_item", create), ("replace_item", replace),
                             ("read_item", read), ("patch_item", patch)):
        setattr(container, method, mock(side_effect=callback))
    asyncio.run(runner.record(name, lambda: runner.scenario(container, name)))
    item = container.create_item.call_args.args[0]["id"]
    operations = [{"op": "incr", "path": "/n", "value": 1}]
    assert requests == [(item, {
        "partition_key": item, "patch_operations": operations,
        "etag": "E1", "match_condition": runner.MatchConditions.IfNotModified,
    })]
    assert events == ["create", *(["replace"] if stale else []), "read", "patch", "read"]
    observation = runner.REPORT["patch_calls"][0]
    before = {"id": item, "pk": item, "n": 8 if stale else 5, "status": "active"}
    assert observation["before_fields"] == before
    assert observation["saved_etag"] == "E1"
    assert observation["before_etag"] == ("E2" if stale else "E1")
    assert observation["version_changed"] is stale
    assert observation["stored_etag"] == stored.get("_etag")
    assert observation["stored_fields"] == {key: stored.get(key) for key in before}
    assert observation["patch_operations"] == operations
    assert observation["operation_count"] == 1
    assert observation["binding_delta"] == int(backend == "rust")
    assert observation["fallback_delta"] == 0
    assert runner.REPORT["cases"][0]["outcome"] == ("PASS" if outcome == "correct" else "FAIL")
    if outcome == "correct":
        expected = before if stale else dict(before, n=6)
        assert observation["stored_fields"] == expected
        assert observation["returned_fields"] == (None if stale else expected)
        assert observation["returned_etag"] == (None if stale else "E3")
        assert observation["status"] == (412 if stale else None)


@pytest.mark.parametrize("asynchronous", [False, True], ids=["sync", "async"])
@pytest.mark.parametrize("name", [
    "etag_current", "etag_stale", "filter_etag_current", "filter_etag_stale",
    "filter_false_etag_current", "filter_false_etag_stale",
])
@pytest.mark.parametrize("invalid", [
    "wrong_number", "wrong_id", "missing_pk", "wrong_status", "wrong_version",
    "empty_saved_etag", "nonstring_saved_etag", "empty_before_etag", "nonstring_before_etag",
])
def test_if_match_requires_verified_starting_state(runner, asynchronous, name, invalid):
    runner.CURRENT.update(backend="core-python", surface="async" if asynchronous else "sync")
    stored = {}

    def create(body):
        etag = "" if invalid == "empty_saved_etag" else 7 if invalid == "nonstring_saved_etag" else "E1"
        stored.update(body, _etag=etag)
        return dict(stored)

    def replace(item, body):
        stored.update(body, _etag="E2")
        return dict(stored)

    def read(item, partition_key):
        body = dict(stored)
        if invalid == "wrong_number":
            body["n"] = -1
        elif invalid == "wrong_id":
            body["id"] = "wrong"
        elif invalid == "missing_pk":
            del body["pk"]
        elif invalid == "wrong_status":
            body["status"] = "wrong"
        elif invalid == "wrong_version":
            body["_etag"] = "E1" if name.endswith("_stale") else "E2"
        elif invalid == "empty_before_etag":
            body["_etag"] = ""
        elif invalid == "nonstring_before_etag":
            body["_etag"] = 7
        return body

    mock = AsyncMock if asynchronous else MagicMock
    container = MagicMock()
    container.create_item = mock(side_effect=create)
    container.replace_item = mock(side_effect=replace)
    container.read_item = mock(side_effect=read)
    container.patch_item = mock(return_value={"n": 6})
    asyncio.run(runner.record(name, lambda: runner.scenario(container, name)))
    assert runner.REPORT["cases"][0]["outcome"] == "FAIL"
    container.read_item.assert_called_once()
    container.patch_item.assert_not_called()
    assert not runner.REPORT["patch_calls"]


@pytest.mark.parametrize("backend", ["core-python", "rust"])
@pytest.mark.parametrize("asynchronous", [False, True], ids=["sync", "async"])
@pytest.mark.parametrize("name", [
    "filter_etag_current", "filter_etag_stale",
    "filter_false_etag_current", "filter_false_etag_stale",
])
@pytest.mark.parametrize("behavior", [
    "correct", "ignore_filter", "ignore_etag", "always_reject", "always_accept",
    "not_stored", "changed_status", "changed_etag", "wrong_returned_id",
])
def test_combined_conditions_require_both_predicate_and_version(
    runner, monkeypatch, backend, asynchronous, name, behavior,
):
    runner.CURRENT.update(backend=backend, surface="async" if asynchronous else "sync")
    monkeypatch.setattr(runner, "_binding_operation_count", MagicMock(side_effect=[0, int(backend == "rust")]))
    monkeypatch.setattr(runner, "_rust_fallback_count", lambda: 0)
    stale = name.endswith("_stale")
    matches = name in ("filter_etag_current", "filter_etag_stale")
    expected_success = matches and not stale
    stored, events, requests, accepted = {}, [], [], []

    def create(body):
        events.append("create")
        stored.update(body, _etag="E1")
        return dict(stored)

    def replace(item, body):
        events.append("replace")
        stored.update(body, _etag="E2")
        return dict(stored)

    def read(item, partition_key):
        events.append("read")
        return dict(stored)

    def patch(item, **kwargs):
        events.append("patch")
        requests.append((item, copy.deepcopy(kwargs)))
        predicate_matches = kwargs["filter_predicate"] == f"FROM c WHERE c.status = '{stored['status']}'"
        version_matches = kwargs["etag"] == stored["_etag"]
        success = (predicate_matches or behavior == "ignore_filter") and (
            version_matches or behavior == "ignore_etag"
        )
        if behavior in ("always_accept", "always_reject"):
            success = behavior == "always_accept"
        accepted.append(success)
        returned = dict(stored, n=stored["n"] + 1, _etag="E3") if success else None
        if success and behavior != "not_stored":
            stored.update(returned)
        if behavior == "changed_status":
            stored["status"] = "wrong"
        elif behavior == "changed_etag":
            stored["_etag"] = "unexpected"
        if not success:
            raise runner.exceptions.CosmosAccessConditionFailedError(status_code=412, message="controlled")
        if behavior == "wrong_returned_id":
            returned["id"] = "wrong"
        return returned

    mock = AsyncMock if asynchronous else MagicMock
    container = MagicMock()
    for method, callback in (("create_item", create), ("replace_item", replace),
                             ("read_item", read), ("patch_item", patch)):
        setattr(container, method, mock(side_effect=callback))
    asyncio.run(runner.record(name, lambda: runner.scenario(container, name)))
    item = container.create_item.call_args.args[0]["id"]
    predicate = "FROM c WHERE c.status = 'active'" if matches else "FROM c WHERE c.status = 'cancelled'"
    operations = [{"op": "incr", "path": "/n", "value": 1}]
    assert requests == [(item, {
        "partition_key": item, "patch_operations": operations, "filter_predicate": predicate,
        "etag": "E1", "match_condition": runner.MatchConditions.IfNotModified,
    })]
    assert events == ["create", *(["replace"] if stale else []), "read", "patch", "read"]
    assert all(call.args == (item,) and call.kwargs == {"partition_key": item}
               for call in container.read_item.call_args_list)
    observation = runner.REPORT["patch_calls"][0]
    before = {"id": item, "pk": item, "n": 8 if stale else 5, "status": "active"}
    assert observation["before_fields"] == before
    assert observation["filter_predicate"] == predicate
    assert observation["filter_matches"] is matches
    assert observation["saved_etag"] == "E1"
    assert observation["before_etag"] == ("E2" if stale else "E1")
    assert observation["version_changed"] is stale
    assert observation["stored_fields"] == {key: stored[key] for key in before}
    assert observation["stored_etag"] == stored["_etag"]
    assert observation["patch_operations"] == operations
    assert observation["operation_count"] == 1
    assert observation["binding_delta"] == int(backend == "rust")
    assert observation["fallback_delta"] == 0
    should_pass = accepted == [expected_success] and behavior != "changed_status"
    if behavior in ("not_stored", "wrong_returned_id") and expected_success:
        should_pass = False
    if behavior == "changed_etag" and not expected_success:
        should_pass = False
    assert runner.REPORT["cases"][0]["outcome"] == ("PASS" if should_pass else "FAIL")
    if behavior == "correct":
        expected = dict(before, n=6) if expected_success else before
        assert observation["stored_fields"] == expected
        assert observation["returned_fields"] == (expected if expected_success else None)
        assert observation["status"] == (None if expected_success else 412)
        if not expected_success:
            assert observation["stored_etag"] == observation["before_etag"]
