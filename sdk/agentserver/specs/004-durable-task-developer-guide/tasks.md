# Tasks: Durable Task Developer Guide

**Input**: Design documents from `/specs/004-durable-task-developer-guide/`  
**Prerequisites**: plan.md (required), spec.md (required), research.md

## Format: `[ID] [P?] [Story] Description`

---

## Phase 1: Scaffolding

**Purpose**: Create file, write table of contents, overview, and getting started

- [ ] T001 [US1] Create `azure-ai-agentserver-core/docs/durable-task-developer-guide.md` with TOC and Overview section (~20 lines). Overview states the framework's value proposition: "you write the task function, the framework handles lifecycle, crash recovery, and state management."
- [ ] T002 [US1] Write "Getting Started" section (~40 lines). Minimal `@durable_task` + `.run()` example in <20 lines of code. Must include: import, decorator, function signature with `ctx: TaskContext[str]`, return value, and `.run("my-task", input="hello")` call.

**Checkpoint**: A developer can copy-paste the getting started example and have a working durable task.

---

## Phase 2: Core API (P1 Stories)

**Purpose**: Document the lifecycle automation engine and TaskContext — the two concepts every developer must understand

- [ ] T003 [US2] Write "Lifecycle Automation" section (~60 lines). Must include: (a) ASCII state diagram showing task states and transitions, (b) entry_mode × task-state decision table from research.md, (c) explanation of `.run()` vs `.start()` vs `.get()` with when to use each, (d) example showing `.start()` auto-resuming a suspended task.
- [ ] T004 [US1,US2] Write "TaskContext" section (~50 lines). Document all properties: `ctx.input`, `ctx.entry_mode`, `ctx.metadata`, `ctx.cancel`, `ctx.shutdown`. Include a code example showing how to branch on `ctx.entry_mode` for fresh/resumed/recovered.

**Checkpoint**: Developer understands the full lifecycle state machine and TaskContext API.

---

## Phase 3: Patterns (P1 Suspend, P3 Streaming)

**Purpose**: Document the two key interaction patterns — suspend/resume for multi-turn and streaming for incremental output

- [ ] T005 [US3] Write "Suspend & Resume" section (~50 lines). Cover `return await ctx.suspend(output=...)`, emphasize the `return await` requirement. Show a multi-turn conversation loop with entry_mode branching.
- [ ] T006 [US5] Write "Streaming" section (~30 lines). Cover `await ctx.stream(item)` inside the task and `async for chunk in task_run` on the caller side. Note: streaming items are in-memory only (not persisted, lost on crash).

**Checkpoint**: Developer can implement suspend/resume and streaming patterns.

---

## Phase 4: Persistence & Invocation Store

**Purpose**: Document the critical persistence responsibility boundary and the durable invocation store pattern

- [ ] T007 [US3] Write "Persistence" section (~40 lines). Must include the responsibility matrix table (what the framework persists vs what the developer persists). Clearly state: "The task store powers lifecycle and recovery. It is NOT your application database."
- [ ] T008 [US3] Write "The Invocation Store Pattern" section (~50 lines). Show the complete pattern: task receives invocation_id in input, writes "running" status, does work, writes "completed" + result, all inside the durable boundary. Reference that this pattern powers the 202+poll HTTP API. Include the durable boundary rule callout.

**Checkpoint**: Developer understands what they must persist themselves and knows the correct pattern.

---

## Phase 5: Reference (Decorator, Retry, Errors)

**Purpose**: Document configuration options and error handling

- [ ] T009 [P] [US1] Write "RetryPolicy" section (~30 lines). Document the three presets: `exponential_backoff()`, `fixed_interval()`, `linear_backoff()`. Show usage on decorator: `@durable_task(name="...", retry=RetryPolicy.exponential_backoff())`.
- [ ] T010 [P] [US1] Write "Decorator Options" section (~30 lines). Document all `DurableTaskOptions` fields: `name` (required), `retry`, `source`, `ephemeral`, `tags`, `title`. Explain ephemeral=True means auto-delete on completion.
- [ ] T011 [P] [US4] Write "Error Handling" section (~40 lines). Table of all exceptions: `TaskConflictError`, `TaskSuspended`, `TaskFailed`, `TaskCancelled`, `TaskNotFound`. When each is raised and how to handle it.

**Checkpoint**: Developer has a complete reference for all configuration and error scenarios.

---

## Phase 6: Safety (Anti-patterns)

**Purpose**: Prevent common mistakes that lead to subtle bugs

- [ ] T012 [US4] Write "Best Practices" section (~30 lines). Numbered list: (1) keep tasks idempotent for recovery, (2) branch on entry_mode, (3) persist results inside the durable boundary, (4) use ephemeral for one-shot tasks, (5) keep task functions focused.
- [ ] T013 [US4] Write "Common Mistakes" section (~40 lines). ❌ BAD / ✅ GOOD code pairs for: (a) missing `return await` on suspend, (b) result collection outside durable boundary via asyncio.create_task, (c) leaking task_id to callers, (d) assuming streaming survives crashes.

**Checkpoint**: Developer knows what NOT to do and why.

---

## Phase 7: Validation

**Purpose**: Verify the guide meets all spec requirements

- [ ] T014 Verify all code examples use only public imports (grep for `_` prefixed module imports). Fix any violations.
- [ ] T015 Verify guide covers all 16 symbols from `__all__` in research.md. Add missing coverage if any.
- [ ] T016 Verify line count is within 400–600 range. Trim or expand as needed.

**Checkpoint**: Guide meets all functional and non-functional requirements from spec.md.

---

## Dependencies & Execution Order

### Phase Dependencies

- **Phase 1 (Scaffolding)**: No dependencies — start immediately
- **Phase 2 (Core API)**: Depends on Phase 1 — builds on overview/getting-started
- **Phase 3 (Patterns)**: Depends on Phase 2 — references lifecycle and TaskContext
- **Phase 4 (Persistence)**: Depends on Phase 3 — references suspend pattern
- **Phase 5 (Reference)**: Depends on Phase 1 only — can parallel with Phase 3/4
- **Phase 6 (Safety)**: Depends on Phase 4 — anti-patterns reference persistence
- **Phase 7 (Validation)**: Depends on all previous phases

### Parallel Opportunities

- T009, T010, T011 (Phase 5) can run in parallel — different topics, same file but different sections
- Phase 5 can run in parallel with Phase 3/4 since they're independent reference sections
