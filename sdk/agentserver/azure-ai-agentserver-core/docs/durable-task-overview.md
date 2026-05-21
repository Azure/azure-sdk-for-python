# Durable Tasks: Crash-Resilient Long-Running Agents

## The Problem

Agent workloads run for minutes to hours — multi-step reasoning, tool loops, batch processing, multi-turn conversations with human-in-the-loop pauses. The sandbox hosting that work can crash, be OOM-killed, redeployed, or idle-deactivated at any time — and most failure modes are unannounced.

```
┌─────────────────────────────────────────────────────────┐
│  Agent starts a 45-minute research task...              │
│                                                         │
│  ██████████████░░░░░░░░░░░░░░░░  35% complete          │
│                     ▲                                   │
│                     │  💥 Sandbox crash / OOM / redeploy │
│                                                         │
│  Result: All progress lost. User must restart.          │
└─────────────────────────────────────────────────────────┘
```

Without a contract for *what's running and where*, the platform can't restart the right thing, and the developer can't recover their work.

---

## What We're Solving

Most agent frameworks already provide durability for state *between* turns (LangGraph checkpointers, Semantic Kernel, Temporal, etc.). What **none** of them solve is the **entrypoint**:

- Who calls the framework when the sandbox starts back up after a crash?
- Who knows there *was* a crash?
- Who tells the platform a unit of work is still in flight so the sandbox doesn't get killed?

**That's the gap `@durable_task` closes.** It wraps a durable boundary around the developer's agent function — a unit of work the platform can see, lease, restart, and resume — so whatever framework is underneath has somewhere to plug in.

---

## The Solution: One Decorator

```python
from azure.ai.agentserver.core.durable import durable_task

@durable_task(name="research-agent")
async def research(ctx, query: str) -> str:
    # This function survives crashes. The framework handles everything.
    results = await do_research(query)
    await ctx.stream(f"Found {len(results)} sources")
    report = await synthesize(results)
    return report
```

The framework handles persistence, crash recovery, streaming, and lifecycle — your code focuses purely on agent logic.

---

## Architecture

### System Layers

The system is structured in three layers, each specified independently:

```
┌─────────────────────────────────────────────────────────────────────┐
│  Layer 1: Developer API                                              │
│  @durable_task decorator + TaskContext                                │
│  (What agent developers write)                                       │
├─────────────────────────────────────────────────────────────────────┤
│  Layer 2: Sandbox Runtime Contract                                   │
│  Startup recovery, lease management, graceful shutdown                │
│  (What the SDK manages automatically)                                │
├─────────────────────────────────────────────────────────────────────┤
│  Layer 3: Foundry Task Storage Protocol                              │
│  CRUDL HTTP API + lease model                                        │
│  (Platform-managed service, always available)                        │
└─────────────────────────────────────────────────────────────────────┘
```

### How the Parts Interact

```
┌───────────────────────────────────────────────────────────────────────┐
│                          Hosted Agent Sandbox                          │
│                                                                       │
│  ┌──────────────┐    ┌───────────────────────┐    ┌───────────────┐  │
│  │  Protocol     │    │  Durable Task         │    │  Developer's  │  │
│  │  Layer        │───▶│  Runtime              │───▶│  Agent        │  │
│  │  (Invocations │    │                       │    │  Function     │  │
│  │   / Responses)│    │  • Lease management   │    │               │  │
│  └──────────────┘    │  • State persistence  │    │  @durable_task│  │
│                       │  • Crash detection    │    └───────────────┘  │
│                       │  • Stream relay       │                       │
│                       └───────────┬───────────┘                       │
│                                   │                                   │
└───────────────────────────────────┼───────────────────────────────────┘
                                    │ HTTP
                       ┌────────────▼────────────────┐
                       │  Foundry Task Storage API    │
                       │  (Platform-managed)          │
                       │                              │
                       │  • CRUDL over task records   │
                       │  • Lease-based ownership     │
                       │  • Dual-identity model       │
                       │  • Optimistic concurrency    │
                       └──────────────────────────────┘
```

### The Lease Model

The lease is the core mechanism that makes crash recovery possible. It answers: **"Is this task still being actively worked on?"**

```
┌──────────────────────────────────────────────────────────────────┐
│                         Lease Lifecycle                            │
│                                                                   │
│   Sandbox A acquires lease              Lease renewed every N sec │
│   ┌─────┐                               ┌─────┐                 │
│   │START│──── acquire ────▶ HELD ◀──────│RENEW│                  │
│   └─────┘                    │           └─────┘                 │
│                              │                                    │
│                    💥 crash (no renewal)                           │
│                              │                                    │
│                              ▼                                    │
│                          EXPIRED  ◀── lease_duration elapsed      │
│                              │                                    │
│                              │  Sandbox B detects expired lease   │
│                              ▼                                    │
│                     RE-ACQUIRED by Sandbox B                      │
│                     (generation counter++)                        │
└──────────────────────────────────────────────────────────────────┘
```

While the function runs, the framework renews the lease in the background. If the sandbox dies, renewals stop. The lease expires. The next sandbox instance detects the expired lease and re-enters the function — that's crash recovery.

---

## The Lifecycle: Start → Crash → Recover

```
 Sandbox A                             Sandbox B (after crash)
 ──────────                            ────────────────────────

 ① CREATE & START                      ④ DETECT & RECOVER
 ┌──────────────────┐                  ┌──────────────────────┐
 │ POST task to store│                  │ On startup: query    │
 │ Acquire lease     │                  │ tasks with expired   │
 │ Persist input     │                  │ leases (dual-identity│
 │ Enter function    │                  │ match)               │
 │ entry_mode="fresh"│                  │ Re-acquire lease     │
 └────────┬─────────┘                  │ generation++         │
          │                            └──────────┬───────────┘
          ▼                                       ▼
 ② EXECUTE                             ⑤ RE-ENTER FUNCTION
 ┌──────────────────┐                  ┌──────────────────────┐
 │ Run agent logic   │                  │ entry_mode="recovered"│
 │ ctx.stream(chunk) │                  │ Same input + metadata │
 │ ctx.metadata[k]=v │                  │ Developer branches on │
 │ Lease renewed     │◀── heartbeat    │ entry_mode to skip    │
 │  automatically    │                  │ completed steps       │
 └────────┬─────────┘                  └──────────┬───────────┘
          │                                       ▼
          ▼                            ⑥ COMPLETE
 ③ CRASH 💥                            ┌──────────────────────┐
 ┌──────────────────┐                  │ return output         │
 │ Sandbox dies      │                  │ Release lease         │
 │ Lease stops       │                  │ Delete task (ephemeral│
 │  renewing         │                  │  =True) or mark done  │
 │ Task remains in   │                  │ Notify consumers      │
 │  storage (safe)   │                  └──────────────────────┘
 └──────────────────┘
```

---

## Four State Buckets

The framework splits task state into four clear buckets — not one opaque payload:

```
┌─ Task Record (live, in Foundry Task Storage) ─────────────────────┐
│                                                                    │
│   INPUT        immutable, set at start                             │
│                typed model passed to ctx.input                     │
│                                                                    │
│   METADATA     mutable progress dict                               │
│                ctx.metadata["phase"] = "reasoning"                 │
│                debounced flush to store                             │
│                                                                    │
│   OUTPUT       written on suspend (snapshot for observers)         │
│                on success: in-process delivery (ephemeral=True)    │
│                            or persisted (ephemeral=False)          │
│                                                                    │
│   ERROR        structured failure detail                           │
│                {type, message, traceback}                          │
│                                                                    │
├────────────────────────────────────────────────────────────────────┤
│   STREAM       NOT on the task record                              │
│                Real-time relay: ctx.stream() → async for chunk     │
│                Pass-through, not persisted                         │
└────────────────────────────────────────────────────────────────────┘
```

---

## Developer Experience

### Before: Fragile Long-Running Agent

```python
@app.invoke_handler
async def research(request):
    query = (await request.json())["query"]
    results = await search(query)          # 10 minutes...
    report = await synthesize(results)     # 💥 crash = all lost
    return JSONResponse({"report": report})
```

### After: Crash-Resilient with One Decorator

```python
@durable_task(name="research-agent")
async def research(ctx, query: str) -> str:
    if ctx.entry_mode == "recovered":
        # Framework tells you this is a recovery
        step = ctx.metadata.get("step", "search")
        if step == "synthesize":
            return await synthesize_from_cache(ctx.task_id)

    results = await search(query)
    ctx.metadata["step"] = "synthesize"

    report = await synthesize(results)
    return report
```

### Starting and Consuming

```python
# Fire-and-forget — returns immediately with a handle
run = await research.start(task_id="inv-123", input="quantum computing")

# Stream incremental output (real-time, while function is running)
async for chunk in run:
    print(chunk)

# Get final result (blocks until terminal exit)
result = await run.result()
print(result.output)
```

---

## Key Patterns

### 1. Multi-Turn Agents (Suspend & Resume)

The function suspends when it needs external input, then resumes with new data:

```
 User              Framework              Agent Function
  │                    │                       │
  │── "plan trip" ────▶│── start ─────────────▶│ entry_mode="fresh"
  │                    │                       │── do research...
  │                    │◀── ctx.suspend() ─────│ reason="need_approval"
  │◀── "here's plan" ─│                       │
  │                    │      (task: suspended, lease released)
  │                    │
  │── "approved" ─────▶│── start (same ID) ───▶│ entry_mode="resumed"
  │                    │                       │── execute plan...
  │◀── "done!" ────────│◀── return result ─────│
```

### 2. Streaming Progress

```
 Consumer                 Framework              Agent Function
    │                        │                       │
    │── async for chunk ────▶│                       │
    │                        │◀── ctx.stream("10%") ─│
    │◀── "10%" ─────────────│                       │
    │                        │◀── ctx.stream("50%") ─│
    │◀── "50%" ─────────────│                       │
    │                        │◀── ctx.stream("done")─│
    │◀── "done" ────────────│                       │
    │◀── StopAsyncIteration ─│◀── return output ────│
```

Streams are **real-time relay** — not persisted. Late-joining consumers pick up from the next live chunk. For durable replay, the developer writes chunks to their own store.

### 3. Steering (Mid-Flight Redirect)

For chat agents where a new user message should redirect the agent without waiting for the current response to finish:

```
 Time ──────────────────────────────────────────────────────────────▶

 User sends "Tell me about Python"
 │
 ▼
 [gen 0: running ████████── ctx.cancel fires ──│ suspend]
                     ▲                          │
                     │                          ▼
 User sends "Actually, tell me about Rust"   [gen 1: running ████ ✓]
                                                        ▲
                                           ctx.was_steered = True
                                           ctx.previous_input = "...Python"
```

The framework atomically queues the new input, signals cancel, and re-enters with the next input. No manual orchestration needed.

### 4. Crash Recovery (Transparent)

```
 Time ────────────────────────────────────────────────────────────────▶

 Sandbox A:  [███ running ██████ 💥 dies]
                                   │
                             lease expires (~60s)
                                   │
 Sandbox B:           [startup ────┤── recover ──── running ──── ✓ ]
                                   │
                             entry_mode = "recovered"
                             Same input + metadata intact
                             generation++ (observable via ctx)
```

---

## What the Framework Manages

| Concern | What the Framework Does | Developer Writes |
|---------|------------------------|-----------------|
| **Crash recovery** | Detects expired leases on startup, re-acquires, re-enters function | Branch on `ctx.entry_mode` for idempotency |
| **Lease renewal** | Background heartbeat keeps the lease alive while function runs | Nothing — automatic |
| **State persistence** | Input persisted at start, metadata flushed on debounce | `ctx.metadata["key"] = value` |
| **Streaming** | Real-time relay from `ctx.stream()` to handle iterators | `await ctx.stream(chunk)` |
| **Suspend/Resume** | PATCH status, release lease, re-enter on next `start()` | `return await ctx.suspend(...)` |
| **Cancellation** | Sets `ctx.cancel` event; waits for cooperative exit | Check `ctx.cancel.is_set()` at break points |
| **Graceful shutdown** | Sets `ctx.shutdown`; waits grace period; force-expires lease | Optionally checkpoint on `ctx.shutdown` |
| **Retry** | Re-enters function with `ctx.run_attempt++` on retryable errors | Configure `retry=RetryPolicy.exponential_backoff(...)` |
| **Source stamping** | Auto-stamps `type`, `name`, `server_version` on every task | Nothing — used for recovery routing |
| **Task listing** | Scoped by function name via auto-stamped tags | `my_task.list(status="suspended")` |

---

## What This Is NOT

| Not This | Use This Instead |
|----------|-----------------|
| A result store (outputs beyond task lifetime) | Developer-chosen store (DB, blob, conversation storage) |
| A stream log (durable replay of every chunk) | Write chunks to your own store as you emit |
| An audit trail (history of all executions) | Logs, telemetry, developer-owned event store |
| A workflow replay engine (deterministic replay, sub-step memoization) | Temporal, Durable Functions, or the framework underneath |

The task store is for **lifecycle** — tracking that work is in flight, surviving crashes, and handing off across sandbox instances. Application data belongs in a store the developer chooses.

---

## Summary

```python
@durable_task(name="my-agent")
async def my_agent(ctx, input: str) -> str:
    # Your agent logic here.
    # Crashes, OOM kills, redeployments — all handled.
    # The framework leases, persists, recovers, and re-enters.
    ...
```

One decorator. Crash-resilient long-running agents. The platform can see, lease, restart, and resume your work — no matter what happens to the sandbox.
