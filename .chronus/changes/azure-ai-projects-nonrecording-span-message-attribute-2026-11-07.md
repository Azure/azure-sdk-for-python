---
changeKind: fix
packages:
  - sdk/ai/azure-ai-projects
---

Fixed an `AttributeError` raised from the responses instrumentation when the span is not recording (for example, when it is sampled out), which made a successful non-streamed `responses.create` call fail. ([GitHub issue 49854](https://github.com/Azure/azure-sdk-for-python/issues/49854))
