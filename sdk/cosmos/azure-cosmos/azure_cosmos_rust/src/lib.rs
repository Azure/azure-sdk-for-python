// Copyright (c) Microsoft Corporation. All rights reserved.
// Licensed under the MIT License.

//! PyO3 binding crate that exposes `azure_data_cosmos_driver` to Python.
//!
//! Compiled into one cdylib that Maturin renames to
//! `_rust.{pyd,so}` and drops into `azure/cosmos/`. The
//! driver crate is statically linked into the same binary so the
//! wheel ships exactly one Rust file.
//!
//! Two Python-callable entry points:
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
//!                                         headers, body)`
//!         Resolves the container, builds a typed
//!         `CosmosOperation::create_item`, runs it on the Tokio
//!         runtime with the GIL released, and converts the
//!         `CosmosResponse` into a 4-tuple matching the Python
//!         `BackendResponse` dataclass.
//!
//!   * `upsert_item(handle, prepared) -> (status, sub_status,
//!                                         headers, body)`
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
//!                                          headers, body)`
//!         Carries a body like `create_item` / `upsert_item`, but the id
//!         of the document to overwrite comes from `PreparedRequest.item_id`
//!         (not the body). Maps to `OperationType::Replace`: an existing
//!         item is overwritten (HTTP 200), a missing one is a 404 (replace
//!         never inserts). Returns the saved document unless
//!         `no_response=True`. `If-Match` / `If-None-Match` flow through
//!         `custom_headers`.
//!
//!   * `delete_item(handle, prepared) -> (status, sub_status,
//!                                         headers, body)`
//!         Same shape as `create_item` but builds a
//!         `CosmosOperation::delete_item` with no body. The document
//!         id rides on `PreparedRequest.item_id` because there is no
//!         body to extract it from. On success the driver returns
//!         HTTP 204 with an empty body.
//!
//!   * `read_item(handle, prepared) -> (status, sub_status,
//!                                       headers, body)`
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
//!                                        headers, body)`
//!         Carries a body like the write-with-body ops, but the body is
//!         the `PatchInstructions` payload (`{"operations": [...]}`) rather
//!         than a document, and the URL id comes from
//!         `PreparedRequest.item_id`. Maps to `OperationType::Patch`: the
//!         driver reads the item, applies the ops, and writes it back with
//!         an `If-Match`-guarded `Replace`. The Python helper only routes
//!         the supported subset here; a `filter_predicate` or an `etag` /
//!         `match_condition` precondition takes the legacy path instead.
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
mod runtime;
mod wire;

use pyo3::prelude::*;

// ---------------------------------------------------------------------------
// Module entry point
// ---------------------------------------------------------------------------

#[pymodule]
fn _rust(_py: Python<'_>, m: &Bound<'_, PyModule>) -> PyResult<()> {
    m.add_function(wrap_pyfunction!(runtime::init_client, m)?)?;
    m.add_function(wrap_pyfunction!(runtime::close_client, m)?)?;
    m.add_function(wrap_pyfunction!(documents::create_item, m)?)?;
    m.add_function(wrap_pyfunction!(documents::upsert_item, m)?)?;
    m.add_function(wrap_pyfunction!(documents::replace_item, m)?)?;
    m.add_function(wrap_pyfunction!(documents::delete_item, m)?)?;
    m.add_function(wrap_pyfunction!(documents::read_item, m)?)?;
    m.add_function(wrap_pyfunction!(documents::patch_item, m)?)?;
    // Async siblings: each returns a Python awaitable that completes on the
    // driver's runtime, so the async backend holds no worker thread per call.
    m.add_function(wrap_pyfunction!(documents::create_item_async, m)?)?;
    m.add_function(wrap_pyfunction!(documents::upsert_item_async, m)?)?;
    m.add_function(wrap_pyfunction!(documents::replace_item_async, m)?)?;
    m.add_function(wrap_pyfunction!(documents::delete_item_async, m)?)?;
    m.add_function(wrap_pyfunction!(documents::read_item_async, m)?)?;
    m.add_function(wrap_pyfunction!(documents::patch_item_async, m)?)?;
    // Concrete backend provenance: a counter incremented inside the binding on
    // every operation, so the perf harness can prove the Rust path actually ran
    // (not just that COSMOS_BACKEND said so). See wire::BINDING_OP_COUNT.
    m.add_function(wrap_pyfunction!(wire::operation_count, m)?)?;
    m.add("__version__", env!("CARGO_PKG_VERSION"))?;
    Ok(())
}
