# Diff the azure-ai-projects Python API surface

Classify the public API changes introduced by one emission or merge. The report drives sample and test authoring.

## Inputs

- `api.md` at the current worktree or `HEAD`.
- `api.md` at the explicitly selected comparison base.
- The same-range diff under `azure\ai\projects` when `api.md` lacks enough context to distinguish a rename from add/remove.

Use one range consistently:

```powershell
# Uncommitted changes
git diff --unified=80 HEAD -- api.md azure\ai\projects

# Committed or merged changes
git diff --unified=80 <base-ref>...HEAD -- api.md azure\ai\projects
```

## Task

Return additions, behaviorally relevant signature changes, likely renames, and removals:

```json
{
  "addedNamespaces": [
    {"name": "azure.ai.projects.operations.ExampleOperations", "isBeta": false}
  ],
  "addedClasses": [
    {"name": "Example", "namespace": "azure.ai.projects.models", "isBeta": false}
  ],
  "addedMethods": [
    {
      "name": "create",
      "owner": "ExampleOperations",
      "namespace": "azure.ai.projects.operations",
      "signature": "create(name: str, *, description: str | None = ...) -> Example",
      "isBeta": false
    }
  ],
  "changedMethods": [
    {
      "name": "update",
      "owner": "ExampleOperations",
      "before": "update(name: str, body: JSON) -> Example",
      "after": "update(name: str, *, description: str) -> Example",
      "changeKinds": ["parameter-removed", "keyword-added"],
      "isBeta": false
    }
  ],
  "renamedSymbols": [
    {"oldName": "OldExample", "newName": "Example", "kind": "class", "confidence": "high"}
  ],
  "removedSymbols": [
    {"name": "delete_legacy", "owner": "ExampleOperations", "kind": "method", "isBeta": false}
  ],
  "affectedAreas": ["examples"]
}
```

Rules:

1. Include public surface only; exclude underscore-prefixed symbols and generated implementation details absent from `api.md`.
2. Collapse overload-only formatting noise. Report a method once with its effective public signatures.
3. Mark anything owned by `BetaOperations`, a `Beta*Operations` type, or exposed through `.beta` as `isBeta: true`.
4. Use source context and matching owners/shapes to identify likely renames. If uncertain, emit separate add/remove entries rather than claiming a rename.
5. Include changed defaults, required/optional transitions, sync/async exposure changes, and return-type changes.
6. Do not treat the expected sync/async duplicate as two product features.
7. Set `affectedAreas` to likely existing `samples\`/`tests\` feature folders; do not invent a folder when no close match exists.

## Output

Return only the JSON report.
