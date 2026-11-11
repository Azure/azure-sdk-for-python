#!/usr/bin/env python3
"""Apply temporary azure-search-documents Python emitter workarounds. Delete when emitter fixes the issues."""

from __future__ import annotations

import argparse
from dataclasses import dataclass
from pathlib import Path


PACKAGE_ROOT = Path(__file__).resolve().parents[4]


@dataclass(frozen=True)
class Replacement:
    path: str
    description: str
    generated: str
    patched: str
    applies_when: str | None = None
    expected_count: int = 1


REPLACEMENTS = (
    Replacement(
        "azure/search/documents/models/_enums.py",
        "render the agentic debug mode separator as a reStructuredText literal",
        "supported modes using |; this selector",
        "supported modes using ``|``; this selector",
    ),
    Replacement(
        "azure/search/documents/indexes/models/_models.py",
        "suppress generated SearchField constructor complexity",
        "    @overload\n    def __init__(\n        self,\n        *,\n        name: str,\n"
        '        type: Union[str, "_models.SearchFieldDataType"],\n',
        "    @overload\n    def __init__(  # pylint: disable=too-many-locals\n"
        "        self,\n        *,\n        name: str,\n"
        '        type: Union[str, "_models.SearchFieldDataType"],\n',
    ),
    Replacement(
        "azure/search/documents/knowledgebases/_operations/_operations.py",
        "suppress generated sync streaming operation complexity",
        "    def retrieve_stream(\n",
        "    def retrieve_stream(  # pylint: disable=too-many-statements\n",
        expected_count=4,
    ),
    Replacement(
        "azure/search/documents/knowledgebases/aio/_operations/_operations.py",
        "suppress generated async streaming operation complexity",
        "    async def retrieve_stream(\n",
        "    async def retrieve_stream(  # pylint: disable=too-many-statements\n",
        expected_count=4,
    ),
    Replacement(
        "azure/search/documents/indexes/_operations/_operations.py",
        "resolve the File ingestion poller model through the imported sync namespace",
        "return LROPoller[_indexes_models1.KnowledgeSourceFile]",
        "return LROPoller[_models1.KnowledgeSourceFile]",
        expected_count=4,
    ),
    Replacement(
        "azure/search/documents/indexes/aio/_operations/_operations.py",
        "resolve the File ingestion poller model through the imported async namespace",
        "return AsyncLROPoller[_indexes_models1.KnowledgeSourceFile]",
        "return AsyncLROPoller[_models2.KnowledgeSourceFile]",
        expected_count=4,
    ),
    Replacement(
        "azure/search/documents/models/__init__.py",
        "export SemanticQueryRewritesResultType",
        """    SemanticFieldState,
    SemanticSearchResultsType,
""",
        """    SemanticFieldState,
    SemanticQueryRewritesResultType,
    SemanticSearchResultsType,
""",
    ),
    Replacement(
        "azure/search/documents/models/__init__.py",
        "include SemanticQueryRewritesResultType in __all__",
        """    "SemanticFieldState",
    "SemanticSearchResultsType",
""",
        """    "SemanticFieldState",
    "SemanticQueryRewritesResultType",
    "SemanticSearchResultsType",
""",
    ),
    Replacement(
        "azure/search/documents/types.py",
        "use the imported SemanticQueryRewritesResultType enum",
        '"@search.semanticQueryRewritesResultType": Union[str, "_enums.SemanticQueryRewritesResultType"],',
        '"@search.semanticQueryRewritesResultType": Union[str, "SemanticQueryRewritesResultType"],',
        applies_when="@search.semanticQueryRewritesResultType",
    ),
    Replacement(
        "azure/search/documents/knowledgebases/types.py",
        "remove the duplicate KnowledgeSourceKind type-only import",
        """        KnowledgeSourceIngestionPermissionOption,
        KnowledgeSourceKind,
        KnowledgeSourceResultsProcessing,
""",
        """        KnowledgeSourceIngestionPermissionOption,
        KnowledgeSourceResultsProcessing,
""",
        applies_when="KnowledgeSourceIngestionPermissionOption",
    ),
    Replacement(
        "azure/search/documents/indexes/types.py",
        "avoid overriding TypedDict field requiredness",
        """class SearchIndexerKnowledgeStoreTableProjectionSelector(
    SearchIndexerKnowledgeStoreProjectionSelector
):  # pylint: disable=name-too-long
    \"\"\"Description for what data to store in Azure Tables.

    :ivar referenceKeyName: Name of reference key to different projection.
    :vartype referenceKeyName: str
    :ivar source: Source data to project.
    :vartype source: str
    :ivar sourceContext: Source context for complex projections.
    :vartype sourceContext: str
    :ivar inputs: Nested inputs for complex projections.
    :vartype inputs: list[\"InputFieldMappingEntry\"]
    :ivar generatedKeyName: Name of generated key to store projection under. Required.
    :vartype generatedKeyName: str
    :ivar tableName: Name of the Azure table to store projected data in. Required.
    :vartype tableName: str
    \"\"\"

    generatedKeyName: Required[str]
    \"\"\"Name of generated key to store projection under. Required.\"\"\"
    tableName: Required[str]
    \"\"\"Name of the Azure table to store projected data in. Required.\"\"\"
""",
        (
            "class SearchIndexerKnowledgeStoreTableProjectionSelector(TypedDict, total=False):  "
            "# pylint: disable=name-too-long\n"
            """    \"\"\"Description for what data to store in Azure Tables.

    :ivar referenceKeyName: Name of reference key to different projection.
    :vartype referenceKeyName: str
    :ivar source: Source data to project.
    :vartype source: str
    :ivar sourceContext: Source context for complex projections.
    :vartype sourceContext: str
    :ivar inputs: Nested inputs for complex projections.
    :vartype inputs: list[\"InputFieldMappingEntry\"]
    :ivar generatedKeyName: Name of generated key to store projection under. Required.
    :vartype generatedKeyName: str
    :ivar tableName: Name of the Azure table to store projected data in. Required.
    :vartype tableName: str
    \"\"\"

    referenceKeyName: str
    \"\"\"Name of reference key to different projection.\"\"\"
    source: str
    \"\"\"Source data to project.\"\"\"
    sourceContext: str
    \"\"\"Source context for complex projections.\"\"\"
    inputs: list[\"InputFieldMappingEntry\"]
    \"\"\"Nested inputs for complex projections.\"\"\"
    generatedKeyName: Required[str]
    \"\"\"Name of generated key to store projection under. Required.\"\"\"
    tableName: Required[str]
    \"\"\"Name of the Azure table to store projected data in. Required.\"\"\"
"""
        ),
    ),
    Replacement(
        "azure/search/documents/indexes/types.py",
        "import KnowledgeSourceIngestionParameters from the public models namespace",
        "    from ..knowledgebases.types import KnowledgeRetrievalReasoningEffort, KnowledgeSourceIngestionParameters\n",
        "    from ..knowledgebases.models import KnowledgeSourceIngestionParameters\n"
        "    from ..knowledgebases.types import KnowledgeRetrievalReasoningEffort\n",
    ),
    Replacement(
        "azure/search/documents/indexes/_operations/_operations.py",
        "suppress protected access for the generated SearchIndexResponse type",
        "                list[_models1._models.SearchIndexResponse],\n"
        '                deserialized.get("value", []),\n'
        "            )",
        "                list[_models1._models.SearchIndexResponse],  # pylint: disable=protected-access\n"
        '                deserialized.get("value", []),\n'
        "            )",
    ),
    Replacement(
        "azure/search/documents/indexes/aio/_operations/_operations.py",
        "suppress protected access for the generated async SearchIndexResponse type",
        "                list[_models2._models.SearchIndexResponse],\n"
        '                deserialized.get("value", []),\n'
        "            )",
        "                list[_models2._models.SearchIndexResponse],  # pylint: disable=protected-access\n"
        '                deserialized.get("value", []),\n'
        "            )",
    ),
    Replacement(
        "azure/search/documents/indexes/types.py",
        "keep the approved GA KnowledgeBaseModel alias",
        "KnowledgeBaseModel = Union[\n"
        "    KnowledgeBaseAzureOpenAIModel, KnowledgeBaseMicrosoftRetriever1Model, KnowledgeBaseOpenAICompatibleModel\n"
        "]\n",
        "KnowledgeBaseModel = Union[KnowledgeBaseAzureOpenAIModel]\n",
    ),
    Replacement(
        "azure/search/documents/indexes/types.py",
        "expose all knowledge-base model variants through a separate input union",
        "KnowledgeBaseModel = Union[KnowledgeBaseAzureOpenAIModel]\nMcpServerAuthentication =",
        "KnowledgeBaseModel = Union[KnowledgeBaseAzureOpenAIModel]\n\n"
        "KnowledgeBaseModelInput = Union[\n"
        "    KnowledgeBaseAzureOpenAIModel, KnowledgeBaseMicrosoftRetriever1Model, KnowledgeBaseOpenAICompatibleModel\n"
        "]\n"
        '"""All supported knowledge-base model variants for dictionary-style inputs."""\n\n'
        "McpServerAuthentication =",
    ),
    Replacement(
        "azure/search/documents/indexes/types.py",
        "preserve the GA knowledge-base model-list field",
        '        "models": Union[list["KnowledgeBaseModel"], list["KnowledgeBaseModelInput"]],\n',
        '        "models": list["KnowledgeBaseModel"],\n',
    ),
    Replacement(
        "azure/search/documents/indexes/types.py",
        "preserve the GA knowledge-base model-list documentation",
        ':vartype models: Union[list["KnowledgeBaseModel"], list["KnowledgeBaseModelInput"]]\n',
        ':vartype models: list["KnowledgeBaseModel"]\n',
    ),
)

REPLACEMENTS += tuple(
    replacement
    for path, model_namespace, types_namespace, kwargs_comma in (
        ("azure/search/documents/indexes/_operations/_operations.py", "_models1", "_types_models1", ","),
        ("azure/search/documents/indexes/aio/_operations/_operations.py", "_models2", "_types_models2", ""),
    )
    for replacement in (
        Replacement(
            path,
            "accept expanded knowledge-base inputs in the generated create overload",
            f"        self, knowledge_base: {types_namespace}.KnowledgeBase, "
            '*, content_type: str = "application/json", **kwargs: Any\n',
            "        self,\n"
            f"        knowledge_base: Union[{types_namespace}.KnowledgeBase, {types_namespace}.KnowledgeBaseInput],\n"
            "        *,\n"
            '        content_type: str = "application/json",\n'
            f"        **kwargs: Any{kwargs_comma}\n",
        ),
        Replacement(
            path,
            "accept expanded knowledge-base inputs in the generated create implementation",
            f"        self, knowledge_base: Union[{model_namespace}.KnowledgeBase, "
            f"{types_namespace}.KnowledgeBase, IO[bytes]], **kwargs: Any\n",
            "        self,\n"
            "        knowledge_base: Union[\n"
            f"            {model_namespace}.KnowledgeBase, {types_namespace}.KnowledgeBase, "
            f"{types_namespace}.KnowledgeBaseInput, IO[bytes]\n"
            "        ],\n"
            f"        **kwargs: Any{kwargs_comma}\n",
        ),
        Replacement(
            path,
            "accept expanded knowledge-base inputs in the generated update overload",
            "        name: str,\n" f"        knowledge_base: {types_namespace}.KnowledgeBase,\n",
            "        name: str,\n"
            f"        knowledge_base: Union[{types_namespace}.KnowledgeBase, {types_namespace}.KnowledgeBaseInput],\n",
        ),
        Replacement(
            path,
            "accept expanded knowledge-base inputs in the generated update implementation",
            "        name: str,\n"
            f"        knowledge_base: Union[{model_namespace}.KnowledgeBase, "
            f"{types_namespace}.KnowledgeBase, IO[bytes]],\n",
            "        name: str,\n"
            "        knowledge_base: Union[\n"
            f"            {model_namespace}.KnowledgeBase, {types_namespace}.KnowledgeBase, "
            f"{types_namespace}.KnowledgeBaseInput, IO[bytes]\n"
            "        ],\n",
        ),
        Replacement(
            path,
            "document expanded knowledge-base inputs in the generated create overload",
            "        :type knowledge_base: ~azure.search.documents.indexes.types.KnowledgeBase\n",
            "        :type knowledge_base: ~azure.search.documents.indexes.types.KnowledgeBase or\n"
            "         ~azure.search.documents.indexes.types.KnowledgeBaseInput\n",
        ),
        Replacement(
            path,
            "document expanded knowledge-base inputs in the generated implementations",
            "         ~azure.search.documents.indexes.types.KnowledgeBase or IO[bytes]\n",
            "         ~azure.search.documents.indexes.types.KnowledgeBase or\n"
            "         ~azure.search.documents.indexes.types.KnowledgeBaseInput or IO[bytes]\n",
            expected_count=2,
        ),
    )
)


for _folder, _stream, _await in (("", "Stream", ""), ("aio/", "AsyncStream", "await ")):
    _stream_assignment = (
        f" = {_stream}(response=response, deserialization_callback=_callback, "
        'terminal_event_names=["error", "response.completed"])  # type: ignore\n'
    )
    REPLACEMENTS += (
        Replacement(
            f"azure/search/documents/knowledgebases/{_folder}_operations/_operations.py",
            f"close the {_stream} when the response callback raises",
            _stream_assignment + "        if cls:\n"
            "            return cls(pipeline_response, deserialized, {})  # type: ignore\n"
            "        return deserialized\n",
            _stream_assignment + "        if cls:\n"
            "            try:\n"
            "                return cls(pipeline_response, deserialized, {})  # type: ignore\n"
            "            except BaseException:\n"
            f"                {_await}deserialized.close()\n"
            "                raise\n"
            "        return deserialized\n",
        ),
    )


def _add_knowledge_base_input(source: str) -> tuple[str, bool]:
    declaration = "KnowledgeBase = TypedDict(\n"
    documentation = 'KnowledgeBase.__doc__ = """'
    if source.count(declaration) != 1 or source.count(documentation) != 1:
        raise RuntimeError("Unexpected emitter output while locating the KnowledgeBase TypedDict")
    start = source.index(declaration)
    end = source.index('"""', source.index(documentation, start) + len(documentation)) + 3
    legacy = source[start:end]
    if legacy.count('list["KnowledgeBaseModel"]') != 2:
        raise RuntimeError("Unexpected emitter output for the legacy KnowledgeBase model-list contract")
    expanded = (
        legacy.replace("KnowledgeBase = TypedDict(", "KnowledgeBaseInput = TypedDict(", 1)
        .replace('    "KnowledgeBase",', '    "KnowledgeBaseInput",', 1)
        .replace("KnowledgeBase.__doc__", "KnowledgeBaseInput.__doc__", 1)
        .replace('list["KnowledgeBaseModel"]', 'list["KnowledgeBaseModelInput"]')
        .replace(
            "Represents a knowledge base definition.",
            "Dictionary-style knowledge-base input supporting all model variants.",
            1,
        )
    )
    if source.count(expanded) == 1 and source.count("KnowledgeBaseInput = TypedDict(") == 1:
        return source, False
    if "KnowledgeBaseInput = TypedDict(" in source:
        raise RuntimeError("Unexpected existing KnowledgeBaseInput definition; regenerate before applying workarounds")
    return source[:end] + "\n\n" + expanded + source[end:], True


def update_sources(*, check: bool) -> int:
    sources: dict[Path, str] = {}
    pending: list[str] = []

    for replacement in REPLACEMENTS:
        path = PACKAGE_ROOT / replacement.path
        source = sources.setdefault(path, path.read_text(encoding="utf-8"))
        generated_count = source.count(replacement.generated)
        patched_count = source.count(replacement.patched)

        if generated_count == replacement.expected_count and patched_count == 0:
            sources[path] = source.replace(replacement.generated, replacement.patched, replacement.expected_count)
            pending.append(replacement.description)
        elif generated_count == 0 and patched_count == replacement.expected_count:
            continue
        elif replacement.applies_when is not None and replacement.applies_when not in source:
            continue
        else:
            raise RuntimeError(
                f"Unexpected emitter output in {replacement.path} while attempting to "
                f"{replacement.description}; expected exactly {replacement.expected_count} generated or patched snippets"
            )

    path = PACKAGE_ROOT / "azure/search/documents/indexes/types.py"
    sources[path], added = _add_knowledge_base_input(sources[path])
    if added:
        pending.append("add a separate complete KnowledgeBaseInput without widening the GA TypedDict")

    if check:
        if pending:
            print("Generator workarounds are required:")
            for description in pending:
                print(f"- {description}")
            return 1
        print("Generator workarounds are applied.")
        return 0

    for path, source in sources.items():
        path.write_text(source, encoding="utf-8")

    if pending:
        print("Applied generator workarounds:")
        for description in pending:
            print(f"- {description}")
    else:
        print("Generator workarounds were already applied.")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--check",
        action="store_true",
        help="verify that all workarounds are applied without changing files",
    )
    args = parser.parse_args()
    return update_sources(check=args.check)


if __name__ == "__main__":
    raise SystemExit(main())
