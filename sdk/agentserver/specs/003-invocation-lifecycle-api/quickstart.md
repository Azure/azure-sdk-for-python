# Quickstart: Durable Task Lifecycle Automation & Public API Simplification

**Phase 1 artifact** — Usage examples showing the before/after API simplification.

## 1. Lifecycle-Managed Multi-Turn Session

The `.run()` and `.start()` methods are lifecycle-aware — they handle start, resume, and recovery automatically.

```python
from azure.ai.agentserver.core.durable import durable_task, TaskContext

@durable_task(title="chat-session")
async def chat_session(ctx: TaskContext[dict]) -> dict:
    """A multi-turn chat session. Called from scratch each turn."""

    if ctx.entry_mode == "fresh":
        # First turn — initialize session state
        history = []
    elif ctx.entry_mode == "resumed":
        # Subsequent turn — load state from checkpoint
        history = load_checkpoint(ctx.session_id)
    elif ctx.entry_mode == "recovered":
        # Crash recovery — reconcile state
        history = load_checkpoint(ctx.session_id) or []

    # Process this turn
    user_message = ctx.input["message"]
    history.append({"role": "user", "content": user_message})
    reply = await generate_reply(history)
    history.append({"role": "assistant", "content": reply})

    # Save checkpoint
    save_checkpoint(ctx.session_id, history)

    # Suspend — wait for next turn
    return await ctx.suspend(output={"reply": reply})
```

### Calling from an invocation handler

```python
@app.invoke_handler
async def handle_invoke(request):
    session_id = request.state.session_id
    data = await request.json()
    task_id = f"session:{session_id}"

    try:
        output = await chat_session.run(task_id=task_id, input=data)
    except TaskSuspended as e:
        return e.output  # {"reply": "..."}
```

**That's it.** No manual status checking, no `manager._provider.get()`, no `TaskPatchRequest`, no `handle_resume()`. The platform handles start/resume/recover internally.

## 2. Entry Mode Branching

The developer can optionally check `ctx.entry_mode` to handle different lifecycle paths:

```python
@durable_task(title="stateful-workflow")
async def my_workflow(ctx: TaskContext[dict]) -> dict:
    match ctx.entry_mode:
        case "fresh":
            # Initialize resources, create DB records, etc.
            state = initialize_state(ctx.input)
        case "resumed":
            # Load existing state, process new input
            state = load_state(ctx.session_id)
            state.process(ctx.input)
        case "recovered":
            # Crash recovery — check what completed, clean up partial work
            state = recover_state(ctx.session_id)
            state.reconcile()

    # Continue with common logic...
    result = await do_work(state)
    save_state(ctx.session_id, state)
    return await ctx.suspend(output=result)
```

**Important**: Checking `entry_mode` is optional. If you don't check it, the function works fine — it just doesn't distinguish between entry paths.

## 3. Deterministic Lifecycle Behavior

The platform follows deterministic rules — no developer configuration needed:

| Task Status | `.run()` / `.start()` Behavior |
|---|---|
| No task exists | Create and start (fresh) |
| `pending` | Start it (fresh) |
| `suspended` | Resume with new input |
| `in_progress` (not stale) | Throw `TaskConflictError` |
| `in_progress` (stale) | Recover automatically |
| `completed` | Throw `TaskConflictError` |

### Handling conflicts

```python
from azure.ai.agentserver.core.durable import TaskConflictError

try:
    output = await my_task.run(task_id="session:s1", input=data)
except TaskConflictError as e:
    # e.task_id, e.current_status
    if e.current_status == "in_progress":
        return {"error": f"Task {e.task_id} is already running"}
    elif e.current_status == "completed":
        return {"error": f"Task {e.task_id} is completed — use a new task_id"}
```

## 4. Querying Task Info

Query the full persisted task info without lifecycle side effects:

```python
# Returns TaskInfo or None — works for any task state
info = await my_task.get(task_id="session:s1")
if info is None:
    print("No such task")
elif info.status == "suspended":
    print("Waiting for next turn")
elif info.status == "in_progress":
    print("Currently processing")
elif info.status == "completed":
    print("Done")
```

## 5. LangGraph Integration (Sample Pattern)

Using the new API with real LangGraph — the handler is under 10 lines:

```python
from azure.ai.agentserver.core.durable import durable_task, TaskContext
from langgraph.graph import StateGraph
from langgraph.checkpoint.sqlite import SqliteSaver

# Build graph (app-level setup)
graph = build_my_graph()
checkpointer = SqliteSaver.from_conn_string("~/.sessions/checkpoints.db")
compiled = graph.compile(checkpointer=checkpointer, interrupt_before=["human_input"])

@durable_task(title="langgraph-session")
async def langgraph_session(ctx: TaskContext[dict]) -> dict:
    config = {"configurable": {"thread_id": ctx.session_id}}

    if ctx.entry_mode == "fresh":
        result = compiled.invoke(ctx.input, config)
    else:
        # Resume or recover — graph state is in SQLite
        from langgraph.types import Command
        result = compiled.invoke(Command(resume=ctx.input["message"]), config)

    # Check if graph is waiting for human input
    state = compiled.get_state(config)
    if state.next:
        return await ctx.suspend(output={"reply": result["messages"][-1].content})
    return result

# Handler: ~5 lines
@app.invoke_handler
async def handle(request):
    data = await request.json()
    task_id = f"session:{request.state.session_id}"
    try:
        output = await langgraph_session.run(task_id=task_id, input=data)
        return output
    except TaskSuspended as e:
        return e.output
```

## 6. Composition Patterns

The `.run()` and `.start()` methods support the sticky session pattern shown above, but it's just ONE of many ways to compose durable tasks:

```python
# Pattern A: One task per invocation (stateless)
@app.invoke_handler
async def stateless_handler(request):
    data = await request.json()
    result = await my_task.run(task_id=f"inv:{request.state.invocation_id}", input=data)
    return {"result": result}

# Pattern B: Sticky session (multi-turn)
@app.invoke_handler
async def session_handler(request):
    task_id = f"session:{request.state.session_id}"
    try:
        output = await my_task.run(task_id=task_id, input=data)
        return output
    except TaskSuspended as e:
        return e.output

# Pattern C: Fan-out (multiple background tasks per invocation)
@app.invoke_handler
async def fanout_handler(request):
    data = await request.json()
    runs = [
        await search_task.start(task_id=f"search:{i}", input=query)
        for i, query in enumerate(data["queries"])
    ]
    results = [await r.result() for r in runs]
    return {"results": results}
```

**The core provides primitives. Developers compose them freely.**

## 7. Stale Task Recovery

Configure how long before an `in_progress` task is considered stale:

```python
# Default: 300 seconds (5 minutes)
output = await my_task.run(task_id="session:s1", input=data)

# Custom timeout for long-running tasks
output = await my_task.run(task_id="session:s1", input=data, stale_timeout=900.0)  # 15 minutes
```

When a stale task is detected, `.run()`/`.start()` recovers it automatically. The function is re-entered with `ctx.entry_mode == "recovered"`.
