---
name: azure-data-tables
description: '**UTILITY SKILL** — Domain knowledge for the azure-data-tables SDK package. Covers architecture, entity encoding/decoding, EDM types, batch transactions, dual-backend (Storage & Cosmos), authentication, and common pitfalls. WHEN: "modify azure-data-tables", "fix tables bug", "add tables feature", "table entity conversion", "tables batch operations".'
---

# azure-data-tables — Package Skill

## Architecture

This package has a **two-layer layout** with generated and hand-authored code:

- `azure/data/tables/_generated/` — Auto-generated from the Azure Tables REST API spec. **Never hand-edit.**
- `azure/data/tables/` — Hand-authored convenience layer wrapping the generated client with Python-idiomatic APIs.

### Sync/Async Mirroring

Every sync module has an async counterpart in `aio/`:

| Sync | Async |
| ---- | ----- |
| `_table_client.py` | `aio/_table_client_async.py` |
| `_table_service_client.py` | `aio/_table_service_client_async.py` |
| `_base_client.py` | `aio/_base_client_async.py` |
| `_authentication.py` | `aio/_authentication_async.py` |
| `_policies.py` | `aio/_policies_async.py` |
| `_models.py` | `aio/_models.py` |

When modifying any client or policy, **always update both sync and async versions**.

### Base Client Pattern

`_base_client.py` / `_base_client_async.py` contain shared client construction logic:
- Connection string parsing
- Endpoint URL normalization
- Pipeline policy configuration
- Credential type detection (SharedKey, SAS, or Token)
- Cosmos vs Storage endpoint detection

## Where to Make Changes

| Goal | Where to edit |
| ---- | ------------- |
| Modify table CRUD (create/delete/query tables) | `_table_service_client.py` / `aio/_table_service_client_async.py` |
| Modify entity CRUD (upsert/get/delete/query entities) | `_table_client.py` / `aio/_table_client_async.py` |
| Change how entities are encoded to wire format | `_encoder.py` |
| Change how entities are decoded from wire format | `_decoder.py` |
| Modify entity types (TableEntity, EntityProperty, EdmType) | `_entity.py` |
| Modify batch transaction logic | `_table_batch.py` |
| Change authentication (SharedKey signing) | `_authentication.py` / `aio/_authentication_async.py` |
| Change SAS token generation | `_table_shared_access_signature.py` |
| Modify pipeline policies (retry, cosmos, etc.) | `_policies.py` / `aio/_policies_async.py` |
| Modify public models (TableAccessPolicy, UpdateMode, etc.) | `_models.py` |
| Modify error handling/mapping | `_error.py` |
| Modify common utilities (URL parsing, connection strings) | `_common_conversion.py` / `_base_client.py` |
| Change serialization of filters/queries | `_serialize.py` |
| Add/remove public exports | `__init__.py` |

**All files listed above are relative to `sdk/tables/azure-data-tables/azure/data/tables/`.**

## The Two Clients

| Client | Constructor | Purpose |
| ------ | ----------- | ------- |
| `TableServiceClient` | `(endpoint, credential, **kwargs)` | Account-level operations: create/delete/list/query tables, get/set service properties |
| `TableClient` | `(endpoint, table_name, credential, **kwargs)` | Table-level entity operations: create/upsert/get/delete/query entities, batch transactions |

### Key Patterns

- Both clients support **context manager** protocol (`with` / `async with`).
- `TableServiceClient` spawns a `TableClient` via `get_table_client(table_name)`.
- `TableClient` has factory classmethods: `from_connection_string(conn_str, table_name)` and `from_table_url(table_url, credential)`.
- `TableServiceClient` also has `from_connection_string(conn_str)`.

### TableServiceClient Operations

- `create_table(table_name)` / `delete_table(table_name)` — CRUD for tables
- `list_tables(**kwargs)` — Returns `ItemPaged[TableItem]`
- `query_tables(query_filter, **kwargs)` — OData-filtered table listing
- `get_service_properties()` / `set_service_properties(...)` — **Storage-only** (see Dual Backend)
- `get_service_stats()` — **Storage-only**

### TableClient Operations

- `create_table()` / `delete_table()` — Create/delete the specific table
- `create_entity(entity)` — Insert a new entity
- `upsert_entity(entity, mode=UpdateMode.MERGE)` — Insert or update
- `update_entity(entity, mode=UpdateMode.MERGE, **kwargs)` — Update with etag support
- `get_entity(partition_key, row_key, **kwargs)` — Get a single entity
- `delete_entity(partition_key, row_key, **kwargs)` — Delete by key or entity object
- `list_entities(**kwargs)` — Returns `ItemPaged[TableEntity]`
- `query_entities(query_filter, **kwargs)` — OData-filtered entity query
- `submit_transaction(operations)` — Atomic batch operations
- `get_table_access_policy()` / `set_table_access_policy(...)` — **Storage-only**

## Entity Model & EDM Types

### TableEntity

`TableEntity` is a subclass of `dict` that represents a table entity. Key properties:
- Always contains `PartitionKey` (str) and `RowKey` (str).
- Metadata (etag, timestamp) is stored separately via `EntityMetadata`, accessed as `entity.metadata`.
- Can be used as a plain dict: `entity = {"PartitionKey": "pk", "RowKey": "rk", "Name": "foo"}`.

### EntityProperty

Wrapper to explicitly specify the EDM type for a property value:

```python
from azure.data.tables import EntityProperty, EdmType

entity = {
    "PartitionKey": "pk",
    "RowKey": "rk",
    "BigNumber": EntityProperty(2**53 + 1, EdmType.INT64),  # Force Int64 encoding
}
```

### EdmType Enum

| EdmType | Python Type | Wire Format |
| ------- | ----------- | ----------- |
| `BINARY` | `bytes` | Base64 string + `Edm.Binary` annotation |
| `BOOLEAN` | `bool` | JSON boolean |
| `DATETIME` | `datetime` | ISO 8601 string + `Edm.DateTime` annotation |
| `DOUBLE` | `float` | JSON number (or `"NaN"`, `"Infinity"`, `"-Infinity"`) |
| `GUID` | `UUID` | String + `Edm.Guid` annotation |
| `INT32` | `int` (≤32-bit) | JSON number |
| `INT64` | `int` (>32-bit) | **String** + `Edm.Int64` annotation |
| `STRING` | `str` | JSON string |

### Auto-Detection Rules (in `_encoder.py`)

When no explicit `EntityProperty` is used, types are auto-detected:
- `bool` → `Edm.Boolean`
- `int` that fits in 32 bits → `Edm.Int32`
- `int` that exceeds 32 bits → `Edm.Int64` (serialized as string)
- `float` → `Edm.Double`
- `str` → `Edm.String`
- `bytes` → `Edm.Binary`
- `datetime` → `Edm.DateTime`
- `UUID` → `Edm.Guid`

## Entity Encoding (Outbound) — `_encoder.py`

The encoder converts Python dicts/TableEntity objects into the OData wire format:

- Each typed property emits a companion `property@odata.type` key:
  ```json
  {
    "Age": 30,
    "BigId": "9007199254740993",
    "BigId@odata.type": "Edm.Int64"
  }
  ```
- `PartitionKey` and `RowKey` **must always be strings** — the encoder enforces this.
- `Int64` values are serialized as **strings** because JSON cannot represent 64-bit integers losslessly.
- `bytes` → base64-encoded string with `Edm.Binary` annotation.
- `datetime` → ISO 8601 UTC string with `Edm.DateTime` annotation.
- `UUID` → string representation with `Edm.Guid` annotation.
- Properties prefixed with `.odata` are passed through without modification (reserved for OData metadata).

## Entity Decoding (Inbound) — `_decoder.py`

The decoder processes JSON responses and restores Python types:

- Reads `property@odata.type` annotations to determine deserialization.
- `Edm.Int64` strings → Python `int`.
- `Edm.Binary` base64 strings → Python `bytes`.
- `Edm.DateTime` ISO strings → Python `datetime` (timezone-aware, UTC).
- `Edm.Guid` strings → Python `UUID`.
- `Edm.Double` handles special values: `"NaN"` → `float('nan')`, `"Infinity"` → `float('inf')`, `"-Infinity"` → `float('-inf')`.
- Properties **without** type annotations are inferred from JSON types (string, number, boolean).

## Batch Transactions — `_table_batch.py`

`TableClient.submit_transaction(operations)` sends a batch of operations atomically.

### Format

- Sent as a **multipart/mixed** HTTP request (OData batch format).
- Each operation is a tuple: `(TransactionOperation, entity)` or `(TransactionOperation, entity, kwargs)`.

### TransactionOperation Enum

- `CREATE` — Insert new entity
- `UPDATE` — Update existing entity (with `mode` kwarg for MERGE vs REPLACE)
- `UPSERT` — Insert or update
- `DELETE` — Delete entity

### Constraints

- All entities in a batch **must share the same `PartitionKey`**.
- Maximum **100 operations** per batch.
- Maximum **4 MB** payload size.
- `TableTransactionError` raised if any operation fails — entire batch is rolled back.
- `RequestTooLargeError` raised if payload exceeds size limit.

### Example

```python
operations = [
    (TransactionOperation.CREATE, {"PartitionKey": "pk", "RowKey": "rk1", "Name": "Alice"}),
    (TransactionOperation.CREATE, {"PartitionKey": "pk", "RowKey": "rk2", "Name": "Bob"}),
    (TransactionOperation.DELETE, {"PartitionKey": "pk", "RowKey": "rk3"}),
]
table_client.submit_transaction(operations)
```

## Authentication

### Credential Types

| Credential | Import | Usage |
| ---------- | ------ | ----- |
| `AzureNamedKeyCredential` | `azure.core.credentials` | SharedKey (account name + key). HMAC-SHA256 signing in `_authentication.py`. |
| `AzureSasCredential` | `azure.core.credentials` | SAS token appended to request URL. |
| `TokenCredential` | `azure.identity` (e.g., `DefaultAzureCredential`) | AAD/Entra ID bearer token authentication. |
| Connection string | Built-in parsing | `TableClient.from_connection_string(conn_str, table_name)` |

### SAS Generation

- `generate_table_sas(credential, table_name, ...)` — Generate a table-level SAS token.
- `generate_account_sas(credential, ...)` — Generate an account-level SAS token.
- Both in `_table_shared_access_signature.py`.

### Credential Scope Differences (Storage vs Cosmos)

- **Storage**: `https://storage.azure.com/.default`
- **Cosmos DB**: `https://{account}.documents.azure.com/.default`
- The auth policies select the correct scope based on the endpoint URL.

## Pipeline Policies — `_policies.py`

- **`StorageHeadersPolicy`** — Adds storage-specific headers: `x-ms-date`, `x-ms-version`, `x-ms-client-request-id`.
- **`CosmosPatchTransformPolicy`** — Transforms HTTP verb for Cosmos DB compatibility (see Dual Backend section).
- **`BufferCopy`** — Copies request body into a buffer for retry support.
- **`TablesRetryPolicy`** — Custom retry logic handling:
  - 409 Conflict on table creation (table being deleted)
  - Secondary endpoint failover for geo-redundant accounts
  - Location-pinned pagination

## Dual Backend: Storage Tables vs Cosmos Tables

The SDK targets **two different Azure services** with the same API surface:

| | Azure Storage Tables | Azure Cosmos DB Table API |
| --- | --- | --- |
| **Endpoint** | `https://{account}.table.core.windows.net` | `https://{account}.table.cosmos.azure.com` |
| **Auth scope** | `https://storage.azure.com/.default` | `https://{account}.documents.azure.com/.default` |
| **Update verb** | `PATCH` | Different verb (transformed by `CosmosPatchTransformPolicy`) |
| **Error format** | Storage-specific JSON/XML | Cosmos-specific JSON |
| **XML operations** | ✅ Supported | ❌ Not available |

### Authentication Differences

The auth policies in `_authentication.py` detect the endpoint URL and select the appropriate credential scope. When using `TokenCredential` (AAD), the wrong scope will cause authentication failures.

### Patch/Update Verb Differences

- Storage Tables uses `PATCH` for merge-update operations.
- Cosmos DB Table API requires a different HTTP verb for the same logical operation.
- The `CosmosPatchTransformPolicy` transparently transforms the request verb when the endpoint is a Cosmos DB endpoint, so consumers see a consistent API.

### Error Handling Differences

- Storage and Cosmos return errors in **different formats** (different JSON/XML structures, different error code strings).
- The SDK normalizes all errors in `_error.py` into consistent Azure SDK exceptions: `HttpResponseError`, `ResourceExistsError`, `ResourceNotFoundError`, etc.
- Error codes may differ between backends for the same logical failure.

### Service Operation Availability

**XML-based operations are Storage-only** — these raise errors on Cosmos DB:

- `TableServiceClient.get_service_properties()` / `set_service_properties()`
- `TableServiceClient.get_service_stats()`
- `TableClient.get_table_access_policy()` / `set_table_access_policy()`

All entity CRUD and table CRUD operations work on both backends.

### Testing Requirement

All new features **must be tested against both Storage and Cosmos endpoints**. The test infrastructure provisions both backends via `test-resources.bicep`, and test classes typically run the same suite against both.

## Query & OData Filters — `_serialize.py`

`_parameter_filter_substitution` safely substitutes parameters into OData filter expressions:

```python
# Parameterized query (safe from injection)
query_filter = "PartitionKey eq @pk and Age gt @age"
parameters = {"pk": "sales", "age": 30}
entities = table_client.query_entities(query_filter, parameters=parameters)
```

Supported parameter types with auto-quoting:
- `str` → single-quoted with escaping (`'` → `''`)
- `datetime` → `datetime'2023-01-01T00:00:00Z'`
- `UUID` → `guid'...'`
- `bytes` → `binary'...'`
- `bool` → `true` / `false`
- `int`, `float` → literal value

## Secondary Location Support & Geo-Redundancy

- **`use_location` keyword argument** — Operations accept a `use_location` kwarg to direct requests to the primary or secondary storage endpoint (for RA-GRS/RA-GZRS accounts).
- Implemented as part of the retry policy in `_policies.py` / `aio/_policies_async.py`.
- **Critical for pagination**: When using `list_tables()` or `query_entities()`, all pages of a paginated result set **must** be retrieved from the same location (primary or secondary) as the first page. Switching locations mid-pagination returns inconsistent or empty results.
- The retry policy handles automatic failover to the secondary endpoint on retriable errors (e.g., 503), but pagination operations pin to the initial location.
- Secondary endpoints follow the naming convention `{account}-secondary.table.core.windows.net`.

## Async Patterns

- Async clients mirror sync clients exactly — every sync method has an `async def` counterpart.
- Use `async with` for the context manager pattern.
- Pagination: `query_entities()` / `list_tables()` return `AsyncItemPaged` instead of `ItemPaged`.
- Batch: `await table_client.submit_transaction(operations)`.

## Testing Patterns

- Tests are in `sdk/tables/azure-data-tables/tests/`.
- Recorded tests using `devtools_testutils` and the test proxy.
- `test-resources.bicep` provisions test resources (Storage account + Cosmos DB account).
- Tests cover **both** Azure Storage Tables and Cosmos DB Table API backends.
- Test setup uses preparers for creating tables and entities.
- Running tests: `pytest tests/ -k "test_name"` (after `pip install -r dev_requirements.txt`).
- Running linting: `tox -e pylint -c ../../../eng/tox/tox.ini --root .` from the `sdk/tables/azure-data-tables` directory.

## Common Pitfalls

- **PartitionKey/RowKey must be strings** — Non-string keys cause silent data corruption or errors.
- **Int64 values** — JSON can't represent 64-bit ints; they're transmitted as strings with `Edm.Int64` annotation. Missing the annotation loses precision for values > 2^53.
- **Datetime timezone** — All datetimes must be timezone-aware (UTC). Naive datetimes may cause unexpected behavior.
- **Batch PartitionKey constraint** — All entities in a single transaction must share the same PartitionKey.
- **Cosmos DB compatibility** — Cosmos Table API has different behaviors (PATCH verb, credential scopes, error formats, missing XML operations). The SDK normalizes these but new features must be tested against both backends.
- **XML operations are Storage-only** — `get/set_service_properties`, `get_service_stats`, `get/set_table_access_policy` are not available on Cosmos DB endpoints.
- **`_generated/` is auto-generated** — Never hand-edit files under `_generated/`. Changes will be overwritten on regeneration.
- **Entity metadata** — `etag` and `timestamp` are stored in `EntityMetadata`, accessed via `entity.metadata`, not `entity["metadata"]`.
- **UpdateMode matters** — `UpdateMode.REPLACE` replaces the entire entity; `UpdateMode.MERGE` merges with existing properties. Using the wrong mode can cause data loss.
- **Pagination location pinning** — Paginated queries (`list_tables`, `query_entities`) must retrieve all pages from the same location (primary or secondary). Mixing locations mid-pagination returns inconsistent data.
- **Always update both sync and async** — Any change to a sync client/policy must be mirrored in the async counterpart in `aio/`.
- **Auth scope is endpoint-dependent** — Using `TokenCredential` with the wrong scope (Storage scope on Cosmos endpoint or vice versa) causes silent auth failures.
- **Batch size limits** — Maximum 100 operations and 4 MB payload per transaction. `RequestTooLargeError` is raised if exceeded.

## Key References

- [Azure Data Tables Python SDK README](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/tables/azure-data-tables/README.md)
- [Azure SDK Python Design Guidelines](https://azure.github.io/azure-sdk/python_design.html)
- [Azure Tables REST API Reference](https://learn.microsoft.com/en-us/rest/api/storageservices/table-service-rest-api)
- [OData Type Annotations / Payload Format](https://learn.microsoft.com/en-us/rest/api/storageservices/payload-format-for-table-service-operations)
- [Migration Guide](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/tables/azure-data-tables/migration_guide.md)
- [Samples directory](https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/tables/azure-data-tables/samples)
- [Azure Tables Docs](https://learn.microsoft.com/en-us/azure/storage/tables/)
- [Cosmos DB Table API Docs](https://learn.microsoft.com/en-us/azure/cosmos-db/table/)
