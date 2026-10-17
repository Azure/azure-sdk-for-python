---
changeKind: fix
packages:
  - sdk/monitor/azure-monitor-opentelemetry-exporter
---

Serialize string arrays in `gen_ai.request.stop_sequences` and `gen_ai.response.finish_reasons` as JSON strings in trace custom properties, preserving existing string values. Native arrays previously used Python sequence representations. Existing property length limits continue to apply after serialization.
