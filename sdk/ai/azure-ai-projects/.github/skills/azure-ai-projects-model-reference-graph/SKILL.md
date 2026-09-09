---
name: azure-ai-projects-model-reference-graph
description: 'Generate and analyze the azure-ai-projects model reference graph from models/_models.py through model references, inheritance, runtime ownership, and public operation methods. WHEN: find which operations use a model; trace model dependencies; generate model-reference-graph.json; generate model-reference-trees.txt; investigate unused or orphaned generated models; assess whether a TypeSpec model may be removable. DO NOT USE FOR: deleting generated models automatically; packages other than azure-ai-projects. INVOKES: GenerateModelReferenceGraph.ps1, Python JSON validation, git diff checks.'
argument-hint: 'Optionally provide a model name to inspect after generating the graph'
---

# Generate the azure-ai-projects model reference graph

Run this workflow from `sdk\ai\azure-ai-projects`.

## 1. Check prerequisites

Confirm the package root and required files:

```powershell
git rev-parse --show-prefix
Test-Path .\.github\skills\azure-ai-projects-model-reference-graph\scripts\GenerateModelReferenceGraph.ps1
Test-Path .\azure\ai\projects\models\_models.py
```

The Git prefix must be `sdk/ai/azure-ai-projects/`. Stop and report the missing prerequisite if either file does not exist.

Prefer the active virtual environment's Python. Use `.\.venv\Scripts\python.exe` when it exists; otherwise use `python`.

## 2. Generate the graph

```powershell
.\.github\skills\azure-ai-projects-model-reference-graph\scripts\GenerateModelReferenceGraph.ps1 `
    -PythonExecutable .\.venv\Scripts\python.exe
```

The script produces:

- `model-reference-graph.json`: structured data keyed by every class in `_models.py`.
- `model-reference-trees.txt`: readable reverse-reference trees rooted at every model.

Do not edit generated artifacts manually. Rerun the script after SDK emission or model changes.

## 3. Interpret the graph

For each model, follow children toward public operations:

```text
ChildModel
  `- BaseModel [base class]
     `- RequestOrResponseModel
        `- SomeOperations.method [operation]
```

Edge and marker meanings:

- An unmarked model child directly references its parent through a field, annotation, decorator, or other model declaration.
- `[base class]` traverses from a derived model to its base type.
- `[derived class]` traverses from a base model to a derived type.
- `[operation]` is a public sync/async-deduplicated operation method.
- `[cycle]` stops a circular model relationship.
- `[already expanded]` identifies a shared branch already rendered under the same root.

The JSON entry additionally contains direct and indirect model referrers, bases, derived models, operation references, paths, public-export status, and non-operation references.

Some runtime ownership is not expressible through Python method annotations. The generator maintains an explicit, reviewed ownership table for WebSocket protocol messages, custom polling results, and flattened request bodies. Do not add a mapping based only on similar names. Verify the owning endpoint, handwritten patch, protocol documentation, or generated method implementation first.

## 4. Inspect a requested model

When the user supplies a model name, report:

1. Its base and derived models.
2. Models that reference it directly and indirectly.
3. Every public operation it reaches, distinguishing direct references from inherited or transitive paths.
4. At least one representative path from the operation to the requested model.
5. Non-operation references from patches, tests, or samples.

Use PowerShell for a focused JSON lookup:

```powershell
$graph = Get-Content .\model-reference-graph.json -Raw | ConvertFrom-Json -AsHashtable
$graph.models['<ModelName>'] | ConvertTo-Json -Depth 10
```

## 5. Validate generated artifacts

Run all checks after generation:

```powershell
$tokens = $null
$errors = $null
[System.Management.Automation.Language.Parser]::ParseFile(
    (Resolve-Path '.\.github\skills\azure-ai-projects-model-reference-graph\scripts\GenerateModelReferenceGraph.ps1'),
    [ref]$tokens,
    [ref]$errors
) | Out-Null
if ($errors.Count) { throw ($errors.Message -join [Environment]::NewLine) }

python -m json.tool .\model-reference-graph.json > $null
git diff --check -- .\.github\skills\azure-ai-projects-model-reference-graph\scripts\GenerateModelReferenceGraph.ps1 .\model-reference-graph.json .\model-reference-trees.txt
```

Also verify the summary against the structured graph:

```powershell
$graph = Get-Content .\model-reference-graph.json -Raw | ConvertFrom-Json -AsHashtable
$withoutOperations = @($graph.models.GetEnumerator() | Where-Object { $_.Value.pathsToOperations.Count -eq 0 })
if ($withoutOperations.Count -ne $graph.metadata.modelsWithoutOperationPaths) {
    throw 'The tree summary does not match the structured graph.'
}
```

## 6. Apply removal safeguards

Operation reachability is not proof that a model is safe or unsafe to remove. Before proposing removal, verify all of the following:

- Public export status in `models/__init__.py`.
- References from `_patch.py`, `_unions.py`, samples, and tests.
- Base classes, derived classes, and discriminator registration.
- Runtime protocol roles such as WebSocket events and LRO polling bodies.
- The corresponding TypeSpec declaration and all TypeSpec references.
- API review impact after regenerating the SDK.

Never delete generated classes directly from `_models.py`. Remove or correct the TypeSpec source, regenerate the SDK, rerun this skill, and run package validation.

## 7. Report results

Report the model count, models with and without operation paths, requested model paths, explicit runtime ownership mappings used, and validation results. Clearly label static-analysis limitations and any model requiring TypeSpec or runtime review.