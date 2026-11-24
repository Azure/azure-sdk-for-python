---
changeKind: fix
packages:
  - azure-ai-agentserver-responses
---

Preserve Foundry storage HTTP 401 and 403 statuses and error messages as user errors across Responses routes, including create history validation and non-streaming persistence failures, instead of returning platform HTTP 500 errors.
