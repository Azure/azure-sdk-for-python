# Research: Python TypeSpec Code Generation Tooling

**Branch**: `34167-python-typespec-codegen` | **Date**: 2026-03-12

## R1: TypeSpec Python Emitter Package

**Decision**: Use `@azure-tools/typespec-python`

**Rationale**: This is the emitter used by the azure-sdk-for-python monorepo. The repo-level `eng/emitter-package.json` declares `"@azure-tools/typespec-python": "0.60.2"` as the standard emitter. An alternative `@typespec/http-client-python` exists in the microsoft/typespec repo but is not what the Azure SDK for Python ecosystem uses today.

**Alternatives considered**:
- `@typespec/http-client-python` — newer generic emitter from microsoft/typespec, but not adopted by azure-sdk-for-python yet.

## R2: TypeSpec Source Synchronization

**Decision**: Use `tsp-client sync` to fetch TypeSpec source files, followed by `tsp-client generate` to compile.

**Rationale**: The project already has a `tsp-location.yaml` that points to `Azure/azure-rest-api-specs` at a pinned commit. The standard Azure SDK tooling is `@azure-tools/typespec-client-generator-cli` (provides the `tsp-client` CLI). Running `tsp-client sync` reads `tsp-location.yaml`, fetches TypeSpec sources from the remote repo, and places them in `TempTypeSpecFiles/`. Running `tsp-client generate` then compiles using the emitter config. This is the established workflow across all Azure SDK language repos.

**Alternatives considered**:
- Manual `tsp compile` invocation — would require manually managing dependencies and emitter installation. The `tsp-client` tool handles this automatically.
- Git submodule for azure-rest-api-specs — heavy, requires full repo clone, and the pinned-commit approach in `tsp-location.yaml` is the standard pattern.

## R3: tspconfig.yaml Python Emitter Configuration

**Decision**: Add `@azure-tools/typespec-python` to `tspconfig.yaml` with the following options:

```yaml
"@azure-tools/typespec-python":
    emitter-output-dir: "{output-dir}"
    package-name: "azure-ai-responses-server"
    package-mode: "dataplane"
    flavor: azure
    generate-test: false
    generate-sample: false
```

**Rationale**: These options match the conventions observed in other Azure SDK for Python packages (e.g., azure-ai-agents). `package-mode: dataplane` is correct for a data-plane SDK. `flavor: azure` enables Azure-specific patterns (credentials, error types). Test and sample generation are disabled because the project has its own test infrastructure.

**Alternatives considered**:
- Using `models-mode: dpg` — this is the default and does not need to be specified explicitly.
- Enabling `generate-test: true` — rejected because the project has its own test patterns (pytest + pytest-asyncio as specified in pyproject.toml).

## R4: Output Directory Structure

**Decision**: Generate into `azure/ai/responses/server/_generated/` under the project root.

**Rationale**: The spec (FR-006) mandates this path. The TypeSpec Python emitter by default generates directly into the package namespace (no `_generated/` subdirectory), but the emitter-output-dir can be configured to target a specific subdirectory. Using `_generated/` provides clear separation between generated and hand-authored code, making it obvious which files should not be manually edited.

**Alternatives considered**:
- Generating directly into `azure/ai/responses/server/` (the standard emitter pattern) — rejected because it mixes generated and hand-authored code, making clean regeneration harder.

## R5: Makefile vs PowerShell/Shell Scripts

**Decision**: Use a Makefile that wraps `tsp-client` commands and provides developer-friendly targets.

**Rationale**: The spec explicitly requires a Makefile (FR-001). Makefile is cross-platform (via GNU Make on Windows via Git Bash or WSL, native on macOS/Linux), provides declarative targets with dependencies, and is the standard build tool in many Azure SDK repos for other languages. The existing `scripts/` directory has PowerShell/shell scripts for Python venv setup; the Makefile adds TypeSpec-specific tooling without replacing those scripts.

**Alternatives considered**:
- PowerShell-only scripts — not cross-platform for macOS/Linux developers without PowerShell Core.
- Python-based build scripts (invoke, nox) — adds a Python dependency for a Node.js-based tool workflow; unnecessary complexity.

## R6: Prerequisite Installation

**Decision**: The `install-typespec-deps` target will install `@azure-tools/typespec-client-generator-cli` globally (for `tsp-client`), then run `tsp-client sync` to fetch TypeSpec sources. npm package dependencies are resolved by `tsp-client` itself.

**Rationale**: `tsp-client` is the single entry point that manages the TypeSpec compiler, emitter packages, and source synchronization. Installing it globally makes `tsp-client` available as a CLI command. The `tsp-client generate` command automatically installs required emitter packages based on `tspconfig.yaml` and `eng/emitter-package.json`.

**Alternatives considered**:
- Local npm install with package.json — rejected because `tsp-client` is designed to be used globally and manages its own transient dependencies.
- Pre-bundling node_modules — rejected; unnecessary complexity and staleness risk.
