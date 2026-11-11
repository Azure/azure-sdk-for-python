---
changeKind: fix
packages:
  - sdk/servicebus/azure-servicebus
  - sdk/eventhub/azure-eventhub
---

Fixed pyAMQP receive-window recovery after a link handler raises or is cancelled. Replenishment happens after delivery and only while the session is mapped, so closing sessions do not advertise new receive capacity.
