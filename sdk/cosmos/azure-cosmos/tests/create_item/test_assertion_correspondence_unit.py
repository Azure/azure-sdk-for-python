# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.
"""Offline source-reference guards; these do not execute or prove native parity."""

import ast
from collections import Counter
from functools import lru_cache
import hashlib
import json
import re
from pathlib import Path

import pytest


ROOT = Path(__file__).resolve().parents[2]
LEDGER = Path(__file__).with_name("assertion_correspondence.json")
FUNCTIONS = (ast.FunctionDef, ast.AsyncFunctionDef)
DISPOSITIONS = {
    "supported-correspondence",
    "partial-correspondence",
    "setup-or-other-api",
    "retired-python-detail",
    "accepted-exclusion",
    "documented-api-change-unapproved",
    "driver-gap",
    "unresolved",
}
LEVELS = {
    "none",
    "python-helper-fake",
    "public-boundary-fake-extension",
    "public-installed-native",
    "native-binding",
}


def _fingerprint(node):
    return hashlib.sha256(ast.dump(node, include_attributes=False).encode("utf-8")).hexdigest()


def _functions(tree, prefix=""):
    for node in tree.body:
        if isinstance(node, (*FUNCTIONS, ast.ClassDef)):
            name = prefix + node.name
            if isinstance(node, FUNCTIONS):
                yield name, node
            yield from _functions(node, name + ".")


def _call_name(node):
    return getattr(node.func, "attr", getattr(node.func, "id", ""))


def _observations(function):
    """Include nested callbacks, assertion helpers, failure sentinels and branches."""
    for node in ast.walk(function):
        if isinstance(node, ast.Assert):
            yield "assertion", node
        elif isinstance(node, ast.Call):
            name = _call_name(node)
            if name == "create_item":
                yield "create-call", node
            elif "assert" in name.lower() or name in {"fail", "raises"}:
                yield "assertion-call", node
            elif name in {"_perform_write_operation", "_perform_read_operation", "_validate_response_uris"}:
                yield "helper-call", node
        elif isinstance(node, ast.If):
            yield "if-branch", node.test
        elif isinstance(node, (ast.For, ast.AsyncFor, ast.While)):
            yield "loop-branch", node.test if isinstance(node, ast.While) else node.iter
        elif isinstance(node, ast.ExceptHandler) and node.type is not None:
            yield "exception-branch", node.type


def _reference(path, symbol, kind, node, text):
    return {
        "path": str(path),
        "symbol": symbol,
        "kind": kind,
        "line": node.lineno,
        "end_line": node.end_lineno,
        "column": node.col_offset,
        "ast_sha256": _fingerprint(node),
        "snippet": node.name if kind == "function" else ast.get_source_segment(text, node),
    }


def _key(reference):
    return tuple(reference[field] for field in ("path", "symbol", "kind", "line", "column", "ast_sha256"))


@lru_cache(maxsize=None)
def _read_file(relative):
    path = ROOT.joinpath(*relative.replace("\\", "/").split("/"))
    assert path.is_relative_to(ROOT), relative
    text = path.read_text(encoding="utf-8-sig")
    return text, dict(_functions(ast.parse(text)))


def _read_function(reference):
    text, functions = _read_file(reference["path"])
    assert reference["symbol"] in functions, reference
    return text, functions[reference["symbol"]]


@lru_cache(maxsize=None)
def _function_references(path, symbol):
    text, function = _read_function({"path": path, "symbol": symbol})
    return [
        _reference(path, symbol, kind, node, text)
        for kind, node in [("function", function), *_observations(function)]
    ]


def _validate_reference(reference):
    if reference["kind"] == "function":
        text, function = _read_function(reference)
        assert reference == _reference(reference["path"], reference["symbol"], "function", function, text)
        return
    actual = _function_references(reference["path"], reference["symbol"])
    assert reference in actual, f"Stale source reference: {reference}"


def _load():
    return json.loads(LEDGER.read_text(encoding="utf-8"))


def _annotation_context(path, symbol):
    text, names = _read_file(path)
    tree = ast.parse(text)
    function = names[symbol]

    def refs(nodes, owner, kind):
        return [_reference(path, owner, kind, node, text) for node in nodes]

    def mark_statements(body):
        return [
            node for node in body if not isinstance(node, (*FUNCTIONS, ast.ClassDef, ast.Import, ast.ImportFrom))
            and any(isinstance(child, ast.Name) and child.id == "pytestmark" for child in ast.walk(node))
        ]

    module_marks = mark_statements(tree.body)
    decorators = list(function.decorator_list)
    classes = []
    class_values = {}
    current = tree
    prefix = []
    for part in symbol.split(".")[:-1]:
        current = next(node for node in current.body if getattr(node, "name", None) == part)
        prefix.append(part)
        if isinstance(current, ast.ClassDef):
            owner = ".".join(prefix)
            decorators.extend(current.decorator_list)
            for value in current.body:
                if isinstance(value, (ast.Assign, ast.AnnAssign)):
                    for target in value.targets if isinstance(value, ast.Assign) else [value.target]:
                        if isinstance(target, ast.Name):
                            class_values[target.id] = value
            lifecycle = [
                node for node in current.body if isinstance(node, FUNCTIONS)
                and node.name in {
                    "setUp", "setUpClass", "asyncSetUp", "setup_class", "setup_method",
                    "tearDown", "tearDownClass", "asyncTearDown", "teardown_class", "teardown_method",
                }
            ]
            classes.append({
                "symbol": owner,
                "bases": [ast.unparse(base) for base in current.bases],
                "decorators": refs(current.decorator_list, owner, "class-decorator"),
                "marks": refs(mark_statements(current.body), owner, "class-pytestmark"),
                "lifecycle": [
                    _reference(path, owner + "." + node.name, "function", node, text) for node in lifecycle
                ],
            })
    local_values = {}
    imports = {}
    for node in tree.body:
        if isinstance(node, (ast.Assign, ast.AnnAssign)):
            for target in node.targets if isinstance(node, ast.Assign) else [node.target]:
                if isinstance(target, ast.Name):
                    local_values[target.id] = node
        elif isinstance(node, ast.ImportFrom):
            for alias in node.names:
                imports[alias.asname or alias.name] = node
        elif isinstance(node, ast.Import):
            for alias in node.names:
                imports[alias.asname or alias.name] = node
    local_values.update(class_values)
    fixture_nodes = {
        name: node for name, node in names.items()
        if any(isinstance(decorator, ast.Call) and _call_name(decorator) == "fixture"
               or isinstance(decorator, ast.Attribute) and decorator.attr == "fixture"
               for decorator in node.decorator_list)
    }
    dependencies = {}
    pending = list(decorators) + module_marks
    pending.extend(decorator for node in fixture_nodes.values() for decorator in node.decorator_list)
    for cls in classes:
        for mark in cls["marks"]:
            pending.append(ast.parse(mark["snippet"]))
    seen = set()
    while pending:
        for node in ast.walk(pending.pop()):
            if not isinstance(node, ast.Name) or node.id in seen:
                continue
            seen.add(node.id)
            if node.id in local_values:
                value = local_values[node.id]
                dependencies[node.id] = _reference(path, node.id, "annotation-value", value, text)
                pending.append(value)
            elif node.id in imports and node.id != "pytest":
                dependencies[node.id] = _reference(path, node.id, "annotation-import", imports[node.id], text)
    fixtures = []
    for name, node in fixture_nodes.items():
        fixtures.append({
            "source": _reference(path, name, "function", node, text),
            "decorators": refs(node.decorator_list, name, "fixture-decorator"),
        })
    conftests = []
    directory = ROOT.joinpath(*path.split("\\")).parent
    while directory.is_relative_to(ROOT / "tests"):
        conftest = directory / "conftest.py"
        if conftest.exists():
            conftests.append({
                "path": str(conftest.relative_to(ROOT)),
                "ast_sha256": _fingerprint(ast.parse(conftest.read_text(encoding="utf-8-sig"))),
            })
        directory = directory.parent
    return {
        "path": path,
        "symbol": symbol,
        "module_marks": refs(module_marks, "<module>", "module-pytestmark"),
        "classes": classes,
        "function_decorators": refs(function.decorator_list, symbol, "function-decorator"),
        "arguments": ast.unparse(function.args),
        "annotation_dependencies": dependencies,
        "local_fixtures": fixtures,
        "conftests": conftests,
    }


def _create_copy_inventory():
    inventory = []
    for path in sorted((ROOT / "tests" / "create_item").rglob("test_*.py")):
        if path.name in {"test_service_failures.py", Path(__file__).name}:
            continue
        relative = str(path.relative_to(ROOT))
        text, names = _read_file(relative)
        for symbol, function in names.items():
            if not function.name.startswith("test_"):
                continue
            match = re.search(
                r"# Source:\s*([^\r\n:]+)::([^\s\r\n]+)", ast.get_source_segment(text, function)
            )
            source = None
            if match:
                source_path, source_symbol = match.groups()
                source_path = source_path.replace("/", "\\")
                source_text, source_functions = _read_file(source_path)
                source = _reference(source_path, source_symbol, "function", source_functions[source_symbol], source_text)
            inventory.append({
                "replacement": _reference(relative, symbol, "function", function, text),
                "source": source,
                "classification": (
                    "original-lineage-copy" if source else
                    "offline-helper-or-guard" if path.name.endswith("_unit.py") else
                    "paired-comparison-without-original-lineage"
                ),
            })
    return inventory


def _category_marks(context):
    refs = context["module_marks"] + context["function_decorators"]
    refs += [mark for cls in context["classes"] for mark in cls["decorators"] + cls["marks"]]
    return {
        node.attr for ref in refs for node in ast.walk(ast.parse(ref["snippet"]))
        if isinstance(node, ast.Attribute) and node.attr.startswith("cosmos")
        and isinstance(node.value, ast.Attribute) and node.value.attr == "mark"
        and isinstance(node.value.value, ast.Name) and node.value.value.id == "pytest"
    }


def _literal_vector(node, names=None):
    names = names or {}
    if isinstance(node, ast.Name):
        return names[node.id]
    if isinstance(node, ast.Constant):
        return node.value
    if isinstance(node, (ast.List, ast.Tuple)):
        return [_literal_vector(value, names) for value in node.elts]
    if isinstance(node, ast.Dict):
        return {_literal_vector(key, names): _literal_vector(value, names) for key, value in zip(node.keys, node.values)}
    if isinstance(node, ast.BinOp):
        left, right = _literal_vector(node.left, names), _literal_vector(node.right, names)
        if isinstance(node.op, ast.Add):
            return left + right
        if isinstance(node.op, ast.Mult):
            return left * right
    if isinstance(node, ast.Call) and _call_name(node) == "param":
        values = [_literal_vector(value, names) for value in node.args]
        return values[0] if len(values) == 1 else values
    raise AssertionError(f"Unreviewed parameter expression: {ast.dump(node)}")


def _assigned_value(path, name, symbol=None):
    text, functions = _read_file(path)
    node = functions[symbol] if symbol else ast.parse(text)
    return next(
        statement.value for statement in ast.walk(node) if isinstance(statement, ast.Assign)
        and any(isinstance(target, ast.Name) and target.id == name for target in statement.targets)
    )


def test_assertion_ledger_references_and_complete_reviewed_scope_rust():
    ledger = _load()
    assert ledger["schema_version"] == 1
    assert ledger["verification"]["kind"] == "static-correspondence-with-separately-recorded-targeted-execution"
    policies = {policy["id"]: policy for policy in ledger["policy_references"]}
    for policy in policies.values():
        text = ROOT.joinpath(*policy["path"].split("\\")).read_text(encoding="utf-8-sig")
        assert policy["excerpt"] in text
        if "approval_excerpt" in policy:
            assert policy["approval_excerpt"] in text
    expected = []
    for scope in ledger["reviewed_functions"]:
        _validate_reference(scope["source"])
        text, function = _read_function(scope["source"])
        expected.extend(
            _key(_reference(scope["source"]["path"], scope["source"]["symbol"], kind, node, text))
            for kind, node in _observations(function)
        )
    actual = [_key(row["source"]) for row in ledger["correspondences"]]
    assert Counter(expected) == Counter(actual), "Added, removed, duplicated or unmapped source observation"
    assert len({row["id"] for row in ledger["correspondences"]}) == len(actual)
    for row in ledger["correspondences"]:
        _validate_reference(row["source"])
        assert row["disposition"] in DISPOSITIONS
        assert row["rationale"].strip()
        assert row["execution_level"] in LEVELS
        assert row["verification"] == "no-per-row-execution-attribution"
        if row["disposition"] == "supported-correspondence":
            assert row["replacements"], row["id"]
        if row["disposition"] == "documented-api-change-unapproved":
            assert row["approval"] == "not-recorded"
        if row["disposition"] in {"accepted-exclusion", "documented-api-change-unapproved"}:
            assert row["policy_ids"], row["id"]
        for policy_id in row["policy_ids"]:
            assert policies[policy_id]["status"] == row["disposition"]
        for replacement in row["replacements"]:
            _validate_reference(replacement)
            assert replacement["kind"] in {"assertion", "assertion-call"}
        for helper in row["helper_sources"]:
            _validate_reference(helper)
        for context in row["replacement_context"]:
            _validate_reference(context)


def test_assertion_ledger_discovery_inventory_is_not_claimed_as_coverage_rust():
    ledger = _load()
    reviewed = {
        (scope["source"]["path"], scope["source"]["symbol"])
        for scope in ledger["reviewed_functions"]
    }
    inventory = set()
    for candidate in ledger["candidate_inventory"]:
        ref = candidate["source"]
        pair = (ref["path"], ref["symbol"])
        assert pair not in inventory
        inventory.add(pair)
        _validate_reference(ref)
        assert candidate["review"] == ("reviewed" if pair in reviewed else "unresolved-not-reviewed")
    assert ledger["summary"]["candidate_functions"] == len(inventory)
    assert ledger["summary"]["reviewed_functions"] == len(reviewed)
    assert ledger["summary"]["observations"] == len(ledger["correspondences"])
    assert ledger["summary"]["dispositions"] == dict(Counter(
        row["disposition"] for row in ledger["correspondences"]
    ))
    # Include callable references and the shared dispatcher, not only direct calls.
    for relative in ledger["source_files"]:
        text = ROOT.joinpath(*relative.split("\\")).read_text(encoding="utf-8-sig")
        for symbol, function in _functions(ast.parse(text)):
            if not function.name.startswith("test_"):
                continue
            create_relevant = any(
                isinstance(node, ast.Attribute) and node.attr == "create_item"
                or isinstance(node, ast.Call) and _call_name(node) == "_perform_write_operation"
                for node in ast.walk(function)
            )
            if create_relevant:
                assert (relative, symbol) in inventory, f"Untriaged create test: {relative}::{symbol}"


@pytest.mark.parametrize("change", ["assertion", "branch", "create", "helper"])
def test_assertion_inventory_detects_new_observations_rust(change):
    original = ast.parse("def scenario():\n    assert True\n").body[0]
    additions = {
        "assertion": "    assert item['id'] == 'new'\n",
        "branch": "    if fault:\n        pass\n",
        "create": "    container.create_item(body)\n",
        "helper": "    assert_persisted(item)\n",
    }
    changed = ast.parse("def scenario():\n    assert True\n" + additions[change]).body[0]
    assert _fingerprint(original) != _fingerprint(changed)
    assert len(list(_observations(changed))) > len(list(_observations(original)))


def test_assertion_reference_guard_rejects_stale_snippets_rust():
    reference = dict(_load()["correspondences"][0]["source"])
    reference["snippet"] += " # stale"
    with pytest.raises(AssertionError, match="Stale source reference"):
        _validate_reference(reference)


def test_assertion_ledger_rejects_missing_disposition_rust(monkeypatch):
    ledger = _load()
    ledger["correspondences"].pop()
    monkeypatch.setitem(globals(), "_load", lambda: ledger)
    with pytest.raises(AssertionError, match="unmapped source observation"):
        test_assertion_ledger_references_and_complete_reviewed_scope_rust()


def test_annotation_contexts_and_review_scope_rust():
    ledger = _load()
    audit = ledger["annotation_audit"]
    assert audit["all_applicable_annotations_preserved"] is False
    expected = {(entry["source"]["path"], entry["source"]["symbol"]) for entry in ledger["reviewed_functions"]}
    expected.update(
        (context["path"], context["symbol"])
        for row in ledger["correspondences"] for context in row["replacement_context"]
    )
    expected.update((ref["path"], ref["symbol"]) for ref in audit["infrastructure_functions"])
    actual = {(context["path"], context["symbol"]) for context in audit["contexts"]}
    assert expected == actual, "Unreviewed source/replacement annotation context"
    for context in audit["contexts"]:
        assert context == _annotation_context(context["path"], context["symbol"]), (
            f"Stale inherited mark, fixture, parameter vector or gate: {context['path']}::{context['symbol']}"
        )
    for ref in audit["infrastructure_functions"]:
        _validate_reference(ref)
    for value in audit["infrastructure_values"]:
        text = ROOT.joinpath(*value["path"].split("\\")).read_text(encoding="utf-8-sig")
        statements = [
            node for node in ast.parse(text).body if isinstance(node, ast.Assign)
            and any(isinstance(target, ast.Name) and target.id == value["symbol"] for target in node.targets)
        ]
        assert len(statements) == 1
        assert value == _reference(value["path"], value["symbol"], "annotation-value", statements[0], text)
    for file in audit["configuration_files"]:
        assert hashlib.sha256(ROOT.joinpath(*file["path"].split("\\")).read_bytes()).hexdigest() == file["sha256"]
    reviewed = {(item["source"]["path"], item["source"]["symbol"]) for item in audit["reviews"]}
    assert reviewed == {
        (entry["source"]["path"], entry["source"]["symbol"])
        for entry in ledger["reviewed_functions"] if entry["source"]["symbol"].split(".")[-1].startswith("test_")
    }


def test_annotation_guard_detects_inherited_marker_and_vector_changes_rust(monkeypatch):
    original = """
import pytest
VALUES = [1, 2]
FIXTURE_VALUES = [3, 4]
pytestmark = pytest.mark.cosmosEmulator
@pytest.fixture(params=FIXTURE_VALUES)
def fixture_value(request):
    return request.param
@pytest.mark.cosmosAADLong
class TestExample:
    _skip_gate: object = pytest.mark.skipif(False, reason="gate")
    @_skip_gate
    @pytest.mark.parametrize("value", VALUES)
    def test_example_rust(self, value):
        pass
"""
    def provide(text):
        return text, dict(_functions(ast.parse(text)))

    monkeypatch.setitem(globals(), "_read_file", lambda _: provide(original))
    expected = _annotation_context("tests\\annotation_fixture.py", "TestExample.test_example_rust")
    for changed in (
        original.replace("pytestmark = pytest.mark.cosmosEmulator", "pytestmark = pytest.mark.skip"),
        original.replace("@pytest.mark.cosmosAADLong", "@pytest.mark.cosmosLong"),
        original.replace("VALUES = [1, 2]", "VALUES = [1]"),
        original.replace("FIXTURE_VALUES = [3, 4]", "FIXTURE_VALUES = [3]"),
        original.replace('skipif(False, reason="gate")', 'skipif(True, reason="gate")'),
        original.replace("class TestExample:", "class TestExample:\n    pytestmark = pytest.mark.skip"),
        original.replace("pytestmark = pytest.mark.cosmosEmulator",
                         "pytestmark: object = pytest.mark.cosmosEmulator\npytestmark = pytest.mark.skip"),
    ):
        monkeypatch.setitem(globals(), "_read_file", lambda _, text=changed: provide(text))
        assert expected != _annotation_context("tests\\annotation_fixture.py", "TestExample.test_example_rust")


def test_actual_create_copy_annotation_inventory_rust():
    audit = _load()["create_copy_annotation_audit"]
    assert audit["inventory"] == _create_copy_inventory()
    assert all(item["replacement"]["symbol"].split(".")[-1].endswith("_rust") for item in audit["inventory"])
    assert len(audit["lineage_reviews"]) == audit["summary"]["source_replacement_pairs"]
    assert audit["all_applicable_annotations_preserved"]
    assert audit["applicable_marker_mismatch_count"] == 0
    expected_categories = {}
    for review in audit["lineage_reviews"]:
        _validate_reference(review["source"])
        _validate_reference(review["replacement"])
        target = review["replacement"]
        if not target["path"].endswith("_unit.py"):
            source = review["source"]
            original = _category_marks(_annotation_context(source["path"], source["symbol"]))
            replacement = _category_marks(_annotation_context(target["path"], target["symbol"]))
            assert original <= replacement, (source, target, original - replacement)
            expected_categories.setdefault((target["path"], target["symbol"]), set()).update(original)
    restored_categories = {"cosmosAADLong", "cosmosAADCircuitBreaker", "cosmosCircuitBreaker"}
    for (path, symbol), original in expected_categories.items():
        actual = _category_marks(_annotation_context(path, symbol))
        assert actual & restored_categories == original & restored_categories, (path, symbol)
    for context in audit["contexts"]:
        assert context == _annotation_context(context["path"], context["symbol"])
    for ref in audit["infrastructure_functions"]:
        _validate_reference(ref)
    for value in audit["vector_sources"]:
        text, _ = _read_file(value["path"])
        node = next(
            statement for statement in ast.parse(text).body if isinstance(statement, ast.Assign)
            and any(isinstance(target, ast.Name) and target.id == value["symbol"] for target in statement.targets)
        )
        assert value == _reference(value["path"], value["symbol"], "annotation-value", node, text)
    for file in audit["vector_files"]:
        assert hashlib.sha256(ROOT.joinpath(*file["path"].split("\\")).read_bytes()).hexdigest() == file["sha256"]


@pytest.mark.parametrize("check", [
    "test_migrated_folders_discovered_rust",
    "test_every_migrated_folder_is_a_package_rust",
    "test_every_test_method_has_a_source_comment_rust",
    "test_every_source_reference_resolves_rust",
    "test_every_migrated_file_pins_rust_backend_rust",
    "test_no_unstructured_skips_rust",
])
def test_create_copies_pass_existing_enforcer_rust(monkeypatch, check):
    from common import test_migration_enforcer_unit as enforcer

    paths = sorted({
        ROOT.joinpath(*item["replacement"]["path"].split("\\"))
        for item in _load()["create_copy_annotation_audit"]["inventory"] if item["source"]
        and Path(item["replacement"]["path"]).name in {
            "test_headers.py", "test_contracts.py", "test_input_variants.py",
        }
    })
    monkeypatch.setattr(enforcer, "_legacy_test_files", lambda: paths)
    getattr(enforcer.LegacyMigrationEnforcerTests(check), check)()


@pytest.mark.parametrize("mode", ["key", "aad"])
@pytest.mark.parametrize("surface", ["sync", "aio"])
@pytest.mark.parametrize("entrypoint", ["contract_fixture", "partition_keys", "unicode", "large_cjk", "header_fixture"])
def test_create_copies_use_configured_data_auth_rust(monkeypatch, mode, surface, entrypoint):
    """Exercise existing factory selection and copy wiring with fake SDK clients."""
    import asyncio
    import importlib
    from types import SimpleNamespace
    import unittest
    from unittest.mock import AsyncMock, MagicMock, Mock

    from config import clients

    asynchronous = surface == "aio"
    monkeypatch.setattr(clients.TestSettings, "host", "https://configured-auth.invalid")
    monkeypatch.setattr(clients.TestSettings, "masterKey", "offline-account-key")
    monkeypatch.setattr(clients.TestSettings, "is_emulator", False)
    monkeypatch.setattr(clients.TestSettings, "data_auth_mode", mode)
    token = object()
    credential = Mock(return_value=token)
    monkeypatch.setattr(clients, "_aad_credential", credential)
    data_client = MagicMock()
    data_client.__enter__.return_value = data_client
    data_client.__aenter__.return_value = data_client
    data_client.close = AsyncMock() if asynchronous else Mock()
    constructor = Mock(return_value=data_client)
    monkeypatch.setattr(clients, "AsyncCosmosClient" if asynchronous else "CosmosClient", constructor)
    container = data_client.get_database_client.return_value.get_container_client.return_value
    stored = {}

    def create(body, **_kwargs):
        stored.clear()
        stored.update(body)
        return dict(body)

    mock_type = AsyncMock if asynchronous else Mock
    container.create_item = mock_type(side_effect=create)
    container.read_item = mock_type(side_effect=lambda *_args, **_kwargs: dict(stored))
    module_name = "test_headers" if entrypoint == "header_fixture" else (
        "test_input_variants" if entrypoint in {"partition_keys", "unicode"} else "test_contracts"
    )
    module = importlib.import_module(f"create_item.{surface}.{module_name}")
    if entrypoint == "header_fixture":
        key_client = MagicMock()
        key_client.close = mock_type()
        key_client.delete_database = mock_type()
        key_client.__aenter__.return_value = key_client
        key_database = MagicMock()
        key_database.create_container = mock_type()
        key_client.create_database = mock_type(return_value=key_database)
        key_constructor = Mock(return_value=key_client)
        monkeypatch.setattr(module, "CosmosClient", key_constructor)
        cls = module.TestHeadersAsync if asynchronous else module.TestHeaders
        method = "test_container_create_item_throughput_bucket" + ("_async" if asynchronous else "") + "_rust"

        def verify(case):
            assert case.client is data_client
            assert case.container is container

        async def verify_async(case):
            verify(case)

        monkeypatch.setattr(cls, method, verify_async if asynchronous else verify)
        result = unittest.TestResult()
        unittest.TestSuite([cls(method)]).run(result)
        assert result.testsRun == 1
        assert result.errors == result.failures == []
        key_constructor.assert_called_once_with(module.HOST, module.KEY, _backend="rust")
        key_client.delete_database.assert_called_once()
        key_client.close.assert_called_once()
        data_client.close.assert_called_once()
    elif entrypoint == "contract_fixture":
        fixture = module._contract_client_fixture.__wrapped__("rust", SimpleNamespace(param={}))
        if asynchronous:
            async def consume():
                assert await anext(fixture) is data_client
                await fixture.aclose()
            asyncio.run(consume())
        else:
            assert next(fixture) is data_client
            fixture.close()
    else:
        monkeypatch.setattr(module, "observe_native_create", Mock(return_value=None))
        monkeypatch.setattr(module, "assert_created", Mock())
        monkeypatch.setattr(module, "assert_fields", Mock())
        args = {
            "variant_database": SimpleNamespace(id="offline-db"),
            "make_variant_container": Mock(return_value=SimpleNamespace(id="offline-container")),
            "monkeypatch": monkeypatch,
            "backend": "rust",
        }
        if entrypoint == "partition_keys":
            function = module.test_partitioned_collection_partition_key_extraction_special_chars_rust
            args.update(case=module.CASES[0], client_suppressed=False, options={}, suppressed=False)
        elif entrypoint == "unicode":
            function = module.test_unicode_characters_in_partition_key_rust
            args["body"] = {"id": "offline", "pk": "\u00e9"}
        else:
            function = module.test_compact_utf8_large_cjk_item_stays_under_wire_limit_rust
        if asynchronous:
            asyncio.run(function(**args))
        else:
            function(**args)
        container.create_item.assert_called_once()
    constructor.assert_called_once()
    assert constructor.call_args.args == (
        clients.TestSettings.host, token if mode == "aad" else clients.TestSettings.masterKey
    )
    assert constructor.call_args.kwargs["_backend"] == "rust"
    if mode == "aad":
        credential.assert_called_once_with(asynchronous)
    else:
        credential.assert_not_called()


@pytest.mark.parametrize("asynchronous", [False, True])
def test_configured_aad_failure_does_not_fall_back_to_key_rust(monkeypatch, asynchronous):
    from unittest.mock import Mock

    from config import clients

    monkeypatch.setattr(clients.TestSettings, "data_auth_mode", "aad")
    monkeypatch.setattr(clients.TestSettings, "is_emulator", False)
    monkeypatch.setattr(clients, "_aad_credential", Mock(side_effect=RuntimeError("AAD prerequisite unavailable")))
    constructor = Mock()
    monkeypatch.setattr(clients, "AsyncCosmosClient" if asynchronous else "CosmosClient", constructor)
    factory = clients.create_data_client_async if asynchronous else clients.create_data_client
    with pytest.raises(RuntimeError, match="AAD prerequisite unavailable"):
        factory(_backend="rust")
    constructor.assert_not_called()


def test_create_copy_exclusion_and_invalid_id_vectors_rust():
    original = "tests\\test_excluded_locations.py"
    symbols = {"L0": "default", "L1": "write", "L2": "read", "L3": "third"}
    inputs = _literal_vector(_assigned_value(original, "CLIENT_ONLY_TEST_DATA"), symbols)
    inputs += _literal_vector(_assigned_value(original, "CLIENT_AND_REQUEST_TEST_DATA"), symbols)
    outputs = _literal_vector(_assigned_value(original, "client_only_output_data", "write_item_test_data"), symbols)
    outputs += _literal_vector(_assigned_value(original, "client_and_request_output_data", "write_item_test_data"), symbols)
    expected = [[value[1], value[2], output[0]] for value, output in zip(inputs, outputs)]
    replacement = _literal_vector(
        _assigned_value("tests\\create_item\\_routing.py", "CREATE_ITEM_TEST_DATA"),
        {"DEFAULT_LOCATION": "default", "WRITE_LOCATION": "write", "READ_LOCATION": "read", "THIRD_LOCATION": "third"},
    )
    assert len(expected) == len(replacement) == 12
    assert expected == replacement
    assert all(value[0] == ["write", "read"] for value in inputs)
    expected_ids = set()
    for path, symbol in (
        ("tests\\test_resource_id.py", "TestResourceIds.test_create_illegal_characters"),
        ("tests\\test_resource_id_async.py", "TestResourceIdsAsync.test_create_illegal_characters_async"),
    ):
        expected_ids.update(_literal_vector(_assigned_value(path, "illegal_strings", symbol)))
    actual_ids = _literal_vector(_assigned_value("tests\\create_item\\_contract_cases.py", "INVALID_IDS"))
    assert len(actual_ids) == len(set(actual_ids)) == 11
    assert set(actual_ids) == expected_ids


def test_repaired_create_live_lane_marks_rust():
    def effective(path, symbol):
        context = _annotation_context(path, symbol)
        refs = context["module_marks"] + context["function_decorators"]
        refs += [mark for cls in context["classes"] for mark in cls["decorators"] + cls["marks"]]
        return " ".join(ref["snippet"] for ref in refs)

    for surface in ("sync", "aio"):
        suffix = "_async" if surface == "aio" else ""
        cls = "TestQueryResponseHeadersAsync" if suffix else "TestQueryResponseHeaders"
        path = f"tests\\response_hook\\{surface}\\test_query_response_headers{suffix}.py"
        marks = effective(path, f"{cls}.test_response_hook_parity_point_ops{suffix}_rust")
        for marker in ("cosmosEmulator", "cosmosQuery", "cosmosAADQuery"):
            assert f"pytest.mark.{marker}" in marks
        for name in (
            "create_illegal_characters", "round_trip_emoji_document_through_full_sdk_stack",
            "round_trip_emoji_document_via_query", "compact_utf8_create",
            "compact_utf8_large_cjk_item_stays_under_wire_limit", "default_ascii_escaping_rejects_large_cjk_item",
            "document_crud_create_persistence", "document_crud_response_payload_on_write_disabled",
        ):
            assert "pytest.mark.cosmosLong" in effective(
                f"tests\\create_item\\{surface}\\test_contracts.py", f"test_{name}_rust"
            )
        for name in (
            "partitioned_collection_partition_key_extraction_special_chars",
            "partitioned_collection_partition_key_extraction",
            "partitioned_collection_partition_key_value_types",
            "partitioned_collection_partition_key_value_types_response_payload_on_write_disabled",
            "partitioned_collection_partition_key_extraction_special_chars_subpartition",
            "partitioned_collection_partition_key_extraction_subpartition",
            "partitioned_collection_document_crud_and_query_subpartition",
            "create_document_with_line_separator_para_seperator_next_line_unicodes",
            "unicode_characters_in_partition_key",
        ):
            assert "pytest.mark.cosmosLong" in effective(
                f"tests\\create_item\\{surface}\\test_input_variants.py", f"test_{name}_rust"
            )


def test_create_copy_unicode_scalar_and_suppression_vectors_rust():
    helper = "tests\\create_item\\_input_variants.py"
    unicode_key = _literal_vector(_assigned_value(helper, "UNICODE_KEY"))
    unicode_content = _literal_vector(_assigned_value(helper, "UNICODE_CONTENT"))
    emoji = _literal_vector(_assigned_value("tests\\create_item\\_contract_cases.py", "EMOJI_CASES"))
    cases = json.loads(LEDGER.with_name("partition_key_reference_cases.json").read_text(encoding="utf-8"))
    assert len(cases) == 15
    scalar_names = {"hash-null", "hash-missing", "hash-boolean", "hash-string", "hash-integer", "hash-float"}
    scalar_bodies = [{key: value for key, value in case["body"].items() if key != "id"}
                     for case in cases if case["name"] in scalar_names]
    assert len(scalar_bodies) == 6
    assert _literal_vector(_assigned_value(helper, "RESPONSE_MODES")) == [
        [False, {}, False], [True, {}, True],
        [False, {"no_response": True}, True], [True, {"no_response": False}, False],
    ]
    for suffix in ("", "_async"):
        path = f"tests\\test_encoding{suffix}.py"
        _, functions = _read_file(path)

        def assigned(leaf, name):
            symbol = next(symbol for symbol, node in functions.items() if node.name == leaf + suffix)
            return _literal_vector(_assigned_value(path, name, symbol))

        assert unicode_key == assigned("test_unicode_characters_in_partition_key", "test_string")
        assert unicode_content == assigned(
            "test_create_document_with_line_separator_para_seperator_next_line_unicodes", "test_string"
        )
        assert emoji == [
            [False, assigned("test_round_trip_emoji_document_through_full_sdk_stack", "emoji_payload")],
            [True, assigned("test_round_trip_emoji_document_via_query", "emoji_payload")],
        ]
        for module in ("test_crud", "test_crud_response_payload_on_write_disabled"):
            _, originals = _read_file(f"tests\\{module}{suffix}.py")
            original = next(node for node in originals.values()
                            if node.name == "test_partitioned_collection_partition_key_value_types" + suffix)
            bodies = []
            for statement in ast.walk(original):
                if not isinstance(statement, ast.Assign) or not isinstance(statement.value, ast.Dict):
                    continue
                if not any(isinstance(target, ast.Name) and target.id == "document_definition"
                           for target in statement.targets):
                    continue
                fields = dict(zip((_literal_vector(key) for key in statement.value.keys), statement.value.values))
                if "id" in fields:
                    bodies.append({key: _literal_vector(value) for key, value in fields.items() if key != "id"})
            assert bodies == scalar_bodies
