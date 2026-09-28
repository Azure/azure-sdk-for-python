---
changeKind: fix
packages:
  - azure-ai-evaluation
---

Fixed multi-turn evaluations failing during Azure OpenAI result conversion when per-turn token-count lists were routed into scalar token-usage fields. Per-turn breakdowns are now excluded from scalar result-field routing, preserving aggregate token counts and scores. ([#49242](https://github.com/Azure/azure-sdk-for-python/pull/49242))
