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


def test_scoring_inputs_preserve_legacy_fields_idempotently():
    package_root = Path(__file__).resolve().parents[1]
    script = package_root / ".github/skills/azure-search-documents/scripts/apply_generator_workarounds.py"
    namespace = runpy.run_path(str(script))
    add_inputs = namespace["_add_scoring_inputs"]
    source = (
        "class ScoringProfile(TypedDict, total=False):\n"
        '    """Defines parameters for a search index that influence scoring in search queries.\n'
        '    :vartype functions: list["ScoringFunction"]\n'
        '    """\n'
        "    name: Required[str]\n"
        '    functions: list["ScoringFunction"]\n\n'
        "SearchIndex = TypedDict(\n"
        '    "SearchIndex",\n'
        '    {"name": Required[str], "fields": Required[list[str]], '
        '"scoringProfiles": list["ScoringProfile"], "@odata.etag": str},\n'
        "    total=False,\n"
        ")\n"
        'SearchIndex.__doc__ = """Represents a search index definition,\n'
        ':vartype scoringProfiles: list["ScoringProfile"]\n'
        '"""\n'
    )
    patched, changed = add_inputs(source)
    assert changed
    assert source.split("SearchIndex =")[0] in patched
    assert 'functions: list["ScoringFunctionInput"]' in patched
    assert '"scoringProfiles": list["ScoringProfileInput"]' in patched
    assert add_inputs(patched) == (patched, False)
    unexpected = patched.replace('functions: list["ScoringFunctionInput"]', 'functions: list["ScoringFunction"]', 1)
    with pytest.raises(RuntimeError, match="Unexpected existing ScoringProfileInput"):
        add_inputs(unexpected)
    for conflicting in (
        "class ScoringProfileInput(TypedDict):\n    name: str\n",
        'SearchIndexInput = TypedDict("ConflictingInput", {"name": str})\n',
    ):
        with pytest.raises(RuntimeError, match="Unexpected existing"):
            add_inputs(patched + "\n" + conflicting)


def test_scoring_inputs_preserve_public_profile_and_index_contracts():
    require_capability(
        "azure.search.documents.indexes.types.ScoringFunctionInput",
        "azure.search.documents.indexes.types.ScoringProfileInput",
        "azure.search.documents.indexes.types.SearchIndexInput",
    )
    from azure.search.documents.indexes import types

    assert get_args(types.ScoringFunction) == (
        types.DistanceScoringFunction,
        types.FreshnessScoringFunction,
        types.MagnitudeScoringFunction,
        types.TagScoringFunction,
    )
    assert set(get_args(types.ScoringFunctionInput)) == set(get_args(types.ScoringFunction)) | {
        types.RandomScoringFunction
    }
    for legacy, expanded, field, legacy_type, expanded_type in (
        (
            types.ScoringProfile,
            types.ScoringProfileInput,
            "functions",
            types.ScoringFunction,
            types.ScoringFunctionInput,
        ),
        (types.SearchIndex, types.SearchIndexInput, "scoringProfiles", types.ScoringProfile, types.ScoringProfileInput),
    ):
        contracts = TypedDict(
            "Contracts",
            {
                "legacy": legacy.__annotations__[field],
                "expanded": expanded.__annotations__[field],
            },
        )
        annotations = get_type_hints(contracts, globalns=vars(types))
        assert annotations["legacy"] == list[legacy_type]
        assert annotations["expanded"] == list[expanded_type]
        assert {key: value for key, value in legacy.__annotations__.items() if key != field} == {
            key: value for key, value in expanded.__annotations__.items() if key != field
        }
        assert legacy.__required_keys__ == expanded.__required_keys__
        assert legacy.__optional_keys__ == expanded.__optional_keys__


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

    def _read_legacy_scoring_types(
        function: types.ScoringFunction,
        profile: types.ScoringProfile,
        index: types.SearchIndex,
    ) -> tuple[float, str]:
        functions: list[types.ScoringFunction] = profile["functions"]
        profiles: list[types.ScoringProfile] = index["scoringProfiles"]
        functions.append(function)
        profiles.append(profile)
        return function["boost"], function["fieldName"]

    async def _check_scoring_input_types(
        client: SearchIndexClient,
        async_client: AsyncSearchIndexClient,
        legacy: types.SearchIndex,
        function: types.ScoringFunctionInput,
    ) -> None:
        random = types.RandomScoringFunction(type="random", random={"seedParameter": "seed"})
        functions: list[types.ScoringFunctionInput] = [random]
        profile = types.ScoringProfileInput(name="random-order", functions=functions)
        profiles: list[types.ScoringProfileInput] = [profile]
        index = types.SearchIndexInput(name="hotels", fields=[], scoringProfiles=profiles)
        models.ScoringProfile(profile)
        models.SearchIndex(index)
        if function["type"] != "random":
            field: str = function["fieldName"]
            _read_legacy_scoring_types(function, types.ScoringProfile(name=field, functions=[function]), legacy)
        client.create_index(legacy)
        client.create_or_update_index(legacy)
        client.create_index(index)
        client.create_or_update_index(index)
        await async_client.create_index(legacy)
        await async_client.create_or_update_index(legacy)
        await async_client.create_index(index)
        await async_client.create_or_update_index(index)
