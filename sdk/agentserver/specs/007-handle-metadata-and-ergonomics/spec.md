# Feature Specification: Handle Operations & API Ergonomics

**Feature Branch**: `007-handle-metadata-and-ergonomics`  
**Created**: 2026-05-12  
**Status**: Implemented  
**Input**: Backlog items 13 (handle.metadata), 14 (handle.delete), 15 (qualname default), 16 (dict-like TaskMetadata). Container spec §2.1, §4.1, §6.2.

## Background & Motivation

Four independently deliverable improvements remain from the container spec gap analysis and backlog. They fall into two themes:

1. **Handle operations** — `TaskRun` (the handle returned by `start()` / `get()`) lacks two capabilities the container spec defines: reading task metadata from outside (`handle.metadata`) and cleaning up completed tasks (`handle.delete()`). Without these, callers cannot observe progress or manage non-ephemeral task lifecycle.

2. **API ergonomics** — Two low-risk improvements to developer experience: switching the task name default from `fn.__name__` to `fn.__qualname__` (aligning with Celery/Dramatiq convention), and making `TaskMetadata` implement the dict protocol so users can write `ctx.metadata["key"] = value` naturally.

### What Needs to Change

| Feature | Current State | Target State |
|---------|--------------|--------------|
| `handle.metadata` | Not available on `TaskRun` | `handle.metadata` returns `dict[str, Any]` snapshot from task record |
| `handle.delete()` | Not available on `TaskRun` | `handle.delete()` removes the task record from the store |
| `name` default | `fn.__name__` (e.g., `process`) | `fn.__qualname__` (e.g., `MyClass.process`) |
| `TaskMetadata` API | Methods only (`.set()`, `.get()`, `.increment()`, `.append()`) | Full dict protocol (`[]`, `in`, `for`, `len`) plus existing methods |

---

## User Scenarios & Testing

### User Story 1 — Dict-Like TaskMetadata (Priority: P1)

A developer writing a durable task wants to track progress using natural Python dict syntax:

```python
@durable_task()
async def process_batch(ctx: TaskContext[BatchInput]) -> BatchOutput:
    ctx.metadata["phase"] = "loading"
    ctx.metadata["total"] = len(ctx.input.items)
    for i, item in enumerate(ctx.input.items):
        await process(item)
        ctx.metadata["processed"] = i + 1

    for key, value in ctx.metadata:  # iteration
        logger.info(f"{key}: {value}")

    if "phase" in ctx.metadata:      # containment
        ...
```

Today they must use `.set()` / `.get()` methods which feel unnatural for what is conceptually a dict.

**Why this priority**: This is the lowest-risk, highest-frequency improvement. Every task that uses metadata benefits. No new I/O, no new dependencies — purely additive protocol methods that delegate to the existing internal `_data` dict with dirty-tracking.

**Independent Test**: Create a `TaskMetadata`, use `[]` assignment, iteration, `in`, and `len`. Verify dirty-tracking triggers auto-flush.

**Acceptance Scenarios**:

1. **Given** a `TaskMetadata` instance, **When** `metadata["key"] = "value"`, **Then** `metadata["key"] == "value"` AND `metadata._dirty == True`.
2. **Given** a `TaskMetadata` with 3 keys, **When** `len(metadata)`, **Then** returns `3`.
3. **Given** a `TaskMetadata` with key `"phase"`, **When** `"phase" in metadata`, **Then** returns `True`.
4. **Given** a `TaskMetadata` with keys `["a", "b"]`, **When** `list(metadata)`, **Then** returns `["a", "b"]`.
5. **Given** a `TaskMetadata` with key `"temp"`, **When** `del metadata["temp"]`, **Then** key is removed AND `metadata._dirty == True`.
6. **Given** a `TaskMetadata`, **When** `metadata.keys()`, `.values()`, `.items()` are called, **Then** they return the same as `dict.keys()`, `.values()`, `.items()`.
7. **Given** existing `.set()`, `.get()`, `.increment()`, `.append()` methods, **When** the dict protocol is added, **Then** existing method-based code continues to work unchanged.

---

### User Story 2 — Handle Metadata Snapshot (Priority: P2)

A caller (dashboard, orchestrator, polling loop) wants to check progress on a running task:

```python
handle = await process_batch.start(task_id="batch-42", input=batch)

# ... later, check progress ...
meta = await handle.metadata
print(f"Processed {meta.get('processed', 0)} / {meta.get('total', '?')}")
```

**Why this priority**: Required for any observability beyond "is it done yet?". The task already writes metadata via `ctx.metadata` — this enables reading it back from outside the task.

**Independent Test**: Start a task that sets metadata, then call `handle.metadata` from the caller side. Verify the snapshot reflects what the task wrote.

**Acceptance Scenarios**:

1. **Given** a running task that set `ctx.metadata["progress"] = 42`, **When** the caller reads `await handle.metadata`, **Then** returns a dict containing `{"progress": 42}` (at least — may include other keys).
2. **Given** a task that has not set any metadata, **When** `await handle.metadata`, **Then** returns an empty dict `{}`.
3. **Given** a completed task with `ephemeral=False`, **When** `await handle.metadata`, **Then** returns the metadata snapshot from the task record.
4. **Given** an ephemeral task that has already completed, **When** `await handle.metadata`, **Then** raises `TaskNotFound` (the record no longer exists).
5. **Given** a task ID that never existed, **When** `await handle.metadata` on a handle from `task.get(bad_id)`, **Then** raises `TaskNotFound`.

---

### User Story 3 — Handle Delete (Priority: P2)

A caller wants to clean up a non-ephemeral task after reading its result:

```python
result = await handle.result()
process_output(result.output)
await handle.delete()  # clean up the task record
```

Without this, non-ephemeral tasks (`ephemeral=False`) accumulate in the task store indefinitely.

**Why this priority**: Same priority as metadata — together they complete the external handle surface from the container spec.

**Independent Test**: Create a non-ephemeral task, let it complete, call `handle.delete()`, then verify `handle.result()` raises `TaskNotFound`.

**Acceptance Scenarios**:

1. **Given** a completed non-ephemeral task, **When** `await handle.delete()`, **Then** the task record is removed from the store.
2. **Given** a deleted task, **When** `await handle.result()` or `await handle.metadata`, **Then** raises `TaskNotFound`.
3. **Given** a task ID that does not exist, **When** `await handle.delete()`, **Then** no-op (idempotent, does not raise).
4. **Given** a running task, **When** `await handle.delete()`, **Then** raises `TaskInProgress` or similar — cannot delete a running task.

---

### User Story 4 — Qualname Default (Priority: P3)

A developer decorates a class method as a durable task:

```python
class DocumentProcessor:
    @durable_task()
    async def process(self, ctx: TaskContext[DocInput]) -> DocOutput: ...

class ImageProcessor:
    @durable_task()
    async def process(self, ctx: TaskContext[ImgInput]) -> ImgOutput: ...
```

Today both tasks get the default name `"process"` (from `fn.__name__`), causing a collision. With `__qualname__`, they get `"DocumentProcessor.process"` and `"ImageProcessor.process"`.

**Why this priority**: Low risk, but also low frequency — most durable tasks are module-level functions where `__name__` and `__qualname__` are identical. This is an alignment fix, not a user-facing blocker.

**Independent Test**: Decorate a class method without an explicit `name`. Verify the default name is `Class.method`, not just `method`.

**Acceptance Scenarios**:

1. **Given** a module-level `@durable_task() async def process(...)`, **When** no explicit `name`, **Then** default is `"process"` (unchanged — `__name__` == `__qualname__` for module-level functions).
2. **Given** a class method `class Foo: @durable_task() async def bar(...)`, **When** no explicit `name`, **Then** default is `"Foo.bar"` (from `__qualname__`).
3. **Given** `@durable_task(name="custom")`, **When** explicit name provided, **Then** uses `"custom"` regardless (existing behavior).
4. **Given** tasks with existing `__name__`-based routing, **When** upgrading, **Then** this is a **breaking change** for class-method tasks — document in CHANGELOG.

---

### Edge Cases

- `TaskMetadata.__delitem__` on a non-existent key: should raise `KeyError` (standard dict behavior).
- `handle.metadata` timing: metadata is eventually consistent — auto-flush runs every 5s, so a snapshot may lag behind in-process mutations by up to one flush interval.
- `handle.delete()` on an ephemeral task that auto-deleted: no-op (idempotent).
- `__qualname__` for nested functions (e.g., `def outer(): @durable_task() async def inner(): ...`): produces `outer.<locals>.inner`. This is technically correct but may be surprising — document it.

## Requirements

### Functional Requirements

#### Dict-Like TaskMetadata (P1)

- **FR-001**: `TaskMetadata` MUST implement `__setitem__(key: str, value: Any)` that calls `_mark_dirty()`.
- **FR-002**: `TaskMetadata` MUST implement `__getitem__(key: str)` that raises `KeyError` on missing key.
- **FR-003**: `TaskMetadata` MUST implement `__delitem__(key: str)` that calls `_mark_dirty()` and raises `KeyError` on missing key.
- **FR-004**: `TaskMetadata` MUST implement `__contains__(key: object)`, `__iter__()`, `__len__()`.
- **FR-005**: `TaskMetadata` MUST implement `keys()`, `values()`, `items()` delegating to internal `_data`.
- **FR-006**: Existing `.set()`, `.get()`, `.increment()`, `.append()`, `.to_dict()`, `.flush()` MUST continue to work unchanged.
- **FR-007**: `TaskMetadata` SHOULD inherit from `collections.abc.MutableMapping` or declare it satisfies the protocol via `__class_getitem__` / registration.

#### Handle Metadata (P2)

- **FR-008**: `TaskRun` MUST expose a `metadata` property that returns `Awaitable[dict[str, Any]]`.
- **FR-009**: The metadata snapshot MUST be read from the task store (not from in-process state).
- **FR-010**: If the task record does not exist, `metadata` MUST raise `TaskNotFound`.

#### Handle Delete (P2)

- **FR-011**: `TaskRun` MUST expose an `async delete()` method that removes the task record.
- **FR-012**: `delete()` on a non-existent task MUST be a no-op (idempotent).
- **FR-013**: `delete()` on a running task MUST raise an error (cannot delete in-progress tasks).

#### Qualname Default (P3)

- **FR-014**: Default `name` in `@durable_task` MUST use `fn.__qualname__` instead of `fn.__name__`.
- **FR-015**: Explicit `name=` argument MUST override the default (unchanged behavior).
- **FR-016**: This is a breaking change for class-method tasks — MUST be documented in CHANGELOG.

### Key Entities

- **`TaskMetadata`**: Existing mutable progress dict. Extended with dict protocol (`MutableMapping`).
- **`TaskRun`**: Existing handle class. Extended with `.metadata` and `.delete()`.

## Success Criteria

### Measurable Outcomes

- **SC-001**: `ctx.metadata["key"] = value` works and triggers auto-flush — natural Python dict syntax.
- **SC-002**: `await handle.metadata` returns a snapshot dict from the task store — observability from outside.
- **SC-003**: `await handle.delete()` removes the task record — lifecycle management for non-ephemeral tasks.
- **SC-004**: Class-method tasks default to `Class.method` name — no collisions.
- **SC-005**: All existing tests pass without modification (except name-default tests for P3).
- **SC-006**: New tests cover all acceptance scenarios above.

## Assumptions

- `handle.metadata` reads from the task store via the existing `_store.get_task()` path. No new storage API is needed — the metadata is already part of the task record payload.
- `handle.delete()` maps to a `DELETE /storage/tasks/{id}` call on the task store. The `InProcessTaskStore` simply removes from its internal dict.
- The `__qualname__` change (P3) is acceptable as a breaking change because the package is in preview. For module-level functions (the common case), behavior is identical.
- `TaskMetadata` will NOT subclass `dict` — it will implement `MutableMapping` protocol or register as a virtual subclass. This preserves dirty-tracking.
