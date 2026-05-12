# Research: Durable Task Lifecycle Automation & Public API Simplification

**Phase 0 artifact** — Analysis of industry lifecycle patterns and current API gaps.

## Prior Art: Lifecycle Automation

### Temporal (Python SDK)

```python
# Start-or-attach: declare policy, platform handles lifecycle
handle = await client.start_workflow(
    my_workflow.run,
    id="session-123",
    id_conflict_policy=IDConflictPolicy.USE_EXISTING,  # ← key
    task_queue="my-queue",
)

# Send new input to running/suspended workflow
await handle.signal(new_turn_signal, data={"message": "hello"})

# Or use Update-With-Start (atomic)
result = await client.execute_update_with_start_workflow(
    UpdateWithStartWorkflowInput(
        start_workflow_input=StartWorkflowInput(..., id_conflict_policy=USE_EXISTING),
        update_input=StartWorkflowUpdateInput(update="new_turn", args=[data]),
    )
)
```

- **id_conflict_policy** options: `FAIL`, `USE_EXISTING`, `TERMINATE_EXISTING`, `REJECT_DUPLICATE`
- Developer declares policy at start time; Temporal server enforces atomically
- Zero manual status checking — the server decides start vs attach
- Workflow function detects signals via `workflow.wait_condition()` or `@workflow.signal`

### Inngest

```python
@inngest_client.create_function(
    fn_id="my-session",
    trigger=inngest.TriggerEvent(event="session/turn"),
    idempotency="event.data.session_id",  # ← key: same session_id = same function instance
)
async def handle_turn(ctx: inngest.Context, step: inngest.Step):
    # Step memoization: completed steps are skipped on replay
    result = await step.run("process", process_input, data=ctx.event.data)
    # Wait for next turn
    next_event = await step.wait_for_event("next-turn", event="session/turn", timeout="1h")
```

- **Fully automatic**: no start/resume concept — events trigger function, memoization handles replay
- `idempotency` key groups events to the same function execution
- `step.wait_for_event()` suspends and resumes automatically
- Developer writes zero lifecycle code — the framework is fully transparent

### LangGraph Cloud

```python
# Create thread (session)
thread = await client.threads.create()

# Create run (invocation) — platform handles lifecycle
run = await client.runs.create(
    thread_id=thread["thread_id"],
    assistant_id="my-agent",
    input={"message": "hello"},
    multitask_strategy="reject",  # ← what to do if already running
)

# Resume after interrupt — new run on same thread
resume_run = await client.runs.create(
    thread_id=thread["thread_id"],
    assistant_id="my-agent",
    command={"resume": user_response},
)
```

- **multitask_strategy** options: `"reject"`, `"enqueue"`, `"rollback"`, `"interrupt"`
- Thread = session, Run = invocation
- Resume is just a new Run with `command={"resume": value}`
- Graph state persistence is automatic via checkpointer (MemorySaver, PostgresSaver, etc.)
- Developer doesn't check thread state — platform manages it

### Azure Durable Functions (Python SDK)

```python
# Developer MUST manually check status
status = await client.get_status(instance_id)
if status and status.runtime_status in ["Running", "Pending"]:
    raise Exception("Already running")
elif status and status.runtime_status == "Suspended":
    await client.resume(instance_id)
else:
    await client.start_new("my_orchestrator", instance_id, input_data)
```

- **Most verbose**: developer writes all lifecycle branching
- `start_new` silently replaces existing if same instance_id (dangerous!)
- No declarative conflict policy
- This is essentially what our current SDK looks like

## Comparative Analysis

| Capability | Temporal | Inngest | LangGraph Cloud | Durable Functions | Our SDK (current) |
|---|---|---|---|---|---|
| Lifecycle automation | ✅ Declarative policy | ✅ Fully automatic | ✅ Strategy param | ❌ Manual | ❌ Manual |
| Conflict handling | `id_conflict_policy` | `idempotency` key | `multitask_strategy` | Manual check | Manual check |
| Resume mechanism | Signal/Update | `wait_for_event` | New Run with `command` | `resume()` call | `handle_resume()` |
| Developer code lines | ~3 | ~5 | ~3 | ~15 | ~30+ |
| Re-entry context | Workflow history | Step memoization | Thread state | `get_input()` | None (gap!) |

## Current API Gaps

### Gap 1: No lifecycle automation

```python
# Current: 30+ lines of boilerplate in EVERY handler
manager = get_task_manager()
task_id = f"session:{session_id}"
existing = await manager._provider.get(task_id)  # ← private API!

if existing and existing.status == "suspended":
    await manager._provider.patch(task_id, TaskPatchRequest(
        payload={"input": new_data}
    ))
    await manager.handle_resume(task_id)
elif existing and existing.status == "in_progress":
    if is_stale(existing):
        # reconcile...
    else:
        return {"error": "already running"}
elif existing and existing.status == "completed":
    await manager._provider.delete(task_id)
    run = await my_task.start(task_id=task_id, input=data)
else:
    run = await my_task.start(task_id=task_id, input=data)
```

### Gap 2: No re-entry context

```python
# Current: function has no idea why it was called
@durable_task(title="session")
async def handle_session(ctx: TaskContext[dict]) -> dict:
    # Is this fresh? Resumed? Recovered from crash?
    # No way to know! Must guess from external state.
    data = ctx.input
    # ... hope for the best
```

### Gap 3: Private API exposure

```python
# Current: samples import private modules
from azure.ai.agentserver.core.durable._manager import get_task_manager
from azure.ai.agentserver.core.durable._models import TaskPatchRequest

manager = get_task_manager()
existing = await manager._provider.get(task_id)  # ← accessing _provider!
await manager._provider.patch(task_id, TaskPatchRequest(...))  # ← manual!
```

## Design Decision: Deterministic Lifecycle (No Developer-Provided Policy)

Based on the research, we adopt a **deterministic lifecycle** model — simpler than Temporal's configurable policies:

1. **No task exists / pending** → create and start (fresh)
2. **Suspended** → resume with new input
3. **In-progress (not stale)** → throw `TaskConflictError`
4. **In-progress (stale)** → recover automatically
5. **Completed** → throw `TaskConflictError` (no restarting)

Unlike Temporal (`id_conflict_policy`) or LangGraph Cloud (`multitask_strategy`), we don't offer developer-configured policies. The platform always does the right thing. If a developer needs a different composition pattern (e.g., one task per invocation), they use `.start()` / `.run()` directly.

The result: `await my_task.run(task_id="session:s1", input=data)` — one line, zero lifecycle code, zero policy decisions.
