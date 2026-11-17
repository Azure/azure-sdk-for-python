---
changeKind: feature
packages:
  - azure-ai-agentserver-invocations
---

Aligned the experimental Voice caller-interruption contract with `user.barge_in`, `UserBargeIn`, `UserBargeInCallback`, and `VoiceAgentServerHost.on_user_barge_in`. Playback snapshots and application-owned cancellation/history are preserved. Voice Live senders must use the same event contract. Generic raw WebSocket handlers are unchanged.
