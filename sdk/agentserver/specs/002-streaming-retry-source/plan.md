# Implementation Plan: Streaming, Retry Policies, and Source Field

**Branch**: `002-streaming-retry-source` | **Date**: 2026-05-09 | **Spec**: [spec.md](spec.md)
**Input**: Feature specification from `specs/002-streaming-retry-source/spec.md`

## Summary

Add three capabilities to the existing durable task subsystem in `azure-ai-agentserver-core`:

1. **Streaming** — `ctx.stream(item)` inside a durable task function emits items to an `asyncio.Queue` that the caller consumes via `async for chunk in run`. In-memory only, not persisted.
2. **Retry policies** — A `RetryPolicy` class (aligned with Temporal/DTF/Celery conventions) with `initial_delay`, `backoff_coefficient`, `max_delay`, `jitter`, `retry_on`. Includes presets: `exponential_backoff()`, `fixed_delay()`, `linear_backoff()`, `no_retry()`.
3. **Source field** — Immutable `source: dict[str, Any]` on `TaskCreateRequest` and `TaskInfo` for provenance tracking.

All changes are additive to the existing `durable/` subpackage. The provider selection logic has already been updated to default to `LocalFileDurableTaskProvider` everywhere (gated by `FOUNDRY_TASK_API_ENABLED`).

## Technical Context

**Language/Version**: Python 3.10+
**Primary Dependencies**: starlette (existing), httpx (existing), asyncio (stdlib), random (stdlib for jitter)
**Storage**: Local JSON files (`$HOME/.durable-tasks/`) by default; HTTP-backed provider gated behind `FOUNDRY_TASK_API_ENABLED=1`
**Testing**: pytest with pytest-asyncio (`asyncio_mode = "auto"`)
**Target Platform**: Linux containers (Azure AI Foundry Hosted Agents) + local dev on any platform
**Project Type**: Library (Python package — `azure-ai-agentserver-core`)
**Performance Goals**: Stream delivery < 50ms latency; retry delay computation O(1)
**Constraints**: No new dependencies. No dataclasses. Plain classes with `__slots__`. All code in `azure.ai.agentserver.core.durable`
**Scale/Scope**: Extends 12 existing modules in `durable/` subpackage; 140 existing tests must continue to pass

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Principle | Status | Notes |
|-----------|--------|-------|
| I. Modular Package Architecture | ✅ PASS | All components in `core` package. No new package needed. RetryPolicy, streaming, and source are additive to existing modules. |
| II. Strong Type Safety | ✅ PASS | `RetryPolicy` with typed slots. `ctx.stream()` accepts `Any` (JSON-serializable). `source` is `dict[str, Any] | None`. No `dataclass` — plain classes with `__slots__`. |
| III. Azure SDK Guidelines | ✅ PASS | Follows naming, versioning, Black formatting. No new public package surface — additions to existing `durable` subpackage. |
| IV. Async-First Design | ✅ PASS | `ctx.stream()` is async. Retry delays use `asyncio.sleep`. Queue-based producer/consumer. |
| V. Fail-Fast Config, Graceful Runtime | ✅ PASS | `RetryPolicy` validates at construction (fail-fast). Retry exhaustion produces structured error (graceful). |
| VI. Observability & Correlation | ✅ PASS | Retry attempts logged with attempt count. Stream items are ephemeral (not observable externally — use `ctx.metadata` for that). |
| VII. Minimal Surface, Maximum Composability | ✅ PASS | `RetryPolicy` is one class with 4 presets. Streaming adds one method (`ctx.stream`) and one protocol (`async for`). Source is one field. |

## Project Structure

### Documentation (this feature)

```text
specs/002-streaming-retry-source/
├── spec.md              # Feature specification (done)
├── plan.md              # This file
├── research.md          # Phase 0: prior art analysis
├── data-model.md        # Phase 1: data model changes
├── contracts/           # Phase 1: public API contract
│   └── public-api.md
├── quickstart.md        # Phase 1: usage examples
└── tasks.md             # Phase 2: implementation tasks
```

### Source Code (modifications to existing files)

```text
azure-ai-agentserver-core/
├── azure/ai/agentserver/core/
│   ├── __init__.py                    # Add RetryPolicy to public exports
│   │
│   └── durable/
│       ├── __init__.py                # Add RetryPolicy to public exports
│       ├── _retry.py                  # NEW — RetryPolicy class + presets + delay computation
│       ├── _context.py                # MODIFY — add stream() method + _stream_queue slot
│       ├── _run.py                    # MODIFY — add __aiter__/__anext__ for stream consumption
│       ├── _models.py                 # MODIFY — add source field to TaskInfo + TaskCreateRequest
│       ├── _decorator.py              # MODIFY — add retry + source params to DurableTaskOptions
│       ├── _manager.py                # MODIFY — retry loop in _execute_task, pass source + stream queue
│       ├── _client.py                 # MODIFY — send source in create request body
│       └── _local_provider.py         # MODIFY — persist + return source field
│
└── tests/
    └── durable/
        ├── test_retry.py              # NEW — RetryPolicy unit tests (presets, delay, jitter)
        ├── test_streaming.py          # NEW — ctx.stream + async for iteration tests
        ├── test_source.py             # NEW — source field round-trip tests
        ├── test_decorator.py          # MODIFY — add retry + source option tests
        ├── test_models.py             # MODIFY — add source field serialization tests
        └── test_sample_e2e.py         # NEW — e2e tests exercising all 5 samples end-to-end
```

**Structure Decision**: No new subpackages. One new module (`_retry.py`) for the RetryPolicy class. Everything else is modifications to existing modules. Tests follow the existing pattern in `tests/durable/`. Sample e2e tests follow the pattern from `azure-ai-agentserver-responses/tests/e2e/test_sample_e2e.py` — replicate sample logic inline and assert outputs programmatically.

## Implementation Phases

### Phase 0 — Research

Analyze retry policies from Temporal, Azure Durable Functions, and Celery. Compare parameter naming, default behaviors, and delay computation formulas. Document findings in `research.md`.

**Already done** — research was incorporated directly into the spec (see "Retry Policy Design — Industry Alignment" section).

### Phase 1 — Data Model & Contracts

Define the exact class interfaces, method signatures, and data flow for all three features.

**Deliverables:**
- `data-model.md` — RetryPolicy class definition, source field schema, stream queue lifecycle
- `contracts/public-api.md` — Updated public API surface showing new parameters on existing types
- `quickstart.md` — Copy of the 5 samples from the spec, annotated with implementation notes

### Phase 2 — RetryPolicy (US2, P2 — implemented first because it's self-contained)

Build the `RetryPolicy` class and integrate it into the execution loop.

**Why first**: RetryPolicy is the most self-contained feature — one new module, one integration point in `_manager.py`. No changes to `TaskRun` or `TaskContext` needed. This establishes the pattern for the retry loop that streaming will later interact with.

**Files:**
1. `_retry.py` — `RetryPolicy` class with `__init__`, `compute_delay(attempt)`, and 4 class-method presets
2. `_decorator.py` — Add `retry: RetryPolicy | None` to `DurableTaskOptions` and `@durable_task` params
3. `_manager.py` — Wrap `_execute_task` in a retry loop: catch exception, check `retry_on`, compute delay, sleep, update error field, increment `run_attempt`
4. `durable/__init__.py` — Export `RetryPolicy`
5. `core/__init__.py` — Re-export `RetryPolicy`
6. `tests/durable/test_retry.py` — Unit tests for delay computation, jitter bounds, presets, edge cases

### Phase 3 — Source Field (US3, P3 — simplest, low risk)

Add the `source` field to models and wire it through creation/retrieval.

**Why second**: Source is a pure pass-through field with zero behavioral complexity. Quick win that touches many files but with trivial changes per file.

**Files:**
1. `_models.py` — Add `source: dict[str, Any] | None` to `TaskInfo.__init__`, `__slots__`, `from_dict`, `to_dict`; add to `TaskCreateRequest.__init__` and `__slots__`
2. `_decorator.py` — Add `source` to `DurableTaskOptions`; add `source` param to `DurableTask.run()` and `.start()`
3. `_manager.py` — Pass `source` through `create_and_run` / `create_and_start` to `TaskCreateRequest`
4. `_client.py` — Include `source` in POST body when not None
5. `_local_provider.py` — Persist `source` in JSON; return in `from_dict` deserialization
6. `tests/durable/test_source.py` — Round-trip tests on both providers
7. `tests/durable/test_models.py` — Update existing model tests for source field

### Phase 4 — Streaming (US1, P1 — most complex, done last)

Add `ctx.stream()` and `async for chunk in run` support.

**Why last**: Streaming touches the most files and has the most complex lifecycle (producer/consumer coordination, error propagation, cleanup). Building it after retry and source means the simpler features are already tested and stable.

**Files:**
1. `_context.py` — Add `_stream_queue: asyncio.Queue | None` slot; add `async def stream(self, item: Any) -> None` method
2. `_run.py` — Add `_stream_queue: asyncio.Queue | None` slot; implement `__aiter__` and `__anext__` that yield from the queue until a sentinel is received
3. `_manager.py` — Create `asyncio.Queue` per task execution; pass to `TaskContext`; send sentinel on completion/failure/suspend; pass queue to `TaskRun`
4. `_decorator.py` — No changes needed (streaming is opt-in via `ctx.stream()` at runtime, not declared at decorator time)
5. `durable/__init__.py` — No new exports needed (stream is a method on existing `TaskContext`)
6. `tests/durable/test_streaming.py` — Happy path, error propagation, suspend mid-stream, non-streaming task iteration, result() still works

### Phase 5 — Integration, Samples & Sample E2E Tests

End-to-end validation, sample files, and e2e tests that verify each sample works.

**Files:**
1. Verify all 140 existing tests still pass
2. Run Black on all modified files
3. Create sample files under `azure-ai-agentserver-core/samples/` and `azure-ai-agentserver-invocations/samples/` matching the 5 samples in the spec
4. `tests/durable/test_sample_e2e.py` — E2E tests for each sample, following the pattern from `azure-ai-agentserver-responses/tests/e2e/test_sample_e2e.py`:
   - Replicate each sample's handler/task logic inline (don't import sample files)
   - Exercise the full lifecycle: create task → run → verify output
   - For streaming samples: verify chunks arrive in order + final result
   - For retry samples: verify retry behavior with intentionally-failing tasks
   - For source samples: verify source round-trips through create → get
   - For multi-turn/LangGraph samples: verify the full conversation flow
5. Final test count target: 140 existing + ≥30 new unit + ≥10 sample e2e = ≥180 total

## Complexity Tracking

No constitution violations. All principles pass.
