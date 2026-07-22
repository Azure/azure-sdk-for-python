---
name: agentserver-resilient-tasks
description: 'Build crash-resilient long-running agent handlers using the `@task` primitive from `azure-ai-agentserver-core`. WHEN: "make my agent crash-resilient", "resume after restart", "long-running agent (>15 min)", "steer / interrupt a running agent turn", "multi-turn conversation that survives container restarts", "hosted agent that needs lease + checkpoint recovery", "agent with cancel / cooperative shutdown", "pass large inputs up to 2 MB to a task (function or steering inputs)". DO NOT USE FOR: persisting conversation history (use LangGraph / your DB), storing large checkpoints (`ctx.metadata` is intentionally small — watermarks only), workflow orchestration (use Temporal), or competing-consumer queues. PRIVATE PREVIEW: the `@task` primitive ships only via pre-release wheels checked into this branch (see references); the surrounding `azure-ai-agentserver-*` packages are on PyPI at stable versions.'
---

# Agentserver Resilient Tasks (`@task`) — Standalone Skill

> **Standalone document.** Copy this file into your project to give your
> AI coding agent (GitHub Copilot, etc.) the context it needs to use the
> `@task` primitive correctly. Pair it with the checked-in pre-release
> wheels (see *Packaging* below) — that's all your project needs to start
> building resilient agents.

The `@task` decorator in `azure-ai-agentserver-core.tasks` turns a single
agent function into a **crash-resilient, steerable, long-running** primitive
backed by a hosted task store. The framework handles lease acquisition,
recovery from container restarts, checkpoint metadata persistence, and
cooperative cancel — the handler stays simple.

## When to use

Use `@task` when **any** of these apply:

- The agent run lasts long enough that container reclaim / crash is a real
  risk and a "restart from scratch" recovery is too expensive.
- You need **steering** — a new user input arriving mid-turn should
  cooperatively wind down the current turn and re-enter with the new
  input (instead of stacking turns).
- You need **multi-turn conversations that survive restarts** — turn N+1
  must resume the persisted state of turn N even if the container died
  between them.
- The agent is **hosted** (e.g., Foundry Hosted Agent) and you want the
  platform's lease-renewal keep-alive path to extend the sandbox idle
  timer past the eviction window.

## When NOT to use

`@task` is intentionally narrow. Do **not** use it for:

- **Conversation history persistence.** `ctx.metadata` is *not* a chat
  log store — it's for small watermarks and dedup tokens (max ~tens of
  KB). Persist messages, tool outputs, and large state through your
  agent framework's native store (LangGraph `SqliteSaver`, your own DB,
  etc.). The two are complementary: `@task` provides the *resilient
  outer boundary*; your framework provides the *content store*.
- **Large checkpoint state.** Same reason. If you want to snapshot
  20 MB of intermediate computation between checkpoints, write it to
  your own storage and put only a pointer (object ID, URL) in
  `ctx.metadata`.
- **Workflow orchestration.** Fan-out/fan-in, child workflows, signals,
  timers as first-class primitives → use Temporal.
  `@task` is the thin resilient boundary around a *single* agent function;
  it can live *inside* such an engine but doesn't replace it.
- **Competing-consumer queues.** A `task_id` identifies one logical
  unit of work owned by one current lifetime. If you want N workers
  pulling jobs off a shared queue, use a queue.
- **Deterministic replay.** `@task` is not Temporal-style replay. After
  a crash the handler re-runs from the top with whatever state survived;
  determinism inside the handler is the developer's responsibility. The
  "at-most-once side effect" pattern below covers the standard case.

## Minimal pattern

```python
from azure.ai.agentserver.core.tasks import task, TaskContext

@task(name="my_agent", steerable=True)
async def my_agent(ctx: TaskContext[dict]) -> dict:
    topic = ctx.input["topic"]

    # ctx.metadata is small, resilient, survives crashes
    completed = ctx.metadata.get("completed_phases", 0)
    results: list = ctx.metadata.get("results", [])

    if ctx.entry_mode == "recovered":
        # we crashed mid-run; resume from last checkpoint
        await emit_recovered_marker(completed)

    for phase_idx in range(completed, TOTAL_PHASES):
        if ctx.cancel.is_set():
            # steering arrived (or operator cancelled) — wind down
            return await _wind_down(ctx, phase_idx, results)

        result = await do_one_phase(topic, phase_idx)
        results.append(result)

        # === CHECKPOINT ===
        ctx.metadata["completed_phases"] = phase_idx + 1
        ctx.metadata["results"] = results  # keep small!
        await ctx.metadata.flush()

    return {"phases_completed": TOTAL_PHASES, "results": results}
```

**Dispatching** from your HTTP handler:

```python
from azure.ai.agentserver.core.tasks import TaskConflictError

# One resilient task per session — steering finds the active run.
try:
    await my_agent.start(task_id=session_id, input={"topic": topic})
    status = "started"
except TaskConflictError:
    # Already active + steerable → framework queued our input as a
    # steering signal; current turn winds down at next checkpoint.
    status = "steered"
```

**Streaming** progress back to a (re)connecting client:

```python
from azure.ai.agentserver.core.streaming import streams

# Producer (inside the handler) emits to a process-level stream id
# (typically the per-turn invocation id from the handler's input):
#     stream = await streams.get_or_create(invocation_id)
#     await stream.emit({"event": "progress", "step": "fetch"})
#     ...
#     await stream.close()

# Consumer (HTTP layer) attaches BEFORE starting the task:
stream = await streams.get_or_create(invocation_id)
run = await my_agent.start(task_id=session_id,
                            input={"invocation_id": invocation_id, ...})
async for ev in stream.subscribe(after=0):
    yield f"data: {ev}\n\n"
result = await run.result()  # TaskRun is awaitable; awaits result()
```

## Pick the right metadata

Rule of thumb: **store the smallest watermark that lets you resume
correctly**. If you can derive everything else by re-running the
non-side-effectful part of the handler, do that.

| Good in `ctx.metadata` | Bad in `ctx.metadata` |
|---|---|
| `"completed_phases": 7` | Full chat transcript |
| `"last_input_id": "msg_..."` | Generated artifacts (KBs+) |
| `"output_store_key": "s3://..."` (a pointer) | The thing the pointer points to |
| `"dedup_token": "uuid-abc"` | Vector embeddings |

Always call `await ctx.metadata.flush()` at the end of a checkpoint
boundary. That's the persistence point — a crash before flush
re-runs the phase; a crash after flush skips it.

## Hosted vs local

In hosted environments (`FOUNDRY_HOSTING_ENVIRONMENT` set by the platform)
`@task` uses the HTTP-backed `HostedTaskProvider` against the Foundry
task-storage API automatically — no opt-in env var required.

In local development (no `FOUNDRY_HOSTING_ENVIRONMENT`) `@task` uses
`LocalFileTaskProvider` rooted at `${AGENTSERVER_STATE_ROOT:-~/.agentserver}/tasks/`
(override the root with `AGENTSERVER_STATE_ROOT`). No service dependency for
local iteration. To force the local backend even when hosted-detection would
otherwise pick the hosted provider, set `AGENTSERVER_TASKS_BACKEND=local`.

## Packaging — private preview wheels

The surrounding `azure-ai-agentserver-core` and
`azure-ai-agentserver-invocations` packages are published on PyPI at
stable versions. **The `@task` resilient primitive is in private preview**
and ships *only* via the pre-release wheels checked into this branch.
There is no PyPI release for the `@task` API until it goes GA — installing
the regular PyPI version of `azure-ai-agentserver-core` will not give you
`azure.ai.agentserver.core.tasks`.

Consume the checked-in wheels per:

- Wheel directory + README: [`sdk/agentserver/wheels/`](https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/agentserver/wheels)

## Authoritative references

| Topic | Link |
|---|---|
| **Full developer guide** (mental model, lifecycle, API reference, patterns) | [`docs/tasks-guide.md`](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/agentserver/azure-ai-agentserver-core/docs/tasks-guide.md) |
| **Streaming developer guide** (registry API, backings, per-turn id convention, exception/wire mapping) | [`docs/streaming-guide.md`](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/agentserver/azure-ai-agentserver-core/docs/streaming-guide.md) |
| Minimal retry sample | [`samples/resilient_retry/resilient_retry.py`](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/agentserver/azure-ai-agentserver-core/samples/resilient_retry/resilient_retry.py) |
| Streaming via the `streams` registry | [`samples/resilient_streaming/resilient_streaming.py`](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/agentserver/azure-ai-agentserver-core/samples/resilient_streaming/resilient_streaming.py) |
| End-to-end **long-running + crash + steer** demo (Foundry hosted) | [`samples/resilient-agent-demo/`](https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/agentserver/azure-ai-agentserver-invocations/samples/resilient-agent-demo) |
| Multi-turn (suspend / resume) | [`samples/resilient_multiturn/`](https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/agentserver/azure-ai-agentserver-invocations/samples/resilient_multiturn) |
| LangGraph integration | [`samples/resilient_langgraph/`](https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/agentserver/azure-ai-agentserver-invocations/samples/resilient_langgraph) |

Read the developer guide first — it covers `EntryMode`, retry semantics,
multi-turn suspend/resume, steering queue backpressure, cancel-cause booleans
(`timeout_exceeded`, `cancel_requested`, `pending_input_count`), shutdown
via `ctx.exit_for_recovery()`, and the patterns referenced above. The
samples ground the API in working code.

## Decision shortcuts

| Need | Use `@task`? | Why |
|---|---|---|
| Multi-turn chat that survives container restart | ✅ | Lease + recovery + checkpoint metadata |
| Steerable long generation (user can change topic mid-run) | ✅ | `steerable=True` + `ctx.cancel.is_set()` |
| Single short-lived (<30s) request/response | ❌ | Overkill — just write a normal handler |
| Persist 100 MB of intermediate artifacts | ❌ | Use your own object store; put the pointer in metadata |
| Pull jobs off a shared queue across N workers | ❌ | Wrong primitive — use a queue |
| Fan-out 10 child workflows and join | ❌ | Use Temporal |
| Want exactly-once side effects | ⚠️ | Use the at-most-once pattern in the guide; framework provides at-most-once via dedup token, not exactly-once |
