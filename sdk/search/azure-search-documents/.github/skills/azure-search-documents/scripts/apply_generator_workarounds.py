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


REPLACEMENTS = (
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
)


def update_sources(*, check: bool) -> int:
    sources: dict[Path, str] = {}
    pending: list[str] = []

    for replacement in REPLACEMENTS:
        path = PACKAGE_ROOT / replacement.path
        source = sources.setdefault(path, path.read_text(encoding="utf-8"))
        generated_count = source.count(replacement.generated)
        patched_count = source.count(replacement.patched)

        if generated_count == 1 and patched_count == 0:
            sources[path] = source.replace(replacement.generated, replacement.patched, 1)
            pending.append(replacement.description)
        elif generated_count == 0 and patched_count == 1:
            continue
        elif replacement.applies_when is not None and replacement.applies_when not in source:
            continue
        else:
            raise RuntimeError(
                f"Unexpected emitter output in {replacement.path} while attempting to "
                f"{replacement.description}; expected exactly one generated or patched snippet"
            )

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