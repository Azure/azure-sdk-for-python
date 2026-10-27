---
changeKind: fix
packages:
  - sdk/monitor/azure-monitor-opentelemetry-exporter
---

Preserve the sampling decision and sample rate of local parent spans when using the rate-limited sampler.
