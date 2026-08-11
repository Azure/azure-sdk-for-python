# Python emitter generates invalid type annotations for Azure AI Search

## Suggested issue title

Python emitter generates invalid enum imports and TypedDict inheritance for Azure AI Search

## Environment

- Package: `azure-search-documents`
- API version: `2026-08-01-preview`
- Python emitter: `@azure-tools/typespec-python` 0.63.3
- TypeSpec project: `specification/search/data-plane/Search`
- TypeSpec commit: `84400eeb46c48ffe88d81e126449725508c17547`
- Validation: MyPy with Python 3.10 compatibility

## Summary

The Python emitter generates four MyPy errors across three `types.py` surfaces. Direct edits to
these files are not viable because SDK regeneration overwrites them.

## Reproduction

Generate `azure-search-documents` from the TypeSpec project above, then run:

```shell
azpysdk --isolate mypy .
```

## Actual diagnostics

```text
azure/search/documents/types.py:16: error: Module "azure.search.documents.models" has no attribute "SemanticQueryRewritesResultType" [attr-defined]
azure/search/documents/types.py:382: error: Name "_enums" is not defined [name-defined]
azure/search/documents/knowledgebases/types.py:28: error: Name "KnowledgeSourceKind" already defined (possibly by an import) [no-redef]
azure/search/documents/indexes/types.py:5443: error: Overwriting TypedDict field "generatedKeyName" while extending [misc]
```

## Bug 1: inconsistent enum export and reference

`SemanticQueryRewritesResultType` is generated in `azure.search.documents.models._enums`, but it is
not exported from `azure.search.documents.models`. The generated `TYPE_CHECKING` import expects the
public export, while `SearchDocumentsResult` refers to the undefined name
`_enums.SemanticQueryRewritesResultType`.

Expected generation:

1. Export `SemanticQueryRewritesResultType` from `azure.search.documents.models`.
2. Use a valid direct or public reference in `SearchDocumentsResult`, consistent with the other
   generated enum annotations.

## Bug 2: duplicate enum import

`azure.search.documents.knowledgebases.types` imports `KnowledgeSourceKind` at runtime from
`indexes.models._enums`, then imports the same name again under `TYPE_CHECKING` from
`indexesmodels`.

Expected generation: emit only one import for `KnowledgeSourceKind`. The existing runtime import is
sufficient for the generated `Literal` annotations.

## Bug 3: TypedDict requiredness override

`SearchIndexerKnowledgeStoreProjectionSelector` declares `generatedKeyName` as optional because the
base `TypedDict` uses `total=False`. `SearchIndexerKnowledgeStoreTableProjectionSelector` inherits
from it and redeclares the same key as `Required[str]`. MyPy does not permit changing a TypedDict
key's requiredness through inheritance.

Expected generation: preserve `generatedKeyName` as required for table projections without
overwriting an inherited TypedDict field. One valid representation is a standalone table-projection
TypedDict containing the shared selector fields plus required `generatedKeyName` and `tableName`.

## Expected result

The generated package passes MyPy without SDK-side edits to generated files, while preserving the
public enum exports and required fields represented by the TypeSpec model.

## Temporary SDK workaround

Until the emitter is fixed, the SDK repository applies exact post-generation replacements with:

```shell
python .github/skills/azure-search-documents/scripts/apply_generator_workarounds.py
python .github/skills/azure-search-documents/scripts/apply_generator_workarounds.py --check
```

The script is idempotent and fails if regenerated output differs from the expected emitter shape.
It repairs only the four diagnostics listed above. Delete the script and its regeneration-guide
references after upgrading to an emitter version that passes MyPy without these replacements.