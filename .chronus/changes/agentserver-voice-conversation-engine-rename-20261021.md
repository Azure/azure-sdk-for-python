---
changeKind: breaking
packages:
  - azure-ai-agentserver-invocations
---

Renamed the standalone Hosted Agent protocol and route from `conversation_engine` / `/conversation_engine` to `voice_conversation_engine` / `/voice_conversation_engine`, with no old-name alias. The independent `/invocations_ws` route and Bridge message version `1.0` are unchanged.
