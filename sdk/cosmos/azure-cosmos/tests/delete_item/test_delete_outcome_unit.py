# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.
"""Exercise the original and copied delete assertions with controlled outcomes."""

import ast
import copy
import importlib.util
from pathlib import Path
from unittest.mock import MagicMock

import pytest

from azure.cosmos.exceptions import CosmosHttpResponseError


ROOT = Path(__file__).resolve().parents[2]
ORIGINAL = ROOT / "tests" / "test_none_options.py"
COPY = ROOT / "tests" / "delete_item" / "sync" / "legacy" / "test_none_options.py"


def test_delete_method_preserves_original_assertions():
    def statements(path):
        tree = ast.parse(path.read_text(encoding="utf-8"))
        cls = next(node for node in tree.body if isinstance(node, ast.ClassDef) and node.name == "TestNoneOptions")
        method = next(node for node in cls.body if getattr(node, "name", None) == "test_delete_item_none_options")
        body = method.body
        if isinstance(body[0], ast.Expr) and isinstance(body[0].value, ast.Constant) and isinstance(body[0].value.value, str):
            body = body[1:]
        return [ast.dump(node) for node in body]

    assert statements(ORIGINAL) == statements(COPY)


@pytest.mark.parametrize("path", [ORIGINAL, COPY], ids=["original", "rust_copy"])
@pytest.mark.parametrize(
    "scenario",
    ["deleted", "still_present", "post_503", "post_403", "missing_before", "wrong_before"],
)
def test_delete_requires_existing_item_then_not_found(path, scenario):
    spec = importlib.util.spec_from_file_location("delete_outcome_test", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    case = module.TestNoneOptions("test_delete_item_none_options")
    container = MagicMock()
    case.container = container
    state = {}
    events = []

    def create(body, **kwargs):
        state.update(copy.deepcopy(body))
        events.append("create")
        return dict(body)

    def read(item_id, partition_key, **kwargs):
        assert item_id == state["id"]
        assert partition_key == state["pk"]
        after_delete = "delete" in events
        events.append("read_after" if after_delete else "read_before")
        if after_delete:
            if scenario == "still_present":
                return dict(state)
            status = {"post_503": 503, "post_403": 403}.get(scenario, 404)
            raise CosmosHttpResponseError(status_code=status, message="controlled read result")
        if scenario == "missing_before":
            raise CosmosHttpResponseError(status_code=404, message="missing before delete")
        result = dict(state)
        if scenario == "wrong_before":
            result["value"] = 0
        return result

    def delete(item_id, partition_key, **kwargs):
        assert item_id == state["id"]
        assert partition_key == state["pk"]
        events.append("delete")

    container.create_item.side_effect = create
    container.read_item.side_effect = read
    container.delete_item.side_effect = delete
    if scenario == "deleted":
        case.test_delete_item_none_options()
        assert events == ["create", "read_before", "delete", "read_after"]
    else:
        error = CosmosHttpResponseError if scenario == "missing_before" else AssertionError
        with pytest.raises(error):
            case.test_delete_item_none_options()
        if scenario in ("missing_before", "wrong_before"):
            container.delete_item.assert_not_called()
