# Agentserver standalone skills

Three "AI-coding-agent skill" files — standalone, portable, copy-into-
your-project artifacts that give a coding agent (GitHub Copilot, etc.)
enough context to use each primitive correctly.

| Skill | What it teaches | Companion package |
|-------|-----------------|-------------------|
| [`durable-task-skill.md`](durable-task-skill.md) | The `@task` durable primitive — crash-resilient long-running handlers, lease + recovery, steering, multi-turn | `azure-ai-agentserver-core` |
| [`streaming-skill.md`](streaming-skill.md) | The `streams` registry — producer/subscriber fan-out, replay backings, durable streaming, `Last-Event-ID` reconnect | `azure-ai-agentserver-core` |
| [`responses-skill.md`](responses-skill.md) | The `ResponsesAgentServerHost` — OpenAI Responses API host, builder events, durable + steerable conversations | `azure-ai-agentserver-responses` |

## Why standalone

Each skill has a YAML frontmatter block (`name:` + `description:`)
that Copilot's skill system recognises, and a body shaped for an
LLM: explicit WHEN / WHEN NOT, a minimal runnable pattern, decision
shortcuts. They're meant to be **copied** into a project — drop the
markdown file next to your code and Copilot picks it up.

## Why on the demo branch

Skills + the [preview wheels](../wheels/) form a single distribution
unit: the skill teaches the API, the wheels provide the implementation.
Both live on this branch (`feature/agentserver-durable-agent-demo`)
so a downstream project can clone one branch and get everything it
needs to build durable / streaming / Responses-API agents.

The long-form developer guides each skill references
(`durable-task-guide.md`, `streaming-guide.md`,
`handler-implementation-guide.md`, etc.) live in the corresponding
package's `docs/` folder — they're SOT reference documentation tied
to the package, while the skills are portable.

## Refreshing

After substantive API or contract changes to a package, the matching
skill should be updated by hand. Skills are not auto-generated — they
distil tribal knowledge that no single doc captures.
