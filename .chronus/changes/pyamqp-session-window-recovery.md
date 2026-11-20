---
changeKind: fix
packages:
  - sdk/servicebus/azure-servicebus
  - sdk/eventhub/azure-eventhub
---

Fixed pyAMQP session-window exhaustion on long-lived connections and rejected negative unsigned AMQP values. Receive-window replenishment now runs after delivery, including when a link handler raises or is cancelled, and only while the session is mapped so teardown does not advertise new receive capacity.
