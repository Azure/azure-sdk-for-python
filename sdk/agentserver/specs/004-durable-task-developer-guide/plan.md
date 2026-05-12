# Implementation Plan: Durable Task Developer Guide

**Branch**: `004-durable-task-developer-guide` | **Date**: 2026-05-12 | **Spec**: `specs/004-durable-task-developer-guide/spec.md`  
**Input**: Feature specification from `/specs/004-durable-task-developer-guide/spec.md`

## Summary

Create a comprehensive developer guide for the durable task API in `azure-ai-agentserver-core`. The guide is the sole deliverable — no code changes. It must enable a developer with no prior durable-task knowledge to implement a crash-resilient agent from the guide alone, following the style and tone of the existing `handler-implementation-guide.md` in the responses package.

## Technical Context

**Language/Version**: Python 3.10+  
**Primary Dependencies**: `azure-ai-agentserver-core` (durable module)  
**Storage**: N/A (documentation only)  
**Testing**: Syntax check of code examples via `python -c "compile(...)"`  
**Target Platform**: Developer documentation (Markdown)  
**Project Type**: Library documentation  
**Performance Goals**: N/A  
**Constraints**: 400–600 lines, self-contained, zero private imports in examples  
**Scale/Scope**: Single markdown file covering 16 public API symbols

## Constitution Check

| Gate | Status | Notes |
|------|--------|-------|
| II. Strong Type Safety | ✅ PASS | All code examples will use precise type annotations |
| III. Azure SDK Compliance | ✅ PASS | Guide follows Azure SDK doc conventions |
| VI. Observability | ✅ N/A | No runtime code |
| VII. Minimal Surface | ✅ PASS | Documents existing API only, no new API |
| Sample E2E Tests | ✅ N/A | No new samples — guide references existing samples |

No constitution violations.

## Project Structure

### Documentation (this feature)

```text
specs/004-durable-task-developer-guide/
├── spec.md              # Feature specification
├── research.md          # API inventory & guide outline
├── plan.md              # This file
└── tasks.md             # Implementation tasks
```

### Source Code (deliverable)

```text
azure-ai-agentserver-core/
└── docs/
    └── durable-task-developer-guide.md   # THE deliverable (~500 lines)
```

**Structure Decision**: Single file. The guide lives alongside the existing `docs/` folder pattern established by the responses package. No other files created.

## Guide Outline (13 Sections)

| # | Section | Approx Lines | Maps to User Story |
|---|---------|-------------|-------------------|
| 1 | Overview | 20 | US1 |
| 2 | Getting Started | 40 | US1 |
| 3 | Lifecycle Automation | 60 | US2 |
| 4 | TaskContext | 50 | US1, US2 |
| 5 | Suspend & Resume | 50 | US3 |
| 6 | Streaming | 30 | US5 |
| 7 | Persistence | 40 | US3 |
| 8 | The Invocation Store Pattern | 50 | US3 |
| 9 | RetryPolicy | 30 | US1 |
| 10 | Decorator Options | 30 | US1 |
| 11 | Error Handling | 40 | US4 |
| 12 | Best Practices | 30 | US4 |
| 13 | Common Mistakes | 40 | US4 |

**Total**: ~510 lines (within 400–600 target)

## Key Design Decisions

1. **One file, not many** — The responses guide is a single file. We follow the same pattern.
2. **Code examples are inline** — No references to sample files. Every example is self-contained in the guide.
3. **Lifecycle state diagram is text-based** — ASCII art, not an image.
4. **"Coming soon" for unimplemented features** — Cancellation, timeout, terminate are mentioned briefly but not documented in detail (they're backlog items 3–5).
5. **Entry mode table is the centerpiece** — The state × action → entry_mode table is the most important reference in the guide.

## Dependencies & Execution Order

This is a linear writing task — each section builds on the previous:

1. **Phase 1**: Scaffolding — create file, write TOC + Overview + Getting Started
2. **Phase 2**: Core API — Lifecycle, TaskContext, Suspend & Resume (the P1 stories)
3. **Phase 3**: Patterns — Persistence, Invocation Store Pattern, Streaming
4. **Phase 4**: Reference — RetryPolicy, Decorator Options, Error Handling
5. **Phase 5**: Safety — Best Practices, Common Mistakes
6. **Phase 6**: Validation — Verify all code examples, check line count, verify API coverage

Phases are sequential (each section references concepts from earlier sections).

## Notes

- The guide documents what IS implemented today — not aspirational features
- All code examples must use only public imports from `azure.ai.agentserver.core.durable`
- The persistence section must clearly state: "The framework persists task lifecycle. You persist everything else."
- Anti-patterns from spec 003 development (asyncio.create_task for result collection, in-memory stores) are real mistakes to document
