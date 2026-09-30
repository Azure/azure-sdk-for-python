# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.
"""Compare copied original patch tests and strict probes on owned live resources.

Set ACCOUNT_HOST and ACCOUNT_KEY, and optionally PATCH_REVIEW_OUTPUT to a new
evidence directory. PATCH_REVIEW_SUPPLEMENTAL=1 selects numeric/trigger probes.
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
import uuid

ROOT = Path(__file__).resolve().parents[2]
sys.path[:0] = [str(ROOT), str(ROOT / "tests")]

from azure.core import MatchConditions
from azure.cosmos import CosmosClient, PartitionKey, exceptions
from azure.cosmos.aio import CosmosClient as AsyncCosmosClient
from azure.cosmos.http_constants import StatusCodes
from common._parity_helpers import _binding_operation_count, _rust_fallback_count


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


async def invoke(method, *args, **kwargs):
    value = method(*args, **kwargs)
    return await value if inspect.isawaitable(value) else value


async def scenario(container, name):
    key = uuid.uuid4().hex
    original = await invoke(container.create_item, {"id": key, "pk": key, "n": 5, "status": "active"})
    operations = [{"op": "incr", "path": "/n", "value": 1}]
    options = {}
    target = key
    expected_error = None
    expected_n = 6
    hook_calls = []
    if name == "integer_increment_on_fraction":
        original = await invoke(container.replace_item, key, dict(original, n=5.5))
        expected_n = 6.5
    elif name in ("pre_trigger", "post_trigger"):
        options[name + "_include"] = "auditPre" if name == "pre_trigger" else "auditPost"
    elif name == "no_response":
        options["no_response"] = True
    elif name == "session_token":
        options["session_token"] = original.get_response_headers()["x-ms-session-token"]
    elif name == "etag_current":
        options.update(etag=original["_etag"], match_condition=MatchConditions.IfNotModified)
    elif name == "etag_stale":
        await invoke(container.replace_item, key, dict(original, n=8))
        options.update(etag=original["_etag"], match_condition=MatchConditions.IfNotModified)
        expected_error, expected_n = 412, 8
    elif name == "invalid_path":
        operations = [{"op": "incr", "path": "/absent/n", "value": 1}]
        expected_error, expected_n = 400, 5
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
        options["response_hook"] = lambda headers, body: hook_calls.append((dict(headers), dict(body)))
    elif name == "if_none_match":
        options.update(etag=original["_etag"], match_condition=MatchConditions.IfModified)
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
    REPORT["patch_calls"].append(observation)
    print(json.dumps(observation), flush=True)
    assert target == target_before
    assert delta[1] == 0
    if CURRENT["backend"] == "rust" and name not in ("filter_false", "filter_true", "if_none_match"):
        assert delta[0] == 1
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
    if name == "response_hook":
        assert len(hook_calls) == 1 and hook_calls[0][1]["n"] == 6
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
        case = unittest.TestCase()
        case.databaseForTest = case.database_for_test = database
        case.configs = SimpleNamespace(TEST_MULTI_PARTITION_CONTAINER_ID="orders")
        for method in ([] if os.environ.get("PATCH_REVIEW_SUPPLEMENTAL") else ASYNC if asynchronous else SYNC):
            await record(method.__name__, lambda method=method: method(case))
        names = ("integer_increment_on_fraction", "pre_trigger", "post_trigger") if os.environ.get(
            "PATCH_REVIEW_SUPPLEMENTAL"
        ) else ("no_response", "session_token", "etag_current", "etag_stale",
                     "invalid_path", "filter_false", "filter_true", "stale_self", "stale_self_set",
                     "self_only", "self_different_id",
                     "response_hook", "if_none_match", "eleven_operations")
        for name in names:
            await record(name, lambda name=name: scenario(container, name))
    finally:
        await invoke(client.close)


async def main():
    for backend in ("core-python", "rust"):
        for asynchronous in (False, True):
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
