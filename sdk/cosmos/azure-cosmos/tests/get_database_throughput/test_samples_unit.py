# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.
"""Exercise throughput sample functions without service requests or config imports."""

import ast
import asyncio
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import AsyncMock, MagicMock

import pytest

from azure.cosmos import exceptions


SAMPLES = Path(__file__).resolve().parents[2] / "samples"


def _function(filename, name, namespace):
    tree = ast.parse((SAMPLES / filename).read_text(encoding="utf-8"))
    function = next(node for node in tree.body if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) and node.name == name)
    exec(compile(ast.Module(body=[function], type_ignores=[]), filename, "exec"), namespace)
    return namespace[name]


@pytest.mark.parametrize("asynchronous", [False, True])
@pytest.mark.parametrize("autoscale", [False, True])
def test_read_sample_uses_public_properties_rust(asynchronous, autoscale, capsys):
    offer = SimpleNamespace(
        auto_scale_max_throughput=5000 if autoscale else None,
        auto_scale_increment_percent=0 if autoscale else None,
        offer_throughput=None if autoscale else 400,
    )
    mock_type = AsyncMock if asynchronous else MagicMock
    database = SimpleNamespace(id="sales", get_throughput=mock_type(return_value=offer))
    container = SimpleNamespace(id="orders", get_throughput=mock_type(return_value=offer))
    filename = "autoscale_throughput_management" + ("_async" if asynchronous else "") + ".py"
    read = _function(filename, "read_autoscale_throughput", {"exceptions": exceptions})
    result = read(database, container)
    if asynchronous:
        asyncio.run(result)
    output = capsys.readouterr().out
    assert ("Maximum throughput: 5000 RU/s" if autoscale else "Manual throughput: 400 RU/s") in output
    if autoscale:
        assert "Increment percent: 0" in output


@pytest.mark.parametrize("fail", [False, True])
def test_sync_sample_always_closes_client_rust(fail):
    client = MagicMock()
    create = MagicMock(return_value=MagicMock())
    if fail:
        create.side_effect = exceptions.CosmosHttpResponseError(status_code=500, message="sample failure")
    namespace = {
        "cosmos_client": SimpleNamespace(CosmosClient=MagicMock(return_value=client)),
        "HOST": "https://example.invalid",
        "MASTER_KEY": "key",
        "DATABASE_ID": "sales",
        "CONTAINER_ID": "orders",
        "exceptions": exceptions,
        "create_database_with_autoscale": create,
        "create_container_with_autoscale": MagicMock(return_value=MagicMock()),
        "read_autoscale_throughput": MagicMock(),
        "update_autoscale_max_throughput": MagicMock(),
    }
    _function("autoscale_throughput_management.py", "run_sample", namespace)()
    client.close.assert_called_once_with()
