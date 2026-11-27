---
changeKind: feature
packages:
  - azure-eventhub
---

Added optional OpenTelemetry operation, event, duration, and AMQP link metrics for synchronous and asynchronous clients. AMQP link opens also emit diagnostic spans and lifecycle logs.
