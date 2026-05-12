# Feature Specification: Durable Task Developer Guide

**Feature Branch**: `004-durable-task-developer-guide`  
**Created**: 2026-05-12  
**Status**: Draft  
**Input**: User description: "We need a good developer guide for durable tasks. This needs to be the single doc that anyone would need to implement durable agents that are resilient to crashes/restarts. Modeled after the handler-implementation-guide for responses."

## Background & Motivation

The durable task API in `azure-ai-agentserver-core` is now feature-complete for the core patterns:

- `@durable_task` decorator with lifecycle automation
- `.run()` (synchronous), `.start()` (background), `.get()` (query)
- `ctx.suspend()`, `ctx.entry_mode`, `ctx.stream()`
- `TaskConflictError`, `TaskSuspended`, `TaskFailed`
- `RetryPolicy` presets
- `TaskMetadata` for progress tracking

**But there is zero developer documentation.**  The only way to learn the API is to read source code or reverse-engineer the samples.  The responses package has an excellent `handler-implementation-guide.md` — we need the equivalent for durable tasks.

### What Exists Today

| Package | Docs | Status |
|---------|------|--------|
| `azure-ai-agentserver-responses` | `docs/handler-implementation-guide.md` (400+ lines) | ✅ Comprehensive |
| `azure-ai-agentserver-core` (durable) | Nothing | ❌ Zero documentation |
| `azure-ai-agentserver-invocations` | Nothing (samples only) | ❌ Zero documentation |

### Container Spec Alignment

The guide should reflect the container spec's design philosophy (from `durable-task-convenience-api.md`):

- §10: "Persistence is the developer's responsibility" — the framework provides lifecycle, NOT a result store
- §8: Three exit modes — success, suspend, failure
- §6: Four state buckets — input (immutable), metadata (mutable), output (final), error (failure)
- §11: What lives on the task record vs what the developer must persist themselves

---

## User Scenarios & Testing

### User Story 1 — New Developer Gets Started (Priority: P1)

A developer with no prior durable task knowledge reads the guide and implements a crash-resilient agent within one sitting.  They understand `@durable_task`, `.run()`, and basic suspend/resume without reading source code.

**Why this priority**: If a new developer can't get started from the guide alone, the guide has failed its primary purpose.

**Independent Test**: Guide contains a minimal "Getting Started" section with copy-paste code that works.

**Acceptance Scenarios**:

1. **Given** a developer has `azure-ai-agentserver-core` installed, **When** they follow the "Getting Started" section, **Then** they have a working durable task in <20 lines of code.
2. **Given** a developer reads only the first two sections, **When** they run the example code, **Then** it executes a task that survives a simulated restart.

---

### User Story 2 — Developer Understands Lifecycle Automation (Priority: P1)

A developer understands that `.run()` and `.start()` are lifecycle-aware — they don't need to manually check task state, branch on suspended/completed, or call resume.

**Why this priority**: Lifecycle automation is the core value proposition.  If developers don't understand it, they'll write the same boilerplate the framework was designed to eliminate.

**Independent Test**: Guide contains a lifecycle state diagram and a table mapping current-state → action → entry_mode.

**Acceptance Scenarios**:

1. **Given** a developer reads the "Lifecycle Automation" section, **When** they call `.start()` on a suspended task, **Then** they understand it auto-resumes with `entry_mode="resumed"`.
2. **Given** a developer's process crashes mid-task, **When** they call `.start()` again, **Then** they understand the stale detection → recovery path with `entry_mode="recovered"`.

---

### User Story 3 — Developer Implements Multi-Turn Agent (Priority: P1)

A developer uses the guide to build a multi-turn conversational agent using `ctx.suspend()` for human-in-the-loop pauses, with a proper invocation store for powering the API.

**Why this priority**: Multi-turn suspend/resume is the most common durable task pattern for hosted agents.

**Independent Test**: Guide contains a complete "Multi-Turn Pattern" section that walks through session → task → invocation mapping.

**Acceptance Scenarios**:

1. **Given** a developer reads the "Suspend & Resume" section, **When** they implement `return await ctx.suspend(output=...)`, **Then** the task pauses and `.start()` with new input resumes it.
2. **Given** a developer reads the "Persistence" section, **When** they understand that the framework does NOT persist invocation results, **Then** they implement their own store (as shown in the guide).

---

### User Story 4 — Developer Understands What NOT to Do (Priority: P2)

A developer avoids common anti-patterns: leaking `task_id` to callers, using `asyncio.create_task` for result collection outside the durable boundary, storing invocation results in memory.

**Why this priority**: Anti-patterns lead to subtle bugs (data loss on crash, inconsistent state).  Calling them out explicitly prevents hours of debugging.

**Independent Test**: Guide has a "Common Mistakes" section with ❌ BAD / ✅ GOOD code pairs.

**Acceptance Scenarios**:

1. **Given** a developer reads the "Common Mistakes" section, **When** they implement result persistence, **Then** they write it inside the durable task function, not in a background asyncio task.

---

### User Story 5 — Developer Uses Streaming (Priority: P3)

A developer uses `ctx.stream()` to emit incremental output and `async for chunk in task_run` to consume it.

**Why this priority**: Streaming is useful but not core to the durability story.

**Independent Test**: Guide contains a "Streaming" section with a working example.

**Acceptance Scenarios**:

1. **Given** a developer reads the "Streaming" section, **When** they call `await ctx.stream(item)` inside their task, **Then** the caller receives items via `async for`.

---

### Edge Cases

- What happens when `ctx.suspend()` is called without `return await`?
- What happens when `.start()` is called on a completed ephemeral task (answer: creates fresh — task was auto-deleted)?
- What happens when `.start()` is called on a completed non-ephemeral task (answer: `TaskConflictError`)?
- What happens when `entry_mode="recovered"` but the developer's external state is stale?

## Requirements

### Functional Requirements

- **FR-001**: Guide MUST live at `azure-ai-agentserver-core/docs/durable-task-developer-guide.md`
- **FR-002**: Guide MUST cover all public API surface: `@durable_task`, `.run()`, `.start()`, `.get()`, `TaskContext`, `ctx.suspend()`, `ctx.entry_mode`, `ctx.stream()`, `ctx.metadata`, `ctx.cancel`, `ctx.shutdown`
- **FR-003**: Guide MUST include a "Getting Started" section with a minimal working example
- **FR-004**: Guide MUST include a lifecycle state diagram (text-based) showing state transitions
- **FR-005**: Guide MUST include a "Persistence" section explaining what the framework persists vs what the developer must persist
- **FR-006**: Guide MUST include a "Common Mistakes" section with anti-patterns
- **FR-007**: Guide MUST include a "Multi-Turn Pattern" section showing suspend/resume with invocation store
- **FR-008**: Guide MUST follow the style and tone of `azure-ai-agentserver-responses/docs/handler-implementation-guide.md`
- **FR-009**: Guide MUST use only public API imports — zero private `_module` references
- **FR-010**: Guide MUST include `RetryPolicy` configuration (presets: exponential, fixed, linear)
- **FR-011**: Guide MUST include `DurableTaskOptions` explanation (name, ephemeral, tags, title, source)
- **FR-012**: Guide MUST include a reference table mapping `entry_mode` × task state

### Non-Functional Requirements

- **NR-001**: Guide MUST be self-contained — no external links required to understand core concepts
- **NR-002**: All code examples MUST be syntactically correct and use current API signatures
- **NR-003**: Guide length should be 400–600 lines (matching the responses guide)

## Success Criteria

### Measurable Outcomes

- **SC-001**: A developer with no prior knowledge can implement a working durable task from the guide alone
- **SC-002**: Guide covers 100% of the public API surface in `azure.ai.agentserver.core.durable.__all__`
- **SC-003**: Zero private imports (`_module`) in any code example
- **SC-004**: All code examples pass a syntax check

## Assumptions

- The public API is stable — no breaking changes planned for the items being documented
- The guide documents what IS implemented, not aspirational features (cancellation patterns, timeout, etc. are noted as "coming soon" if mentioned at all)
- The guide is for Python developers familiar with async/await but not necessarily with durable execution concepts
- The responses handler-implementation-guide.md style is the approved documentation standard for this project
