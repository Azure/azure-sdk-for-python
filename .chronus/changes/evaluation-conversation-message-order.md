---
changeKind: breaking
packages:
  - sdk/evaluation/azure-ai-evaluation
---

Evaluators that support both `messages` inputs and whole-conversation scoring now treat `conversation={"messages": ...}` as the equivalent `messages=...` input. Their default scoring changes from per-turn aggregation to whole-conversation scoring. Explicit evaluation levels follow the existing `messages` behavior. Evaluators without whole-conversation support retain their existing conversion path.

Conversation transcripts preserve chronological message order, including assistant-first greetings and unmatched final user or assistant turns, without synthesizing user messages. Existing conversation-history formatter callers retain their previous behavior.
