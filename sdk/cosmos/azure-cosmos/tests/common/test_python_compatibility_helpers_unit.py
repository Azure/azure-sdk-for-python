# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.
"""Cross-version guards for test execution and reviewed source fingerprints."""

import ast
import asyncio

import pytest

from common.async_test_helpers import run_async
from common.source_fingerprints import stable_ast_dump


@pytest.mark.parametrize("error", [asyncio.CancelledError("cancelled"), RuntimeError("failed")])
def test_async_runner_preserves_error_identity_and_cleanup_rust(error):
    cleaned = []

    async def operation():
        try:
            await asyncio.sleep(0)
            raise error
        finally:
            cleaned.append(True)

    with pytest.raises(type(error)) as caught:
        run_async(operation())
    assert caught.value is error
    assert cleaned == [True]


def test_fingerprints_preserve_meaning_without_version_specific_empty_fields_rust():
    source = "def example():\n    return None\n"
    expected = (
        "Module(body=[FunctionDef(name='example', args=arguments(), "
        "body=[Return(value=Constant(value=None))])])"
    )
    assert stable_ast_dump(ast.parse(source)) == expected
    for changed in ("def example():\n    return False\n", "def example(value):\n    return None\n"):
        assert stable_ast_dump(ast.parse(changed)) != expected
