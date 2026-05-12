# Future Specs Backlog

## Spec Candidates: 

Tracked items from container spec (`durable-task-convenience-api.md`) gap analysis that are out of scope for spec 003 but should be addressed in subsequent iterations.

### Task Lifecycle Policies

#### ~~1. `ephemeral` flag (container spec §8)~~ ✅ Done
- Default `True` — task is auto-deleted on terminal exit (success or failure)
- `ephemeral=False` — task kept as `completed` for cross-process retrieval

#### ~~2. `store_input` flag (container spec §3.2)~~ ✅ Done
- Default `True` — input persisted on task record for restart recovery
- `store_input=False` — input held in-process only, not written to task store

#### ~~3. `timeout` on decorator (container spec §2.1)~~ ✅ Done (spec 005)
- Configurable per-task timeout that auto-fires `ctx.cancel`
- Two-phase watchdog: cooperative cancel → hard cancel after `cancel_grace_seconds`

#### ~~4. `wait_timeout` on `.run()` (container spec §4.2)~~ ❌ Removed by design
- Decided against: confusing alongside `timeout`. Callers who need fire-and-forget use `.start()` and can wrap `result()` in their own `asyncio.wait_for`.

### Advanced Task Control

#### ~~5. `handle.terminate()` (container spec §9)~~ ✅ Done (spec 005)
- Forced non-recoverable exit, distinct from cooperative `cancel()`
- Sets `terminate_event`, hard-cancels execution task, goes through failure path
- Raises `TaskTerminated` on `result()`

#### ~~6. `TaskResult[Output]` wrapper for `result()` and `run()`~~ ✅ Done (spec 006)
- Replace raw `Output` return with `TaskResult[Output]` that carries `output`, `status`, and `suspension_reason`
- `status: Literal["completed", "suspended"]` — only the two "normal exit" paths
- `output: Output | None` — present for both success and suspended (suspended output is optional snapshot from `ctx.suspend(output=...)`)
- `suspension_reason: str | None` — only set when suspended
- Convenience properties: `is_suspended`, `is_completed`
- `TaskSuspended` exception removed from `result()`/`run()` — suspension becomes a return value, not an error
- Failures/cancel/terminate stay as exceptions (those are genuinely exceptional)
- **Motivation**: Multi-turn agents (LangGraph, workflows) suspend on every turn — making that an exception is awkward when it's the normal path

#### ~~7. Function-style API (container spec §2.2)~~ ❌ Removed by design
- `durable_task()` already works as a plain function call (not just a decorator), so `app.tasks.run(fn=...)` adds near-zero value while introducing a second entry point and `app` host coupling.

*Source*: Gap analysis performed 2026-05-11 comparing `durable-task-convenience-api.md` (container spec) against specs 001-003.
---

### Docs

#### ~~8. Developer guide for durable tasks~~ ✅ Done (spec 004)

---

### Decorator Enhancements

#### ~~9. Callable factories for decorator options (container spec §2.1)~~ ✅ Done (spec 006)
- `title` already supports `Callable[[Input, str], str]` — extend the same pattern to other options where it makes sense
- **`tags`**: `dict[str, str] | Callable[[Input, str], dict[str, str]]` — compute tags from input at runtime (e.g., tag by tenant, model, priority)
- **`description`**: `str | Callable[[Input, str], str]` — generate description from input context
- **`title`**: Already supported ✅
- **Use case**: Dynamic metadata that depends on the input value rather than static decorator-time constants
- **Signature convention**: `(input: Input, task_id: str) -> T` — same as existing title callable
- **Type safety requirement**: The callable signature must carry the `Input` generic so developers get type-checked parameters. The decorator already knows `Input` from `TaskContext[Input]` — thread it through to the callable type so IDE autocomplete and mypy validate the input parameter.

---

### Container Lifecycle

#### 10. ~~`ctx.shutdown` event (container spec §9.2)~~ ✅ Already implemented
- Already on `TaskContext` as `shutdown: asyncio.Event`

#### 11. ~~`ctx.agent_name` (container spec §5)~~ ✅ Already implemented
- Already on `TaskContext` as `agent_name: str`

---

### Observable Progress

#### 12. ~~`TaskMetadata` rich mutation API (container spec §5, §6.2)~~ ✅ Already implemented
- `ctx.metadata.set(key, value)`, `.increment(key, delta)`, `.append(key, value)` all exist in `_metadata.py`
- Debounced auto-flush to task store (5s interval) with explicit `.flush()`

#### ~~13. `handle.metadata` snapshot read (container spec §4.1, §6.2)~~ ✅ Already implemented
- `TaskRun.metadata` property returns live `TaskMetadata` reference
- `TaskRun.refresh()` pulls latest snapshot from task store
- No live subscription — callers poll via `refresh()` if needed

---

### Task Cleanup

#### ~~14. `handle.delete()` (container spec §4.1)~~ ✅ Already implemented
- `TaskRun.delete()` calls `_provider.delete(task_id, force=True)`
- Raises `TaskNotFound` if record does not exist

---

### Naming Conventions

#### ~~15. Switch `name` default from `fn.__name__` to `fn.__qualname__` (container spec §2.1)~~ ✅ Already implemented
- `_decorator.py:675` already uses `func.__qualname__`
- Aligns with Celery/Dramatiq convention

---

### API Ergonomics

#### ~~16. Make `TaskMetadata` dict-like (container spec §6.2)~~ ✅ Done (spec 007)
- Added `__setitem__`, `__getitem__`, `__delitem__`, `__iter__`, `__len__`, `__contains__`
- Added `keys()`, `values()`, `items()` delegating to internal `_data`
- Registered as `collections.abc.MutableMapping` virtual subclass
- Mutating operations call `_mark_dirty()` for auto-flush
- Existing `.set()`, `.get()`, `.increment()`, `.append()` unchanged
