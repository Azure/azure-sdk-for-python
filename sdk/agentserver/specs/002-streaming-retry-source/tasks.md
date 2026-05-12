# Tasks: Streaming, Retry Policies, and Source Field

**Input**: Design documents from `specs/002-streaming-retry-source/`
**Prerequisites**: plan.md ✅, spec.md ✅, research.md ✅, data-model.md ✅, contracts/ ✅, quickstart.md ✅

**Tests**: Included — each phase includes its own test tasks.

**Organization**: Tasks grouped by implementation phase from the plan. Phases are ordered by dependency (retry → source → streaming → integration).

## Format: `[ID] [P?] [Phase] Description`

- **[P]**: Can run in parallel with other [P] tasks in the same phase
- **[Phase]**: Which implementation phase (Ph2=Retry, Ph3=Source, Ph4=Streaming, Ph5=Integration)
- Exact file paths included in all descriptions

## Path Conventions

- **Source**: `azure-ai-agentserver-core/azure/ai/agentserver/core/durable/`
- **Tests**: `azure-ai-agentserver-core/tests/durable/`
- **Core samples**: `azure-ai-agentserver-core/samples/`
- **Invocations samples**: `azure-ai-agentserver-invocations/samples/`

---

## Phase 2: RetryPolicy (self-contained — US2)

**Purpose**: Build `RetryPolicy` class and integrate into the execution loop.

**⚠️ CRITICAL**: Must be complete before Phase 4 (streaming interacts with retry loop).

### Implementation

- [ ] T101 [P] Create `_retry.py` — Define `RetryPolicy` class with `__slots__` (`initial_delay`, `backoff_coefficient`, `max_delay`, `max_attempts`, `retry_on`, `jitter`). Constructor takes keyword-only args with defaults: `initial_delay=timedelta(seconds=1)`, `backoff_coefficient=2.0`, `max_delay=timedelta(seconds=60)`, `max_attempts=3`, `retry_on=None`, `jitter=True`. Add `__init__` validation: `initial_delay > 0`, `backoff_coefficient >= 1.0`, `max_delay >= initial_delay`, `max_attempts >= 1`, `retry_on` entries must be `Exception` subclasses. Add `__repr__` and `__eq__`.

- [ ] T102 [P] Add `compute_delay(attempt: int) -> float` to `RetryPolicy` in `_retry.py` — Formula: `min(initial_delay.total_seconds() * backoff_coefficient ** attempt, max_delay.total_seconds())`. When `jitter=True`, multiply by `random.uniform(0.75, 1.25)`. Return seconds as float.

- [ ] T103 [P] Add `should_retry(attempt: int, error: Exception) -> bool` to `RetryPolicy` in `_retry.py` — Return `False` if `attempt >= max_attempts - 1` (0-indexed, so attempt 0 is the first try). If `retry_on is None`, return `True` for any exception. If `retry_on` is set, return `True` only if `isinstance(error, self.retry_on)`.

- [ ] T104 [P] Add 4 class-method presets to `RetryPolicy` in `_retry.py`:
  - `exponential_backoff(*, max_attempts=3)` → `RetryPolicy(initial_delay=1s, backoff_coefficient=2.0, max_delay=60s, max_attempts=max_attempts, jitter=True)`
  - `fixed_delay(*, delay=timedelta(seconds=5), max_attempts=3)` → `RetryPolicy(initial_delay=delay, backoff_coefficient=1.0, max_delay=delay, max_attempts=max_attempts, jitter=False)`
  - `linear_backoff(*, initial_delay=timedelta(seconds=1), max_attempts=5)` → `RetryPolicy(initial_delay=initial_delay, backoff_coefficient=1.0, max_delay=60s, max_attempts=max_attempts, jitter=False)` — Note: linear uses additive delay via `compute_delay` override logic: `initial_delay * (attempt + 1)` capped at `max_delay`.
  - `no_retry()` → `RetryPolicy(initial_delay=timedelta(0), backoff_coefficient=1.0, max_delay=timedelta(0), max_attempts=1, jitter=False)`

- [ ] T105 Modify `_decorator.py` — Add `retry: RetryPolicy | None` to:
  1. `DurableTaskOptions.__slots__` (add `"retry"`)
  2. `DurableTaskOptions.__init__` (add `retry: RetryPolicy | None = None` param, assign `self.retry = retry`)
  3. `DurableTaskOptions.__repr__` (include retry)
  4. `@durable_task` function signature (add `retry: RetryPolicy | None = None` kwarg)
  5. `@durable_task` overload signatures (add retry param)
  6. `_wrap` inside `durable_task` (pass `retry=retry` to `DurableTaskOptions`)
  7. `DurableTask.run()` signature (add `retry: RetryPolicy | None = None` kwarg)
  8. `DurableTask.start()` signature (add `retry: RetryPolicy | None = None` kwarg)
  9. `DurableTask.run()` body — pass retry to `manager.create_and_run(retry=retry or self._opts.retry)`
  10. `DurableTask.start()` body — pass retry to `manager.create_and_start(retry=retry or self._opts.retry)`
  11. `DurableTask.options()` — add `retry` param and merge

- [ ] T106 Modify `_manager.py` — Add retry parameter plumbing:
  1. Add `retry: RetryPolicy | None = None` param to `create_and_run` and `create_and_start` signatures
  2. Pass `retry` through to `_execute_task` call
  3. Add `retry: RetryPolicy | None = None` param to `_execute_task` signature
  4. Import `RetryPolicy` from `._retry`

- [ ] T107 Modify `_manager.py` `_execute_task` — Wrap the existing body in a retry loop:
  ```
  attempt = 0
  while True:
      ctx.run_attempt = attempt
      try:
          result = await fn(ctx)
          # ... existing success/suspend handling ...
          break
      except asyncio.CancelledError:
          # ... existing cancel handling (no retry) ...
          break
      except Exception as exc:
          if retry and retry.should_retry(attempt, exc):
              delay = retry.compute_delay(attempt)
              logger.warning("Task %s attempt %d failed (%s), retrying in %.1fs", task_id, attempt, exc, delay)
              # Update error field so observers see intermediate failures
              await self._provider.update(task_id, TaskPatchRequest(error={"type": type(exc).__name__, "message": str(exc), "attempt": attempt}))
              await asyncio.sleep(delay)
              attempt += 1
              continue
          # Exhausted or non-retryable — existing failure handling
          # If retry was active, use structured exhausted error
          ...
          break
  ```

- [ ] T108 Modify `durable/__init__.py` — Add `RetryPolicy` to imports and `__all__`

- [ ] T109 Modify `core/__init__.py` — Add `RetryPolicy` to imports from `.durable` and `__all__`

### Tests

- [ ] T110 [P] Create `tests/durable/test_retry.py` — RetryPolicy construction tests:
  - `test_default_construction` — verify all defaults match spec
  - `test_custom_construction` — all params specified
  - `test_validation_initial_delay_zero` — raises ValueError
  - `test_validation_initial_delay_negative` — raises ValueError
  - `test_validation_backoff_coefficient_below_one` — raises ValueError
  - `test_validation_max_delay_below_initial` — raises ValueError
  - `test_validation_max_attempts_zero` — raises ValueError
  - `test_validation_retry_on_non_exception` — raises TypeError
  - `test_repr` — string contains key params

- [ ] T111 [P] Add delay computation tests to `tests/durable/test_retry.py`:
  - `test_compute_delay_exponential` — coefficient=2, attempts 0-5, verify formula
  - `test_compute_delay_fixed` — coefficient=1, verify constant delay
  - `test_compute_delay_capped_at_max` — verify delay never exceeds max_delay
  - `test_compute_delay_jitter_bounds` — jitter=True, verify delay is within ±25% of base, run 100 times
  - `test_compute_delay_no_jitter` — jitter=False, verify exact formula output
  - `test_compute_delay_linear` — linear preset, verify additive: delay = initial * (attempt + 1)

- [ ] T112 [P] Add should_retry and preset tests to `tests/durable/test_retry.py`:
  - `test_should_retry_within_attempts` — attempt < max-1 returns True
  - `test_should_retry_exhausted` — attempt >= max-1 returns False
  - `test_should_retry_matching_exception` — retry_on=(ValueError,), ValueError → True
  - `test_should_retry_non_matching` — retry_on=(ValueError,), RuntimeError → False
  - `test_should_retry_none_means_all` — retry_on=None, any exception → True
  - `test_preset_exponential_backoff` — verify defaults
  - `test_preset_fixed_delay` — verify coefficient=1, no jitter
  - `test_preset_linear_backoff` — verify coefficient=1
  - `test_preset_no_retry` — max_attempts=1

- [ ] T113 Add retry integration test to `tests/durable/test_retry.py` — Test full lifecycle with `@durable_task(retry=RetryPolicy.exponential_backoff(max_attempts=3))`. Define a task function that fails the first 2 attempts then succeeds. Initialize manager, run task, verify result returned, verify `ctx.run_attempt` was 2 on the successful attempt. Use monkeypatched `asyncio.sleep` to avoid real delays.

- [ ] T114 Add retry exhaustion test to `tests/durable/test_retry.py` — Task that always raises `ValueError`. `retry=RetryPolicy(max_attempts=3, retry_on=(ValueError,))`. Verify `TaskFailed` is raised. Verify error dict contains `"type": "exhausted_retries"`, `"attempts": 3`.

- [ ] T115 Add non-retryable exception test to `tests/durable/test_retry.py` — Task raises `TypeError`. `retry=RetryPolicy(retry_on=(ValueError,))`. Verify `TaskFailed` is raised immediately on first attempt (no retry).

**Checkpoint**: RetryPolicy class + integration + tests done. Run all 140 existing tests to verify no regressions.

---

## Phase 3: Source Field (simple pass-through — US3)

**Purpose**: Add `source` field to models and wire through creation/retrieval.

- [ ] T201 Modify `_models.py` `TaskInfo`:
  1. Add `"source"` to `__slots__`
  2. Add `source: dict[str, Any] | None = None` param to `__init__`, assign `self.source = source`
  3. In `from_dict`: add `source=data.get("source")` to constructor call
  4. In `to_dict`: add `if self.source is not None: result["source"] = self.source`

- [ ] T202 Modify `_models.py` `TaskCreateRequest`:
  1. Add `"source"` to `__slots__`
  2. Add `source: dict[str, Any] | None = None` param to `__init__`, assign `self.source = source`
  3. Add `__repr__` if missing

- [ ] T203 Modify `_decorator.py` — Add `source: dict[str, Any] | None` to:
  1. `DurableTaskOptions.__slots__` (add `"source"`)
  2. `DurableTaskOptions.__init__` (add `source: dict[str, Any] | None = None`, assign `self.source = source`)
  3. `@durable_task` function signature (add `source` kwarg)
  4. `@durable_task` overloads (add `source` param)
  5. `_wrap` inside `durable_task` (pass `source=source` to `DurableTaskOptions`)
  6. `DurableTask.run()` — add `source: dict[str, Any] | None = None` param, pass `source=source or self._opts.source` to manager
  7. `DurableTask.start()` — same as run
  8. `DurableTask.options()` — add `source` param and merge

- [ ] T204 Modify `_manager.py` — Add source plumbing:
  1. Add `source: dict[str, Any] | None = None` to `create_and_run` and `create_and_start`
  2. Pass `source=source` to `TaskCreateRequest` constructor in `create_and_start`

- [ ] T205 Modify `_client.py` — In the `create` method, if `request.source is not None`, include `"source": request.source` in the POST body dict.

- [ ] T206 Modify `_local_provider.py` — In the `create` method, persist `source` from the request into the `TaskInfo`. In the JSON serialization/deserialization, ensure `source` round-trips through `to_dict`/`from_dict`.

### Tests

- [ ] T207 [P] Create `tests/durable/test_source.py` — Source field unit tests:
  - `test_source_set_at_decorator` — `@durable_task(source={"origin": "test"})`, run, verify source on TaskInfo
  - `test_source_set_at_call_site` — `task.run(source={"req": "abc"})`, verify override
  - `test_source_call_overrides_decorator` — decorator source + call source, verify call wins
  - `test_source_none_by_default` — no source anywhere, verify TaskInfo.source is None
  - `test_source_immutable_on_patch` — verify PATCH/update does not modify source
  - `test_source_round_trip_local_provider` — create with source, get, verify identical dict
  - `test_source_complex_nested` — source with nested dicts/lists, verify round-trip

- [ ] T208 [P] Modify existing `tests/durable/test_models.py` (if exists, otherwise add to `test_source.py`):
  - `test_task_info_from_dict_with_source` — JSON dict with source, verify from_dict
  - `test_task_info_to_dict_with_source` — TaskInfo with source, verify to_dict includes it
  - `test_task_info_from_dict_without_source` — JSON dict without source, verify source is None
  - `test_task_create_request_with_source` — verify slots + init

**Checkpoint**: Source field wired through all layers. Run all tests.

---

## Phase 4: Streaming (most complex — US1)

**Purpose**: Add `ctx.stream(item)` producer and `async for chunk in run` consumer.

### Implementation

- [ ] T301 Modify `_context.py` — Add streaming support to `TaskContext`:
  1. Add `"_stream_queue"` to `__slots__`
  2. Add `stream_queue: asyncio.Queue[Any] | None = None` param to `__init__`, assign `self._stream_queue = stream_queue`
  3. Add `async def stream(self, item: Any) -> None` method:
     - If `self._stream_queue is None`, raise `RuntimeError("Streaming is not enabled for this task run")`
     - `await self._stream_queue.put(item)`

- [ ] T302 Modify `_run.py` — Add async iteration to `TaskRun`:
  1. Define module-level `_STREAM_SENTINEL = object()`
  2. Add `"_stream_queue"` to `TaskRun.__slots__`
  3. Add `stream_queue: asyncio.Queue[Any] | None = None` param to `__init__`, assign `self._stream_queue = stream_queue`
  4. Add `def __aiter__(self) -> TaskRun[Output]: return self`
  5. Add `async def __anext__(self) -> Any`:
     - If `self._stream_queue is None`: raise `StopAsyncIteration`
     - `item = await self._stream_queue.get()`
     - If `item is _STREAM_SENTINEL`: raise `StopAsyncIteration`
     - Return `item`

- [ ] T303 Modify `_manager.py` `create_and_start` — Add stream queue lifecycle:
  1. After creating `cancel_event` and `metadata`, create `stream_queue = asyncio.Queue()`
  2. Pass `stream_queue=stream_queue` to `TaskContext` constructor
  3. Pass `stream_queue=stream_queue` to `TaskRun` constructor

- [ ] T304 Modify `_manager.py` `_execute_task` — Send sentinel on completion:
  1. Import `_STREAM_SENTINEL` from `._run`
  2. In the success branch (after setting result on future): if there's a stream queue on ctx, `await ctx._stream_queue.put(_STREAM_SENTINEL)`
  3. In the suspend branch: put sentinel before setting exception on future
  4. In the exception branch: put sentinel before setting exception on future
  5. In the cancel branch: put sentinel
  6. Ensure sentinel is put in `finally` block as a fallback (idempotent — queue just gets extra sentinel)

- [ ] T305 Modify `_manager.py` `_resume_task` — Add stream queue to resumed tasks (same pattern as create_and_start — create queue, pass to context and new TaskRun).

- [ ] T306 Export `_STREAM_SENTINEL` from `_run.py` (private, but needed by `_manager.py` — underscore prefix is sufficient).

### Tests

- [ ] T307 [P] Create `tests/durable/test_streaming.py` — Happy path tests:
  - `test_stream_items_in_order` — task streams 5 items, consumer receives them in order via `async for`
  - `test_stream_then_result` — task streams items, returns result; consumer iterates stream, then calls `result()`, both succeed
  - `test_non_streaming_task_iteration` — task never calls `ctx.stream()`, `async for` yields nothing, `result()` still works
  - `test_stream_various_types` — stream strings, dicts, lists, ints; verify all received
  - `test_stream_empty` — task calls zero `ctx.stream()`, iterator terminates cleanly

- [ ] T308 [P] Add error propagation tests to `tests/durable/test_streaming.py`:
  - `test_stream_then_fail` — task streams 2 items then raises; consumer gets 2 items then `StopAsyncIteration`; `result()` raises `TaskFailed`
  - `test_stream_then_suspend` — task streams 2 items then `ctx.suspend()`; consumer gets 2 items then stops; `result()` raises `TaskSuspended`
  - `test_stream_then_cancel` — task is cancelled mid-stream; iterator terminates; `result()` raises `TaskCancelled`

- [ ] T309 [P] Add edge case tests to `tests/durable/test_streaming.py`:
  - `test_stream_without_consumer` — task streams items but caller only uses `result()`; verify no error/leak
  - `test_stream_with_retry` — task with retry streams items, fails, retries, streams more; verify consumer gets items from ALL attempts
  - `test_stream_not_enabled_raises` — call `ctx.stream()` on a context without stream_queue; verify RuntimeError

**Checkpoint**: Streaming fully working. Run all tests including Phase 2 and 3 tests.

---

## Phase 5: Integration, Samples & Sample E2E Tests

**Purpose**: End-to-end validation, sample files, and e2e tests.

### Regression & Formatting

- [ ] T401 Run all 140 existing tests — verify zero regressions from Phase 2/3/4 changes
- [ ] T402 Run Black on all modified/new files: `_retry.py`, `_context.py`, `_run.py`, `_models.py`, `_decorator.py`, `_manager.py`, `_client.py`, `_local_provider.py`, `durable/__init__.py`, `core/__init__.py`, all new test files

### Sample Files

- [ ] T403 Create `azure-ai-agentserver-core/samples/durable_streaming/durable_streaming.py` — Streaming research agent sample from spec (Sample 1). Uses `ctx.stream()` to emit search results, file-based store with `⚠️` production warning.

- [ ] T404 Create `azure-ai-agentserver-core/samples/durable_retry/durable_retry.py` — Retry policy sample from spec (Sample 2). Demonstrates `RetryPolicy.exponential_backoff()` with flaky external API, file-based store.

- [ ] T405 Create `azure-ai-agentserver-core/samples/durable_source/durable_source.py` — Source field provenance sample from spec (Sample 3). Sets source at decorator and call site, queries by source.

- [ ] T406 Create `azure-ai-agentserver-invocations/samples/durable_multiturn/durable_multiturn.py` — Multi-turn durable research agent sample from spec (Sample 4). Shows suspend/resume with streaming and retry, file-based store with production warnings.

- [ ] T407 Create `azure-ai-agentserver-invocations/samples/durable_langgraph/durable_langgraph.py` — LangGraph + durable tasks sample from spec (Sample 5). Shows durable wrapper around LangGraph graph, streaming node outputs.

### Sample E2E Tests

- [ ] T408 Create `tests/durable/test_sample_e2e.py` — Test infrastructure:
  - `_setup_test_manager()` helper — initialize `DurableTaskManager` with `LocalFileDurableTaskProvider` pointing to temp directory
  - `_cleanup_test_manager()` helper — shutdown manager, clean temp dir
  - `@pytest.fixture` for auto manager setup/teardown per test

- [ ] T409 [P] Add Sample 1 e2e test to `test_sample_e2e.py` — Streaming research agent:
  - Replicate the streaming task logic inline (search through topics, stream results)
  - Run with `.start()`, collect all streamed items via `async for`
  - Assert: items arrive in order, each item is a dict with expected keys, `result()` returns final summary

- [ ] T410 [P] Add Sample 2 e2e test to `test_sample_e2e.py` — Retry policy:
  - Define a task that fails N times then succeeds
  - Apply `RetryPolicy.exponential_backoff(max_attempts=3)`
  - Monkeypatch `asyncio.sleep` to record delays without waiting
  - Assert: task succeeds on attempt 2, delays recorded match exponential formula

- [ ] T411 [P] Add Sample 3 e2e test to `test_sample_e2e.py` — Source field:
  - Define a task with `source={"origin": "e2e"}` at decorator level
  - Run with call-site override `source={"origin": "call", "req_id": "123"}`
  - Verify source on TaskInfo matches call-site override (not decorator)

- [ ] T412 [P] Add Sample 4 e2e test to `test_sample_e2e.py` — Multi-turn durable:
  - Define a task that does 2 turns: first run streams partial results and suspends, resume completes
  - Verify first run: streamed items + TaskSuspended
  - Resume task, verify second run: more items + final result

- [ ] T413 [P] Add Sample 5 e2e test to `test_sample_e2e.py` — LangGraph-style:
  - Define a task that simulates graph node execution (no real LangGraph dependency)
  - Stream node outputs as the "graph" executes
  - Verify all node outputs received in order

### Final Verification

- [ ] T414 Run full test suite — all existing + new tests must pass. Target: ≥180 total tests.
- [ ] T415 Update `durable/__init__.py` docstring to mention new public APIs (RetryPolicy, streaming, source).

**Checkpoint**: All features implemented, tested, and validated. Ready for review.

---

## Summary

| Phase | Tasks | New Files | Modified Files |
|-------|-------|-----------|----------------|
| Phase 2 (Retry) | T101–T115 (15) | `_retry.py`, `test_retry.py` | `_decorator.py`, `_manager.py`, `__init__.py` ×2 |
| Phase 3 (Source) | T201–T208 (8) | `test_source.py` | `_models.py`, `_decorator.py`, `_manager.py`, `_client.py`, `_local_provider.py` |
| Phase 4 (Streaming) | T301–T309 (9) | `test_streaming.py` | `_context.py`, `_run.py`, `_manager.py` |
| Phase 5 (Integration) | T401–T415 (15) | 5 samples, `test_sample_e2e.py` | formatting only |
| **Total** | **47 tasks** | **9 new files** | **8 modified files** |
