---
name: azure-data-tables
description: 'Domain knowledge for azure-data-tables. Covers dual-backend pitfalls, auth, SAS, codegen, versioning, and testing.'
---

# azure-data-tables — Package Skill

Paths relative to `sdk/tables/azure-data-tables/azure/data/tables/`.

## Key Rules

- **Never hand-edit `_generated/`** except as temporary patch for emitter regressions.
- **Always update both sync and async** — every sync module has an `aio/` counterpart.
- **Don't hand-concatenate OData filters** — use `_parameter_filter_substitution` in `_serialize.py`.

## API Design for New Convenience Methods

Design for the customer — don't mirror the generated signature.

1. Required params positional (before `*`); optional keyword-only (after `*`).
2. Don't expose `timeout` query param — handled via `**kwargs`.
3. Surface all other generated options via explicit kwargs or `**kwargs`.
4. Match naming/ordering/style of neighboring methods on the same client.
5. Use Python-idiomatic types (`datetime`, enums) — convert internally if necessary.
6. Wrap in `try/except HttpResponseError` with `_process_table_error(error)` + `raise`.
7. Export new models from `__init__.py` + `__all__`.
8. Update `_SUPPORTED_API_VERSIONS` in `_base_client.py` if newer API version needed.

## Dual Backend: Storage vs Cosmos

| | Storage | Cosmos |
|---|---|---|
| **Endpoint** | `{acct}.table.core.windows.net` | `{acct}.table.cosmos.azure.com` |
| **AAD scope** | `https://storage.azure.com/.default` | `https://cosmos.azure.com/.default` |
| **Update verb** | `PATCH` | Transformed by `CosmosPatchTransformPolicy` |
| **XML ops** | ✅ | ❌ |
| **Error format** | Storage JSON/XML | Cosmos JSON (different codes/structure) |
| **SAS format** | Standard | Different string-to-sign for same `sv` |

- Scope auto-selected by endpoint URL. Wrong scope → silent auth failure.
- **Storage-only:** `get/set_service_properties`, `get_service_stats`, `get/set_table_access_policy`.
- `_error.py` normalizes errors to `HttpResponseError`, `ResourceExistsError`, `ResourceNotFoundError`, etc. Error codes differ between backends for same logical failure.

## SharedKey Auth — CRITICAL

Uses **Lite-format string-to-sign** with the **`SharedKey` scheme name**:

```
Authorization: SharedKey {account}:{signature}
String-to-sign: x-ms-date-value\n/{account}/{resource}?comp={value}
```

Works for `x-ms-version` ≤ `2019-02-02` only. **Newer versions break auth** unless format is updated. #1 regression source on API version changes.

## API Versioning

| Constant | File | Controls |
|----------|------|----------|
| `X_MS_VERSION` | `_constants.py` | SAS `sv` + `StorageHeadersPolicy` header |
| `api_version` | `_generated/_configuration.py` | Wire `x-ms-version` (codegen) |
| `_SUPPORTED_API_VERSIONS` | `_base_client.py` | Allowed versions for client construction |

**Independent.** SAS `sv=2019-02-02` works with `x-ms-version: 2025-07-05`.

On codegen version bump: (1) add to `_SUPPORTED_API_VERSIONS`, (2) do NOT auto-bump `X_MS_VERSION` — breaks Cosmos SAS, (3) verify SharedKey auth, (4) run live tests on both backends.

## SAS Signing

- `sv` ≥ `2015-04-05` adds `signedIP`, `signedProtocol`.
- `sv` ≥ `2020-12-06` adds `signedEncryptionScope` (account SAS only). Including it for older `sv` adds extra `\n` breaking Cosmos signatures.
- Storage and Cosmos use **different string-to-sign formats** for same `sv`. Always test both. Cosmos errors include the **expected string-to-sign** for debugging.

## Codegen Pitfalls

**URL paths break auth silently.** Emitter may produce `/?param=value` vs `?param=value`. Path is part of SharedKey signature — single char diff breaks auth. **Always diff generated URLs after regen.**

**XML serialization:** Set `contentType: "application/xml"` explicitly in TypeSpec (emitter defaults JSON).

**TypeSpec spec:** `specification/cosmos-db/data-plane/Tables/` in `azure-rest-api-specs`. Templates: `TablesXmlOperation` (XML) and `TablesJsonOperation` (JSON). XML template does NOT auto-set content-type.

## Testing Requirements

**MANDATORY:** All features need tests for **BOTH** Storage and Cosmos.

- **Both supported** — positive tests for each.
- **One backend only** — positive tests + negative tests on other backend asserting exception type, `status_code`, `error_code`/message.

| Pattern | Backend |
|---------|---------|
| `test_<feature>.py` / `_async.py` | Storage (`tables_decorator`) |
| `test_<feature>_cosmos.py` / `_cosmos_async.py` | Cosmos (`cosmos_decorator`) |

`test-resources.bicep` at `sdk/tables/test-resources.bicep` provisions both backends.

## Pagination

All pages of `list_tables()`/`list_entities()`/`query_entities()` **must** come from same location (primary/secondary). Switching mid-pagination → inconsistent data.

## Common Pitfalls

- `PartitionKey`/`RowKey` must be strings — non-string keys → silent corruption.
- Int64 as strings with `Edm.Int64` annotation. Missing → precision loss > 2^53.
- Entity metadata on `TableEntity.metadata`, not `entity["metadata"]`.
- `UpdateMode.REPLACE` replaces entire entity; `MERGE` merges. Wrong mode → data loss.
- Datetimes returned from the service may contain precision beyond what Python can support, use `TableEntityDatetime` to preserve precision for round-tripping.
- Storage Tables uses `PATCH` for merge-update operations, Cosmos DB Table API requires a different HTTP verb for the same logical operation. We use the `CosmosPatchTransformPolicy` to unite them.
