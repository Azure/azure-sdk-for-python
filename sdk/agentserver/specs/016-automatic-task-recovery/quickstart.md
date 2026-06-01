# Quickstart: durable-task primitive (post-spec-016)

A developer-facing tour of the rewritten contract. After this spec lands, the following patterns are the prescribed shapes; the developer guide (`docs/durable-task-guide.md`) is the authoritative source.

## Define a steerable, time-bounded handler

```python
from datetime import timedelta
from azure.ai.agentserver.core.durable import task

@task(steerable=True, timeout=timedelta(seconds=30))
async def chat_turn(ctx) -> str:
    # 1. Restore prior turn's state from durable metadata.
    history = ctx.metadata.get("history", [])
    history.append({"role": "user", "content": ctx.input})

    # 2. Do work, periodically checkpointing + checking for cancellation.
    response_chunks = []
    async for chunk in llm.stream(history):
        if ctx.cancel.is_set():
            break
        response_chunks.append(chunk)

    response = "".join(response_chunks)
    history.append({"role": "assistant", "content": response})
    ctx.metadata["history"] = history

    # 3. Suspend so the next turn can resume with new input.
    return await ctx.suspend(output=response)
```

That's the whole pattern. No recovery knob to configure, no force-stop API, no superseded status to branch on.

## React to cancellation

`ctx.cancel.is_set() == True` means "stop". If the handler wants to know *why* — to vary strategy or terminal action — it inspects the independent cause state on `ctx`:

```python
if ctx.cancel.is_set():
    if ctx.cancel_requested:
        # Operator called TaskRun.cancel(). Commit current work and exit.
        await ctx.metadata.flush()
        return await ctx.suspend(output=partial_response)
    if ctx.timeout_exceeded:
        # Deadline blown. Decide: suspend (allow retry) or raise (give up).
        return await ctx.suspend(output=partial_response, reason="deadline")
    if ctx.pending_input_count > 0:
        # Steering pressure. Wind down to a safe checkpoint and yield.
        if ctx.pending_input_count > 2:
            return await ctx.suspend(output=partial_response)  # rapid-drain mode
        # Or: just let the current turn finish naturally — both are valid.
```

The booleans accumulate. A handler that experienced steering → then timeout → then explicit cancel sees ALL THREE `True` at the next checkpoint.

## React to shutdown (restore on restart)

`ctx.shutdown` is a SEPARATE signal from `ctx.cancel`. When the container is shutting down (SIGTERM), the handler should preserve the task `in_progress` so the next process picks it up and re-enters with `ctx.entry_mode == "recovered"`:

```python
if ctx.shutdown.is_set():
    await ctx.metadata.flush()
    return await ctx.exit_for_recovery()  # framework leaves status=in_progress
```

`ctx.exit_for_recovery()` takes no parameters and is only callable when `ctx.shutdown.is_set()` is true (else it raises `RuntimeError` at the call site — misuse cannot accidentally leave a task `in_progress`).

## Handle recovery on re-entry

```python
@task(timeout=timedelta(seconds=30))
async def long_running(ctx):
    if ctx.entry_mode == "recovered":
        # Previous lifetime died mid-turn. Resume from the last checkpoint.
        progress = ctx.metadata.get("progress", {"done": 0, "total": 100})
    else:
        progress = {"done": 0, "total": 100}

    while progress["done"] < progress["total"] and not ctx.cancel.is_set():
        await do_one_step()
        progress["done"] += 1
        ctx.metadata["progress"] = progress
        await ctx.metadata.flush()  # fence before next iteration's side-effect

    return progress
```

The handler must be idempotent on recovery — that's the only thing the developer owes the framework. Recovery itself is automatic.

## Steering: it's multi-turn with a queue

A second caller can call `.start(task_id, input=new_input)` while turn 1 is running. The framework queues `new_input`, drains it when turn 1 suspends, and re-enters the handler. Caller 1 sees the natural `TaskResult(status="suspended", output=X)` for whatever the handler emitted; caller 2 sees the natural outcome of turn 2.

If turn 1 instead terminates (return or raise), the task is terminal and caller 2's future raises `TaskConflictError` — identical to a fresh `.start()` against an already-terminal task. There's no special "superseded" status to branch on.

## Cancel a running task

```python
await run.cancel()  # cooperative; handler chooses how to react
```

`TaskRun.cancel()` is the only "stop this task" API. There is no `.terminate()`. To force a failure terminal, write the handler to raise on `ctx.cancel.is_set()` — the handler chooses the terminal shape.

## What changed from the prior pre-release

If you were testing against an earlier pre-release on the same branch:

- `stale_timeout` no longer exists on `@task` / `Task.options` / `TaskOptions` / `TaskContext`. Recovery is automatic.
- `TaskResult.status` is `"completed" | "suspended"` only. `"superseded"` is gone; `is_superseded` is gone.
- `TaskRun.terminate()` is gone; `TaskTerminated` is no longer importable. Use `.cancel()` and decide the terminal shape in the handler.
- `ctx.pending_inputs` (Sequence) → `ctx.pending_input_count` (int, live).
- `ctx.was_steered` → `ctx.is_steered_turn` (semantically fixed: True ONLY when the current invocation is a drain re-entry).
- `ctx.steering_generation` removed from the public surface.
- New: `ctx.timeout_exceeded`, `ctx.cancel_requested`, `ctx.exit_for_recovery()`.
- `@task(timeout=...)` is now per-turn / wall-clock / durable; the per-turn budget persists across crashes within the turn.

## Where to read more

- `docs/durable-task-guide.md` — full developer guide.
- `specs/016-automatic-task-recovery/spec.md` — the locked-in contract.
- `specs/016-automatic-task-recovery/research.md` — the design decisions with rationale and alternatives.
