# Implementation Plan: Python TypeSpec Code Generation Tooling

**Branch**: `34167-python-typespec-codegen` | **Date**: 2026-03-12 | **Spec**: [spec.md](spec.md)
**Input**: Feature specification from `/specs/34167-python-typespec-codegen/spec.md`

## Summary

Introduce a Makefile that wraps the Azure SDK `tsp-client` CLI to compile TypeSpec definitions into Python model classes. The Makefile provides three targets — `generate-models` (invoke `tsp-client generate`), `clean` (remove generated output), and `install-typespec-deps` (install `tsp-client` CLI globally and sync TypeSpec sources). The Python emitter `@azure-tools/typespec-python` is added to `tspconfig.yaml` alongside the existing OpenAPI3 emitter. Generated output lands in `azure/ai/responses/server/_generated/`.

## Technical Context

**Language/Version**: Python 3.10+; build tooling in GNU Make + Node.js 18+  
**Primary Dependencies**: `@azure-tools/typespec-python` (v0.60.2 emitter), `@azure-tools/typespec-client-generator-cli` (provides `tsp-client` CLI)  
**Storage**: N/A (build tooling — file system only)  
**Testing**: Manual validation via `make generate-models` + project linting (ruff) and type checking (mypy)  
**Target Platform**: Developer workstations (macOS, Linux, Windows via Git Bash / WSL)  
**Project Type**: Build tooling / configuration (no runtime code)  
**Performance Goals**: Code generation completes in under 2 minutes (SC-001)  
**Constraints**: Must use Azure SDK emitter ecosystem (`tsp-client`, not raw `tsp compile`); generated code must pass ruff + mypy without manual edits  
**Scale/Scope**: Single Makefile, single tspconfig.yaml update; generates ~10-20 Python source files

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Principle | Status | Notes |
|-----------|--------|-------|
| I. Specification-First Development | **PASS** | Spec complete with user stories, acceptance criteria, and success criteria before planning |
| II. Test-Driven Quality | **PASS (adapted)** | This is build tooling, not production code. Validation is via running `make generate-models` and verifying output passes project linting/type-checking. No runtime unit tests needed — the "test" is that generation succeeds and output is correct. |
| III. Azure SDK Compliance | **PASS** | Generated models use `@azure-tools/typespec-python` which produces Azure SDK-compliant Python models by design (snake_case, azure.core types, namespace packaging) |
| IV. API Contract Stability | **PASS** | TypeSpec sources are pinned to a specific commit in `tsp-location.yaml`; regeneration is idempotent on unchanged input |
| V. Simplicity & YAGNI | **PASS** | Makefile wraps existing `tsp-client` CLI — no custom abstraction layers, no framework, no intermediate scripts |

## Project Structure

### Documentation (this feature)

```text
specs/34167-python-typespec-codegen/
├── plan.md              # This file
├── research.md          # Phase 0 output
├── data-model.md        # Phase 1 output
├── contracts/           # Phase 1 output
│   └── makefile-interface.md
└── checklists/
    └── requirements.md
```

### Source Code (repository root)

```text
# Files to create / modify
Makefile                                          # NEW — build targets
type_spec/tspconfig.yaml                          # MODIFY — add Python emitter config

# Generated output (created by make generate-models)
azure/ai/responses/server/_generated/
├── __init__.py
├── models/
│   ├── __init__.py
│   ├── _models.py
│   └── _enums.py
└── _utils/
    ├── model_base.py
    └── serialization.py

# Existing files (unchanged)
type_spec/main.tsp
type_spec/client.tsp
type_spec/tsp-location.yaml
pyproject.toml
scripts/setup-dev-env.ps1
scripts/setup-dev-env.sh
```

**Structure Decision**: Minimal footprint — one new file (Makefile) and one modified file (tspconfig.yaml). Generated output goes into a dedicated `_generated/` subdirectory to separate machine-generated code from hand-authored code. This aligns with Azure SDK conventions and satisfies FR-006.

## Complexity Tracking

No constitution violations. No complexity justifications required.
