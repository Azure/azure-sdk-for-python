# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
"""Tests for package-owned post-generation workarounds."""

import ast
from pathlib import Path
import runpy
import subprocess
import sys
from typing import get_args, get_type_hints, Union


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


def test_knowledge_base_model_inputs_preserve_legacy_constructor_idempotently(tmp_path, monkeypatch):
    package_root = Path(__file__).resolve().parents[1]
    script = package_root / ".github/skills/azure-search-documents/scripts/apply_generator_workarounds.py"
    namespace = runpy.run_path(str(script))
    rules = tuple(
        rule
        for rule in namespace["REPLACEMENTS"]
        if rule.generated.startswith("KnowledgeBaseModel =")
        or rule.generated == '        "models": list["KnowledgeBaseModel"],\n'
        or rule.generated == ':vartype models: list["KnowledgeBaseModel"]\n'
    )
    update = namespace["update_sources"]
    monkeypatch.setitem(update.__globals__, "PACKAGE_ROOT", tmp_path)
    monkeypatch.setitem(update.__globals__, "REPLACEMENTS", rules)
    target = tmp_path / "azure/search/documents/indexes/types.py"
    target.parent.mkdir(parents=True)
    target.write_text(
        "from typing import TypedDict, Union\n"
        "class KnowledgeBaseAzureOpenAIModel(TypedDict):\n"
        "    kind: str\n"
        "class KnowledgeBaseMicrosoftRetriever1Model(TypedDict):\n"
        "    kind: str\n"
        "class KnowledgeBaseOpenAICompatibleModel(TypedDict):\n"
        "    kind: str\n"
        "KnowledgeBase = TypedDict(\n"
        '    "KnowledgeBase",\n'
        "    {\n"
        '        "models": list["KnowledgeBaseModel"],\n'
        "    },\n"
        ")\n"
        'KnowledgeBase.__doc__ = """\n:vartype models: list["KnowledgeBaseModel"]\n"""\n'
        "KnowledgeBaseModel = Union[\n"
        "    KnowledgeBaseAzureOpenAIModel, KnowledgeBaseMicrosoftRetriever1Model, KnowledgeBaseOpenAICompatibleModel\n"
        "]\n"
        "McpServerAuthentication = Union[str]\n",
        encoding="utf-8",
    )

    assert update(check=True) == 1
    assert update(check=False) == 0
    patched = target.read_text(encoding="utf-8")
    restored = runpy.run_path(str(target))
    assert restored["KnowledgeBaseModel"](kind="azureOpenAI") == {"kind": "azureOpenAI"}
    assert get_args(restored["KnowledgeBaseModelInput"]) == (
        restored["KnowledgeBaseAzureOpenAIModel"],
        restored["KnowledgeBaseMicrosoftRetriever1Model"],
        restored["KnowledgeBaseOpenAICompatibleModel"],
    )
    annotations = get_type_hints(restored["KnowledgeBase"], globalns=restored)
    assert (
        annotations["models"] == Union[list[restored["KnowledgeBaseModel"]], list[restored["KnowledgeBaseModelInput"]]]
    )
    assert update(check=False) == 0
    assert update(check=True) == 0
    assert target.read_text(encoding="utf-8") == patched
