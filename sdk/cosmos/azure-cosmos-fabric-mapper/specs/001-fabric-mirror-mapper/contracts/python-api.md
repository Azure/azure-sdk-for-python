# Contract: Public Python API (Mapper Package)

This contract defines the expected public interfaces exported by the `azure-cosmos-fabric-mapper` package.

## Goals

- Provide a stable API surface for:
  - translating Cosmos-style queries to driver SQL
  - executing via a driver client
  - mapping results back to Cosmos-like documents
- Keep driver and SDK coupling minimal.

## Proposed Public Modules

- `azure_cosmos_fabric_mapper.config`
- `azure_cosmos_fabric_mapper.credentials`
- `azure_cosmos_fabric_mapper.translate`
- `azure_cosmos_fabric_mapper.driver`
- `azure_cosmos_fabric_mapper.results`
- `azure_cosmos_fabric_mapper.sdk_hook`

## Core Functions (Conceptual)

### Translate

Input:
- Cosmos-style query text
- Cosmos-style parameters
- optional request options

Output:
- driver-ready SQL string
- driver parameters
- translation warnings
- redacted/normalized query string for diagnostics

### Execute

Input:
- MirrorQueryRequest
- DriverClient

Output:
- DriverResultSet

### Map Results

Input:
- DriverResultSet

Output:
- Cosmos-like items + metadata

## Errors

- Missing-mapper installation (when called from SDK hook)
- Unsupported feature/construct
- Connection/auth/driver errors

## Non-Goals

- No requirement to expose a full CLI.
- No requirement to implement a full Cosmos SQL grammar.
