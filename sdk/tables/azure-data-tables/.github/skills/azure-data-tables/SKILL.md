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
| Change base SAS/account SAS signing | `_shared_access_signature.py` |
| Modify pipeline policies (retry, cosmos, etc.) | `_policies.py` / `aio/_policies_async.py` |
| Modify public models (TableAccessPolicy, UpdateMode, etc.) | `_models.py` |
| Modify error handling/mapping | `_error.py` |
| Modify common utilities (URL parsing, connection strings) | `_common_conversion.py` / `_base_client.py` |
| Change serialization of filters/queries | `_serialize.py` |
| Add/remove public exports | `__init__.py` |
| Change API version defaults or allowed versions | `_constants.py` + `_base_client.py` (`_SUPPORTED_API_VERSIONS`) |

**All files listed above are relative to `sdk/tables/azure-data-tables/azure/data/tables/`.**

## Adding a New Convenience Method

When adding a new operation from the generated client to the convenience layer:

### API design rules

> **CRITICAL:** The convenience layer is the public API that customers use. It must be well-designed, consistent, and Pythonic. Do NOT simply mirror the generated operation signature — design the API for the customer.

1. **Required parameters are positional.** Place them before the `*` or `**kwargs` separator.
2. **Optional parameters are keyword-only.** Place them after `*` using keyword-only syntax.
3. **Do NOT expose the `timeout` query parameter.** The `timeout` parameter from the generated operation is an internal detail — it's already handled by `**kwargs`.
4. **Surface all other generated options/properties.** Every meaningful parameter, header, or option from the generated operation should be accessible through the convenience layer — either as explicit keyword parameters or passed through via `**kwargs`.
5. **Evaluate consistency with existing methods.** Look at neighboring methods on the same client class. Match naming patterns, parameter ordering, return type conventions, and docstring style. For example, if other methods accept `datetime` objects, don't accept ISO strings.
6. **Use Python-idiomatic types.** Accept `datetime` instead of ISO strings, Python enums instead of raw strings, etc. Convert to the generated types internally.


### Step-by-step pattern

1. **Find the generated operation** in `_generated/operations/_operations.py`. Note the method signature, parameter types, and return type.
2. **Add the convenience wrapper** to the appropriate client file (`_table_service_client.py` or `_table_client.py`):
   - Use `@distributed_trace` decorator (sync) or `@distributed_trace_async` (async).
   - Construct any internal models (e.g., `KeyInfo`) from user-friendly parameters.
   - Evaluate the public parameter names for short, consistent, concise and efficient naming.
   - Call `self._client.service.<operation>(...)` or `self._client.table.<operation>(...)`.
   - Wrap in `try/except HttpResponseError` with `_process_table_error(error)` in the except block.
3. **Mirror in async** — copy the method to the async client file with `async def` and `await`.
4. **Export new types** from `__init__.py` — add any new public models to imports and `__all__`.
5. **Update `_SUPPORTED_API_VERSIONS`** in `_base_client.py` if the new operation requires a newer API version.

### Error handling pattern

The convenience layer uses a consistent error handling pattern. The `except` branch must raise to satisfy pylint `inconsistent-return-statements`:

```python
@distributed_trace
def my_operation(self, param: str, **kwargs: Any) -> ReturnType:
    try:
        return self._client.service.my_operation(param=param, **kwargs)
    except HttpResponseError as error:
        _process_table_error(error)
        raise  # unreachable but satisfies pylint
```

### Checklist for new operations

- [ ] Sync method in `_table_service_client.py` or `_table_client.py`
- [ ] Async mirror in `aio/_table_service_client_async.py` or `aio/_table_client_async.py`
- [ ] New models exported from `__init__.py` + added to `__all__`
- [ ] `_SUPPORTED_API_VERSIONS` updated if needed
- [ ] Docstrings with `:param`, `:type`, `:return`, `:rtype`, `:raises`
- [ ] Tests for both sync and async
- [ ] Tests for both Storage and Cosmos backends — positive if supported, negative (with error code/message assertions) if not
- [ ] `datetime` imports added if type annotations reference `datetime`

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

### SharedKey Authentication Format

The Tables SDK uses **SharedKey** with a **SharedKeyLite-style string-to-sign**:

```
Authorization: SharedKey {account}:{signature}
```

The string-to-sign is:
```
x-ms-date-value\n/{account}/{resource}?comp={value}
```

This is NOT the full SharedKey format (which includes verb, content-md5, content-type, and all canonicalized headers). It's the Lite format but with the `SharedKey` authorization scheme name. This combination works for `x-ms-version` up to `2019-02-02`. **For `x-ms-version: 2025-07-05`, this combination breaks** — the service requires the auth scheme name to match the actual format used.

> **CRITICAL:** If the `x-ms-version` header changes (e.g., due to a TypeSpec regeneration that bumps the default API version), SharedKey authentication WILL break unless the auth format is also updated. This is a common regression source when upgrading API versions.

### SAS Generation

- `generate_table_sas(credential, table_name, ...)` — Generate a table-level SAS token. Also accepts `UserDelegationKey` for user delegation SAS.
- `generate_account_sas(credential, ...)` — Generate an account-level SAS token.
- Both in `_table_shared_access_signature.py`.

### SAS Version vs Client API Version

These are **independent concepts**:

- **SAS `sv` parameter** — Controls how the service validates the SAS signature (string-to-sign format). Set by `X_MS_VERSION` in `_constants.py`.
- **Client `x-ms-version` header** — Controls request/response wire format. Set by `api_version` from `_generated/_configuration.py`.

A SAS token with `sv=2019-02-02` works correctly with a client sending `x-ms-version: 2025-07-05`. They do NOT need to match.

> **IMPORTANT:** `X_MS_VERSION` in `_constants.py` controls the SAS signing version. `api_version` in `_generated/_configuration.py` controls the wire request version. Changing one does NOT require changing the other. Bumping `X_MS_VERSION` affects ALL SAS tokens and may break Cosmos compatibility (see below).

### SAS String-to-Sign Differences by Version

The string-to-sign format for table service SAS changes between API versions:

| Field | `sv` < 2015-04-05 | `sv` >= 2015-04-05 | `sv` >= 2020-12-06 |
|-------|-------------------|--------------------|--------------------|
| signedPermissions | ✅ | ✅ | ✅ |
| signedStart | ✅ | ✅ | ✅ |
| signedExpiry | ✅ | ✅ | ✅ |
| canonicalizedResource | ✅ | ✅ | ✅ |
| signedIdentifier | ✅ | ✅ | ✅ |
| signedIP | ❌ | ✅ | ✅ |
| signedProtocol | ❌ | ✅ | ✅ |
| signedVersion | ✅ | ✅ | ✅ |
| signedEncryptionScope | ❌ | ❌ | ✅ (account SAS only) |
| startPk/startRk/endPk/endRk | ✅ | ✅ | ✅ |

### User Delegation SAS

User delegation SAS uses a different string-to-sign that includes the delegation key fields. For Table Storage with `sv=2025-07-05`:

```
signedPermissions\n + signedStart\n + signedExpiry\n + canonicalizedResource\n +
signedKeyObjectId\n + signedKeyTenantId\n + signedKeyStart\n + signedKeyExpiry\n +
signedKeyService\n + signedKeyVersion\n +
signedKeyDelegatedUserTenantId\n + signedDelegatedUserObjectId\n +
signedIP\n + signedProtocol\n + signedVersion\n +
startingPartitionKey\n + startingRowKey\n + endingPartitionKey\n + endingRowKey
```

The signature is signed with the delegation key's `value` (HMAC-SHA256, base64-decoded) instead of the account key.

### Credential Scope Differences (Storage vs Cosmos)

- **Storage**: `https://storage.azure.com/.default`
- **Cosmos DB**: `https://{account}.documents.azure.com/.default`
- The auth policies select the correct scope based on the endpoint URL.

### SAS Compatibility: Storage vs Cosmos

> **CRITICAL:** Storage and Cosmos use **different SAS string-to-sign formats** for the same `sv` version. A SAS token that works on Storage may fail on Cosmos, and vice versa. When bumping the `X_MS_VERSION` (SAS version), always test against BOTH backends.

Specifically for Cosmos DB:
- Cosmos error messages include the **expected string-to-sign**, which you can compare directly against your computed value to debug mismatches.
- The `signedEncryptionScope` field was added in `sv=2020-12-06` for account SAS, but Cosmos does NOT include it in its expected string-to-sign for older SAS versions. Including it when the version is < `2020-12-06` produces an invalid signature on Cosmos.

## API Versioning

### Version Constants

| Constant | File | Purpose |
|----------|------|---------|
| `X_MS_VERSION` | `_constants.py` | Default SAS token `sv` version. Also used by `StorageHeadersPolicy` for the `x-ms-version` header on some requests. |
| `DEFAULT_X_MS_VERSION` | `_constants.py` | Legacy default, used by `_shared_access_signature.py` base class. |
| `api_version` | `_generated/_configuration.py` | Default `x-ms-version` header sent on wire requests. Set by the TypeSpec code generator. |
| `_SUPPORTED_API_VERSIONS` | `_base_client.py` | Allowed list of API versions the convenience layer accepts. |

### How API Version Flows Through the SDK

1. User creates `TableServiceClient(url, credential)` — no explicit `api_version`.
2. Generated `_configuration.py` sets `api_version` to its default (e.g., `2025-07-05`).
3. `_base_client.py` line 167: `get_api_version(api_version, self._client._config.api_version)` — user's value (None) falls through to the generated default.
4. `_base_client.py` line 294: Adds `"x-ms-version": self.api_version` as a custom header in the pipeline.
5. Generated request builders also set `x-ms-version` from `api_version` in the request headers.
6. `_authentication.py` computes SharedKey signature — the `x-ms-version` value is included in canonicalized headers and affects signature validation.

### Adding a New API Version

When a TypeSpec regeneration bumps the default API version:

1. Add the new version to `_SUPPORTED_API_VERSIONS` in `_base_client.py`.
2. **Do NOT automatically bump `X_MS_VERSION`** in `_constants.py` — this affects SAS generation and may break Cosmos compatibility.
3. Verify SharedKey authentication still works with the new `x-ms-version` header value.
4. Run the full test suite live against both Storage and Cosmos backends.

## Code Generation Pitfalls

### URL Path Differences

Code generators may produce slightly different URL paths between versions. For example:
- Old emitter: `_url = "/?restype=service&comp=properties"` (with leading `/`)
- New emitter: `_url = "?restype=service&comp=properties"` (without leading `/`)

The leading `/` affects the URL path component, which changes the canonicalized resource in the SharedKey signature. A missing or extra `/` **silently breaks authentication** for all SharedKey-authenticated requests to that endpoint.

> **Always check the generated URL paths after regeneration** by comparing `git diff` on the generated operations file. If URL paths changed, verify SharedKey auth still works.

### XML Serialization

When defining TypeSpec models that are sent/received as XML:
- Use `@Xml.name("ElementName")` on each property to control XML element names.
- For request body content-type, explicitly set `@header("Content-Type") contentType: "application/xml"` in the operation's request parameters. Without this, the emitter defaults to JSON serialization.
- For datetime fields in XML responses, use `string` type instead of `@encode("rfc7231") utcDateTime` — the XML deserializer may not correctly apply format conversions, leaving raw XML `Element` objects instead of parsed `datetime` values.
- When passing `datetime` values to the service in XML, strip microseconds (`.replace(microsecond=0)`) — the Tables service rejects datetime strings with microsecond precision in XML payloads.

## TypeSpec-to-SDK Generation for Tables

### Spec location
The Tables TypeSpec is at `specification/cosmos-db/data-plane/Tables/` in the `azure-rest-api-specs` repo.

### Key files in the spec
| File | Purpose |
|------|---------|
| `main.tsp` | Service definition, namespace, `Versions` enum |
| `models.tsp` | Request/response models (`KeyInfo`, `UserDelegationKey`, etc.) |
| `routes.tsp` | Operations — defines `TablesXmlOperation` and `TablesJsonOperation` templates |
| `client.tsp` | Python client customizations (`@clientName`, `@access`, parameter renames) |
| `tspconfig.yaml` | Emitter configuration, package version, namespace |

### Operation templates
The Tables spec defines two operation templates:
- **`TablesXmlOperation`** — For XML-based operations (service properties, stats, access policy, user delegation key). Request/response bodies are XML.
- **`TablesJsonOperation`** — For JSON-based operations (table CRUD, entity CRUD). Request/response bodies are JSON.

When adding a new XML operation, you MUST include `@header("Content-Type") contentType: "application/xml"` and `@header("Accept") accept: "application/xml"` in the request parameters — the template does NOT set these automatically.

### Generation command
```bash
cd <sdk_repo>/<sdk.package_dir>
npx tsp-client update
```

### Post-generation checklist
After regeneration, always:
1. `git diff` the generated operations file — check for URL path changes (e.g., missing leading `/`).
2. Verify `_configuration.py` default `api_version` — if it changed, add the new version to `_SUPPORTED_API_VERSIONS`.
3. Re-install the package (`pip install -e .`) before running any tests.
4. Run a quick smoke test with SharedKey auth to verify auth isn't broken.

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

> **MANDATORY:** All new features must have tests for **BOTH** Storage and Cosmos endpoints — no exceptions. This applies even when the feature is only supported on one backend.

- **Supported on both backends** — Write positive tests that exercise the feature on Storage and Cosmos.
- **Supported on Storage only** (e.g., `get_user_delegation_key`, `get_service_properties`) — Write positive tests for Storage AND negative tests for Cosmos that verify the operation is correctly rejected. Negative tests must assert on the specific exception type (e.g., `HttpResponseError`) and validate the error message or error code.
- **Supported on Cosmos only** — Write positive tests for Cosmos AND negative tests for Storage.

Negative tests must:
- Use `pytest.raises(ExpectedExceptionType)` to catch the error.
- Assert on the `status_code` (e.g., 403, 404, 400) when possible.
- Assert on the `error_code` or error message substring to confirm the failure reason is correct (not a generic auth or network error).

Example pattern for a Storage-only feature tested against Cosmos:
```python
@cosmos_decorator
@recorded_by_proxy
def test_my_storage_only_feature_cosmos_fails(self, tables_cosmos_account_name, tables_primary_cosmos_account_key):
    """Verify that this Storage-only feature is correctly rejected on Cosmos DB."""
    url = self.account_url(tables_cosmos_account_name, "cosmos")
    tsc = TableServiceClient(endpoint=url, credential=tables_primary_cosmos_account_key)

    with pytest.raises(HttpResponseError) as exc_info:
        tsc.my_storage_only_operation(...)
    assert "AuthenticationFailed" in str(exc_info.value)
    assert exc_info.value.status_code == 403
```

The test infrastructure provisions both backends via `test-resources.bicep`, and test file naming follows the pattern: `test_<feature>.py` (Storage), `test_<feature>_cosmos.py` (Cosmos), plus async variants.

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
- `test-resources.bicep` is at `sdk/tables/test-resources.bicep` (service directory level, not package level). It provisions both a Storage account and a Cosmos DB account.
- Tests cover **both** Azure Storage Tables and Cosmos DB Table API backends.
- Test setup uses preparers for creating tables and entities.
- Running tests: `pytest tests/ -k "test_name"` (after `pip install -r dev_requirements.txt`).
- Running linting: `tox -e pylint -c ../../../eng/tox/tox.ini --root .` from the `sdk/tables/azure-data-tables` directory.

### Test File Naming Convention

| Pattern | Backend | Auth |
|---------|---------|------|
| `test_<feature>.py` | Storage | SharedKey via `tables_decorator` |
| `test_<feature>_async.py` | Storage (async) | SharedKey via `tables_decorator_async` |
| `test_<feature>_cosmos.py` | Cosmos DB | SharedKey via `cosmos_decorator` |
| `test_<feature>_cosmos_async.py` | Cosmos DB (async) | SharedKey via `cosmos_decorator_async` |
| `test_table_aad.py` / `test_table_aad_async.py` | Storage | AAD via `self.get_token_credential()` |

### Test Resource Deployment

- Deploy: `.\eng\common\TestResources\New-TestResources.ps1 tables` from the SDK repo root.
- The script creates both Storage and Cosmos accounts and outputs environment variables.
- The `test-resources.bicep` accepts a `supportsSafeSecretStandard` parameter (passed automatically for TME tenants) to control `allowSharedKeyAccess` on the storage account.
- If adding a new feature that requires additional RBAC roles, add the role assignment to `test-resources.bicep` and redeploy.
- TME tenant resources are prefixed with `SSS3PT_` and auto-expire after 120 hours.

### Known Test Issues

- `test_empty_batch` — Known test proxy bug (https://github.com/Azure/azure-sdk-tools/issues/2900). The test proxy fails to record/end sessions for empty batch (submit_transaction with `[]`). These tests are marked `@pytest.mark.live_test_only` but still fail due to the `@recorded_by_proxy` decorator attempting to manage the recording session.
- Leftover tables from previous test runs can cause `TableAlreadyExists` errors. Clean up before re-running: list and delete all tables via `TableServiceClient.list_tables()` / `delete_table()`.

### Recordings

- Recordings are stored in the `azure-sdk-assets` repo, managed via `assets.json` in the package root.
- Use `python scripts/manage_recordings.py locate -p sdk/tables/azure-data-tables` to find the local recordings directory.
- Use `python scripts/manage_recordings.py push -p sdk/tables/azure-data-tables/assets.json` to push recordings after updating.

## Common Pitfalls

- **PartitionKey/RowKey must be strings** — Non-string keys cause silent data corruption or errors.
- **Int64 values** — JSON can't represent 64-bit ints; they're transmitted as strings with `Edm.Int64` annotation. Missing the annotation loses precision for values > 2^53.
- **Datetime timezone** — All datetimes must be timezone-aware (UTC). Naive datetimes may cause unexpected behavior.
- **Datetime microseconds in XML** — The Tables service rejects datetime strings with microsecond precision in XML payloads. Strip microseconds with `.replace(microsecond=0)` before passing to XML operations like `get_user_delegation_key`.
- **Batch PartitionKey constraint** — All entities in a single transaction must share the same PartitionKey.
- **Cosmos DB compatibility** — Cosmos Table API has different behaviors (PATCH verb, credential scopes, error formats, missing XML operations, different SAS signing format). The SDK normalizes these but new features must be tested against both backends.
- **XML operations are Storage-only** — `get/set_service_properties`, `get_service_stats`, `get/set_table_access_policy` are not available on Cosmos DB endpoints. `get_user_delegation_key` is also Storage-only.
- **`_generated/` is auto-generated** — Never hand-edit files under `_generated/`. Changes will be overwritten on regeneration. **Exception:** If the code generator produces a regression (e.g., wrong URL paths), you may need to patch generated code until the emitter is fixed.
- **Entity metadata** — `etag` and `timestamp` are stored in `EntityMetadata`, accessed via `entity.metadata`, not `entity["metadata"]`.
- **UpdateMode matters** — `UpdateMode.REPLACE` replaces the entire entity; `UpdateMode.MERGE` merges with existing properties. Using the wrong mode can cause data loss.
- **Pagination location pinning** — Paginated queries (`list_tables`, `query_entities`) must retrieve all pages from the same location (primary or secondary). Mixing locations mid-pagination returns inconsistent data.
- **Always update both sync and async** — Any change to a sync client/policy must be mirrored in the async counterpart in `aio/`.
- **Auth scope is endpoint-dependent** — Using `TokenCredential` with the wrong scope (Storage scope on Cosmos endpoint or vice versa) causes silent auth failures.
- **Batch size limits** — Maximum 100 operations and 4 MB payload per transaction. `RequestTooLargeError` is raised if exceeded.
- **SharedKey auth format is version-sensitive** — The `SharedKey` auth header with a Lite-format string-to-sign works for `x-ms-version` ≤ `2019-02-02` but breaks for newer versions. If the API version changes, auth WILL break.
- **SAS version changes break Cosmos** — Changing `X_MS_VERSION` in `_constants.py` affects all generated SAS tokens. Cosmos uses a different string-to-sign format than Storage for the same `sv` version. Always test SAS changes against both backends.
- **Generated URL paths change between emitter versions** — The TypeSpec Python emitter may produce different URL paths (e.g., `/?param=value` vs `?param=value`). The path is part of the SharedKey signature, so even a single character difference breaks authentication silently.
- **`signedEncryptionScope` is version-conditional** — The `ses` field in account SAS string-to-sign was added in `sv=2020-12-06`. Including it for older versions adds an extra `\n` that breaks the signature on Cosmos.

## Key References

- [Azure Data Tables Python SDK README](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/tables/azure-data-tables/README.md)
- [Azure SDK Python Design Guidelines](https://azure.github.io/azure-sdk/python_design.html)
- [Azure Tables REST API Reference](https://learn.microsoft.com/en-us/rest/api/storageservices/table-service-rest-api)
- [OData Type Annotations / Payload Format](https://learn.microsoft.com/en-us/rest/api/storageservices/payload-format-for-table-service-operations)
- [Migration Guide](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/tables/azure-data-tables/migration_guide.md)
- [Samples directory](https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/tables/azure-data-tables/samples)
- [Azure Tables Docs](https://learn.microsoft.com/en-us/azure/storage/tables/)
- [Cosmos DB Table API Docs](https://learn.microsoft.com/en-us/azure/cosmos-db/table/)
