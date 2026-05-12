# Tasks: TaskResult Wrapper & API Polish

**Input**: Design documents from `/specs/006-task-result-and-api-polish/`  
**Prerequisites**: plan.md (required), spec.md (required)

## Format: `[ID] [P?] [Story] Description`

---

## Phase 1: TaskResult Class

**Purpose**: Create the `TaskResult[Output]` generic wrapper — pure addition, zero changes to existing code

- [ ] T001 [US1] Create `_result.py` with `TaskResult[Output]` class. Generic with `__slots__`: `task_id: str`, `output: Output | None`, `status: Literal["completed", "suspended"]`, `suspension_reason: str | None`. Properties: `is_completed -> bool`, `is_suspended -> bool`. `__repr__` showing status, truncated output, and suspension_reason. Type annotations for mypy/pyright: `Output` TypeVar bound.
- [ ] T002 [US1] Export `TaskResult` from `__init__.py` — add to imports from `._result` and to `__all__`. Update module docstring's public API listing.

**Checkpoint**: `TaskResult` class exists and is importable. All 227+ existing tests pass unchanged.

---

## Phase 2: Wire TaskResult into Core

**Purpose**: Change `result()` and `run()` to return `TaskResult[Output]` instead of raw `Output`. Stop raising `TaskSuspended` from these paths.

- [ ] T003 [US1] Modify `_manager.py` `_execute_task_loop` (line ~718-744): Change success path from `result_future.set_result(result)` to `result_future.set_result(TaskResult(task_id=task_id, output=result, status="completed"))`. Change suspend path from `result_future.set_exception(TaskSuspended(...))` to `result_future.set_result(TaskResult(task_id=task_id, output=result.output, status="suspended", suspension_reason=result.reason))`. Import `TaskResult` from `._result`. Change `result_future` type annotation from `asyncio.Future[Output]` to `asyncio.Future[TaskResult[Output]]` in `_ActiveTask`, `create_and_start`, `_start_existing_task`.
- [ ] T004 [US1] Modify `TaskRun` in `_run.py`: Change `result()` return type from `Output` to `TaskResult[Output]`. Update type annotation of `_result_future` from `asyncio.Future[Output]` to `asyncio.Future[TaskResult[Output]]`. Update docstring. Remove `TaskSuspended` from `result()` raises list. Import `TaskResult` from `._result`.
- [ ] T005 [US1] Modify `DurableTask.run()` in `_decorator.py`: Change return type from `Output` to `TaskResult[Output]`. Update docstring — remove `:raises TaskSuspended:`, update return description. Import `TaskResult`. Update both `@overload` signatures if `run()` has them.

**Checkpoint**: `result()` and `run()` return `TaskResult[Output]`. Suspension is a return value. Failures/cancel/terminate still raised as exceptions. Existing tests will FAIL at this point (expected — they need updating in Phase 3).

---

## Phase 3: Update Existing Tests

**Purpose**: Fix all existing tests that expect raw `Output` from `run()`/`result()` or catch `TaskSuspended` from these paths.

- [ ] T006 [P] [US1] Update `tests/durable/test_entry_mode.py`: Change `with pytest.raises(TaskSuspended)` blocks (lines ~81, 86, 105) to `result = await ...` then `assert result.is_suspended`. Update fresh/recovered tests that assert raw output to unpack via `result.output`. Import `TaskResult` instead of (or alongside) `TaskSuspended`.
- [ ] T007 [P] [US1] Update `tests/durable/test_lifecycle.py`: Change `with pytest.raises(TaskSuspended)` blocks (lines ~143, 147) to `result = await ...` then `assert result.is_suspended`. Update success assertions to unpack `result.output`.
- [ ] T008 [P] [US1] Update `tests/durable/test_sample_e2e.py`: Change all `with pytest.raises(TaskSuspended)` blocks (lines ~282, 482, 590, 603, 740) to `result = await ...` then `assert result.is_suspended`. Where tests inspect `exc_info.value.output` or `exc_info.value.reason`, switch to `result.output` and `result.suspension_reason`.
- [ ] T009 [P] [US1] Update `tests/durable/test_get.py`: Change `with pytest.raises(TaskSuspended)` (line ~60) to assert `result.is_suspended`.
- [ ] T010 [P] [US1] Update `tests/durable/test_streaming.py`: Change `assert await run.result() == "final"` (line ~136) to `result = await run.result(); assert result.output == "final"`.
- [ ] T011 [P] [US2] Update `tests/durable/test_streaming.py`: Verify streaming + TaskResult works together — stream chunks then assert `result.is_completed`.
- [ ] T012 [P] [US1] Update `tests/durable/test_cancellation_timeout.py`: Where tests assert `result = await run.result()` for success (lines ~90, 130), change to `result.output`. Tests that expect `TaskCancelled`/`TaskTerminated` exceptions remain unchanged.
- [ ] T013 [P] [US1] Update `tests/durable/test_retry.py`: Where tests call `await task.run(...)` and compare result, unpack `.output` from `TaskResult`. Tests that expect `TaskFailed` remain unchanged.

**Checkpoint**: All 227+ existing tests pass with `TaskResult` unpacking. Zero regressions.

---

## Phase 4: Callable Factories for Tags & Description

**Purpose**: Extend `tags` to accept callables, add new `description` option — independent of TaskResult

- [ ] T014 [P] [US3,US4] Modify `DurableTaskOptions` in `_decorator.py`: Change `tags` type from `dict[str, str]` to `dict[str, str] | Callable[..., dict[str, str]]`. Add `description: str | Callable[..., str] | None = None` to `__slots__`, `__init__`, and `__repr__`.
- [ ] T015 [P] [US3] Add `_resolve_tags(self, input_val: Input, task_id: str, call_tags: dict[str, str] | None) -> dict[str, str]` method to `DurableTask` in `_decorator.py`. If `self._opts.tags` is callable, invoke it with `(input_val, task_id)`, then merge `call_tags` on top. If static dict, use existing `_merge_tags` logic.
- [ ] T016 [P] [US4] Add `_resolve_description(self, input_val: Input, task_id: str) -> str | None` method to `DurableTask` in `_decorator.py`. If callable, invoke; if string, return as-is; if None, return None.
- [ ] T017 [US3,US4] Wire `_resolve_tags` and `_resolve_description` into `_lifecycle_start` in `_decorator.py`. Replace `self._merge_tags(tags)` with `self._resolve_tags(input, task_id, tags)`. Pass resolved description to `create_and_start` as part of metadata or a new param. Update `create_and_start` in `_manager.py` if needed to accept/store description.
- [ ] T018 [US3,US4] Update `durable_task()` function signature and both `@overload`s in `_decorator.py`: Add `description: str | Callable[..., str] | None = None`. Update `tags` type hint to include `Callable`. Add to `_wrap` inner function and `DurableTaskOptions` construction. Update `.options()` method to include `description`.

**Checkpoint**: `@durable_task(tags=lambda i, tid: {...}, description="...")` works. Static tags still work. Description stored in metadata.

---

## Phase 5: New Tests

**Purpose**: Test coverage for TaskResult semantics and callable factories

### TaskResult Tests (test_task_result.py)

- [ ] T019 [P] [US1] Test: Task completes normally → `result.is_completed == True`, `result.output == expected`, `result.suspension_reason is None`, `result.status == "completed"`.
- [ ] T020 [P] [US1] Test: Task suspends with output and reason → `result.is_suspended == True`, `result.output == snapshot`, `result.suspension_reason == "waiting for user"`.
- [ ] T021 [P] [US1] Test: Task suspends without output → `result.is_suspended == True`, `result.output is None`.
- [ ] T022 [P] [US1] Test: Task that returns `None` → `result.is_completed == True`, `result.output is None` — distinguishable from suspended-without-output via `result.status`.
- [ ] T023 [P] [US1] Test: `TaskResult.__repr__` shows status and output summary.
- [ ] T024 [P] [US1] Test: `TaskFailed` still raised as exception from `run()` — not wrapped in TaskResult.
- [ ] T025 [P] [US1] Test: `TaskCancelled` still raised as exception from `result()`.
- [ ] T026 [P] [US1] Test: `TaskTerminated` still raised as exception from `result()`.

### Callable Factory Tests (test_callable_factories.py)

- [ ] T027 [P] [US3] Test: `@durable_task(tags=lambda i, tid: {"tenant": i.tenant_id})` — verify task record has computed tags.
- [ ] T028 [P] [US3] Test: Callable tags + per-call `tags={"extra": "v"}` — per-call merged on top.
- [ ] T029 [P] [US3] Test: Static `tags={"k": "v"}` — existing behavior preserved.
- [ ] T030 [P] [US4] Test: `@durable_task(description=lambda i, tid: f"Processing {i}")` — verify metadata has computed description.
- [ ] T031 [P] [US4] Test: Static `description="fixed"` — verify metadata has static description.
- [ ] T032 [P] [US4] Test: No description set — verify no description in metadata.

**Checkpoint**: All new tests pass. Full suite green.

---

## Phase 6: Samples, Documentation & Polish

**Purpose**: Update samples, developer guide, and run all validation

### Sample Updates

- [ ] T033 [P] [US1] Update `samples/durable_source/durable_source.py`: Unpack `.output` from `TaskResult` on lines that call `.run()` (3 call sites).
- [ ] T034 [P] [US1] Update `samples/durable_retry/durable_retry.py`: Unpack `.output` from `TaskResult` on lines that call `.run()` (2 call sites).
- [ ] T035 [P] [US1] Update `samples/durable_streaming/durable_streaming.py`: Unpack `.output` from `TaskResult` on the `.result()` call.

### Documentation

- [ ] T036 [US1] Update `durable-task-developer-guide.md`: Replace the "Result Handling" section with `TaskResult` pattern. Show `result.is_suspended` / `result.is_completed` pattern. Document that `TaskSuspended` is no longer raised by `result()`/`run()`. Update the error handling table.
- [ ] T037 [US3,US4] Update `durable-task-developer-guide.md`: Add "Callable Factories" subsection in Decorator Options showing `tags` and `description` callable patterns.

### Validation

- [ ] T038 Run Black formatting on all changed files.
- [ ] T039 Run full test suite and verify all tests pass.

**Checkpoint**: Documentation, samples, formatting, and all tests green.

---

## Dependencies & Execution Order

### Phase Dependencies

- **Phase 1 (TaskResult class)**: No dependencies — start immediately
- **Phase 2 (Wire TaskResult)**: Depends on Phase 1 (needs `TaskResult` class)
- **Phase 3 (Update tests)**: Depends on Phase 2 (tests break until updated)
- **Phase 4 (Callable factories)**: Independent — can run in parallel with Phases 1-3
- **Phase 5 (New tests)**: Depends on Phase 2 (TaskResult tests) and Phase 4 (factory tests)
- **Phase 6 (Docs)**: Depends on all

### Parallel Opportunities

- All Phase 3 tasks (T006-T013) can run in parallel — different test files
- Phase 4 tasks T014-T016 can run in parallel — different methods
- All Phase 5 tests (T019-T032) can run in parallel — different test files
- **Phase 4 is fully independent of Phases 1-3** — can start immediately

### Within Each Phase

- Phase 2 is sequential: T003 → T004 → T005
- Phase 4 tasks T014-T016 are parallel, then T017 depends on them, then T018 depends on T017
