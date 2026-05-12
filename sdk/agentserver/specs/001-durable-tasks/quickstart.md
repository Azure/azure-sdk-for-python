# Quickstart: Durable Tasks for Long-Running Agents

This guide walks through building a crash-resilient agent using the `@durable_task` decorator.

---

## 1. Define a Durable Task

```python
from pydantic import BaseModel
from azure.ai.agentserver.core.durable import durable_task, TaskContext


class ResearchInput(BaseModel):
    query: str
    max_steps: int = 10


class ResearchOutput(BaseModel):
    answer: str
    sources: list[str]


@durable_task
async def research(ctx: TaskContext[ResearchInput]) -> ResearchOutput:
    """Multi-step research task that survives crashes."""
    ctx.metadata.set("phase", "searching")

    # Your business logic here
    sources = await search_web(ctx.input.query)
    ctx.metadata.set("phase", "synthesizing")
    ctx.metadata.set("sources_found", len(sources))

    answer = await synthesize(sources, ctx.input.query)

    return ResearchOutput(answer=answer, sources=sources)
```

---

## 2. Run the Task (Invoke-and-Wait)

```python
result = await research.run(
    task_id="research-q1-revenue",
    input=ResearchInput(query="Q1 revenue trends", max_steps=5),
)
print(result.answer)
```

---

## 3. Start the Task (Fire-and-Forget)

```python
handle = await research.start(
    task_id="research-q1-revenue",
    input=ResearchInput(query="Q1 revenue trends"),
)
print(f"Task started: {handle.task_id}")

# Later...
result = await handle.result()
```

---

## 4. Suspend and Resume (Human-in-the-Loop)

```python
from azure.ai.agentserver.core.durable import Suspended


class ApprovalInput(BaseModel):
    draft: str
    reviewer: str


@durable_task(ephemeral=False)
async def review_draft(ctx: TaskContext[ApprovalInput]) -> str:
    """Submit a draft for human review, suspend until approved."""

    # On first run: submit for review and suspend
    if ctx.lease_generation == 0:
        await notify_reviewer(ctx.input.reviewer, ctx.input.draft)
        return await ctx.suspend(reason="awaiting reviewer approval")

    # On resume: reviewer has approved
    return f"Approved by {ctx.input.reviewer}"
```

The task suspends and releases resources. When the reviewer approves,
an external system sends `POST /tasks/resume` with the task ID, and
the framework re-enters the function.

---

## 5. Graceful Shutdown Handling

```python
@durable_task
async def long_running(ctx: TaskContext[MyInput]) -> MyOutput:
    for step in range(100):
        # Check if the container is shutting down
        if ctx.shutdown.is_set():
            ctx.metadata.set("checkpoint_step", step)
            return await ctx.suspend(reason="container shutting down")

        await do_step(step)

    return MyOutput(...)
```

On SIGTERM, the framework signals `ctx.shutdown`. The function can
checkpoint and suspend cleanly. The task will be recovered on the
next container startup.

---

## 6. Per-Call Overrides

```python
# Override defaults for a specific call
result = await research \
    .options(timeout=timedelta(hours=2), ephemeral=False) \
    .run(task_id="big-research", input=ResearchInput(query="..."))
```

---

## 7. Local Development

No special configuration needed. When `FOUNDRY_HOSTING_ENVIRONMENT`
is not set, the framework automatically uses a local filesystem
provider. Tasks are stored as JSON files under `$HOME/.durable-tasks/`.

```bash
# Run your agent locally — full durable task lifecycle works
python -m my_agent

# Kill the process mid-execution
# Restart — stale tasks are automatically recovered
python -m my_agent
```

---

## 8. Crash Recovery

Recovery is automatic. On startup, the framework:

1. Queries owned tasks in `in_progress` status
2. Identifies stale tasks (same `lease_owner`, different `lease_instance_id`)
3. Reclaims the lease (increments `lease_generation`)
4. Dispatches the function to the resume callback

The developer sees `ctx.lease_generation > 0` on recovery, and can
use this to decide whether to restart from scratch or resume from
a checkpoint stored in `ctx.metadata`.
