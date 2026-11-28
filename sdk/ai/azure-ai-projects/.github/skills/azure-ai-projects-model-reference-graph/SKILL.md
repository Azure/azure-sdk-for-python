---
name: azure-ai-projects-model-reference-graph
description: 'Generate the azure-ai-projects model reference graph, trace operation dependencies, and identify unreferenced models. Writes validated, timestamped JSON and TXT reports to the user temp folder. Use for model-reference graphs, unused models, or TypeSpec removal investigation; not automatic model deletion or other packages.'
argument-hint: 'Optional model name'
---

# Generate the azure-ai-projects model reference graph

Run from `sdk\ai\azure-ai-projects`:

```powershell
.\.github\skills\azure-ai-projects-model-reference-graph\scripts\GenerateModelReferenceGraph.ps1
```

Add `-ModelName '<ModelName>'` when inspecting a specific model.

The script handles prerequisites, Python selection, report generation, validation,
and summaries. Report its results and both absolute output paths.
Unreferenced models require TypeSpec/runtime/API review, not automatic deletion.