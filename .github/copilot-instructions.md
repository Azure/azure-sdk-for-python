# Copilot instructions

Follow [`../AGENTS.md`](../AGENTS.md) as the canonical repository-wide agent
guidance.

- Apply the nearest `AGENTS.md` and every matching path-specific instruction
  under `.github/instructions/`.
- Load the matching skill under `.github/skills/` for specialized work instead
  of copying its procedure into the conversation or improvising a parallel
  workflow.
- Use the
  [Azure SDK Python Design Guidelines](https://azure.github.io/azure-sdk/python_design.html)
  as the authority when a task concerns SDK design or public APIs.
- Run `azsdk_verify_setup` before the first operation that depends on Azure SDK
  MCP tools, not before ordinary reading, searching, reviewing, editing, or
  local validation.
- Prefer focused changes and the smallest existing validation that covers
  them. Do not claim a check passed unless it was run successfully.
