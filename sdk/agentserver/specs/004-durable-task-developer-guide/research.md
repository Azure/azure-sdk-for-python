# Research: Durable Task Developer Guide

## Public API Surface Inventory

Complete list of public symbols from `azure.ai.agentserver.core.durable.__all__`:

| Symbol | Type | Must Document |
|--------|------|---------------|
| `durable_task` | Decorator factory | ✅ Primary entry point |
| `DurableTask` | Class | ✅ The decorated function type |
| `DurableTaskOptions` | Dataclass | ✅ Decorator configuration |
| `RetryPolicy` | Dataclass | ✅ Retry presets |
| `TaskContext` | Class (Generic[Input]) | ✅ The single function parameter |
| `TaskMetadata` | Class | ✅ Mutable progress metadata |
| `TaskRun` | Class (Generic[Output]) | ✅ Handle from `.start()` |
| `Suspended` | Sentinel class | ⚠️ Internal sentinel, mention briefly |
| `TaskStatus` | Literal type | ✅ Status values |
| `TaskFailed` | Exception | ✅ Unhandled exception wrapper |
| `TaskSuspended` | Exception | ✅ Raised on `.run()` when task suspends |
| `TaskCancelled` | Exception | ✅ Cancellation signal |
| `TaskNotFound` | Exception | ⚠️ Brief mention |
| `TaskConflictError` | Exception | ✅ Lifecycle conflict |
| `EntryMode` | Literal type | ✅ Core lifecycle concept |
| `TaskInfo` | Model | ✅ Return type of `.get()` |

## Guide Structure (Modeled on Responses Guide)

The responses `handler-implementation-guide.md` follows this pattern:

1. **Overview** — 1 paragraph, "the library handles X, you provide Y"
2. **Getting Started** — minimal code that works
3. **Core Concepts** — the main classes/types with examples
4. **Patterns** — common usage patterns
5. **Error Handling** — what can go wrong
6. **Configuration** — optional settings
7. **Best Practices** — dos
8. **Common Mistakes** — don'ts

Our guide structure:

1. **Overview**
2. **Getting Started** — minimal `@durable_task` + `.run()`
3. **Lifecycle Automation** — state diagram, `.run()` vs `.start()` vs `.get()`
4. **TaskContext** — `ctx.input`, `ctx.entry_mode`, `ctx.metadata`, `ctx.cancel`, `ctx.shutdown`
5. **Suspend & Resume** — `ctx.suspend()`, multi-turn pattern
6. **Streaming** — `ctx.stream()` + `async for`
7. **Persistence** — what the framework stores vs what you store
8. **The Invocation Store Pattern** — result persistence inside the durable boundary
9. **RetryPolicy** — presets and custom
10. **Decorator Options** — `DurableTaskOptions` fields
11. **Error Handling** — exceptions table
12. **Best Practices**
13. **Common Mistakes**

## Key Concepts to Explain

### Lifecycle State Machine

```
          ┌──────────────────────────────────────┐
          │                                      │
    No task found              .start()/.run()   │
          │                 with new input        │
          ▼                       │               │
    ┌──────────┐                  │               │
    │  (none)  │──── create ────► │               │
    └──────────┘                  │               │
                                  ▼               │
                           ┌────────────┐         │
                     ┌───► │ in_progress │ ───┐   │
                     │     └────────────┘     │   │
                     │           │            │   │
                  stale?      success       suspend
                     │           │            │   │
                     │           ▼            ▼   │
                     │    ┌───────────┐  ┌────────────┐
                     │    │ completed │  │ suspended  │
                     │    └───────────┘  └────────────┘
                     │                        │
                     └────── recovered ───────┘
```

### Entry Mode Decision Table

| Current State | `.start()`/`.run()` Action | `ctx.entry_mode` |
|---|---|---|
| No task | Create and start | `"fresh"` |
| `pending` | Start | `"fresh"` |
| `suspended` | Resume with new input | `"resumed"` |
| `in_progress` (stale) | Recover | `"recovered"` |
| `in_progress` (not stale) | **Raise `TaskConflictError`** | — |
| `completed` (ephemeral=True) | Task was auto-deleted → create fresh | `"fresh"` |
| `completed` (ephemeral=False) | **Raise `TaskConflictError`** | — |

### Persistence Responsibility

| What | Who persists | Where |
|------|-------------|-------|
| Task status, input, metadata, output | Framework (task store) | `/storage/tasks/{task_id}` |
| Invocation results | **Developer** | File store, Redis, DB — your choice |
| Conversation state / checkpoints | **Developer** | File store, SQLite, DB — your choice |
| Streaming items | **Nobody** — in-memory only | Lost on crash |

### The Durable Boundary Rule

> **Everything that must survive a crash must happen inside the durable task function.**

- ✅ Write invocation results inside the task (durable — recovers on crash)
- ❌ Write invocation results in `asyncio.create_task` outside the task (lost on crash)

## Anti-Patterns to Document

1. **Leaking `task_id`** — task_id is internal; expose invocation_id or session_id instead
2. **In-memory result collection** — `asyncio.create_task` for result persistence is NOT durable
3. **Missing `return await` on suspend** — `ctx.suspend()` without `return await` silently breaks
4. **Testing ephemeral tasks for conflict** — completed ephemeral tasks are auto-deleted, so `.start()` creates fresh instead of raising conflict
5. **Coupling core to protocol** — core has no knowledge of invocation IDs, response IDs, etc.
