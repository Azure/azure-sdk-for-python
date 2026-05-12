# Tasks: Cancellation & Timeout

**Input**: Design documents from `/specs/005-cancellation-and-timeout/`  
**Prerequisites**: plan.md (required), spec.md (required), research.md

## Format: `[ID] [P?] [Story] Description`

---

## Phase 1: New Exception Types

**Purpose**: Add `TaskWaitTimeout` and `TaskTerminated` exception classes — pure additions, zero changes to existing code

- [ ] T001 [P] [US1,US2,US3] Add `TaskWaitTimeout` and `TaskTerminated` to `_exceptions.py`. Both follow the existing pattern: `__slots__`, `task_id` attribute, clear message. `TaskTerminated` also has optional `reason: str | None`. `TaskWaitTimeout` extends `Exception`. `TaskTerminated` extends `Exception`.
- [ ] T002 [P] [US1,US2,US3] Export `TaskWaitTimeout` and `TaskTerminated` from `__init__.py` — add to imports and `__all__`. Update module docstring's public API listing.

**Checkpoint**: Two new exception types exist and are importable. All existing tests pass unchanged.

---

## Phase 2: Wait Timeout (US2)

**Purpose**: Add `wait_timeout` parameter to `.run()` and `task_run.result()` so callers can bound wait time without killing the task

- [ ] T003 [US2] Modify `TaskRun.result()` in `_run.py` to accept `wait_timeout: timedelta | None = None`. When set, wrap `self._result_future` with `asyncio.wait_for` + `asyncio.shield`. On `asyncio.TimeoutError`, raise `TaskWaitTimeout(self.task_id)`. When `None`, current behavior preserved.
- [ ] T004 [US2] Add `wait_timeout: timedelta | None = None` parameter to `DurableTask.run()` in `_decorator.py`. Pass it through to `handle.result(wait_timeout=wait_timeout)`. Add to docstring and both `@overload` signatures.

**Checkpoint**: `.run(wait_timeout=timedelta(seconds=1))` raises `TaskWaitTimeout` on slow tasks. Task keeps running after timeout.

---

## Phase 3: Terminate (US3)

**Purpose**: Add `handle.terminate()` for forced non-recoverable task exit

- [ ] T005 [US3] Add `_terminate_event: asyncio.Event` to `TaskRun.__init__` in `_run.py`. Add new parameter `terminate_event: asyncio.Event | None = None` (defaulting to a fresh event). Store as `self._terminate_event`.
- [ ] T006 [US3] Add `terminate(reason: str | None = None)` method to `TaskRun` in `_run.py`. It sets both `self._cancel_event` and `self._terminate_event`. Optionally stores the reason.
- [ ] T007 [US3] Thread `terminate_event` through `_manager.py`: create one `asyncio.Event` per task, pass to both `TaskRun` constructor and `_execute_task`. Update `_ActiveTask` slots to include `terminate_event`.
- [ ] T008 [US3] Modify `_execute_task` in `_manager.py`: in the `asyncio.CancelledError` handler (line ~653), check `terminate_event.is_set()`. If set, use `_handle_failure` path and set `TaskTerminated` on the future instead of `TaskCancelled`. Pass the reason through.
- [ ] T009 [US3] Update both `create_and_start` and `_start_existing_task` in `_manager.py` to pass `terminate_event` to `TaskRun` constructor (lines ~419 and ~587).

**Checkpoint**: `await task_run.terminate()` kills the task. `task_run.result()` raises `TaskTerminated`. Task does NOT stay `in_progress` for recovery.

---

## Phase 4: Execution Timeout (US1)

**Purpose**: Enforce `timeout=` on the decorator via a background watchdog that fires `ctx.cancel` then escalates to hard cancel

- [ ] T010 [US1] Add `cancel_grace_seconds: float = 5.0` parameter to `DurableTaskOptions` in `_decorator.py`. Add to `__slots__`, `__init__`, `__repr__`, and the `durable_task()` decorator function + overloads. Also add to `.options()` method.
- [ ] T011 [US1] Add `_timeout_watchdog` coroutine in `_manager.py`. Takes `timeout_seconds: float`, `cancel_event: asyncio.Event`, `grace_seconds: float`, `execution_task: asyncio.Task`. Phase 1: `await asyncio.sleep(timeout_seconds)` then `cancel_event.set()`. Phase 2: `await asyncio.sleep(grace_seconds)` then `execution_task.cancel()`.
- [ ] T012 [US1] Wire the watchdog into `_execute_task` in `_manager.py`. Accept `timeout: timedelta | None` and `cancel_grace_seconds: float` parameters. If `timeout` is not None, start the watchdog as an `asyncio.Task` before entering the retry loop. Cancel the watchdog on any exit (success, suspend, failure, cancel). Use try/finally to ensure cleanup.
- [ ] T013 [US1] Thread `opts.timeout` and `opts.cancel_grace_seconds` from `create_and_start` and `_start_existing_task` into the `_execute_task` call.
- [ ] T014 [US1] Add per-call `timeout: timedelta | None = None` override to `.run()` and `.start()` in `_decorator.py`. When set, overrides decorator-level timeout. Pass through `_lifecycle_start` into `_execute_task`.

**Checkpoint**: `@durable_task(timeout=timedelta(seconds=1))` auto-cancels tasks after 1 second. Grace period allows clean exit before hard cancel.

---

## Phase 5: Tests

**Purpose**: Comprehensive test coverage for all three features

- [ ] T015 [P] [US1] Test: task with `timeout=timedelta(seconds=0.5)` that observes `ctx.cancel` and returns partial result. Verify result is returned (not a failure).
- [ ] T016 [P] [US1] Test: task with `timeout=timedelta(seconds=0.5)` that ignores `ctx.cancel` (sleeps 10s). Verify `TaskCancelled` is raised after timeout + grace period.
- [ ] T017 [P] [US1] Test: task with no timeout runs to completion normally (regression guard).
- [ ] T018 [P] [US2] Test: `.run(wait_timeout=timedelta(seconds=0.5))` on a 5-second task. Verify `TaskWaitTimeout` raised. Verify task is still `in_progress` via `.get()`.
- [ ] T019 [P] [US2] Test: `.run()` without `wait_timeout` blocks until completion (regression guard).
- [ ] T020 [P] [US2] Test: `task_run.result(wait_timeout=timedelta(seconds=0.5))` raises `TaskWaitTimeout`.
- [ ] T021 [P] [US3] Test: `await task_run.terminate()` on a running task. Verify `TaskTerminated` raised by `.result()`.
- [ ] T022 [P] [US3] Test: terminated task does NOT stay `in_progress` — verify `.get()` shows completed/failed status (not in_progress).
- [ ] T023 [P] [US3] Test: `cancel()` vs `terminate()` — cancelled task stays in_progress for recovery, terminated does not.

**Checkpoint**: All new tests pass. All 221+ existing tests pass unchanged.

---

## Phase 6: Documentation & Polish

**Purpose**: Update developer guide and run all validation

- [ ] T024 [US1,US2,US3] Update `durable-task-developer-guide.md`: add "Timeout" subsection in Decorator Options, add `wait_timeout` to `.run()` documentation, add `terminate()` to TaskRun docs, add `TaskWaitTimeout` and `TaskTerminated` to Error Handling table.
- [ ] T025 Run Black formatting on all changed files.
- [ ] T026 Run full test suite and verify all tests pass (existing + new).

**Checkpoint**: All documentation, formatting, and tests green.

---

## Dependencies & Execution Order

### Phase Dependencies

- **Phase 1 (Exceptions)**: No dependencies — start immediately
- **Phase 2 (Wait Timeout)**: Depends on T001 (needs `TaskWaitTimeout`)
- **Phase 3 (Terminate)**: Depends on T001 (needs `TaskTerminated`)
- **Phase 4 (Execution Timeout)**: Depends on Phase 3 (shares terminate_event pattern + cancel escalation)
- **Phase 5 (Tests)**: Depends on all implementation phases (1-4)
- **Phase 6 (Docs)**: Depends on Phase 5

### Parallel Opportunities

- T001 and T002 (Phase 1) can run in parallel
- Phase 2 and Phase 3 can run in parallel (after Phase 1)
- All test tasks T015-T023 (Phase 5) can run in parallel
- T024, T025, T026 (Phase 6) are sequential

### Within Each Phase

- Phase 3 tasks are sequential: T005 → T006 → T007 → T008 → T009
- Phase 4 tasks are sequential: T010 → T011 → T012 → T013 → T014
