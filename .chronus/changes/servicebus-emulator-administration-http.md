---
changeKind: fix
packages:
  - sdk/servicebus/azure-servicebus
---

Fixed synchronous and asynchronous administration operations sending HTTPS to the
emulator's HTTP management port when `UseDevelopmentEmulator=true` is present in
the connection string. Omitted or false flags continue to use HTTPS.
