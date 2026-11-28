# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.
"""Source drift guards, not service parity or migration-completion evidence."""

import ast
import importlib.util
import json
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
SPEC = importlib.util.spec_from_file_location(
    "batch_correspondence_builder",
    ROOT / "scripts" / "v5" / "build_batch_assertion_correspondence.py",
)
BUILDER = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(BUILDER)


def test_batch_assertion_ledger_matches_sources_rust():
    expected = json.loads(
        Path(__file__)
        .with_name("assertion_correspondence.json")
        .read_text(encoding="utf-8")
    )
    assert len(expected["source_modules"]) == 27
    assert (
        BUILDER.build() == expected
    ), "Review drift, then regenerate with scripts/v5/build_batch_assertion_correspondence.py"
    for record in expected["records"]:
        for row in record["observations"]:
            if row["disposition"] in {
                "supported-correspondence",
                "partial-correspondence",
            }:
                assert row["replacements"], row["source"]
                assert all(
                    target["kind"] != "function" for target in row["replacements"]
                )
            if row["disposition"] == "partial-correspondence":
                assert row["remaining"], row["source"]


@pytest.mark.parametrize(
    "surface,filename,factory",
    [
        ("sync", "test_transactional_batch.py", "create_data_client"),
        ("aio", "test_transactional_batch_async.py", "create_data_client_async"),
    ],
)
def test_batch_copies_preserve_annotations_and_configured_auth_rust(
    surface, filename, factory
):
    original = ast.parse((ROOT / "tests" / filename).read_text(encoding="utf-8-sig"))
    copied = ast.parse(
        (ROOT / "tests" / "execute_item_batch" / surface / filename).read_text(
            encoding="utf-8-sig"
        )
    )
    original_class = next(
        node for node in original.body if isinstance(node, ast.ClassDef)
    )
    copied_class = next(node for node in copied.body if isinstance(node, ast.ClassDef))
    assert [ast.dump(node) for node in original_class.decorator_list] == [
        ast.dump(node) for node in copied_class.decorator_list
    ]
    for original_body, copied_body in (
        (original.body, copied.body),
        (original_class.body, copied_class.body),
    ):
        marks = [
            [
                ast.dump(node)
                for node in body
                if isinstance(node, (ast.Assign, ast.AnnAssign))
                and any(
                    isinstance(child, ast.Name) and child.id == "pytestmark"
                    for child in ast.walk(node)
                )
            ]
            for body in (original_body, copied_body)
        ]
        assert marks[0] == marks[1]
    copies = {
        node.name.removesuffix("_rust"): node
        for node in copied_class.body
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))
        and node.name.startswith("test_")
    }
    for node in original_class.body:
        if isinstance(
            node, (ast.FunctionDef, ast.AsyncFunctionDef)
        ) and node.name.startswith("test_"):
            assert [ast.dump(decorator) for decorator in node.decorator_list] == [
                ast.dump(decorator) for decorator in copies[node.name].decorator_list
            ]
    data_assignments = [
        node
        for node in ast.walk(copied_class)
        if isinstance(node, ast.Assign)
        and any(
            isinstance(target, ast.Attribute) and target.attr == "client"
            for target in node.targets
        )
    ]
    assert len(data_assignments) == 1
    call = data_assignments[0].value
    assert isinstance(call, ast.Call)
    assert isinstance(call.func, ast.Attribute)
    assert isinstance(call.func.value, ast.Name) and call.func.value.id == "clients"
    assert call.func.attr == factory
    assert not call.args
    assert [keyword.arg for keyword in call.keywords] == ["_backend"]


def test_batch_discovery_keeps_helper_assertions_and_serialization_rust():
    ledger = BUILDER.build()
    symbols = {
        (record["source"]["path"], record["source"]["symbol"])
        for record in ledger["records"]
    }
    assert (r"tests\test_partition_key.py", "_assert_pk") in symbols
    assert (r"tests\test_headers.py", "assert_request_throughput_bucket") in symbols
    assert (
        r"tests\test_availability_strategy.py",
        "_validate_response_uris",
    ) in symbols
    assert any(
        "test_batch_wire_shape_is_what_the_detector_keys_off" in symbol
        for _, symbol in symbols
    )
    assert r"tests\test_config.py::assert_session_token" in ledger["external_helpers"]


@pytest.mark.parametrize(
    "family,target",
    [
        ("encoding", "test_batch_unicode_write_read_delete_rust"),
        (
            "container_properties_cache",
            "test_batch_same_name_container_recreation_rust",
        ),
        ("partition_key", "test_batch_null_and_undefined_partition_keys_rust"),
        ("none_options", "test_batch_none_options_rust"),
        ("backwards_compatibility", "test_batch_ignored_top_level_conditions_rust"),
        ("cosmos_responses", "test_batch_headers_lsn_and_session_progression_rust"),
        ("headers", "test_batch_request_throughput_bucket_rust"),
    ],
)
def test_shared_batch_cases_preserve_source_lanes_rust(family, target):
    source = ast.parse(
        (ROOT / "tests" / ("test_" + family + ".py")).read_text(encoding="utf-8-sig")
    )
    original = next(
        node
        for node in source.body
        if isinstance(node, ast.ClassDef) and node.name.startswith("Test")
    )
    # pylint: disable=protected-access
    context = BUILDER.REF._annotation_context(BUILDER.SHARED, target)
    # pylint: enable=protected-access
    target_nodes = [
        ast.parse(reference["snippet"])
        for reference in context["module_marks"] + context["function_decorators"]
    ]

    def lanes(nodes):
        return {
            child.attr
            for node in nodes
            for child in ast.walk(node)
            if isinstance(child, ast.Attribute)
            and (child.attr.startswith("cosmos") or child.attr == "unittest")
        }

    assert lanes(original.decorator_list) <= lanes(target_nodes)
