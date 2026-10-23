# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
"""Tests for package-owned post-generation workarounds."""

import ast
from pathlib import Path
import subprocess
import sys


def test_agentic_debug_documentation_uses_literal_mode_separator():
    package_root = Path(__file__).resolve().parents[1]
    source = ast.parse((package_root / "azure/search/documents/models/_enums.py").read_text(encoding="utf-8"))
    enum = next(node for node in source.body if isinstance(node, ast.ClassDef) and node.name == "QueryDebugMode")
    member_index = next(
        index
        for index, node in enumerate(enum.body)
        if isinstance(node, ast.Assign)
        and any(isinstance(target, ast.Name) and target.id == "AGENTIC" for target in node.targets)
    )
    documentation = ast.literal_eval(enum.body[member_index + 1].value)
    assert "using ``|``;" in documentation


def test_generator_workarounds_are_applied():
    package_root = Path(__file__).resolve().parents[1]
    script = package_root / ".github/skills/azure-search-documents/scripts/apply_generator_workarounds.py"

    result = subprocess.run(
        [sys.executable, str(script), "--check"],
        cwd=package_root,
        check=False,
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0, result.stdout + result.stderr
