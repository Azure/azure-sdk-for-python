# Tasks: Handle Operations & API Ergonomics

**Input**: Design documents from `/specs/007-handle-metadata-and-ergonomics/`
**Prerequisites**: plan.md (required), spec.md (required)

## Phase 1: Dict-Like TaskMetadata (Priority: P1) 🎯 MVP

**Goal**: Make `TaskMetadata` support standard Python dict syntax while preserving dirty-tracking.

**Independent Test**: Use `[]` assignment, iteration, `in`, `len`, `del` on a `TaskMetadata` instance.

### Implementation

- [ ] T001 [US1] Add `__setitem__`, `__getitem__`, `__delitem__` to `TaskMetadata` in `_metadata.py`
- [ ] T002 [US1] Add `__contains__`, `__iter__`, `__len__` to `TaskMetadata` in `_metadata.py`
- [ ] T003 [US1] Add `keys()`, `values()`, `items()` to `TaskMetadata` in `_metadata.py`
- [ ] T004 [US1] Register `TaskMetadata` with `collections.abc.MutableMapping`

### Tests

- [ ] T005 [US1] Add dict protocol tests to `test_metadata.py` — `[]` read/write, `KeyError`, dirty-tracking
- [ ] T006 [US1] Add `del`, `in`, `len`, `iter` tests to `test_metadata.py`
- [ ] T007 [US1] Add `keys()`, `values()`, `items()` tests to `test_metadata.py`

**Checkpoint**: `TaskMetadata` fully supports dict syntax. All tests pass.

---

## Phase 2: Backlog Housekeeping

- [ ] T008 Strike off completed backlog items (13, 14, 15) and mark 16 as done
- [ ] T009 Update spec.md status from Draft to Implemented

---

## Dependencies & Execution Order

- T001–T003 can be done as a single edit (same file, same class)
- T004 depends on T001–T003
- T005–T007 depend on T001–T003
- T008–T009 depend on all tests passing
