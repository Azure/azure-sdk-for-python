// Copyright (c) Microsoft Corporation. All rights reserved.
// Licensed under the MIT License.

//! PyO3 binding crate that exposes `azure_data_cosmos_driver` to Python.
//!
//! Compiled into one cdylib that Maturin renames to
//! `_rust.{pyd,so}` and drops into `azure/cosmos/`. The
//! driver crate is statically linked into the same binary so the
//! wheel ships exactly one Rust file.
//!
//! Python-callable entry points include:
//!
//!   * `init_client(endpoint, master_key=None, config=None, credential=None) -> handle`
//!         Lazily stands up a per-process Tokio runtime + driver
//!         runtime, builds a `CosmosDriver` for the given endpoint
//!         (applying the optional `PreparedClientConfig`'s settings,
//!         e.g. preferred_locations), and returns a string handle the
//!         Python side keeps and passes back on every operation. Auth is
//!         either the `master_key` or a `credential` (a synchronous Python
//!         token credential wrapped as `PyTokenCredential`); the Python
//!         factory supplies exactly one.
//!
//!   * `close_client(handle) -> None`
//!         Drops one client's reference to the per-endpoint driver in the
//!         process-local cache. The driver is evicted only when the last client
//!         sharing that account closes (the cache is reference-counted), so
//!         closing one of several clients to one account does not break the
//!         others. An unknown or already-evicted handle is a no-op, so close is
//!         idempotent.
//!
//!   * `create_item(handle, prepared) -> (status, sub_status,
//!                                         headers, body, diagnostics)`
//!         Resolves the container, builds a typed
//!         `CosmosOperation::create_item`, runs it on the Tokio
//!         runtime with the GIL released, and converts the
//!         `CosmosResponse` into a tuple matching the Python
//!         `BackendResponse` dataclass.
//!
//!   * `upsert_item(handle, prepared) -> (status, sub_status,
//!                                         headers, body, diagnostics)`
//!         Same input/output shape as `create_item` (write-with-body:
//!         the document id rides inside `body_bytes`). The only
//!         difference is the operation kind —
//!         `CosmosOperation::upsert_item` — which makes the driver
//!         pipeline stamp `x-ms-documentdb-is-upsert: true` and POST to
//!         the collection feed, so an existing `(partition_key, id)` is
//!         replaced (HTTP 200) rather than rejected with 409; a new id
//!         inserts (HTTP 201). `If-Match` / `If-None-Match` (built by
//!         the Python helper from `etag` + `match_condition`:
//!         insert-only or version-guarded replace) flow through
//!         `custom_headers`.
//!
//!   * `replace_item(handle, prepared) -> (status, sub_status,
//!                                          headers, body, diagnostics)`
//!         Carries a body like `create_item` / `upsert_item`, but the id
//!         of the document to overwrite comes from `PreparedRequest.item_id`
//!         (not the body). Maps to `OperationType::Replace`: an existing
//!         item is overwritten (HTTP 200), a missing one is a 404 (replace
//!         never inserts). Returns the saved document unless
//!         `no_response=True`. `If-Match` / `If-None-Match` flow through
//!         `custom_headers`.
//!
//!   * `delete_item(handle, prepared) -> (status, sub_status,
//!                                         headers, body, diagnostics)`
//!         Same shape as `create_item` but builds a
//!         `CosmosOperation::delete_item` with no body. The document
//!         id rides on `PreparedRequest.item_id` because there is no
//!         body to extract it from. On success the driver returns
//!         HTTP 204 with an empty body.
//!
//!   * `read_item(handle, prepared) -> (status, sub_status,
//!                                       headers, body, diagnostics)`
//!         Same input shape as `delete_item` (bodiless GET, document
//!         id on `PreparedRequest.item_id`). On success returns HTTP
//!         200 with the document JSON. Conditional reads
//!         (`If-None-Match` driven by Python's `etag` +
//!         `MatchConditions.IfModified`) surface as **HTTP 304** with
//!         an empty body when the customer's cached etag still
//!         matches the server version — the Python parser treats 304
//!         as a non-error and returns an empty `CosmosDict`.
//!         `x-ms-dedicatedgateway-max-age` (driven by
//!         `max_integrated_cache_staleness_in_ms`) is forwarded
//!         through `custom_headers` like any other per-request header.
//!
//!   * `patch_item(handle, prepared) -> (status, sub_status,
//!                                        headers, body, diagnostics)`
//!         Carries a body like the write-with-body ops, but the body is
//!         the `PatchInstructions` payload (`{"operations": [...]}`) rather
//!         than a document, and the URL id comes from
//!         `PreparedRequest.item_id`. Maps to `OperationType::Patch`: the
//!         driver reads the item, applies the ops, and writes it back with
//!         an `If-Match`-guarded `Replace`. The Python helper only routes
//!         the supported subset here; a `filter_predicate` or an `etag` /
//!         `match_condition` precondition takes the legacy path instead.
//!
//!   * `query_items(handle, prepared) -> (status, sub_status,
//!                                        headers, body, diagnostics)`
//!         Executes one query page. The query JSON is in
//!         `PreparedRequest.body_bytes`; `PreparedRequest.partition_key_header`
//!         selects the scope (`["pk"]` for one logical partition, `[]` for
//!         cross-partition/full-container). Returns a feed envelope body
//!         (`{"Documents":[...]}`) so the Python query iterator can consume it
//!         with the same shape as the legacy path.
//!
//!   * `read_all_items(handle, prepared) -> (status, sub_status,
//!                                           headers, body, diagnostics)`
//!         Executes native read-feed on the driver (no synthetic SQL rewrite).
//!         Scope is selected from `PreparedRequest.partition_key_header`:
//!         `[]` for full-container (`read_all_items_cross_partition`) or a
//!         non-empty array for one logical partition (`read_all_items`).
//!
//!   * `read_feed_ranges(handle, prepared) -> (status, sub_status,
//!                                             headers, body, diagnostics)`
//!         Enumerates the container's partition-key ranges (routing map view).
//!         The request body may carry `{"forceRefresh": true}` to force a cache
//!         refresh. Returns body shape
//!         `{"PartitionKeyRanges":[{"id","minInclusive","maxExclusive"},...]}`.
//!
//!   * `feed_range_from_partition_key(handle, prepared) -> (status, sub_status,
//!                                                     headers, body, diagnostics)`
//!         Computes the feed-range envelope for one partition key and returns body
//!         shape `{"Range":{"min","max","isMinInclusive","isMaxInclusive"}}`.
//!
//!   * `read_offer(handle, prepared) -> (status, sub_status,
//!                                       headers, body, diagnostics)`
//!         Reads a container's provisioned throughput by querying the account's
//!         `/offers` feed (an account-level, non-partitioned resource). The request
//!         body carries the same offer query JSON the legacy path sends; the binding
//!         adds the query `Content-Type`/`x-ms-documentdb-isquery` markers that
//!         `query_offers` requires. Returns body shape `{"Offers":[...]}`.
//!
//!   * `replace_offer(handle, prepared) -> (status, sub_status,
//!                                          headers, body, diagnostics)`
//!         Replaces a container's provisioned throughput by PUTting the mutated
//!         offer document to `/offers/{rid}` (an account-level, non-partitioned
//!         resource). The offer RID rides in `PreparedRequest.item_id`; the mutated
//!         offer document rides in the body. Unlike the read path there is no query
//!         `Content-Type` to force -- a replace carries a resource body and the
//!         driver defaults `Content-Type` to `application/json`. Returns the single
//!         updated offer document.
//!
//! `x-ms-activity-id` and `x-ms-session-token` are forwarded to the
//! driver's typed operation fields. `responsePayloadOnWriteDisabled`
//! is lifted to the typed `OperationOptions::content_response_on_write`
//! field. Every other per-request header (intended-collection-rid,
//! indexing directive, pre/post triggers, priority, throughput bucket,
//! plus any already-`x-ms-...`-named entry) is pushed through the
//! driver's `OperationOptions::with_custom_headers` passthrough so
//! it lands on the wire.

mod credential;
mod documents;
mod feed_range_subset;
mod runtime;
mod wire;

use pyo3::prelude::*;

macro_rules! add_pyfn {
    ($module:expr, $function:path) => {
        $module.add_function(wrap_pyfunction!($function, $module)?)?;
    };
}

// ---------------------------------------------------------------------------
// Module entry point
// ---------------------------------------------------------------------------

#[pymodule]
fn _rust(_py: Python<'_>, m: &Bound<'_, PyModule>) -> PyResult<()> {
    add_pyfn!(m, runtime::init_client);
    add_pyfn!(m, runtime::close_client);
    add_pyfn!(m, documents::create_item);
    add_pyfn!(m, documents::upsert_item);
    add_pyfn!(m, documents::replace_item);
    add_pyfn!(m, documents::delete_item);
    add_pyfn!(m, documents::read_item);
    add_pyfn!(m, documents::patch_item);
    add_pyfn!(m, documents::query_items);
    add_pyfn!(m, documents::read_all_items);
    add_pyfn!(m, documents::read_feed_ranges);
    add_pyfn!(m, documents::feed_range_from_partition_key);
    add_pyfn!(m, documents::is_feed_range_subset);
    add_pyfn!(m, documents::read_offer);
    add_pyfn!(m, documents::replace_offer);
    add_pyfn!(m, documents::create_database);
    add_pyfn!(m, documents::create_database_if_not_exists);
    // Async siblings: each returns a Python awaitable that completes on the
    // driver's runtime, so the async backend holds no worker thread per call.
    add_pyfn!(m, documents::create_item_async);
    add_pyfn!(m, documents::upsert_item_async);
    add_pyfn!(m, documents::replace_item_async);
    add_pyfn!(m, documents::delete_item_async);
    add_pyfn!(m, documents::read_item_async);
    add_pyfn!(m, documents::patch_item_async);
    add_pyfn!(m, documents::query_items_async);
    add_pyfn!(m, documents::read_all_items_async);
    add_pyfn!(m, documents::read_feed_ranges_async);
    add_pyfn!(m, documents::feed_range_from_partition_key_async);
    add_pyfn!(m, documents::is_feed_range_subset_async);
    add_pyfn!(m, documents::read_offer_async);
    add_pyfn!(m, documents::replace_offer_async);
    add_pyfn!(m, documents::create_database_async);
    add_pyfn!(m, documents::create_database_if_not_exists_async);
    // Concrete backend provenance: a counter incremented inside the binding on
    // every operation, so the perf harness can prove the Rust path actually ran
    // (not just that COSMOS_BACKEND said so). See wire::BINDING_OP_COUNT.
    add_pyfn!(m, wire::operation_count);
    // Per-attempt wire-diagnostics counters: total attempts and driver-issued
    // retries/failovers/hedges folded from each response's DiagnosticsContext.
    // Read by the perf harness as `_rust.attempt_count()` / `_rust.retry_count()`
    // to distinguish operations requested from wire round trips actually made
    // (e.g. PATCH ~= 2 attempts/op via client-side Read-Modify-Write; a nonzero
    // retry count means the retry machinery fired even with 0 terminal errors).
    add_pyfn!(m, wire::attempt_count);
    add_pyfn!(m, wire::retry_count);
    // Typed transport error the Python backend maps to azure-core's
    // ServiceResponseError (see wire::DriverTransportError).
    m.add(
        "DriverTransportError",
        m.py().get_type_bound::<wire::DriverTransportError>(),
    )?;
    m.add(
        "UnsupportedQueryFeatureError",
        m.py()
            .get_type_bound::<wire::UnsupportedQueryFeatureError>(),
    )?;
    m.add("__version__", env!("CARGO_PKG_VERSION"))?;
    Ok(())
}
