---
changeKind: breaking
packages:
  - azure-ai-agentserver-invocations
---

Renamed the experimental Voice caller-interruption event to `user.barge_in`, with public `UserBargeIn`, `UserBargeInCallback`, and `VoiceAgentServerHost.on_user_barge_in` APIs. The former `barge_in`, `BargeIn`, `BargeInCallback`, and `on_barge_in` names are no longer supported. Voice Live senders must be updated together. Generic raw WebSocket handlers are unchanged.
