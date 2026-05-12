# Feature Specification: Streaming, Retry Policies, and Source Field for Durable Tasks

**Feature Branch**: `002-streaming-retry-source`  
**Created**: 2026-05-09  
**Status**: Draft  
**Input**: User description: "Add streaming output support, industry-standard retry policies, and source field to the durable task subsystem. All components live in the core package."

## User Scenarios & Testing *(mandatory)*

### User Story 1 — Stream incremental output from a long-running task (Priority: P1)

A developer building a research agent that produces results incrementally (e.g., search results, analysis steps, generated chunks) needs to emit output as it becomes available rather than waiting for the entire task to complete. The developer calls `ctx.stream(item)` inside their durable task function and the framework delivers each chunk to an async iterator on the caller's side.

**Why this priority**: Streaming is the most impactful missing capability. Long-running tasks that run for minutes or hours are opaque without it — callers cannot show progress, partial results, or real-time updates. This unlocks the interactive agent UX that users expect.

**Independent Test**: A developer decorates a function that calls `ctx.stream("chunk-1")` and `ctx.stream("chunk-2")`, invokes it with `.start(...)`, and iterates the returned `TaskRun` to receive each chunk in order. After the function completes, the iterator terminates cleanly.

**Acceptance Scenarios**:

1. **Given** a durable task function that calls `ctx.stream(item)` multiple times, **When** the caller iterates the `TaskRun` handle via `async for chunk in run`, **Then** each streamed item is yielded in order, and the iterator terminates after the function returns.
2. **Given** a streaming durable task, **When** the caller calls `run.start(...)` and begins iterating, **Then** intermediate chunks are available before the function completes (no buffering until completion).
3. **Given** a streaming durable task, **When** the function raises an unhandled exception after emitting some chunks, **Then** the iterator yields the chunks already emitted and then raises `TaskFailed` on the next iteration.
4. **Given** a streaming durable task, **When** the function calls `ctx.suspend(...)` after emitting some chunks, **Then** the iterator yields the chunks and then raises `TaskSuspended`.
5. **Given** a non-streaming durable task (never calls `ctx.stream(...)`), **When** the caller tries `async for chunk in run`, **Then** the iterator yields nothing but the final result is accessible via `run.result()`.
6. **Given** a durable task function, **When** the caller uses `run.result()` (blocking for completion), **Then** streaming is not required — `result()` waits for the final return value regardless of whether `ctx.stream()` was used.

---

### User Story 2 — Apply industry-standard retry policies to durable tasks (Priority: P2)

A developer building a tool-calling agent that invokes flaky external APIs (search engines, databases, LLMs) needs automatic retry on transient failures with configurable backoff, max attempts, and jitter. The developer configures a `RetryPolicy` on the `@durable_task` decorator or at call time, and the framework automatically retries the function on failure — tracking each attempt via the task's `error` field.

**Why this priority**: Retry is the second most requested feature after streaming. Real-world agents hit transient errors constantly. Without built-in retry, every developer hand-rolls exponential backoff with subtle bugs. Industry-standard policies (exponential backoff + jitter, fixed delay, linear backoff) eliminate this boilerplate.

**Independent Test**: A developer configures `retry=RetryPolicy(max_retries=3, strategy="exponential_backoff")`, the function fails twice and succeeds on the third attempt, and the caller receives the result — with the task's `error` field showing the last transient failure was cleared.

**Acceptance Scenarios**:

1. **Given** a durable task with `retry=RetryPolicy.exponential_backoff(max_retries=3)`, **When** the function raises `Exception` on the first two calls and succeeds on the third, **Then** the framework retries automatically and the caller receives the final result. The `ctx.run_attempt` reflects the current attempt number (0, 1, 2).
2. **Given** a durable task with a retry policy, **When** all retry attempts are exhausted, **Then** the framework marks the task as completed with a structured error `{"type": "exhausted_retries", "attempts": N, "last_error": "..."}` and the caller receives `TaskFailed`.
3. **Given** a durable task with `retry=RetryPolicy(initial_delay=1.0, backoff_coefficient=2.0, max_delay=30.0)`, **When** retries occur, **Then** the delay between attempts follows `min(1.0 * 2.0^attempt, 30.0)` with jitter (±25%) applied by default.
4. **Given** a durable task with a retry policy, **When** the function raises an exception listed in `retry_on` (e.g., `ConnectionError`, `TimeoutError`), **Then** the framework retries. If the exception is not in `retry_on`, the task fails immediately without retrying.
5. **Given** a durable task with `retry=RetryPolicy(...)`, **When** each retry occurs, **Then** the task's `error` field is updated with the latest failure details (via PATCH) so external observers can see intermediate failures.
6. **Given** a durable task with no retry policy (the default), **When** the function raises, **Then** the task fails immediately as before — no behavioral change from the existing implementation.
7. **Given** `RetryPolicy.fixed_delay(delay=5.0, max_retries=3)`, **When** retries occur, **Then** every retry waits exactly 5 seconds (coefficient=1.0, no exponential growth).
8. **Given** `RetryPolicy.linear_backoff(initial_delay=1.0, max_retries=5)`, **When** retries occur, **Then** delays grow as 1s, 2s, 3s, 4s, 5s (additive, not multiplicative).

---

### User Story 3 — Attach source provenance to durable tasks (Priority: P3)

A developer building a multi-agent orchestrator needs to record where each task came from — which upstream service, API call, or user action triggered it. The developer passes `source={"type": "api_call", "endpoint": "/chat", "request_id": "req_123"}` when creating a task and the framework persists it as an immutable field on the task record.

**Why this priority**: Source provenance is the simplest feature to implement but valuable for debugging, auditing, and multi-agent tracing. It's a pass-through field that requires minimal framework logic — just wire it through creation, storage, and retrieval.

**Independent Test**: A developer creates a durable task with `source={"type": "webhook", "url": "..."}`, retrieves the task info, and sees the `source` field intact and unchanged.

**Acceptance Scenarios**:

1. **Given** a durable task created with `source={"type": "api_call", "request_id": "req_123"}`, **When** the task is retrieved (via the provider or `TaskInfo`), **Then** the `source` field contains the exact dictionary passed at creation time.
2. **Given** a durable task created without a `source` field, **When** the task is retrieved, **Then** `source` is `None`.
3. **Given** a durable task with a `source` field, **When** the task is updated (PATCH), **Then** the `source` field is immutable — it cannot be changed after creation.
4. **Given** a durable task function decorated with `@durable_task(source={"origin": "system"})`, **When** tasks are created via `.run()` or `.start()`, **Then** the decorator-level source is used as the default, overridable at call time.

---

### Edge Cases

- What happens when `ctx.stream()` is called after the task is cancelled or shutdown is signaled? → The stream item is silently dropped and the function should check `ctx.cancel.is_set()`.
- What happens when a retry policy is combined with `ctx.suspend()`? → Suspension is not a failure; it bypasses retry logic entirely. Only raised exceptions trigger retries.
- What happens when `ctx.stream()` is called with a non-serializable object? → `TypeError` is raised immediately at the call site.
- What happens when `RetryPolicy(max_retries=0)` is configured? → Equivalent to no retry — the function runs once and fails on exception.
- What if the caller never iterates the stream (uses `run.result()` instead)? → Streamed items are buffered in memory and discarded after the task completes. No backpressure.
- What happens when `source` contains nested objects? → It's stored as-is (JSON-serializable dict). The framework does not validate its structure beyond serializability.

## Requirements *(mandatory)*

### Functional Requirements

**Streaming (US1)**

- **FR-001**: `TaskContext` MUST provide a `stream(item: Any) -> None` async method that emits an item to the caller's async iterator.
- **FR-002**: `TaskRun` MUST support `async for chunk in run` iteration that yields streamed items in order as they are produced.
- **FR-003**: `TaskRun.result()` MUST continue to work for both streaming and non-streaming tasks, returning the final return value of the function.
- **FR-004**: When a streaming task fails or suspends after emitting items, the iterator MUST yield all previously emitted items before raising the terminal exception (`TaskFailed` or `TaskSuspended`).
- **FR-005**: `ctx.stream()` MUST accept any JSON-serializable value (strings, dicts, lists, primitives).
- **FR-006**: Streamed items are in-memory only (delivered via `asyncio.Queue`) — they are NOT persisted to the task store.

**Retry Policies (US2)**

- **FR-007**: The framework MUST provide a `RetryPolicy` class with configurable `max_retries`, `initial_delay`, `max_delay`, `backoff_coefficient`, `jitter`, and `retry_on`.
- **FR-008**: Delay MUST be computed as `min(initial_delay * backoff_coefficient ^ attempt, max_delay)`. This formula covers exponential (`coefficient=2.0`), fixed (`coefficient=1.0`), and custom backoff curves.
- **FR-009**: `RetryPolicy` MUST provide class-method presets: `exponential_backoff(...)`, `fixed_delay(...)`, `linear_backoff(...)`, and `no_retry()`.
- **FR-010**: `RetryPolicy` MUST support an optional `retry_on` parameter — a tuple of exception types that trigger retry. When `retry_on=None` (default), ALL exceptions trigger retry. When specified, only matching exceptions retry; others fail immediately.
- **FR-011**: When retries are exhausted, the framework MUST mark the task completed with error `{"type": "exhausted_retries", "attempts": N, "last_error": "..."}` and raise `TaskFailed`.
- **FR-012**: Between retries, the framework MUST update the task's `error` field with the latest failure details so observers can see intermediate failures.
- **FR-013**: `RetryPolicy` can be set on `@durable_task(retry=...)` and/or overridden at call time via `.run(retry=...)` or `.start(retry=...)`.
- **FR-014**: The `ctx.run_attempt` field MUST reflect the current attempt (0-indexed).
- **FR-015**: When `jitter=True` (default), the delay MUST include a random component of ±25% of the computed delay to prevent thundering herd.

**Source Field (US3)**

- **FR-015**: `TaskCreateRequest` MUST support an optional `source: dict[str, Any] | None` field.
- **FR-016**: `TaskInfo` MUST include a `source: dict[str, Any] | None` field, populated from creation.
- **FR-017**: The `source` field MUST be immutable after task creation — PATCH requests MUST NOT modify it.
- **FR-018**: `@durable_task(source=...)` MUST allow setting a default source at the decorator level, overridable at `.run(source=...)` / `.start(source=...)`.
- **FR-019**: Both providers (`HostedDurableTaskProvider` and `LocalFileDurableTaskProvider`) MUST persist and return the `source` field.

### Key Entities

- **`RetryPolicy`**: Configuration for automatic retry behavior. Properties: `max_retries` (int), `strategy` (Literal), `initial_delay` (float, seconds), `max_delay` (float, seconds), `backoff_coefficient` (float), `jitter` (bool), `retry_on` (tuple of exception types | None).
- **Source**: An opaque `dict[str, Any]` attached at creation time. Not a separate class — just a field on `TaskCreateRequest`, `TaskInfo`, and `DurableTaskOptions`.
- **Stream queue**: An `asyncio.Queue` bridging `ctx.stream()` calls (producer) to `TaskRun.__aiter__` (consumer). Created per-task execution, not persisted.

### Retry Policy Design — Industry Alignment

The `RetryPolicy` design draws from three production-grade frameworks:

| Framework | Key Properties | Our Equivalent |
|-----------|---------------|----------------|
| **Temporal** (`temporalio.common.RetryPolicy`) | `initial_interval`, `backoff_coefficient`, `maximum_interval`, `maximum_attempts`, `non_retryable_error_types` | `initial_delay`, `backoff_coefficient`, `max_delay`, `max_retries`, `retry_on` (inverted — opt-in vs opt-out) |
| **Azure Durable Functions** (`RetryOptions`) | `first_retry_interval`, `max_number_of_attempts`, `backoff_coefficient` | `initial_delay`, `max_retries`, `backoff_coefficient` |
| **Celery** (`@task(autoretry_for=..., retry_backoff=...)`) | `autoretry_for`, `retry_backoff`, `retry_backoff_max`, `retry_jitter`, `max_retries` | `retry_on`, `backoff_coefficient`, `max_delay`, `jitter`, `max_retries` |

**Design decisions:**

1. **`initial_delay` + `backoff_coefficient`** replaces `strategy` enum — this is what Temporal and DTF both use. `coefficient=1.0` gives fixed delay, `coefficient=2.0` gives exponential backoff, linear is `coefficient=1.0` with increasing base.
2. **`retry_on` (opt-in)** rather than Temporal's `non_retryable_error_types` (opt-out) — simpler default: nothing retries unless you say so. When `retry_on=None`, ALL exceptions trigger retry (Temporal's default behavior).
3. **`jitter=True` by default** — Celery defaults to jitter=True, and it's the right default for distributed systems (thundering herd prevention).
4. **Built-in presets** for the most common patterns (see Convenience Presets below).

#### RetryPolicy Class

```python
class RetryPolicy:
    """Retry configuration for durable tasks.

    Delay formula: min(initial_delay * backoff_coefficient ^ attempt, max_delay)
    With jitter: delay * uniform(0.75, 1.25)
    """

    __slots__ = (
        "max_retries", "initial_delay", "max_delay",
        "backoff_coefficient", "jitter", "retry_on",
    )

    def __init__(
        self,
        *,
        max_retries: int = 3,
        initial_delay: float = 1.0,
        max_delay: float = 60.0,
        backoff_coefficient: float = 2.0,
        jitter: bool = True,
        retry_on: tuple[type[BaseException], ...] | None = None,
    ) -> None: ...
```

#### Convenience Presets

```python
# Exponential backoff — the most common pattern (Temporal/DTF default)
RetryPolicy.exponential_backoff(
    max_retries=5,
    initial_delay=1.0,
    max_delay=60.0,
    jitter=True,
)

# Fixed delay — retry at constant intervals (useful for rate-limited APIs)
RetryPolicy.fixed_delay(
    max_retries=3,
    delay=5.0,
)

# Linear backoff — delay grows linearly (1s, 2s, 3s, 4s, ...)
RetryPolicy.linear_backoff(
    max_retries=5,
    initial_delay=1.0,
    max_delay=30.0,
)

# No retry — explicit opt-out (equivalent to not setting retry at all)
RetryPolicy.no_retry()
```

## Samples *(mandatory)*

### Sample 1 — Core: Streaming research agent

A minimal core-only example showing `ctx.stream()` for incremental output.

```python
"""Streaming research agent — emits findings as they're discovered.

Usage::

    python streaming_research_agent.py

    # In another terminal:
    import asyncio
    from streaming_research_agent import research

    async def main():
        run = await research.start(
            task_id="research-001",
            input={"topic": "quantum computing breakthroughs 2026"},
        )
        # Stream partial results as they arrive
        async for finding in run:
            print(f"Finding: {finding}")

        # Final summary
        result = await run.result()
        print(f"Summary: {result}")

    asyncio.run(main())
"""
from azure.ai.agentserver.core import AgentServerHost
from azure.ai.agentserver.core.durable import (
    TaskContext,
    durable_task,
)


app = AgentServerHost()


@durable_task(title="web-research")
async def research(ctx: TaskContext[dict]) -> dict:
    """Research a topic and stream findings incrementally."""
    topic = ctx.input["topic"]
    sources = [
        "arxiv papers",
        "news articles",
        "industry reports",
    ]
    findings = []

    for i, source in enumerate(sources):
        ctx.metadata.set("phase", f"searching {source}")
        ctx.metadata.set("progress", f"{i + 1}/{len(sources)}")

        # Simulate searching each source
        finding = {
            "source": source,
            "summary": f"Key insight from {source} about {topic}",
            "relevance": 0.9 - (i * 0.1),
        }
        findings.append(finding)

        # Stream each finding to the caller as it's discovered
        await ctx.stream(finding)

    return {
        "topic": topic,
        "total_findings": len(findings),
        "findings": findings,
    }


if __name__ == "__main__":
    app.run()
```

### Sample 2 — Core: Retry with exponential backoff

Shows a flaky tool-calling task with retry policies.

```python
"""Flaky tool agent — demonstrates retry policies with backoff.

Usage::

    result = await flaky_search.run(
        task_id="search-001",
        input={"query": "latest AI papers"},
    )
"""
from azure.ai.agentserver.core.durable import (
    RetryPolicy,
    TaskContext,
    durable_task,
)


# Exponential backoff: 1s → 2s → 4s → 8s → 16s (capped at 30s)
# Only retry on ConnectionError and TimeoutError
@durable_task(
    title="web-search",
    retry=RetryPolicy.exponential_backoff(
        max_retries=5,
        initial_delay=1.0,
        max_delay=30.0,
        retry_on=(ConnectionError, TimeoutError),
    ),
)
async def flaky_search(ctx: TaskContext[dict]) -> dict:
    """Search the web — may fail transiently."""
    query = ctx.input["query"]

    # ctx.run_attempt tracks which attempt we're on (0-indexed)
    ctx.metadata.set("attempt", ctx.run_attempt)

    # Simulate a flaky API call
    result = await call_search_api(query)  # may raise ConnectionError
    return {"query": query, "results": result}


# Fixed delay: retry every 5 seconds (for rate-limited APIs)
@durable_task(
    title="rate-limited-api",
    retry=RetryPolicy.fixed_delay(
        max_retries=3,
        delay=5.0,
        retry_on=(RateLimitError,),
    ),
)
async def call_rate_limited(ctx: TaskContext[dict]) -> dict:
    """Call a rate-limited API with fixed-delay retry."""
    return await make_api_call(ctx.input)
```

### Sample 3 — Core: Source provenance tracking

Shows `source` for multi-agent tracing.

```python
"""Source provenance — trace where tasks come from.

Usage::

    result = await analysis.run(
        task_id="analysis-001",
        input={"data": [1, 2, 3]},
        source={
            "type": "api_call",
            "endpoint": "/analyze",
            "request_id": "req_abc123",
            "triggered_by": "user:alice",
        },
    )
"""
from azure.ai.agentserver.core.durable import (
    TaskContext,
    durable_task,
)


# Default source at decorator level — all tasks created by this
# function inherit this source unless overridden at call time.
@durable_task(
    title="data-analysis",
    source={"origin": "analytics-service", "version": "2.1"},
)
async def analysis(ctx: TaskContext[dict]) -> dict:
    """Analyze data — source is recorded for auditing."""
    return {"mean": sum(ctx.input["data"]) / len(ctx.input["data"])}
```

### Sample 4 — Invocations: Multi-turn durable research agent

A complete invocations-based agent that uses durable tasks for crash-safe
multi-turn conversations with streaming progress, retry on flaky tools,
and human-in-the-loop suspend/resume.

```python
"""Multi-turn durable research agent with streaming, retry, and suspend/resume.

Demonstrates:
  - Durable tasks for crash-safe long-running work
  - Streaming intermediate results to callers
  - Retry policies on flaky tool calls
  - Human-in-the-loop suspend/resume for approval workflows
  - Source provenance for multi-turn tracing

.. warning::

    **File-based persistence is for sample/development purposes ONLY.**

    This sample uses JSON files on disk (``$HOME/.sample-store/``) for
    session history and invocation results. This is NOT suitable for
    production. In production, use a proper persistence backend such as
    Cosmos DB, Redis, PostgreSQL, or Azure Blob Storage. File-based stores
    do not support concurrent access, have no transactional guarantees,
    and are not replicated across instances.

Usage::

    # Start the agent
    python multiturn_durable_agent.py

    # Turn 1 — start research
    curl -X POST "http://localhost:8088/invocations?agent_session_id=sess-001" \
        -H "Content-Type: application/json" \
        -d '{"message": "Research the latest advances in protein folding"}'
    # -> 202 {"invocation_id": "inv-001", "status": "in_progress"}

    # Poll for results (streamed progress visible via metadata)
    curl http://localhost:8088/invocations/inv-001
    # -> {"status": "completed", "output": {...}}

    # Turn 2 — agent asks for approval (suspend)
    curl -X POST "http://localhost:8088/invocations?agent_session_id=sess-001" \
        -d '{"message": "Write a report and publish it"}'
    # -> 202 (agent suspends for approval)

    # Poll — sees awaiting_input
    curl http://localhost:8088/invocations/inv-002
    # -> {"status": "suspended", "reason": "awaiting_approval", ...}

    # Turn 3 — approve and resume
    curl -X POST http://localhost:8088/tasks/resume \
        -d '{"id": "inv-002"}'
    # -> 202

    curl -X POST "http://localhost:8088/invocations?agent_session_id=sess-001" \
        -d '{"message": "Yes, approved"}'
"""
import json
import os
from typing import Any

from starlette.requests import Request
from starlette.responses import JSONResponse, Response

from azure.ai.agentserver.core.durable import (
    RetryPolicy,
    TaskContext,
    TaskRun,
    durable_task,
)
from azure.ai.agentserver.invocations import InvocationAgentServerHost


app = InvocationAgentServerHost()


# ─── File-based persistence (SAMPLE ONLY — NOT FOR PRODUCTION) ────
#
# ⚠️  Replace with Cosmos DB, Redis, PostgreSQL, or another durable
#     store before deploying to production.  File-based stores lack
#     concurrency safety, replication, and transactional guarantees.
#

HOME = os.environ.get("HOME", "/home/session")
_STORE_DIR = os.path.join(HOME, ".sample-store")


def _store_path(kind: str, key: str) -> str:
    """Return the file path for a given store kind and key."""
    d = os.path.join(_STORE_DIR, kind)
    os.makedirs(d, exist_ok=True)
    safe_key = key.replace("/", "_").replace("..", "_")
    return os.path.join(d, f"{safe_key}.json")


def _save(kind: str, key: str, data: Any) -> None:
    """Write a JSON record to a file. NOT production-safe."""
    path = _store_path(kind, key)
    with open(path, "w") as f:
        json.dump(data, f, default=str)


def _load(kind: str, key: str) -> dict | None:
    """Read a JSON record from a file, or None if missing."""
    path = _store_path(kind, key)
    if not os.path.exists(path):
        return None
    with open(path) as f:
        return json.load(f)


def _load_session(session_id: str) -> list[dict]:
    """Load session history from file."""
    data = _load("sessions", session_id)
    return data if isinstance(data, list) else []


def _save_session(session_id: str, history: list[dict]) -> None:
    """Save session history to file."""
    _save("sessions", session_id, history)


# ─── Durable task: the agent's per-turn work ───────────────────────

@durable_task(
    title=lambda input, tid: f"research-turn-{tid[:8]}",
    retry=RetryPolicy.exponential_backoff(
        max_retries=3,
        initial_delay=2.0,
        max_delay=30.0,
        retry_on=(ConnectionError, TimeoutError),
    ),
)
async def research_turn(ctx: TaskContext[dict]) -> dict:
    """Process one turn of multi-turn research.

    Streams intermediate findings, suspends for approval when needed.
    """
    message = ctx.input["message"]
    history = ctx.input.get("history", [])

    # Phase 1: Research (stream findings as they arrive)
    ctx.metadata.set("phase", "researching")
    findings = []
    for i in range(3):
        finding = await _search_web(message, page=i)  # may raise ConnectionError
        findings.append(finding)
        await ctx.stream({"type": "finding", "data": finding})
        ctx.metadata.set("findings_count", i + 1)

    # Phase 2: Check if approval is needed
    if "publish" in message.lower() or "report" in message.lower():
        ctx.metadata.set("phase", "awaiting_approval")
        return await ctx.suspend(
            reason="awaiting_approval",
            output={"draft_findings": findings},
        )

    # Phase 3: Synthesize
    ctx.metadata.set("phase", "synthesizing")
    summary = f"Based on {len(findings)} sources: {message}"
    await ctx.stream({"type": "summary", "data": summary})

    return {
        "reply": summary,
        "findings": findings,
        "turn": len(history) + 1,
    }


# ─── HTTP handlers ─────────────────────────────────────────────────

@app.invoke_handler
async def handle_invoke(request: Request) -> Response:
    """Start a research turn as a crash-safe durable task."""
    data = await request.json()
    session_id = request.state.session_id
    invocation_id = request.state.invocation_id

    # Load session history from file store
    history = _load_session(session_id)
    history.append({"role": "user", "content": data.get("message", "")})
    _save_session(session_id, history)

    # Seed result store so polling returns something immediately
    _save("results", invocation_id, {
        "invocation_id": invocation_id,
        "status": "in_progress",
    })

    # Fire-and-forget: the durable task runs in the background
    run: TaskRun = await research_turn.start(
        task_id=invocation_id,
        input={
            "message": data.get("message", ""),
            "history": history,
        },
        session_id=session_id,
        source={
            "type": "invocation",
            "invocation_id": invocation_id,
            "session_id": session_id,
        },
    )

    # Consume stream in background, persist result when done
    import asyncio
    asyncio.create_task(
        _consume_and_store(invocation_id, session_id, run)
    )

    return JSONResponse(
        {"invocation_id": invocation_id, "status": "in_progress"},
        status_code=202,
    )


async def _consume_and_store(
    invocation_id: str,
    session_id: str,
    run: TaskRun,
) -> None:
    """Consume streamed chunks, then persist final result to file store."""
    chunks = []
    try:
        async for chunk in run:
            chunks.append(chunk)

        result = await run.result()

        # Update session history with assistant reply
        history = _load_session(session_id)
        history.append({"role": "assistant", "content": result.get("reply", "")})
        _save_session(session_id, history)

        # Persist invocation result
        _save("results", invocation_id, {
            "invocation_id": invocation_id,
            "status": "completed",
            "output": result,
            "streamed_chunks": len(chunks),
        })
    except Exception as exc:
        _save("results", invocation_id, {
            "invocation_id": invocation_id,
            "status": "failed",
            "error": str(exc),
        })


@app.get_invocation_handler
async def handle_get(request: Request) -> Response:
    """Poll for results from the file store."""
    invocation_id = request.state.invocation_id
    record = _load("results", invocation_id)
    if record:
        return JSONResponse(record)
    return JSONResponse(
        {"invocation_id": invocation_id, "status": "in_progress"},
    )


# ─── Helpers ───────────────────────────────────────────────────────

async def _search_web(query: str, page: int = 0) -> dict:
    """Simulate a flaky web search API."""
    import asyncio
    await asyncio.sleep(0.5)
    return {"query": query, "page": page, "result": f"Finding for '{query}' (page {page})"}


if __name__ == "__main__":
    app.run()
```

### Sample 5 — Invocations: LangGraph durable agent with streaming

A LangGraph-based multi-turn agent on the invocations protocol that uses
durable tasks for crash-safe execution, streaming for token-by-token
delivery, and suspend/resume for human-in-the-loop approval.

```python
"""LangGraph durable agent — multi-turn with streaming and crash recovery.

Architecture:
  - LangGraph handles conversation state + tool orchestration
  - Durable tasks handle crash safety + lease management
  - Streaming delivers LLM tokens and tool results incrementally
  - $HOME/.checkpoints/ stores LangGraph checkpoints (survives restarts)

Each invocation maps to one durable task. The task's lifetime is
exactly one turn — it is deleted on completion. LangGraph checkpoints
carry state across turns; the task store coordinates execution.

.. warning::

    **File-based result store is for sample/development purposes ONLY.**

    This sample uses JSON files under ``$HOME/.sample-store/`` for
    invocation results. This is NOT suitable for production. In production,
    replace the file store with Cosmos DB, Redis, PostgreSQL, or another
    properly replicated, concurrency-safe persistence backend.

    The LangGraph checkpoint SQLite DB (``$HOME/.checkpoints/``) is also
    a local convenience; in production consider LangGraph's Postgres or
    Redis checkpointers.

Usage::

    python langgraph_durable_agent.py

    # Turn 1 — ask a question
    curl -X POST "http://localhost:8088/invocations?agent_session_id=sess-001" \
        -H "Content-Type: application/json" \
        -d '{"message": "Search for the latest news about Mars exploration"}'

    # Poll until complete
    curl http://localhost:8088/invocations/{invocation_id}
"""
import json
import os
from typing import Any

from starlette.requests import Request
from starlette.responses import JSONResponse, Response

from azure.ai.agentserver.core.durable import (
    RetryPolicy,
    TaskContext,
    durable_task,
)
from azure.ai.agentserver.invocations import InvocationAgentServerHost

# LangGraph imports
from langchain_openai import AzureChatOpenAI
from langchain.tools import tool
from langgraph.checkpoint.sqlite.aio import AsyncSqliteSaver
from langgraph.graph import START, MessagesState, StateGraph
from langgraph.prebuilt import ToolNode, tools_condition
from langgraph.types import Command, interrupt
from langchain_core.messages import HumanMessage


app = InvocationAgentServerHost()

HOME = os.environ.get("HOME", "/home/session")
CHECKPOINT_DB = os.path.join(HOME, ".checkpoints", "langgraph.db")


# ─── File-based result store (SAMPLE ONLY — NOT FOR PRODUCTION) ───
#
# ⚠️  Replace with Cosmos DB, Redis, PostgreSQL, or another durable
#     store before deploying to production.  File-based stores lack
#     concurrency safety, replication, and transactional guarantees.
#

_STORE_DIR = os.path.join(HOME, ".sample-store", "lg-results")


def _save_result(invocation_id: str, data: dict) -> None:
    """Persist invocation result as a JSON file. NOT production-safe."""
    os.makedirs(_STORE_DIR, exist_ok=True)
    safe_id = invocation_id.replace("/", "_").replace("..", "_")
    path = os.path.join(_STORE_DIR, f"{safe_id}.json")
    with open(path, "w") as f:
        json.dump(data, f, default=str)


def _load_result(invocation_id: str) -> dict | None:
    """Load invocation result from file, or None if missing."""
    safe_id = invocation_id.replace("/", "_").replace("..", "_")
    path = os.path.join(_STORE_DIR, f"{safe_id}.json")
    if not os.path.exists(path):
        return None
    with open(path) as f:
        return json.load(f)


# ─── LangGraph tools ──────────────────────────────────────────────

@tool
def ask_user(question: str) -> str:
    """Ask the human user a clarifying question and wait for their reply."""
    return interrupt({"question": question})

@tool
def web_search(query: str) -> str:
    """Search the web and return findings."""
    return f"[Results for: {query}] - Top findings about the topic..."


# ─── Build the LangGraph ──────────────────────────────────────────

def create_graph():
    llm = AzureChatOpenAI(model="gpt-4o", api_version="2024-12-01-preview")
    llm_with_tools = llm.bind_tools([ask_user, web_search])

    def agent_node(state: MessagesState):
        return {"messages": [llm_with_tools.invoke(state["messages"])]}

    g = StateGraph(MessagesState)
    g.add_node("agent", agent_node)
    g.add_node("tools", ToolNode([ask_user, web_search]))
    g.add_edge(START, "agent")
    g.add_conditional_edges("agent", tools_condition)
    g.add_edge("tools", "agent")
    return g


# ─── Durable task: one turn of the LangGraph agent ────────────────

@durable_task(
    title=lambda input, tid: f"lg-turn-{tid[:8]}",
    retry=RetryPolicy.exponential_backoff(
        max_retries=3,
        initial_delay=1.0,
        retry_on=(ConnectionError, TimeoutError),
    ),
)
async def langgraph_turn(ctx: TaskContext[dict]) -> dict:
    """Execute one LangGraph turn with streaming + suspend/resume.

    Crash-safety:
      - Before delivering input to LangGraph, mark `input_applied=True`
        in task metadata.
      - On recovery (ctx.run_attempt > 0 or metadata shows input_applied),
        drain the graph (continue from last checkpoint) instead of
        re-applying input.
    """
    thread_id = ctx.input["thread_id"]
    user_message = ctx.input["message"]

    os.makedirs(os.path.dirname(CHECKPOINT_DB), exist_ok=True)
    config = {"configurable": {"thread_id": thread_id}}

    async with AsyncSqliteSaver.from_conn_string(CHECKPOINT_DB) as saver:
        compiled = create_graph().compile(checkpointer=saver)
        state = await compiled.aget_state(config)

        # Determine if we need to resume (interrupt) or start fresh
        is_at_interrupt = (
            state and getattr(state, "tasks", None)
            and any(getattr(t, "interrupts", None) for t in state.tasks)
        )

        if is_at_interrupt:
            ctx.metadata.set("phase", "resuming_from_interrupt")
            await ctx.stream({"type": "status", "message": "Resuming from interrupt..."})
            cmd = Command(resume=user_message)
        else:
            ctx.metadata.set("phase", "processing_message")
            await ctx.stream({"type": "status", "message": "Processing your message..."})
            cmd = {"messages": [HumanMessage(content=user_message)]}

        # Mark before delivery for crash recovery
        ctx.metadata.set("input_applied", True)
        await compiled.ainvoke(cmd, config=config)
        final_state = await compiled.aget_state(config)

    # Stream the final messages back
    messages = final_state.values.get("messages", []) if final_state.values else []
    for msg in messages[-3:]:  # Last few messages
        await ctx.stream({
            "type": "message",
            "role": getattr(msg, "type", "unknown"),
            "content": getattr(msg, "content", ""),
        })

    # Check if graph is now at an interrupt (human-in-the-loop)
    awaiting = (
        final_state and getattr(final_state, "tasks", None)
        and any(getattr(t, "interrupts", None) for t in final_state.tasks)
    )
    if awaiting:
        prompts = []
        for t in final_state.tasks:
            for it in getattr(t, "interrupts", None) or []:
                prompts.append(getattr(it, "value", it))

        return await ctx.suspend(
            reason="awaiting_user_input",
            output={"awaiting_input": True, "prompts": prompts},
        )

    # Collect final reply
    last_ai = next(
        (m for m in reversed(messages) if getattr(m, "type", "") == "ai"),
        None,
    )
    return {
        "reply": getattr(last_ai, "content", "") if last_ai else "",
        "awaiting_input": False,
        "message_count": len(messages),
    }


# ─── HTTP handlers ─────────────────────────────────────────────────

@app.invoke_handler
async def handle_invoke(request: Request) -> Response:
    session_id = request.state.session_id
    invocation_id = request.state.invocation_id
    data = await request.json()

    # Seed result store so polling returns something immediately
    _save_result(invocation_id, {
        "invocation_id": invocation_id,
        "status": "in_progress",
    })

    run = await langgraph_turn.start(
        task_id=invocation_id,
        input={
            "message": data.get("message", ""),
            "thread_id": session_id,
        },
        session_id=session_id,
        source={"type": "invocation", "session_id": session_id},
    )

    # Consume stream and persist result to file store
    import asyncio
    asyncio.create_task(_consume(invocation_id, run))

    return JSONResponse(
        {"invocation_id": invocation_id, "status": "in_progress"},
        status_code=202,
    )


async def _consume(invocation_id: str, run) -> None:
    """Consume streamed output and persist final result to file store."""
    try:
        chunks = []
        async for chunk in run:
            chunks.append(chunk)
        result = await run.result()
        _save_result(invocation_id, {
            "invocation_id": invocation_id,
            "status": "completed",
            "output": result,
        })
    except Exception as exc:
        _save_result(invocation_id, {
            "invocation_id": invocation_id,
            "status": "failed" if "Suspended" not in type(exc).__name__ else "suspended",
            "error": str(exc),
        })


@app.get_invocation_handler
async def handle_get(request: Request) -> Response:
    """Poll for results from the file store."""
    invocation_id = request.state.invocation_id
    record = _load_result(invocation_id)
    if record:
        return JSONResponse(record)
    return JSONResponse({"invocation_id": invocation_id, "status": "in_progress"})


if __name__ == "__main__":
    app.run()
```

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: A streaming durable task delivers the first chunk to the caller within 50ms of `ctx.stream()` being called (no artificial buffering).
- **SC-002**: Retry policies correctly compute delays matching the configured strategy (verified by unit tests with mocked sleep).
- **SC-003**: The `source` field round-trips through create → get → list without modification on both hosted and local providers.
- **SC-004**: All existing 140 tests continue to pass — zero regressions from these additions.
- **SC-005**: Each new feature has ≥10 unit tests covering happy paths, edge cases, and error conditions.
- **SC-006**: All 5 samples run without import errors (tested via `python -c "import ..."` or equivalent syntax check).
- **SC-007**: Each sample MUST have a corresponding e2e test that exercises the sample's handler/logic end-to-end, following the pattern established in `azure-ai-agentserver-responses/tests/e2e/test_sample_e2e.py`. Tests replicate the sample handler inline and verify outputs/behavior programmatically — not just import checks.

## Assumptions

- **Local file provider is the default everywhere**: The Task Storage API is not yet generally available. Even in hosted environments (`FOUNDRY_HOSTING_ENVIRONMENT` is set), the `LocalFileDurableTaskProvider` is used by default. The HTTP-backed `HostedDurableTaskProvider` is gated behind the `FOUNDRY_TASK_API_ENABLED=1` environment variable. When the APIs are lit up and stable, the default will flip to use the hosted provider automatically when `FOUNDRY_HOSTING_ENVIRONMENT` is present.
- **Streaming is in-memory only**: Streamed items are delivered via `asyncio.Queue` between the task function and the caller within the same process. They are not persisted to the task store or forwarded over HTTP. This is a local-process convenience — external observers see progress via `ctx.metadata`, not the stream.
- **Retry is per-execution, not per-crash**: `RetryPolicy` controls retries within a single process execution. Crash recovery (re-acquiring a stale lease after container restart) is handled by the existing recovery mechanism and is orthogonal to `RetryPolicy`.
- **No backpressure on streams**: If the caller is slow to consume, items accumulate in the queue without bound. Backpressure (bounded queue with blocking put) is out of scope for this iteration.
- **`source` immutability is enforced by the SDK, not the server**: The Task Storage API may not enforce immutability on `source`. Our SDK simply never includes `source` in PATCH requests.
- **`TaskSuspended` bypasses retry**: Calling `ctx.suspend()` is an intentional action, not a failure. It does not consume a retry attempt.
- **No new dependencies**: Retry delays use `asyncio.sleep`. Jitter uses `random`. No external libraries needed.
- **All changes are in `azure-ai-agentserver-core`**: The `durable/` subpackage within core. Protocol packages (`invocations`, `responses`) integrate via the existing public API.

### Provider Selection Logic

```
┌──────────────────────────────────────────────────────────────┐
│  FOUNDRY_HOSTING_ENVIRONMENT set?                            │
│    NO  ──────────────────────────► LocalFileDurableTaskProvider│
│    YES ──► FOUNDRY_TASK_API_ENABLED=1?                       │
│              NO  ────────────────► LocalFileDurableTaskProvider│
│              YES ────────────────► HostedDurableTaskProvider   │
└──────────────────────────────────────────────────────────────┘
```

| Environment variable | Values | Effect |
|---|---|---|
| `FOUNDRY_HOSTING_ENVIRONMENT` | any non-empty string | Indicates hosted container. Does NOT automatically enable Task API. |
| `FOUNDRY_TASK_API_ENABLED` | `1`, `true`, `yes` | Opts in to the HTTP-backed provider. Only effective when `FOUNDRY_HOSTING_ENVIRONMENT` is also set. |

When `FOUNDRY_TASK_API_ENABLED` is not set in a hosted environment, the manager logs:
```
Hosted environment detected but Task Storage API not yet enabled.
Using local file provider. Set FOUNDRY_TASK_API_ENABLED=1 to use
the HTTP-backed provider when the APIs are available.
```
