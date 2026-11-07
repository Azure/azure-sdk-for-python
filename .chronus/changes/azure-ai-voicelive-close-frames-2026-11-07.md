---
changeKind: fix
packages:
  - sdk/voicelive/azure-ai-voicelive
---

Fixed `VoiceLiveConnection.recv()` and `recv_bytes()` so that an aiohttp `CLOSING` message raises `ConnectionClosed` with the connection's close code instead of logging an unexpected message type and raising `ConnectionClosed(1006, "Empty WebSocket frame")`. `ConnectionClosed` raised for a server `CLOSE` frame now also carries the close code and reason sent by the server.
