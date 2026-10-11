---
changeKind: fix
packages:
  - azure-monitor-opentelemetry-exporter
---

Suppress OpenTelemetry instrumentation around the internal OneSettings configuration refresh request and the Statsbeat Azure VM metadata (IMDS) probe, so these background SDK housekeeping HTTP calls no longer appear as spurious top-level traces/spans alongside real application telemetry.
