# Data Model: Python TypeSpec Code Generation Tooling

**Branch**: `34167-python-typespec-codegen` | **Date**: 2026-03-12

## Entities

This feature is a build-tooling feature. It does not introduce runtime data models into the application. The "entities" are configuration files and build artifacts.

### TypeSpec Emitter Configuration

**Source**: `type_spec/tspconfig.yaml`

| Field | Type | Description |
|-------|------|-------------|
| emit | list[string] | Emitter package names to invoke |
| options.`<emitter>`.emitter-output-dir | string | Output directory path (supports placeholders) |
| options.`<emitter>`.package-name | string | Target package name |
| options.`<emitter>`.package-mode | string | `"dataplane"` or `"mgmt"` |
| options.`<emitter>`.flavor | string | `"azure"` for Azure SDK styling |
| options.`<emitter>`.generate-test | bool | Generate test stubs |
| options.`<emitter>`.generate-sample | bool | Generate sample code |
| imports | list[string] | TypeSpec library imports |

### TypeSpec Source Location

**Source**: `type_spec/tsp-location.yaml`

| Field | Type | Description |
|-------|------|-------------|
| directory | string | Path within the specs repo |
| commit | string | Git commit SHA to pin |
| repo | string | GitHub repository (org/repo) |
| additionalDirectories | list[string] | Extra spec directories to fetch |

### Makefile Targets

| Target | Dependencies | Description |
|--------|-------------|-------------|
| `generate-models` | (prerequisites installed) | Runs `tsp-client generate` to compile TypeSpec → Python models |
| `clean` | none | Removes generated output directory |
| `install-typespec-deps` | Node.js available | Installs `tsp-client` CLI and syncs TypeSpec sources |

### Generated Output Structure

**Destination**: `azure/ai/responses/server/_generated/`

| Path | Description |
|------|-------------|
| `models/_models.py` | Generated model classes |
| `models/_enums.py` | Generated enum types |
| `models/__init__.py` | Model re-exports |
| `_utils/model_base.py` | Base model class |
| `_utils/serialization.py` | Serialization utilities |
| `__init__.py` | Package init |

## Relationships

```
tsp-location.yaml  ──fetches──▶  TempTypeSpecFiles/  ──compiled by──▶  tspconfig.yaml
                                                                            │
                                                                            ▼
                                                              azure/ai/responses/server/_generated/
```

## Validation Rules

- `tspconfig.yaml` MUST include `@azure-tools/typespec-python` in the `emit` list
- `tsp-location.yaml` MUST point to a valid commit in `Azure/azure-rest-api-specs`
- The output directory MUST be `azure/ai/responses/server/_generated/`
- Generated files MUST NOT be manually edited (use `_patch.py` pattern for customizations)

## State Transitions

Not applicable — this feature is stateless build tooling. Each invocation is an independent transformation from TypeSpec sources to Python output.
