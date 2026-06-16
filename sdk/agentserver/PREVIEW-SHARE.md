# Agentserver durable preview — share bundle

This branch is a **self-contained preview distribution** of the
`azure-ai-agentserver-*` durable + Responses/Invocations primitives,
assembled for internal teams to experiment with. It bundles
pre-built wheels, runnable samples, reference guides, and copy-into-
your-project Copilot skills — no PyPI publish or source build required.

> Built off `main`. The package **source** under
> `azure-ai-agentserver-*/azure/...` is `main`'s — consume the
> **wheels** below, not the in-tree source.

## What's here

| Path | Contents |
|------|----------|
| [`wheels/`](wheels/) | Pre-built `core` / `invocations` / `responses` wheels. Install these. |
| [`skills/`](skills/) | 4 standalone Copilot skills (durable-task, streaming, invocations, responses). Drop next to your code. |
| [`azure-ai-agentserver-core/docs/`](azure-ai-agentserver-core/docs/) | Durable-task + streaming guides and the SOT spec. |
| [`azure-ai-agentserver-responses/docs/`](azure-ai-agentserver-responses/docs/) | Responses durability + handler-implementation guides. |
| `azure-ai-agentserver-responses/samples/` | Responses host samples + the `durable-responses-agent-demo` (azd-deployable). |
| `azure-ai-agentserver-invocations/samples/` | Invocations host samples + the `durable-agent-demo`. |

## Install

```bash
pip install wheels/*.whl
```

The wheels carry the durable-task crash-recovery primitives and the
Responses spec-025 checkpoint API. Recovery is exercised locally with
no hosted task API via:

```bash
export AGENTSERVER_TASKS_BACKEND=local
export AGENTSERVER_DURABLE_ROOT=/tmp/durable   # task + response store
```

## Versions

| Wheel | Version |
|-------|---------|
| `azure-ai-agentserver-core` | `2.0.0b7` |
| `azure-ai-agentserver-invocations` | `1.0.0b6` |
| `azure-ai-agentserver-responses` | `1.0.0b8` |

These are unreleased preview (`bN`) builds. To rebuild the wheels from
updated source, see [`wheels/build-wheels.sh`](wheels/build-wheels.sh).
