---

description: "Task list template for feature implementation"
---

# Tasks: [FEATURE NAME]

**Input**: Design documents from `/specs/[###-feature-name]/`
**Prerequisites**: plan.md (required), spec.md (required for user stories), research.md, data-model.md, contracts/

**Tests**: The examples below include test tasks. Tests are OPTIONAL - only include them if explicitly requested in the feature specification.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

## Path Conventions

- **Single project**: `src/`, `tests/` at repository root
- **Web app**: `backend/src/`, `frontend/src/`
- **Mobile**: `api/src/`, `ios/src/` or `android/src/`
- Paths shown below assume single project - adjust based on plan.md structure

<!-- 
  ============================================================================
  IMPORTANT: The tasks below are SAMPLE TASKS for illustration purposes only.
  
  The /speckit.tasks command MUST replace these with actual tasks based on:
  - User stories from spec.md (with their priorities P1, P2, P3...)
  - Feature requirements from plan.md
  - Entities from data-model.md
  - Endpoints from contracts/
  
  Tasks MUST be organized by user story so each story can be:
  - Implemented independently
  - Tested independently
  - Delivered as an MVP increment
  
  DO NOT keep these sample tasks in the generated tasks.md file.
  ============================================================================
-->

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and basic structure

- [ ] T001 Create project structure per implementation plan
- [ ] T002 Initialize [language] project with [framework] dependencies
- [ ] T003 [P] Configure linting and formatting tools

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure that MUST be complete before ANY user story can be implemented

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

Examples of foundational tasks (adjust based on your project):

- [ ] T004 Setup database schema and migrations framework
- [ ] T005 [P] Implement authentication/authorization framework
- [ ] T006 [P] Setup API routing and middleware structure
- [ ] T007 Create base models/entities that all stories depend on
- [ ] T008 Configure error handling and logging infrastructure
- [ ] T009 Setup environment configuration management

**Checkpoint**: Foundation ready - user story implementation can now begin in parallel

---

## Phase 3: User Story 1 - [Title] (Priority: P1) 🎯 MVP

**Goal**: [Brief description of what this story delivers]

**Independent Test**: [How to verify this story works on its own]

### Tests for User Story 1 (OPTIONAL - only if tests requested) ⚠️

> **NOTE: Write these tests FIRST, ensure they FAIL before implementation**

- [ ] T010 [P] [US1] Contract test for [endpoint] in tests/contract/test_[name].py
- [ ] T011 [P] [US1] Integration test for [user journey] in tests/integration/test_[name].py

### Implementation for User Story 1

- [ ] T012 [P] [US1] Create [Entity1] model in src/models/[entity1].py
- [ ] T013 [P] [US1] Create [Entity2] model in src/models/[entity2].py
- [ ] T014 [US1] Implement [Service] in src/services/[service].py (depends on T012, T013)
- [ ] T015 [US1] Implement [endpoint/feature] in src/[location]/[file].py
- [ ] T016 [US1] Add validation and error handling
- [ ] T017 [US1] Add logging for user story 1 operations

**Checkpoint**: At this point, User Story 1 should be fully functional and testable independently

---

## Phase 4: User Story 2 - [Title] (Priority: P2)

**Goal**: [Brief description of what this story delivers]

**Independent Test**: [How to verify this story works on its own]

### Tests for User Story 2 (OPTIONAL - only if tests requested) ⚠️

- [ ] T018 [P] [US2] Contract test for [endpoint] in tests/contract/test_[name].py
- [ ] T019 [P] [US2] Integration test for [user journey] in tests/integration/test_[name].py

### Implementation for User Story 2

- [ ] T020 [P] [US2] Create [Entity] model in src/models/[entity].py
- [ ] T021 [US2] Implement [Service] in src/services/[service].py
- [ ] T022 [US2] Implement [endpoint/feature] in src/[location]/[file].py
- [ ] T023 [US2] Integrate with User Story 1 components (if needed)

**Checkpoint**: At this point, User Stories 1 AND 2 should both work independently

---

## Phase 5: User Story 3 - [Title] (Priority: P3)

**Goal**: [Brief description of what this story delivers]

**Independent Test**: [How to verify this story works on its own]

### Tests for User Story 3 (OPTIONAL - only if tests requested) ⚠️

- [ ] T024 [P] [US3] Contract test for [endpoint] in tests/contract/test_[name].py
- [ ] T025 [P] [US3] Integration test for [user journey] in tests/integration/test_[name].py

### Implementation for User Story 3

- [ ] T026 [P] [US3] Create [Entity] model in src/models/[entity].py
- [ ] T027 [US3] Implement [Service] in src/services/[service].py
- [ ] T028 [US3] Implement [endpoint/feature] in src/[location]/[file].py

**Checkpoint**: All user stories should now be independently functional

---

[Add more user story phases as needed, following the same pattern]

---

## Phase N: Polish & Cross-Cutting Concerns

**Purpose**: Improvements that affect multiple user stories

- [ ] TXXX [P] Documentation updates in docs/
- [ ] TXXX Code cleanup and refactoring
- [ ] TXXX Performance optimization across all stories
- [ ] TXXX [P] Additional unit tests (if requested) in tests/unit/
- [ ] TXXX Security hardening
- [ ] TXXX Run quickstart.md validation

---

## Phase N+1: Continuous Code Review

*REQUIRED when the spec has three or more implementation phases or user-story phases (Constitution Principle XIII — Continuous Code Review Discipline). For specs with fewer phases, this section is replaced by a single end-of-PR review task in Phase N (Polish).*

**Purpose**: catch quality issues — hacks, scope creep, premature abstraction, under-design, dev-guide drift, spec-violation slips — at the cheapest possible moment. Per-phase reviews catch local issues; cross-phase seam reviews catch architectural drift at hand-off boundaries; the final review catches anything that requires the full picture.

**How**: each review task dispatches the `code-review` agent (via the `task` tool with `agent_type: "code-review"`) with a precise SCOPE statement tailored to the phase. BLOCKING / HIGH findings MUST be addressed before the next phase begins. MEDIUM / LOW findings get logged in the spec's conformance-gap-list (or equivalent tracking artifact) for the final-review sweep to verify resolution or accept with sign-off.

### Per-story / per-phase reviews (execute at each user-story phase Checkpoint)

- [ ] TXXX CODE REVIEW (Phase N / US1): Dispatch the code-review agent. Scope: review the commits implementing US1 against the spec's FR list for this story. Verify: (a) every FR has corresponding implementation; (b) every SC has a behavior-deep test (no shape-only assertions); (c) pre-existing tests broken by this phase were PORTED per the spec's "Hardening pre-existing tests" subsection (deletion requires gap-list justification); (d) RED commits precede GREEN commits in git history; (e) no new public surface beyond what spec / data-model authorized; (f) no `# type: ignore` / `# pylint: disable` without justification; (g) no hacks introduced (no premature abstraction, no scaffolding-that-will-be-removed-later, no internal-symbol monkey-patching in tests). Address BLOCKING / HIGH findings before next phase begins.
- [ ] TXXX CODE REVIEW (Phase N+1 / US2): [same template, scoped to US2]
- [ ] TXXX CODE REVIEW (Phase N+2 / US3): [same template, scoped to US3]
- [Add one per user-story / implementation phase]

### Cross-phase seam reviews (execute at architectural phase boundaries)

*Required at any phase boundary whose hand-off is architecturally significant — e.g., a phase that introduces an API surface another phase will consume, or a phase that mutates a hot-path another phase will further mutate. The plan's Implementation Ordering Strategy identifies these boundaries.*

- [ ] TXXX CODE REVIEW (Phase A→B seam): Dispatch the code-review agent. Scope: review the seam between completed Phase A and upcoming Phase B from a "is the next phase's consumer going to love this or fight it?" perspective. Verify: (a) the seam signature is parameter-stable for Phase B consumers; (b) no premature abstraction in Phase A that Phase B will invalidate; (c) no under-design in Phase A that Phase B will have to monkey-patch around; (d) data formats are stable; (e) public surface introduced in Phase A is consistent with what Phase B will introduce (no naming inconsistencies, no overlapping concerns); (f) no Phase A scaffolding will be removed by Phase B (no throw-away code shipped). Findings here often surface design issues that are cheap to fix now and expensive later.
- [ ] TXXX CODE REVIEW (Phase B→C seam): [same template, scoped to that boundary]
- [Add one per architecturally-significant phase boundary]

### Final whole-PR holistic review (last task before PR ready for human review)

- [ ] TXXX CODE REVIEW (whole PR / holistic): Dispatch the code-review agent. Scope: review the entire PR against the spec holistically. Verify:
  - **Spec coverage**: every FR has implementation + test; conformance-gap-list (or equivalent) is complete; every SC passes with a behavior-deep test.
  - **Public surface match**: the spec's affected-symbols enumeration matches the implementation symbol-for-symbol — no extras, no missing, no aliased re-exports of removed symbols.
  - **Documentation truth**: dev guide accurately reflects the implementation; doc-review meta-test (if any) passes; CHANGELOG reflects every public-surface change; source docstrings agree with the guide on every contract claim.
  - **Sample handling**: samples either updated per the spec's Samples Affected matrix OR deferred-with-justification recorded in `tasks.md` / conformance-gap-list.
  - **Plan-phase decisions resolved**: any deferred implementation decisions from the plan-phase are decided and documented.
  - **Constitution exit checklists**: all applicable Constitution Principle X / XII / XIII exit checklists are complete.
  - **No hacks**: no synthetic-bypass mechanisms in tests; no monkey-patched internal symbols; no scaffolding-that-will-be-removed-later code present; no "TODO: revisit in next PR" comments without a tracked issue.
  - **No regression**: the existing test suite passes at the same count as the baseline plus the new tests; no test was deleted without gap-list justification.
  - **Commit history hygiene**: RED-first commits precede GREEN commits for every conformance test per Constitution Principle XII §3.
  - **Lint / type / build clean**: all release-blocking checks (pylint, mypy, pyright, sphinx) green.

Address BLOCKING / HIGH findings before marking the PR ready for human review. MEDIUM / LOW findings should be either resolved or explicitly accepted with a one-line justification in the conformance-gap-list.

**Checkpoint annotations**: each Checkpoint marker in the intervening phases MUST be annotated with `→ Run TXXX before moving to Phase Y` arrows pointing at its gating review task. This makes the review fence explicit at the point of execution.

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion - BLOCKS all user stories
- **User Stories (Phase 3+)**: All depend on Foundational phase completion
  - User stories can then proceed in parallel (if staffed)
  - Or sequentially in priority order (P1 → P2 → P3)
- **Polish (Final Phase)**: Depends on all desired user stories being complete

### User Story Dependencies

- **User Story 1 (P1)**: Can start after Foundational (Phase 2) - No dependencies on other stories
- **User Story 2 (P2)**: Can start after Foundational (Phase 2) - May integrate with US1 but should be independently testable
- **User Story 3 (P3)**: Can start after Foundational (Phase 2) - May integrate with US1/US2 but should be independently testable

### Within Each User Story

- Tests (if included) MUST be written and FAIL before implementation
- Models before services
- Services before endpoints
- Core implementation before integration
- Story complete before moving to next priority

### Parallel Opportunities

- All Setup tasks marked [P] can run in parallel
- All Foundational tasks marked [P] can run in parallel (within Phase 2)
- Once Foundational phase completes, all user stories can start in parallel (if team capacity allows)
- All tests for a user story marked [P] can run in parallel
- Models within a story marked [P] can run in parallel
- Different user stories can be worked on in parallel by different team members

---

## Parallel Example: User Story 1

```bash
# Launch all tests for User Story 1 together (if tests requested):
Task: "Contract test for [endpoint] in tests/contract/test_[name].py"
Task: "Integration test for [user journey] in tests/integration/test_[name].py"

# Launch all models for User Story 1 together:
Task: "Create [Entity1] model in src/models/[entity1].py"
Task: "Create [Entity2] model in src/models/[entity2].py"
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup
2. Complete Phase 2: Foundational (CRITICAL - blocks all stories)
3. Complete Phase 3: User Story 1
4. **STOP and VALIDATE**: Test User Story 1 independently
5. Deploy/demo if ready

### Incremental Delivery

1. Complete Setup + Foundational → Foundation ready
2. Add User Story 1 → Test independently → Deploy/Demo (MVP!)
3. Add User Story 2 → Test independently → Deploy/Demo
4. Add User Story 3 → Test independently → Deploy/Demo
5. Each story adds value without breaking previous stories

### Parallel Team Strategy

With multiple developers:

1. Team completes Setup + Foundational together
2. Once Foundational is done:
   - Developer A: User Story 1
   - Developer B: User Story 2
   - Developer C: User Story 3
3. Stories complete and integrate independently

---

## Notes

- [P] tasks = different files, no dependencies
- [Story] label maps task to specific user story for traceability
- Each user story should be independently completable and testable
- Verify tests fail before implementing
- Commit after each task or logical group
- Stop at any checkpoint to validate story independently
- Avoid: vague tasks, same file conflicts, cross-story dependencies that break independence
