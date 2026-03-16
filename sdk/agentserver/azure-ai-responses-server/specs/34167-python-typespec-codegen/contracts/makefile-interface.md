# Makefile Interface Contract

**Purpose**: Defines the public interface of the Makefile — the targets developers invoke.

## Targets

### `make generate-models`

**Description**: Compiles TypeSpec definitions into Python model classes.

**Prerequisites**: `tsp-client` CLI installed, TypeSpec sources synced (`TempTypeSpecFiles/` populated).

**Behavior**:
1. Validates that `tsp-client` is available on PATH
2. Runs `tsp-client generate` from the `type_spec/` directory
3. Generated output lands in `azure/ai/responses/server/_generated/`

**Exit codes**:
- `0`: Generation succeeded
- Non-zero: Generation failed (TypeSpec compile error, missing prerequisites, etc.)

**Stdout/Stderr**: Passes through `tsp-client` output. On prerequisite failure, prints an actionable error message before exiting.

---

### `make clean`

**Description**: Removes all previously generated Python model files.

**Prerequisites**: None.

**Behavior**:
1. Removes the `azure/ai/responses/server/_generated/` directory and all contents

**Exit codes**:
- `0`: Clean succeeded (including if directory did not exist)

---

### `make install-typespec-deps`

**Description**: Installs TypeSpec tooling prerequisites and syncs TypeSpec source files.

**Prerequisites**: Node.js (v18+) and npm available on PATH.

**Behavior**:
1. Validates that `node` and `npm` are available
2. Installs `@azure-tools/typespec-client-generator-cli` globally via npm (provides `tsp-client` CLI)
3. Runs `tsp-client sync` from the `type_spec/` directory to fetch TypeSpec sources into `TempTypeSpecFiles/`

**Exit codes**:
- `0`: All prerequisites installed and sources synced
- Non-zero: Node.js/npm not found, or network error during install/sync

**Stdout/Stderr**: Passes through npm/tsp-client output. On missing Node.js, prints: `"Error: Node.js (v18+) is required. Install from https://nodejs.org/"`

---

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `OUTPUT_DIR` | `azure/ai/responses/server/_generated` | Override generated output directory |
| `TYPESPEC_DIR` | `type_spec` | Directory containing TypeSpec definitions |

## Invocation Examples

```bash
# First-time setup
make install-typespec-deps

# Generate Python models
make generate-models

# Clean and regenerate
make clean generate-models

# Override output directory
make generate-models OUTPUT_DIR=custom/path
```
