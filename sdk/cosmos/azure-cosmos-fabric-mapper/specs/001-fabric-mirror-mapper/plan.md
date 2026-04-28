# Implementation Plan: Azure Cosmos → Fabric Mirror Mapper (Python)

**Branch**: `001-fabric-mirror-mapper` | **Date**: 2026-01-30 | **Spec**: [specs/001-fabric-mirror-mapper/spec.md](spec.md)
**Input**: Feature specification from `specs/001-fabric-mirror-mapper/spec.md`

**Status**: Updated with SQL driver research findings (mssql-python as primary driver)

## Summary

Build a separately installable Python package (`azure-cosmos-fabric-mapper`) that can:
- Translate Cosmos-style query text + parameters into driver-ready SQL for querying Fabric Warehouse endpoints that serve mirrored Cosmos data.
- Pass through credentials/configuration securely to the underlying SQL driver.
- Map tabular driver results back into Cosmos-like result shapes.

This repo does not modify the Azure Cosmos DB Python SDK directly; instead it produces **minimal SDK integration instructions** that keep all mapping concerns isolated in the mapper module and preserve normal SDK behavior when the mapper is not installed.

**Key Update (2026-01-30)**: Driver strategy changed from pyodbc to `mssql-python` as primary driver based on [research findings](research/python-sql-driver-options.md) - eliminates system ODBC driver requirement on Windows.

## Technical Context

**Language/Version**: Python 3.11+  
**Primary Dependencies**: `mssql-python` (primary SQL driver, pure Python), `lark` (query parsing), `azure-identity` (authentication), stdlib `logging`  
**Storage**: N/A  
**Testing**: pytest  
**Target Platform**: Windows + Linux + macOS  
**Project Type**: single (Python library package)  
**Performance Goals**: query translation overhead typically < 2ms per query for common patterns; no extra network hops beyond driver execution  
**Constraints**: no secrets in logs/errors; mapping OFF by default; deterministic translation for supported subset  
**Scale/Scope**: start with a well-defined Cosmos SQL subset used by typical applications; expand via feature flags and a compatibility matrix

**Driver Strategy Update (2026-01-30)**:
- **Primary driver**: `mssql-python` (Microsoft's official pure Python TDS driver)
  - **Windows**: Zero system dependencies - just `pip install`
  - **Linux/macOS**: Minimal system libraries (libltdl, krb5, openssl)
  - **Benefits**: No ODBC driver installation, official Fabric support, simplified deployment
- **Legacy support**: `pyodbc` maintained for backward compatibility (optional)
- Both drivers use same DB-API 2.0 interface, minimal code duplication
- See [research/python-sql-driver-options.md](research/python-sql-driver-options.md) for detailed analysis

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

Based on [.specify/memory/constitution.md](../../.specify/memory/constitution.md):

- ✅ **Optional dependency**: mapper is a separately published package; SDK only imports it when mirror serving is explicitly enabled.
- ✅ **Minimal SDK changes**: integration requires only a narrow hook + dynamic import; no mapping logic lands in the SDK.
- ✅ **Security**: credentials are never logged/persisted by default and are never interpolated into query text.
- ✅ **Correctness**: translation preserves semantics for the supported subset; unsupported constructs fail fast with targeted errors.
- ✅ **Simplified installation** (NEW): `mssql-python` primary driver eliminates system ODBC driver requirement on Windows, significantly reducing onboarding friction.

Status: **PASS** - No violations required. Driver change actually strengthens the "optional dependency" principle by removing system-level installation barriers.

## Project Structure

### Documentation (this feature)

```text
specs/001-fabric-mirror-mapper/
├── plan.md              # This file (implementation plan)
├── spec.md              # Feature specification
├── research.md          # Phase 0 output (main research)
├── research/            # Additional research artifacts
│   └── python-sql-driver-options.md  # SQL driver comparison & decision
├── data-model.md        # Phase 1 output
├── quickstart.md        # Phase 1 output
├── contracts/           # Phase 1 output
│   ├── python-api.md
│   └── sdk-integration-implementation.md
├── checklists/
│   └── requirements.md
└── tasks.md             # Phase 2 output
```

### Source Code (repository root)

```text
src/azure_cosmos_fabric_mapper/
├── __init__.py
├── config.py                 # MirrorServingConfiguration + validation
├── credentials.py            # CredentialSource abstractions
├── errors.py                 # Dedicated errors (missing module, unsupported feature, auth, etc.)
├── diagnostics.py            # Redaction + normalized query representations
├── translate/
│   ├── __init__.py
│   ├── ast.py                # Minimal AST for supported Cosmos query subset
│   ├── parser.py             # Cosmos SQL subset parser
│   ├── fabric_sql.py         # AST → Fabric SQL (parameterized)
│   └── parameters.py         # Cosmos params → driver params
├── driver/
│   ├── __init__.py
│   ├── base.py               # DriverClient protocol (DB-API 2.0 compliant)
│   ├── mssql_driver.py       # PRIMARY: mssql-python adapter (pure Python, no system deps on Windows)
│   └── pyodbc_driver.py      # LEGACY: pyodbc adapter (optional, for backward compatibility)
├── results/
│   ├── __init__.py
│   └── mapper.py             # Tabular rows/cols → Cosmos-like documents
└── sdk_hook/
    ├── __init__.py
    └── contract.py           # The minimal interface the Cosmos SDK calls into

tests/
├── unit/
│   ├── test_translation_golden.py
│   ├── test_parameterization.py
│   ├── test_result_mapping.py
│   ├── test_redaction.py
│   └── fixtures/
│       └── golden_queries.json
└── integration/
    ├── test_e2e_cosmos_fabric_comparison.py
    └── test_driver_roundtrip.py

pyproject.toml           # Updated with mssql-python as primary dependency
README.md                # Updated installation instructions (much simpler!)
CHANGELOG.md
```

**Structure Decision**: Single Python library with strict separation between translation, driver connectivity (now primarily `mssql-python`), and SDK-facing hook surfaces.

## Phase 0: Outline & Research

**Status**: ✅ **COMPLETED**

Output artifacts:
- `specs/001-fabric-mirror-mapper/research.md` - Core research decisions
- `specs/001-fabric-mirror-mapper/research/python-sql-driver-options.md` - **NEW**: SQL driver comparison and decision

### Research Summary

All critical decisions have been locked:

1. ✅ **Translation Strategy**: Parser + AST (using `lark`)
2. ✅ **Parsing Library**: `lark` for Cosmos SQL subset
3. ✅ **Driver Interface**: DB-API 2.0 protocol with `mssql-python` as primary driver
   - **Key finding**: `mssql-python` eliminates system ODBC driver requirement on Windows
   - Backward compatibility maintained via optional `pyodbc` support
4. ✅ **Credential Handling**: Pass-through, no persistence
5. ✅ **Diagnostics**: Normalized/redacted query representation
6. ✅ **Initial Cosmos SQL Subset**: SELECT, FROM, WHERE, parameters, ORDER BY, OFFSET/LIMIT
7. ✅ **SDK Integration**: Dynamic import hook

**Major Update (2026-01-30)**: Driver strategy changed from pyodbc-only to `mssql-python`-primary based on research showing:
- No system driver installation on Windows (just `pip install`)
- Official Microsoft support for Fabric SQL endpoints
- Simplified deployment and user onboarding
- Full Microsoft Entra ID authentication support
- DB-API 2.0 compliant (drop-in replacement for pyodbc)

See [research/python-sql-driver-options.md](research/python-sql-driver-options.md) for detailed analysis.

## Phase 1: Design & Contracts

**Status**: ✅ **COMPLETED** (needs minor updates for driver change)

Output artifacts:
- `specs/001-fabric-mirror-mapper/data-model.md`
- `specs/001-fabric-mirror-mapper/contracts/python-api.md`
- `specs/001-fabric-mirror-mapper/contracts/sdk-integration-implementation.md`
- `specs/001-fabric-mirror-mapper/quickstart.md`

**Action Required**: Update documentation to reflect `mssql-python` as primary driver:
1. Update installation instructions (much simpler on Windows!)
2. Update driver adapter examples
3. Add migration guide for existing pyodbc users

## Phase 2: Implementation Tasks

**Status**: ⚠️ **IN PROGRESS** - Driver migration needed

See `specs/001-fabric-mirror-mapper/tasks.md` for detailed task breakdown.

**Key tasks for driver migration**:
1. Create `src/azure_cosmos_fabric_mapper/driver/mssql_driver.py`
2. Update `pyproject.toml` dependencies
3. Update README.md installation instructions
4. Add tests for `mssql-python` driver
5. Document migration path from pyodbc
6. Test against actual Fabric SQL endpoint

**Estimated effort**: 2-4 hours for driver adapter + 1-2 hours for documentation updates.

## Next Steps

1. ✅ Research completed - SQL driver decision locked
2. ⏭️ Update documentation with new driver approach
3. ⏭️ Implement `mssql_driver.py` adapter
4. ⏭️ Test against Fabric SQL endpoint
5. ⏭️ Update README and migration guide
6. ⏭️ Release with clear changelog about driver change
```

**Structure Decision**: [Document the selected structure and reference the real
directories captured above]

## Complexity Tracking

> **Fill ONLY if Constitution Check has violations that must be justified**

| Violation | Why Needed | Simpler Alternative Rejected Because |
|-----------|------------|-------------------------------------|
| [e.g., 4th project] | [current need] | [why 3 projects insufficient] |
| [e.g., Repository pattern] | [specific problem] | [why direct DB access insufficient] |
