# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.
"""Execute file-based batch examples without service calls or sample configuration."""

import ast
import asyncio
from itertools import takewhile
import json
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import AsyncMock, Mock

import pytest


SAMPLES = Path(__file__).resolve().parents[2] / "samples"


def _file_batch_example(filename, asynchronous):
    source = (SAMPLES / filename).read_text(encoding="utf-8")
    if filename.startswith("transactional_batch"):
        lines = source.splitlines()
        start = lines.index("    # import json")
        snippet = "\n".join(line[6:] for line in takewhile(lambda line: line.startswith("    # "), lines[start:]))
        statements = ast.parse(snippet).body
    else:
        tree = ast.parse(source)
        json_import = next(
            node
            for node in tree.body
            if isinstance(node, ast.Import) and any(alias.name == "json" for alias in node.names)
        )
        function = next(
            node
            for node in tree.body
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))
            and node.name == "execute_item_batch"
        )
        statements = [json_import, next(node for node in function.body if isinstance(node, ast.With))]
    tree = ast.parse(("async " if asynchronous else "") + "def example(container):\n    pass\n")
    tree.body[0].body = statements
    namespace = {}
    exec(compile(ast.fix_missing_locations(tree), filename, "exec"), namespace)  # pylint: disable=exec-used
    return namespace["example"]


@pytest.mark.parametrize("sample", ["document_management", "transactional_batch"])
@pytest.mark.parametrize("asynchronous", [False, True], ids=["sync", "async"])
@pytest.mark.parametrize("malformed", [False, True], ids=["valid-json", "invalid-json"])
def test_file_batch_example_decodes_documents_and_supplies_partition_key_rust(
    sample, asynchronous, malformed, tmp_path, monkeypatch
):
    documents = [
        {"id": "order-1", "account_number": "Account1", "description": "caf\u00e9", "quantity": 2},
        {"id": "order-2", "account_number": "Account1", "details": {"paid": True}},
    ]
    content = "\n".join(json.dumps(document, ensure_ascii=False) for document in documents) + "\n"
    if malformed:
        content += "invalid-json\n"
    (tmp_path / "file_name.txt").write_text(content, encoding="utf-8")
    monkeypatch.chdir(tmp_path)
    batch = AsyncMock() if asynchronous else Mock()
    container = SimpleNamespace(execute_item_batch=batch)
    filename = sample + ("_async" if asynchronous else "") + ".py"
    example = _file_batch_example(filename, asynchronous)

    def run():
        result = example(container)
        if asynchronous:
            asyncio.run(result)

    if malformed:
        with pytest.raises(json.JSONDecodeError):
            run()
        batch.assert_not_called()
    else:
        run()
        operations = [("upsert", (document,)) for document in documents]
        if asynchronous:
            batch.assert_awaited_once_with(operations, partition_key="Account1")
        else:
            batch.assert_called_once_with(operations, partition_key="Account1")
