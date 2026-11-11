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
from typing import get_args, get_type_hints, TYPE_CHECKING, TypedDict

import pytest

from _capabilities import require_capability


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


@pytest.mark.parametrize("widened", [False, True])
def test_knowledge_base_model_inputs_preserve_legacy_constructor_idempotently(tmp_path, monkeypatch, widened):
    package_root = Path(__file__).resolve().parents[1]
    script = package_root / ".github/skills/azure-search-documents/scripts/apply_generator_workarounds.py"
    namespace = runpy.run_path(str(script))
    rules = tuple(
        rule
        for rule in namespace["REPLACEMENTS"]
        if rule.generated.startswith("KnowledgeBaseModel =")
        or rule.patched == '        "models": list["KnowledgeBaseModel"],\n'
        or rule.patched == ':vartype models: list["KnowledgeBaseModel"]\n'
    )
    update = namespace["update_sources"]
    monkeypatch.setitem(update.__globals__, "PACKAGE_ROOT", tmp_path)
    monkeypatch.setitem(update.__globals__, "REPLACEMENTS", rules)
    target = tmp_path / "azure/search/documents/indexes/types.py"
    target.parent.mkdir(parents=True)
    source = (
        "from typing import Union\n"
        "from typing_extensions import Required, TypedDict\n"
        "class KnowledgeBaseAzureOpenAIModel(TypedDict):\n"
        "    kind: str\n"
        "class KnowledgeBaseMicrosoftRetriever1Model(TypedDict):\n"
        "    kind: str\n"
        "class KnowledgeBaseOpenAICompatibleModel(TypedDict):\n"
        "    kind: str\n"
        "KnowledgeBase = TypedDict(\n"
        '    "KnowledgeBase",\n'
        "    {\n"
        '        "name": Required[str],\n'
        '        "knowledgeSources": Required[list[str]],\n'
        '        "models": list["KnowledgeBaseModel"],\n'
        '        "description": str,\n'
        "    },\n"
        "    total=False,\n"
        ")\n"
        'KnowledgeBase.__doc__ = """\n:vartype models: list["KnowledgeBaseModel"]\n"""\n'
        "KnowledgeBaseModel = Union[\n"
        "    KnowledgeBaseAzureOpenAIModel, KnowledgeBaseMicrosoftRetriever1Model, KnowledgeBaseOpenAICompatibleModel\n"
        "]\n"
        "McpServerAuthentication = Union[str]\n"
    )
    if widened:
        source = source.replace(
            'list["KnowledgeBaseModel"]',
            'Union[list["KnowledgeBaseModel"], list["KnowledgeBaseModelInput"]]',
        )
        for rule in rules:
            if rule.generated.startswith("KnowledgeBaseModel ="):
                source = source.replace(rule.generated, rule.patched)
    target.write_text(source, encoding="utf-8")

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
    expanded = get_type_hints(restored["KnowledgeBaseInput"], globalns=restored)
    assert annotations.pop("models") == list[restored["KnowledgeBaseModel"]]
    assert expanded.pop("models") == list[restored["KnowledgeBaseModelInput"]]
    assert annotations == expanded
    for name in ("KnowledgeBase", "KnowledgeBaseInput"):
        assert restored[name].__required_keys__ == {"name", "knowledgeSources"}
        assert restored[name].__optional_keys__ == {"models", "description"}
    assert update(check=False) == 0
    assert update(check=True) == 0
    assert target.read_text(encoding="utf-8") == patched
    unexpected = patched.replace('    "KnowledgeBaseInput",', '    "ConflictingInput",', 1)
    target.write_text(unexpected, encoding="utf-8")
    with pytest.raises(RuntimeError, match="Unexpected existing KnowledgeBaseInput"):
        update(check=False)
    assert target.read_text(encoding="utf-8") == unexpected


def test_knowledge_base_inputs_preserve_public_model_list_contracts():
    require_capability(
        "azure.search.documents.indexes.types.KnowledgeBaseInput",
        "azure.search.documents.indexes.types.KnowledgeBaseModelInput",
    )
    from azure.search.documents.indexes import types

    contracts = TypedDict(
        "Contracts",
        {
            "legacy": types.KnowledgeBase.__annotations__["models"],
            "expanded": types.KnowledgeBaseInput.__annotations__["models"],
        },
    )
    annotations = get_type_hints(contracts, globalns=vars(types))
    assert annotations["legacy"] == list[types.KnowledgeBaseModel]
    assert annotations["expanded"] == list[types.KnowledgeBaseModelInput]
    assert types.KnowledgeBase.__required_keys__ == types.KnowledgeBaseInput.__required_keys__
    assert types.KnowledgeBase.__optional_keys__ == types.KnowledgeBaseInput.__optional_keys__
    assert {key: value for key, value in types.KnowledgeBase.__annotations__.items() if key != "models"} == {
        key: value for key, value in types.KnowledgeBaseInput.__annotations__.items() if key != "models"
    }


if TYPE_CHECKING:
    from azure.search.documents.indexes import SearchIndexClient, models, types
    from azure.search.documents.indexes.aio import SearchIndexClient as AsyncSearchIndexClient

    async def _check_knowledge_base_caller_types(
        client: SearchIndexClient,
        async_client: AsyncSearchIndexClient,
        legacy: types.KnowledgeBase,
        expanded: types.KnowledgeBaseInput,
        model: types.KnowledgeBaseModelInput,
    ) -> None:
        legacy_models: list[types.KnowledgeBaseModel] = legacy["models"]
        legacy_models.append(
            types.KnowledgeBaseModel(
                kind=models.KnowledgeBaseModelKind.AZURE_OPEN_AI,
                azureOpenAIParameters={"resourceUri": "https://example.openai.azure.com", "deploymentId": "query"},
            )
        )
        legacy = types.KnowledgeBase(name="legacy", knowledgeSources=[], models=legacy_models)
        input_models: list[types.KnowledgeBaseModelInput] = expanded["models"]
        input_models.append(model)
        expanded = types.KnowledgeBaseInput(name="expanded", knowledgeSources=[], models=input_models)
        client.create_knowledge_base(legacy)
        client.create_or_update_knowledge_base(legacy)
        client.create_knowledge_base(expanded)
        client.create_or_update_knowledge_base(expanded)
        await async_client.create_knowledge_base(legacy)
        await async_client.create_or_update_knowledge_base(legacy)
        await async_client.create_knowledge_base(expanded)
        await async_client.create_or_update_knowledge_base(expanded)
