# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.
"""Compare copied original patch tests and strict probes on owned live resources.

Set ACCOUNT_HOST and ACCOUNT_KEY, and optionally PATCH_REVIEW_OUTPUT to a new
evidence directory. PATCH_REVIEW_SUPPLEMENTAL=1 selects numeric/trigger probes.
PATCH_REVIEW_NONE_OPTIONS=1 selects only the synchronous original None-options
method on both backends. The default run also includes this method and both
integer-starting-value and fractional-starting-value integer increment probes.
The if_none_match probes compare legacy acceptance in both version states;
a passing legacy case does not establish enforcement of the condition.
Known incompatibilities remain failures; this runner does not mark them xfail.
"""
import ast
import asyncio
import hashlib
import inspect
import json
import os
from pathlib import Path
import sys
import textwrap
from types import SimpleNamespace
import unittest
from unittest.mock import patch
import uuid

ROOT = Path(__file__).resolve().parents[2]
sys.path[:0] = [str(ROOT), str(ROOT / "tests")]

from azure.core import MatchConditions
from azure.cosmos import CosmosClient, PartitionKey, exceptions
from azure.cosmos.aio import CosmosClient as AsyncCosmosClient
from azure.cosmos.http_constants import StatusCodes
from common._parity_helpers import _binding_operation_count, _rust_fallback_count


NONE_OPTIONS_ONLY = os.environ.get("PATCH_REVIEW_NONE_OPTIONS") == "1"
if NONE_OPTIONS_ONLY and os.environ.get("PATCH_REVIEW_SUPPLEMENTAL"):
    raise ValueError("PATCH_REVIEW_NONE_OPTIONS and PATCH_REVIEW_SUPPLEMENTAL are mutually exclusive")

OUT = Path(os.environ.get(
    "PATCH_REVIEW_OUTPUT", str(ROOT / "docs" / "V5" / "_parity_runs" / ("patch_item_" + uuid.uuid4().hex))
))
OUT.mkdir(parents=True, exist_ok=False)
REPORT = {"cases": [], "patch_calls": [], "sources": {}, "cleanup": []}
CURRENT = {}


def copy_original(filename, names):
    source = (ROOT / "tests" / filename).read_text(encoding="utf-8-sig")
    nodes = {n.name: n for n in ast.walk(ast.parse(source))
             if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef)) and n.name in names}
    assert set(nodes) == set(names)
    copied = "\n\n".join(textwrap.dedent(ast.get_source_segment(source, nodes[n])) for n in names)
    (OUT / ("copied_" + filename)).write_text(copied + "\n", encoding="utf-8")
    namespace = dict(globals())
    exec(compile(copied, filename, "exec"), namespace)
    REPORT["sources"][filename] = hashlib.sha256(source.encode()).hexdigest()
    for name in names:
        copied_node = next(n for n in ast.parse(copied).body if n.name == name)
        assert ast.dump(nodes[name], include_attributes=False) == ast.dump(copied_node, include_attributes=False)
    return [namespace[name] for name in names]


SYNC = copy_original("test_crud.py", ["test_patch_operations", "test_conditional_patching"])
ASYNC = copy_original("test_crud_async.py", ["test_patch_operations_async", "test_conditional_patching_async"])
NONE_OPTIONS = copy_original("test_none_options.py", ["_create_sample_item", "test_patch_item_none_options"])


def run_none_options(container):
    case = unittest.TestCase()
    case.container = container
    case._create_sample_item = lambda: NONE_OPTIONS[0](case)
    observation = dict(CURRENT, operation="test_patch_item_none_options")
    REPORT["patch_calls"].append(observation)
    original_patch, original_read = container.patch_item, container.read_item
    fields = ("id", "pk", "value", "patched")

    def observed_patch(item, **kwargs):
        observation.update(target=item, partition_key=kwargs["partition_key"],
                           patch_operations=kwargs["patch_operations"])
        before = (_binding_operation_count(), _rust_fallback_count())
        try:
            result = original_patch(item, **kwargs)
        finally:
            observation["binding_delta"] = _binding_operation_count() - before[0]
            observation["fallback_delta"] = _rust_fallback_count() - before[1]
        observation["returned_fields"] = {key: result[key] for key in fields if key in result}
        assert observation["fallback_delta"] == 0
        assert observation["binding_delta"] == (1 if CURRENT["backend"] == "rust" else 0)
        return result

    def observed_read(item, **kwargs):
        result = original_read(item, **kwargs)
        observation["stored_fields"] = {key: result[key] for key in fields if key in result}
        return result

    with patch.object(container, "patch_item", observed_patch), patch.object(container, "read_item", observed_read):
        NONE_OPTIONS[1](case)
    print(json.dumps(observation), flush=True)


async def invoke(method, *args, **kwargs):
    value = method(*args, **kwargs)
    return await value if inspect.isawaitable(value) else value


async def scenario(container, name):
    key = uuid.uuid4().hex
    array_patch = name in ("array_add", "array_set", "array_add_then_remove", "array_remove_then_add")
    initial_item = {"id": key, "pk": key, "n": 5, "status": "active"}
    if array_patch:
        initial_item["labels"] = ["received", "approved"]
    original = await invoke(container.create_item, initial_item)
    operations = [{"op": "incr", "path": "/n", "value": 1}]
    options = {}
    target = key
    expected_error = None
    expected_n = 6
    expected_fields = None
    if_none_match = name in ("if_none_match", "if_none_match_stale")
    combined_filter = name in (
        "filter_etag_current", "filter_etag_stale",
        "filter_false_etag_current", "filter_false_etag_stale",
    )
    if_match = name in ("etag_current", "etag_stale") or combined_filter
    atomic_patch = name in ("atomic_patch_control", "atomic_patch_rejection")
    numeric_increment = name in ("integer_increment_on_integer", "integer_increment_on_fraction")
    no_response = name in ("no_response", "no_response_rejection")
    state_before = None
    hook_calls = []
    if array_patch:
        operation = "set" if name == "array_set" else "add"
        operations = [{"op": operation, "path": "/labels/1", "value": "reviewed"}]
        if name in ("array_add_then_remove", "array_remove_then_add"):
            operations.append({"op": "remove", "path": "/labels/2"})
            if name == "array_remove_then_add":
                operations.reverse()
                expected_error = 400
        state_before = await invoke(container.read_item, key, partition_key=key)
        initial_fields = {
            "id": key, "pk": key, "n": 5, "status": "active", "labels": ["received", "approved"],
        }
        assert {key: state_before.get(key) for key in initial_fields} == initial_fields, (
            "Unexpected starting customer fields"
        )
        expected_n = 5
        labels = ["received", "reviewed", "approved"] if name == "array_add" else ["received", "reviewed"]
        if name == "array_remove_then_add":
            labels = ["received", "approved"]
        expected_fields = dict(initial_fields, labels=labels)
    elif numeric_increment:
        initial_n = 5
        if name == "integer_increment_on_fraction":
            initial_n = 5.5
            original = await invoke(container.replace_item, key, dict(original, n=initial_n))
        expected_n = initial_n + 1
        state_before = await invoke(container.read_item, key, partition_key=key)
        initial_fields = {"id": key, "pk": key, "n": initial_n, "status": "active"}
        assert {key: state_before.get(key) for key in initial_fields} == initial_fields, (
            "Unexpected starting customer fields"
        )
        expected_fields = dict(initial_fields, n=expected_n)
    elif name in ("pre_trigger", "post_trigger"):
        options[name + "_include"] = "auditPre" if name == "pre_trigger" else "auditPost"
    elif no_response:
        options["no_response"] = True
        state_before = await invoke(container.read_item, key, partition_key=key)
        initial_fields = {"id": key, "pk": key, "n": 5, "status": "active"}
        assert {key: state_before.get(key) for key in initial_fields} == initial_fields, (
            "Unexpected starting customer fields"
        )
        assert "missing_field" not in state_before, "Invalid removal would target an existing field"
        if name == "no_response_rejection":
            operations = [{"op": "remove", "path": "/missing_field"}]
            expected_error, expected_n = 400, 5
        expected_fields = dict(initial_fields, n=expected_n)
    elif name == "session_token":
        options["session_token"] = original.get_response_headers()["x-ms-session-token"]
    elif if_match:
        options.update(etag=original["_etag"], match_condition=MatchConditions.IfNotModified)
        changed = name in ("etag_stale", "filter_etag_stale", "filter_false_etag_stale")
        if changed:
            await invoke(container.replace_item, key, dict(original, n=8))
            expected_error, expected_n = 412, 8
        state_before = await invoke(container.read_item, key, partition_key=key)
        assert isinstance(original["_etag"], str) and original["_etag"]
        assert isinstance(state_before["_etag"], str) and state_before["_etag"]
        assert (state_before["_etag"] != original["_etag"]) == changed, "Unexpected starting ETag"
        initial_fields = {"id": key, "pk": key, "n": 8 if changed else 5, "status": "active"}
        assert {key: state_before.get(key) for key in initial_fields} == initial_fields, (
            "Unexpected starting customer fields"
        )
        if combined_filter:
            filter_status = "cancelled" if name in (
                "filter_false_etag_current", "filter_false_etag_stale",
            ) else "active"
            options["filter_predicate"] = f"FROM c WHERE c.status = '{filter_status}'"
            if state_before["status"] != filter_status:
                expected_error, expected_n = 412, initial_fields["n"]
        expected_fields = dict(initial_fields, n=expected_n)
    elif name == "invalid_path":
        operations = [{"op": "incr", "path": "/absent/n", "value": 1}]
        expected_error, expected_n = 400, 5
    elif atomic_patch:
        operations = [
            {"op": "incr", "path": "/n", "value": 1},
            {"op": "set", "path": "/status", "value": "reviewed"},
        ]
        state_before = await invoke(container.read_item, key, partition_key=key)
        initial_fields = {"id": key, "pk": key, "n": 5, "status": "active"}
        assert {key: state_before.get(key) for key in initial_fields} == initial_fields, (
            "Unexpected starting customer fields"
        )
        assert "missing_field" not in state_before, "Invalid final operation would remove an existing field"
        if name == "atomic_patch_rejection":
            operations.append({"op": "remove", "path": "/missing_field"})
            expected_error, expected_n = 400, 5
            expected_fields = initial_fields
        else:
            expected_fields = dict(initial_fields, n=6, status="reviewed")
    elif name == "filter_false":
        options["filter_predicate"] = "FROM c WHERE c.status = 'cancelled'"
        expected_error, expected_n = 412, 5
    elif name == "filter_true":
        options["filter_predicate"] = "FROM c WHERE c.status = 'active'"
    elif name in ("self_only", "self_different_id"):
        target = {"_self": original["_self"]}
        if name == "self_different_id":
            target["id"] = "different-id"
    elif name in ("stale_self", "stale_self_set"):
        await invoke(container.delete_item, key, partition_key=key)
        await invoke(container.create_item, {"id": key, "pk": key, "n": 100, "status": "new"})
        target = original
        if name == "stale_self_set":
            operations = [{"op": "set", "path": "/n", "value": 6}]
        expected_error, expected_n = 404, 100
    elif name == "response_hook":
        state_before = await invoke(container.read_item, key, partition_key=key)
        initial_fields = {"id": key, "pk": key, "n": 5, "status": "active"}
        assert {key: state_before.get(key) for key in initial_fields} == initial_fields, (
            "Unexpected starting customer fields"
        )
        expected_fields = dict(initial_fields, n=6)
        options["response_hook"] = lambda headers, body: hook_calls.append((dict(headers), dict(body)))
    elif if_none_match:
        options.update(etag=original["_etag"], match_condition=MatchConditions.IfModified)
        changed = name == "if_none_match_stale"
        if changed:
            await invoke(container.replace_item, key, dict(original, n=8))
            expected_n = 9
        state_before = await invoke(container.read_item, key, partition_key=key)
        assert isinstance(original["_etag"], str) and original["_etag"]
        assert isinstance(state_before["_etag"], str) and state_before["_etag"]
        assert (state_before["_etag"] != original["_etag"]) == changed, "Unexpected starting ETag"
        expected_fields = {"id": key, "pk": key, "n": expected_n, "status": "active"}
        assert {key: state_before.get(key) for key in expected_fields} == dict(
            expected_fields, n=expected_n - 1,
        ), "Unexpected starting customer fields"
    elif name == "ten_operations":
        operations = [{"op": "set", "path": f"/field{i}", "value": i} for i in range(10)]
        expected_n = 5
        expected_fields = {
            "id": key, "pk": key, "n": 5, "status": "active",
            **{f"field{i}": i for i in range(10)},
        }
    elif name == "eleven_operations":
        operations = [{"op": "set", "path": "/n", "value": n} for n in range(11)]
        expected_error, expected_n = 400, 5
    before = (_binding_operation_count(), _rust_fallback_count())
    target_before = dict(target) if isinstance(target, dict) else target
    result, error = None, None
    try:
        result = await invoke(container.patch_item, target, partition_key=key, patch_operations=operations, **options)
    except Exception as exc:
        error = exc
    delta = (_binding_operation_count() - before[0], _rust_fallback_count() - before[1])
    stored = await invoke(container.read_item, key, partition_key=key)
    observation = dict(CURRENT, operation=name, binding_delta=delta[0], fallback_delta=delta[1],
                       error=type(error).__name__ if error else None,
                       status=getattr(error, "status_code", None),
                       returned_n=result.get("n") if result is not None else None,
                       stored_n=stored["n"], returned_keys=sorted(result) if result is not None else None,
                       stored_keys=sorted(stored), hooks=len(hook_calls),
                       stored_stamp=stored.get("auditStamp"),
                       response_stamp=result.get("auditStamp") if result is not None else None)
    if expected_fields is not None:
        observation.update(
            operation_count=len(operations),
            returned_fields={key: result.get(key) for key in expected_fields} if result is not None else None,
            stored_fields={key: stored.get(key) for key in expected_fields},
        )
    if if_none_match or if_match:
        observation.update(
            saved_etag=original["_etag"], before_etag=state_before["_etag"],
            version_changed=state_before["_etag"] != original["_etag"],
            before_fields={key: state_before[key] for key in expected_fields},
            returned_etag=result.get("_etag") if result is not None else None,
            stored_etag=stored.get("_etag"),
        )
    if combined_filter:
        observation.update(
            filter_predicate=options["filter_predicate"],
            filter_matches=state_before["status"] == filter_status,
        )
    if atomic_patch or numeric_increment or array_patch or no_response or if_match or name == "response_hook":
        observation.update(
            patch_operations=operations,
            before_fields={key: state_before[key] for key in expected_fields},
        )
    if atomic_patch or no_response:
        observation.update(
            missing_field_before="missing_field" in state_before,
            missing_field_after="missing_field" in stored,
        )
    if no_response:
        observation.update(no_response=True, returned_body=dict(result) if result is not None else None)
    if name == "response_hook":
        observation["hook_fields"] = [
            {key: body[key] for key in expected_fields if key in body} for _, body in hook_calls
        ]
    REPORT["patch_calls"].append(observation)
    print(json.dumps(observation), flush=True)
    assert target == target_before
    assert delta[1] == 0
    if CURRENT["backend"] == "rust":
        expected_binding = 0 if if_none_match and isinstance(error, NotImplementedError) else 1
        assert delta[0] == expected_binding
    if (if_none_match or if_match or numeric_increment or array_patch or no_response) and error is not None:
        assert observation["stored_fields"] == observation["before_fields"], (
            "Rejected patch changed stored customer fields"
        )
    if (if_none_match or if_match) and error is not None:
        assert observation["stored_etag"] == observation["before_etag"], "Rejected patch changed stored ETag"
    if expected_error is not None:
        assert isinstance(error, exceptions.CosmosHttpResponseError), f"Expected HTTP {expected_error}, got {type(error).__name__}"
        assert error.status_code == expected_error
    else:
        assert error is None, f"{type(error).__name__}: {error}"
        if name == "no_response":
            assert dict(result) == {}
        else:
            assert result["n"] == expected_n
    assert stored["n"] == expected_n
    if expected_fields is not None:
        if expected_error is None and not no_response:
            assert observation["returned_fields"] == expected_fields
        assert observation["stored_fields"] == expected_fields
    if atomic_patch or no_response:
        assert not observation["missing_field_after"]
    if name == "response_hook":
        assert len(hook_calls) == 1, "Expected exactly one response-hook call"
        assert observation["hook_fields"] == [expected_fields], "Unexpected response-hook customer fields"
    if name == "pre_trigger":
        assert stored.get("auditStamp") == "pre"
    if name == "post_trigger":
        assert result.get("auditStamp") == "post"


async def record(name, function):
    try:
        await invoke(function)
    except Exception as error:
        row = dict(CURRENT, case=name, outcome="FAIL", error=type(error).__name__, detail=str(error))
    else:
        row = dict(CURRENT, case=name, outcome="PASS")
    REPORT["cases"].append(row)
    print(json.dumps(row), flush=True)


async def run_backend(backend, asynchronous, database_id):
    CURRENT.update(backend=backend, surface="async" if asynchronous else "sync")
    cls = AsyncCosmosClient if asynchronous else CosmosClient
    client = cls(os.environ["ACCOUNT_HOST"], os.environ["ACCOUNT_KEY"], _backend=backend)
    try:
        if asynchronous:
            await client.__aenter__()
        database = client.get_database_client(database_id)
        container = database.get_container_client("orders")
        if not asynchronous and not os.environ.get("PATCH_REVIEW_SUPPLEMENTAL"):
            await record("test_patch_item_none_options", lambda: run_none_options(container))
        if NONE_OPTIONS_ONLY:
            return
        case = unittest.TestCase()
        case.databaseForTest = case.database_for_test = database
        case.configs = SimpleNamespace(TEST_MULTI_PARTITION_CONTAINER_ID="orders")
        for method in ([] if os.environ.get("PATCH_REVIEW_SUPPLEMENTAL") else ASYNC if asynchronous else SYNC):
            await record(method.__name__, lambda method=method: method(case))
        names = ("integer_increment_on_fraction", "pre_trigger", "post_trigger") if os.environ.get(
            "PATCH_REVIEW_SUPPLEMENTAL"
        ) else ("no_response", "no_response_rejection", "session_token", "etag_current", "etag_stale",
                     "invalid_path", "atomic_patch_control", "atomic_patch_rejection",
                     "filter_false", "filter_true", "filter_etag_current", "filter_etag_stale",
                     "filter_false_etag_current", "filter_false_etag_stale",
                     "stale_self", "stale_self_set",
                     "self_only", "self_different_id",
                     "response_hook", "if_none_match", "if_none_match_stale",
                     "ten_operations", "eleven_operations",
                     "integer_increment_on_integer", "integer_increment_on_fraction",
                     "array_add", "array_set", "array_add_then_remove", "array_remove_then_add")
        for name in names:
            await record(name, lambda name=name: scenario(container, name))
    finally:
        await invoke(client.close)


async def main():
    for backend in ("core-python", "rust"):
        for asynchronous in ((False,) if NONE_OPTIONS_ONLY else (False, True)):
            with CosmosClient(os.environ["ACCOUNT_HOST"], os.environ["ACCOUNT_KEY"], _backend="core-python") as owner:
                database = owner.create_database("patch_review_" + uuid.uuid4().hex)
                try:
                    container = database.create_container("orders", partition_key=PartitionKey(path="/pk"))
                    if os.environ.get("PATCH_REVIEW_SUPPLEMENTAL"):
                        for name, kind, object_name, stamp in (
                            ("auditPre", "Pre", "getRequest", "pre"),
                            ("auditPost", "Post", "getResponse", "post"),
                        ):
                            container.scripts.create_trigger({
                                "id": name, "triggerType": kind, "triggerOperation": "All",
                                "body": "function audit() { var r = getContext()." + object_name
                                + "(); var b = r.getBody(); b.auditStamp = '" + stamp
                                + "'; r.setBody(b); }",
                            })
                    await run_backend(backend, asynchronous, database.id)
                finally:
                    owner.delete_database(database.id)
                    try:
                        database.read()
                    except exceptions.CosmosResourceNotFoundError as error:
                        assert error.status_code == 404
                        REPORT["cleanup"].append({"database": database.id, "status": 404})
                    else:
                        raise AssertionError("Owned database survived cleanup")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    finally:
        from azure.cosmos import _rust
        REPORT["extension_sha256"] = hashlib.sha256(Path(_rust.__file__).read_bytes()).hexdigest()
        (OUT / "report.json").write_text(json.dumps(REPORT, indent=2) + "\n", encoding="utf-8")
    failures = [row for row in REPORT["cases"] if row["outcome"] == "FAIL"]
    print(f"TOTAL {len(REPORT['cases'])} cases; {len(failures)} failures; {len(REPORT['cleanup'])} verified database deletions")
    raise SystemExit(1 if failures else 0)
