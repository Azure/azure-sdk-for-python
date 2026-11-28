---
changeKind: fix
packages:
  - azure-eventhub
---

Fixed asynchronous consumers silently ignoring `com.microsoft:georeplication:invalid-offset` errors while opening a receiver link. These errors now propagate to the application's `on_error` callback without changing the checkpoint or falling back to another offset.
