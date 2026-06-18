# Agentserver durable preview — share bundle

This branch is a **self-contained preview distribution** of the
`azure-ai-agentserver-*` durable + Responses/Invocations primitives,
assembled for internal teams to experiment with. It bundles
pre-built wheels, runnable **durable** samples, developer guides, and
copy-into-your-project Copilot skills — no PyPI publish or source build
required.

> Built off `main`. The package **source** under
> `azure-ai-agentserver-*/azure/...` is `main`'s — consume the
> **wheels** below, not the in-tree source.

## What's here

| Path | Contents |
|------|----------|
| [`wheels/`](wheels/) | Pre-built `core` / `invocations` / `responses` wheels. Install these. |
| [`skills/`](skills/) | 4 standalone Copilot skills (durable-task, streaming, invocations, responses). Drop next to your code. |
| [`azure-ai-agentserver-core/docs/`](azure-ai-agentserver-core/docs/) | Durable-task + streaming developer guides + the `task-and-streaming-spec.md` source-of-truth spec. |
| [`azure-ai-agentserver-responses/docs/`](azure-ai-agentserver-responses/docs/) | Responses durability + handler-implementation guides + the `responses-durability-spec.md` SOT spec and `durability-contract.md` contract matrix. |
| `azure-ai-agentserver-responses/samples/` | Durable Responses samples + the `durable-responses-agent-demo`. |
| `azure-ai-agentserver-invocations/samples/` | Durable Invocations samples + the `durable-agent-demo`. |

Only **durable** samples are included.

## Latest refresh

The bundled wheels carry the current durable + responses fixes:

- **core** — steering fixes: `ctx.pending_input_count` now reflects the live
  queued-input count (was always `0`); the steering drain transitions the
  record `suspended→in_progress` so the steered turn runs on hosted (was
  failing with "lease renewal is only supported for in_progress tasks");
  plus write-serialization hardening (read-inside-lock, lock-held update
  primitive, no blind writes). Validated end-to-end on a hosted deployment.
- **responses** — durable stored streams are created under SSE keep-alive
  (hosted responses no longer hang `in_progress`).
- **invocations sample** — `durable-agent-demo` uses `gpt-4o`; `demo-client.sh`
  auto-resolves the endpoint from your azd env after `azd deploy`.

## Install

```bash
pip install wheels/*.whl
```

## Run the crash → recover demo locally

The durable demos run end-to-end against a **hosted** Foundry deployment
(`azd deploy` the sample, then drive it with `demo-client.sh` — the client
auto-resolves the endpoint from your azd env). An equivalent **local**,
file-backed kit (task store + response store on disk, no hosted dependency)
is also provided for offline experimentation. A ready-to-run, verified kit
lives at
**[`azure-ai-agentserver-responses/samples/durable-responses-agent-demo/local/`](azure-ai-agentserver-responses/samples/durable-responses-agent-demo/local/README.md)**:

```bash
cd azure-ai-agentserver-responses/samples/durable-responses-agent-demo/local
./setup.sh                                  # venv from ../../../../wheels
az login
export FOUNDRY_PROJECT_ENDPOINT=https://<account>.services.ai.azure.com/api/projects/<project>
export AZURE_AI_MODEL_DEPLOYMENT_NAME=gpt-4o
./run.sh                                    # stream -> crash -> recover -> verify
```

The local switch is two env vars (the kit sets them for you):

```bash
export AGENTSERVER_TASKS_BACKEND=local
export AGENTSERVER_DURABLE_ROOT=/tmp/durable   # task + response store
```

There is an equivalent verified kit for the **invocations** durable demo at
[`azure-ai-agentserver-invocations/samples/durable-agent-demo/local/`](azure-ai-agentserver-invocations/samples/durable-agent-demo/local/README.md)
(same `./setup.sh` → `./run.sh` flow).

## Versions

| Wheel | Version |
|-------|---------|
| `azure-ai-agentserver-core` | `2.0.0b7` |
| `azure-ai-agentserver-invocations` | `1.0.0b6` |
| `azure-ai-agentserver-responses` | `1.0.0b8` |

These are unreleased preview (`bN`) builds. To rebuild the wheels from
updated source, see [`wheels/build-wheels.sh`](wheels/build-wheels.sh).
