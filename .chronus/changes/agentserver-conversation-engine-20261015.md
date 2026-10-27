---
changeKind: feature
packages:
  - azure-ai-agentserver-invocations
---

Added a standalone `/voice_conversation_engine` WebSocket route to `VoiceAgentServerHost`, reusing the typed Bridge event relay alongside its unchanged `/invocations_ws` route without new constructor options. Generic `InvocationAgentServerHost` raw WebSocket handlers are unchanged.
