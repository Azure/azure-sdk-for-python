# Phase 0 Research: Azure Cosmos → Fabric Mirror Mapper (Python)

This document resolves key technical unknowns and locks the decisions needed to proceed to design and implementation planning.

## Decision: Translation Strategy (Parser + AST)

- **Decision**: Use a real parser for a defined Cosmos SQL subset and translate via an internal AST (not ad-hoc string rewriting).
- **Rationale**:
  - Preserves semantics more reliably than regex/string manipulation.
  - Enables deterministic translation and targeted unsupported-feature detection.
  - Simplifies adding features incrementally with tests.
- **Alternatives considered**:
  - Regex-based rewriting: too brittle for nested expressions and aliasing.
  - Full Cosmos SQL grammar implementation: too large for MVP.

## Decision: Parsing Library (`lark`)

- **Decision**: Use `lark` for the initial Cosmos SQL subset grammar.
- **Rationale**:
  - Lightweight, pure Python, good for building a constrained grammar.
  - Supports explicit AST construction.
- **Alternatives considered**:
  - `antlr4`: heavier operational complexity for a subset grammar.
  - `pyparsing`: workable, but grammar management tends to become harder over time.

## Decision: Driver Interface (DB-API 2.0 Protocol + `mssql-python` Primary)

- **Decision**: Define a small internal "driver client" protocol following Python DB-API 2.0 specification, with `mssql-python` as the primary driver and optional `pyodbc` support for backward compatibility.
- **Rationale**:
  - **`mssql-python` advantages** (see [detailed research](research/python-sql-driver-options.md)):
    - **Zero system dependencies on Windows** - Single `pip install`, no ODBC driver installation required
    - **Official Microsoft driver** - First-party support, actively maintained
    - **Explicitly documented for Fabric SQL** - Microsoft docs show usage with "SQL database in Fabric"
    - **Simplified cross-platform** - Minimal system libs on Linux/macOS vs full ODBC driver stack
    - **Native TDS protocol** - No ODBC layer overhead
    - **Full Entra ID support** - ActiveDirectoryInteractive, MSI, ServicePrincipal, Password
  - Keeps the core mapper independent of any single driver package via DB-API 2.0 protocol.
  - Allows future adapters or fallback to `pyodbc` for specific use cases.
  - Dramatically reduces installation friction and user onboarding complexity.
- **Alternatives considered**:
  - Hard dependency on `pyodbc`: Requires system-level ODBC driver installation (separate download, admin rights on Windows) - poor UX.
  - `pymssql` (FreeTDS-based): Not officially maintained by Microsoft, limited Entra ID support, still requires system FreeTDS library.
  - Building a custom driver: Out of scope and duplicates Microsoft's work.

## Decision: Credential Handling (Pass-through + No Persistence)

- **Decision**: Treat credentials as opaque inputs passed to driver connection creation; never persist credentials by default.
- **Rationale**:
  - Matches non-negotiable security requirement.
  - Avoids accidental leakage through logging or file-based config.
- **Alternatives considered**:
  - Mapper-managed secret storage: out of scope and risky.

## Decision: Diagnostics & Redaction (Normalize + Explicit Redaction)

- **Decision**: Diagnostics report a normalized/redacted query representation and metadata (correlation id, feature flags); never log full query text with literals.
- **Rationale**:
  - Enables troubleshooting without leaking sensitive data.
  - Works even when users include secrets or PII in query parameters.
- **Alternatives considered**:
  - Logging the mapped SQL: too risky; can include inferred shapes and identifiers.

## Decision: Initial Supported Cosmos SQL Subset

- **Decision**: Start with a common subset:
  - `SELECT` projections (including `SELECT *`-like patterns as documented)
  - `FROM c`
  - `WHERE` with boolean expressions, comparisons, AND/OR/NOT
  - Parameter references (e.g., `@param`)
  - `ORDER BY` (single/multi column as supported)
  - `OFFSET`/`LIMIT` pagination
- **Rationale**:
  - Covers the majority of typical read/query workloads.
  - Keeps MVP focused; unsupported features can fail fast with targeted messages.
- **Alternatives considered**:
  - Supporting the entire Cosmos SQL surface: too large for initial delivery.

## Decision: Minimal Cosmos SDK Integration Contract (Dynamic Import Hook)

- **Decision**: Cosmos SDK should integrate via a tiny opt-in hook:
  - A new config knob enables mirror serving.
  - SDK performs dynamic import of the mapper module only when enabled.
  - Missing module results in a dedicated, actionable error.
- **Rationale**:
  - Satisfies “no breakage when not installed” and “minimal SDK change” requirements.
  - Keeps mapping concerns isolated in the mapper package.
- **Alternatives considered**:
  - Monkey-patching only: avoids SDK changes, but is fragile and harder to support.

## Open Items (intentionally deferred)

- Exact Fabric SQL dialect nuances for mirrored Cosmos schemas (to be captured in compatibility matrix).
- Continuation token semantics parity (document and best-effort support).
