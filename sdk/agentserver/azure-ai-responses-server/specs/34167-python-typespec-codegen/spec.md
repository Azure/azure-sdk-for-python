# Feature Specification: Python TypeSpec Code Generation Tooling

**Feature Branch**: `34167-python-typespec-codegen`  
**Created**: 2026-03-12  
**Status**: Draft  
**Input**: User description: "files in type_spec contains Response API contract definitions. Current configuration generates models for C#. I need a Makefile tool to generate the contract model for python."

## User Scenarios & Testing

### User Story 1 - Generate Python Models from TypeSpec Definitions (Priority: P1)

A developer working on the Azure AI Responses Server Python SDK runs a single make command and the tooling compiles the TypeSpec contract definitions in the `type_spec/` directory into Python model classes. The generated models correspond to the same API contract currently used to produce C# models, ensuring parity between the two language targets.

**Why this priority**: This is the core value of the feature. Without the ability to generate Python models from the existing TypeSpec definitions, the Python SDK must hand-author and manually maintain contract models, which is error-prone and drifts from the canonical API definition.

**Independent Test**: Can be fully tested by running the make target in a clean environment with TypeSpec tooling installed and verifying that Python model files are generated in the expected output directory without errors.

**Acceptance Scenarios**:

1. **Given** the TypeSpec definitions exist in the `type_spec/` directory, **When** the developer runs the Python code generation make target, **Then** Python model source files are generated in the designated output directory.
2. **Given** the TypeSpec definitions include all response, request, and event types from the Azure AI Responses protocol, **When** code generation completes, **Then** every model type present in the C# output has a corresponding Python model generated.
3. **Given** the developer has already generated models previously, **When** they run the make target again without changes to the TypeSpec source, **Then** the output is identical (idempotent generation).

---

### User Story 2 - Clean and Regenerate Models (Priority: P2)

A developer wants to do a clean regeneration of all Python models — removing previously generated output and producing a fresh set. The Makefile provides a clean target that removes generated artifacts and a workflow to regenerate from scratch.

**Why this priority**: During iterative development on the TypeSpec definitions or code generation configuration, stale or orphaned generated files can cause confusion. A clean + regenerate workflow ensures a known-good state.

**Independent Test**: Can be tested by generating models, manually adding a spurious file in the output directory, running the clean target, and verifying all generated and spurious files are removed. Then running the generate target and verifying a fresh, correct set of models is produced.

**Acceptance Scenarios**:

1. **Given** previously generated Python models exist in the output directory, **When** the developer runs the clean make target, **Then** all generated files are removed.
2. **Given** a clean output directory, **When** the developer runs the generate target, **Then** a complete set of Python models is generated from the current TypeSpec definitions.

---

### User Story 3 - Install Prerequisites for Code Generation (Priority: P2)

A developer cloning the repository for the first time needs to install the TypeSpec compiler and the Python emitter plugin before they can generate models. The Makefile provides a target to install or verify all required prerequisites.

**Why this priority**: Code generation depends on external tooling (TypeSpec compiler, Python emitter). An explicit setup step reduces onboarding friction and ensures the correct versions are installed.

**Independent Test**: Can be tested by running the setup/install target on a machine with Node.js available but no TypeSpec tooling installed, and verifying that subsequent code generation succeeds.

**Acceptance Scenarios**:

1. **Given** a developer has Node.js installed but not the TypeSpec compiler or Python emitter, **When** they run the prerequisites/install make target, **Then** the required TypeSpec packages are installed.
2. **Given** a developer already has the correct versions of all prerequisites, **When** they run the install target, **Then** the command completes successfully without reinstalling or erroring.

---

### Edge Cases

- What happens when the TypeSpec definitions contain syntax errors? The tooling should surface clear TypeSpec compiler error messages.
- What happens when the Python emitter is not installed? The Makefile should fail with a clear message indicating the missing prerequisite and how to install it.
- What happens when Node.js is not available on the system? The Makefile should detect this and provide an actionable error message.
- How does the tooling handle TypeSpec definitions that import remote dependencies (e.g., azure-rest-api-specs)? The prerequisite step should handle dependency resolution.

## Requirements

### Functional Requirements

- **FR-001**: The project MUST provide a Makefile with a target that invokes the TypeSpec compiler to generate Python model code from the definitions in the `type_spec/` directory.
- **FR-002**: The Makefile MUST include a `clean` target that removes all previously generated Python model files.
- **FR-003**: The Makefile MUST include a target to install or verify TypeSpec compiler and Python emitter prerequisites.
- **FR-004**: The Python code generation MUST use a TypeSpec Python emitter that produces idiomatic Python model classes compatible with the Azure SDK for Python conventions.
- **FR-005**: The generated Python models MUST cover the same set of API contract types as the existing C# model generation (full parity with the C# emitter output).
- **FR-006**: The generated Python models MUST be output to `azure/ai/responses/server/_generated/` under the project root.
- **FR-007**: The code generation MUST fail with a clear, actionable error message when prerequisites are missing or TypeSpec definitions contain errors.
- **FR-008**: The code generation MUST be idempotent — running it multiple times on unchanged input produces identical output.

### Key Entities

- **TypeSpec Definition**: The `.tsp` source files in the `type_spec/` directory that define the Azure AI Responses API contract (models, routes, namespaces).
- **Python Model**: A generated Python source file containing typed class definitions that represent the API contract entities (requests, responses, events, enums, etc.).
- **Makefile Target**: A named command in the Makefile that the developer invokes (e.g., `make generate-models`, `make clean`, `make install-typespec-deps`).
- **TypeSpec Emitter Configuration**: The settings (in `tspconfig.yaml` or Makefile variables) that control how the Python emitter generates code — package name, output directory, namespace mapping, etc.

## Success Criteria

### Measurable Outcomes

- **SC-001**: A developer can generate all Python contract models from TypeSpec definitions with a single make command, completing in under 2 minutes on a standard development machine.
- **SC-002**: 100% of the model types produced by the existing C# emitter have corresponding Python models generated.
- **SC-003**: A new contributor can go from a fresh clone to successfully generated Python models within 10 minutes, following documentation and Makefile targets alone.
- **SC-004**: The generated Python model files pass the project's standard linting and type-checking validations without requiring manual edits.
- **SC-005**: Running clean followed by generate produces an output identical to a first-time generation — zero stale or orphaned artifacts.

## Assumptions

- The TypeSpec compiler and its Python emitter plugin are available as npm packages that can be installed via Node.js tooling.
- Developers have Node.js (v18+) and Python (3.10+) installed on their development machines.
- The existing `type_spec/` directory structure and `tspconfig.yaml` provide the foundation; the Python emitter configuration will be added alongside the existing C# emitter configuration.
- The Python emitter will be `@typespec/http-client-python` or an equivalent Azure SDK Python emitter package.
- The Makefile will coexist with the existing `scripts/` directory tooling and not replace any current workflows.
- Generated Python models are checked into the repository (not generated at build time), following Azure SDK conventions.
