<!--
  Sync Impact Report
  ==================
  Version change: N/A → 1.0.0 (initial ratification)
  Modified principles: N/A (initial creation)
  Added sections:
    - Core Principles (5 principles defined)
    - Technology Standards (new section)
    - Development Workflow (new section)
    - Governance (filled from template)
  Removed sections: None
  Templates requiring updates:
    - .specify/templates/plan-template.md ✅ no update needed
      (Constitution Check uses dynamic placeholder)
    - .specify/templates/spec-template.md ✅ no update needed
      (no constitution-specific references)
    - .specify/templates/tasks-template.md ✅ no update needed
      (phase structure aligns with principles)
  Follow-up TODOs: None
-->

# Azure AI Responses Server Constitution

## Core Principles

### I. Specification-First Development

All features MUST be fully specified before implementation begins.
Every feature MUST have a written specification (`spec.md`) with
user stories, acceptance criteria, and measurable success criteria
before any code is written. Design artifacts (plan, data model,
contracts) MUST be reviewed and validated against this constitution
before task generation. Rationale: specifications eliminate ambiguity,
reduce rework, and ensure alignment between stakeholders and
implementers.

### II. Test-Driven Quality (NON-NEGOTIABLE)

Tests MUST be written before production code. The Red-Green-Refactor
cycle is strictly enforced: write a failing test, implement the
minimum code to pass, then refactor. Contract tests MUST be written
for every public API endpoint. Integration tests MUST cover
cross-service communication and shared data schemas. No feature is
considered complete until all acceptance scenarios from the
specification pass.

### III. Azure SDK Compliance

All public APIs MUST follow Azure SDK design guidelines for Python.
This includes: consistent naming conventions (`snake_case` for
methods and parameters), standard credential handling via
`azure-identity`, idiomatic error types inheriting from
`azure.core.exceptions`, pagination via standard Azure patterns,
and long-running operations via the Azure poller pattern. The
package MUST be structured as a proper Azure SDK namespace package
under `azure.ai`.

### IV. API Contract Stability

Public API contracts MUST be versioned and backward-compatible within
a major version. Breaking changes MUST increment the major version,
be documented in a changelog, and include a migration guide.
All API contracts MUST be defined in specification artifacts before
implementation. Internal interfaces SHOULD be kept minimal and
decoupled to enable independent evolution of components.

### V. Simplicity & YAGNI

Start with the simplest solution that satisfies the specification.
All architectural complexity MUST be justified against a concrete
requirement — not a hypothetical future need. Abstractions MUST NOT
be introduced until at least two concrete use cases exist. If a
simpler alternative is rejected, the rationale MUST be documented
in the complexity tracking section of the implementation plan.

## Technology Standards

- **Language**: Python 3.10+
- **Framework**: Azure SDK for Python ecosystem
  (`azure-core`, `azure-identity`)
- **Testing**: `pytest` with `pytest-asyncio` for async tests
- **Linting**: `ruff` for formatting and linting
- **Type Checking**: `mypy` in strict mode for public API surfaces
- **Packaging**: `pyproject.toml` with Azure SDK namespace packaging
- **Dependencies**: MUST be kept minimal; every external dependency
  MUST be justified against the simplicity principle

## Development Workflow

- **Feature branches**: Named `###-feature-name` (e.g.,
  `001-initial-api`); auto-numbered across all specs
- **Workflow sequence**: Specify → Clarify → Plan → Tasks →
  Implement → Analyze
- **Code review**: All changes MUST be reviewed before merge;
  reviewers MUST verify constitution compliance
- **Quality gates**: Specification MUST pass clarification before
  planning; plan MUST pass constitution check before tasking;
  all checklist items MUST be resolved before delivery
- **Commit messages**: Follow conventional commits format
  (`feat:`, `fix:`, `docs:`, `test:`, `refactor:`)

## Governance

This constitution is the supreme governing document for the
Azure AI Responses Server project. All specifications, plans,
and implementations MUST comply with the principles defined here.

- **Amendments**: Any change to this constitution MUST be
  documented with a version bump, rationale, and sync impact
  report. Amendments MUST be reviewed and approved before taking
  effect.
- **Versioning**: This constitution follows semantic versioning.
  MAJOR for principle removals or redefinitions, MINOR for new
  principles or material expansions, PATCH for clarifications
  and wording fixes.
- **Compliance review**: The `speckit.analyze` agent MUST verify
  constitution compliance during cross-artifact analysis.
  Violations MUST be resolved or explicitly justified in the
  complexity tracking section before implementation proceeds.

**Version**: 1.0.0 | **Ratified**: 2026-03-12 | **Last Amended**: 2026-03-12
