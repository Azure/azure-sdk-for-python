# Implementation Plan: Durable Tasks for Long-Running Agents

**Branch**: `feat/durable-tasks` | **Date**: 2026-05-09 | **Spec**: [spec.md](spec.md)
**Input**: Feature specification from `specs/001-durable-tasks/spec.md`

## Summary

Add crash-resilient durable task execution to `azure-ai-agentserver-core`. Developers decorate an async function with `@durable_task` and the framework manages the full lifecycle — task registration via the Foundry Task Storage API, lease acquisition, automatic background renewal, restart recovery via dual-identity, graceful shutdown (force-expire on SIGTERM), and cleanup. The lower-level primitives (`DurableTaskClient`, `TaskHandle`) are internal; the public API is the `@durable_task` decorator, `TaskContext`, and `TaskRun` handle. A local filesystem provider enables full-parity offline development.

## Technical Context

**Language/Version**: Python 3.10+  
**Primary Dependencies**: starlette (existing), httpx (HTTP client for Task Storage API), pydantic (input validation — optional, supported but not required), azure-identity (DefaultAzureCredential for hosted auth)  
**Storage**: Foundry Task Storage API (`/storage/tasks`) in hosted mode; local JSON files (`$HOME/.durable-tasks/`) in local dev  
**Testing**: pytest with pytest-asyncio (`asyncio_mode = "auto"`), httpx `AsyncClient` with ASGI transport for in-process testing  
**Target Platform**: Linux containers (Azure AI Foundry Hosted Agents) + local dev on any platform  
**Project Type**: Library (Python package — `azure-ai-agentserver-core`)  
**Performance Goals**: Lease renewal at 30s interval (half of 60s default TTL); HTTP calls to task storage API < 500ms p95  
**Constraints**: No new top-level package dependencies beyond httpx + azure-identity; all code in `azure.ai.agentserver.core`  
**Scale/Scope**: One active durable task per invocation (typical); multiple concurrent tasks supported

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Principle | Status | Notes |
|-----------|--------|-------|
| I. Modular Package Architecture | ✅ PASS | All components in `core` package as specified. Protocol packages integrate via host builder. No new package needed. |
| II. Strong Type Safety | ✅ PASS | `TaskContext[Input]` is generic. All public types fully annotated. `Literal` for status values. `Protocol` for provider abstraction. |
| III. Azure SDK Guidelines | ✅ PASS | Follows naming (`azure.ai.agentserver.core`), versioning, Black formatting, CHANGELOG conventions. |
| IV. Async-First Design | ✅ PASS | All task operations are `async def`. Lease renewal runs in `asyncio.Task`. Handlers must be coroutines. |
| V. Fail-Fast Config, Graceful Runtime | ✅ PASS | Validates env vars at startup (fail-fast). Lease failures logged but don't crash. Structured error responses. |
| VI. Observability & Correlation | ✅ PASS | HTTP spans on task storage calls. Counters for status transitions. Lease generation/expiry in logs. |
| VII. Minimal Surface, Maximum Composability | ✅ PASS | One decorator (`@durable_task`) + one context type (`TaskContext`) + one handle type (`TaskRun`). Lower-level API internal. |

## Project Structure

### Documentation (this feature)

```text
specs/001-durable-tasks/
├── plan.md              # This file
├── research.md          # Phase 0 output
├── data-model.md        # Phase 1 output
├── contracts/           # Phase 1 output (Task Storage API client contract)
└── tasks.md             # Phase 2 output (/speckit.tasks command)
```

### Source Code

```text
azure-ai-agentserver-core/
├── azure/ai/agentserver/core/
│   ├── __init__.py                    # Add durable task public exports
│   ├── _version.py                    # Existing
│   ├── _base.py                       # Existing — hook durable task lifecycle
│   ├── _config.py                     # Existing — already has env var resolution
│   │
│   ├── durable/                       # NEW — durable task subsystem
│   │   ├── __init__.py                # Public API: durable_task, TaskContext, TaskRun, TaskMetadata
│   │   ├── _decorator.py             # @durable_task decorator → DurableTask[Input, Output]
│   │   ├── _context.py               # TaskContext[Input] — the function parameter
│   │   ├── _run.py                    # TaskRun[Output] — external handle
│   │   ├── _metadata.py              # TaskMetadata — mutable progress dict
│   │   ├── _exceptions.py            # TaskFailed, TaskSuspended, TaskCancelled, TaskNotFound
│   │   ├── _manager.py               # DurableTaskManager — lifecycle orchestration (internal)
│   │   ├── _client.py                # DurableTaskClient — HTTP client for /storage/tasks (internal)
│   │   ├── _handle.py                # TaskHandle — lease management, auto-renewal (internal)
│   │   ├── _local_provider.py        # LocalFileDurableTaskProvider — filesystem backend (internal)
│   │   ├── _provider.py              # DurableTaskProvider protocol (internal)
│   │   ├── _lease.py                 # Lease identity derivation + renewal loop (internal)
│   │   ├── _models.py                # TaskInfo, TaskStatus, LeaseInfo data models (internal)
│   │   └── _resume_route.py          # POST /tasks/resume Starlette route (internal)
│   └── ...
│
└── tests/
    ├── test_durable_decorator.py      # @durable_task decorator tests
    ├── test_durable_context.py        # TaskContext tests
    ├── test_durable_lifecycle.py      # Full lifecycle (create → run → complete/fail)
    ├── test_durable_suspend_resume.py # Suspend/resume flow tests
    ├── test_durable_recovery.py       # Crash recovery + dual-identity reclaim tests
    ├── test_durable_shutdown.py       # SIGTERM graceful shutdown tests
    ├── test_durable_metadata.py       # TaskMetadata set/get/increment/append tests
    ├── test_durable_local_provider.py # Local filesystem provider tests
    └── test_durable_resume_route.py   # POST /tasks/resume endpoint tests
```

**Structure Decision**: All durable task code lives in a `durable/` subpackage within `azure.ai.agentserver.core`. This keeps it contained while following the existing pattern of private modules (`_*.py`) for internal implementation. The public API is re-exported from `azure.ai.agentserver.core.durable.__init__` and optionally from the top-level `azure.ai.agentserver.core.__init__`.

## Complexity Tracking

No constitution violations. All principles pass.
