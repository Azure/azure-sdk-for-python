# Data Model: Azure Cosmos → Fabric Mirror Mapper (Python)

This is a technology-agnostic description of the main entities, their fields, and relationships.

## Entities

### MirrorServingConfiguration

Represents user intent to enable mirror serving and the configuration required to route queries to the Fabric mirror.

- `enabled`: boolean
- `endpoint`: string (Fabric Warehouse endpoint identifier/connection target)
- `database`: string (optional)
- `credential_source`: CredentialSource
- `fallback_policy`: enum (e.g., fail-closed, fallback-to-cosmos)
- `diagnostics`: DiagnosticsOptions
- `feature_flags`: map<string, boolean>

### CredentialSource

Represents how credentials are supplied without prescribing storage mechanisms.

- `kind`: enum (e.g., connection_string, token, external_provider)
- `value_ref`: opaque reference (never logged)
- `metadata`: map<string, string> (non-secret)

### CosmosQueryRequest

Represents the query request as seen by the Cosmos client layer.

- `query_text`: string
- `parameters`: list<QueryParameter>
- `request_options`: map<string, any>

### QueryParameter

- `name`: string (e.g., `@id`)
- `value`: any
- `type_hint`: optional string

### MirrorQueryRequest

Represents the driver-ready query.

- `sql_text`: string
- `parameters`: list<DriverParameter>
- `execution_options`: map<string, any>

### DriverParameter

- `name`: string (if supported)
- `value`: any
- `driver_type`: optional string

### QueryTranslationResult

- `mirror_request`: MirrorQueryRequest
- `warnings`: list<TranslationWarning>
- `redacted_query`: string (normalized, safe for logs)

### TranslationWarning

- `code`: string
- `message`: string

### DriverResultSet

Represents tabular results from the driver.

- `columns`: list<Column>
- `rows`: list<Row>
- `metadata`: map<string, any>

### Column

- `name`: string
- `type`: optional string

### CosmosLikeQueryResult

Represents mapped results returned to callers.

- `items`: list<map<string, any>>
- `continuation`: optional string
- `metadata`: map<string, any>

### Error Taxonomy

- `MissingMapperModuleError`: thrown when mirror serving is enabled but the mapper is not installed.
- `UnsupportedFeatureError`: thrown when a Cosmos query construct cannot be translated.
- `MirrorAuthError`: thrown for auth/authorization failures.
- `MirrorConnectionError`: thrown for network/driver connection issues.
- `MirrorExecutionError`: thrown for driver execution errors.

## Relationships

- MirrorServingConfiguration → CredentialSource (1:1)
- CosmosQueryRequest → QueryTranslationResult (1:1)
- QueryTranslationResult → MirrorQueryRequest (1:1)
- MirrorQueryRequest → DriverResultSet (1:1, via DriverClient)
- DriverResultSet → CosmosLikeQueryResult (1:1)

## Notes

- Secrets only live inside `CredentialSource.value_ref` (or equivalent) and must never appear in `redacted_query`, warnings, or logs.
- Continuation semantics may be best-effort depending on mirror endpoint capabilities; document limitations.
