// Copyright (c) Microsoft Corporation. All rights reserved.
// Licensed under the MIT License.

//! PyO3 binding crate that exposes `azure_data_cosmos_driver` to Python.
//!
//! Compiled into one cdylib that Maturin renames to
//! `_rust.{pyd,so}` and drops into `azure/cosmos/`. The
//! driver crate is statically linked into the same binary so the
//! wheel ships exactly one Rust file.
//!
//! Operations take the driver handle returned by `acquire_driver_handle` plus a
//! `PreparedRequest`, and return the 5-tuple
//! `(status, sub_status, headers, body, diagnostics)`, which Python builds
//! back into its `BackendResponse` dataclass. Each one resolves the container,
//! builds a typed driver operation, and runs it on the shared Tokio runtime
//! with the GIL released.
//!
//! Every operation below has an `_async` twin that returns a Python awaitable
//! instead of a ready result. The driver lifecycle, diagnostics, and settings
//! entry points are sync only, because they read process-local state rather
//! than the network; most of them take no arguments at all. The detail for each
//! entry point lives on the function itself, not here.
//!
//! Driver lifecycle (`runtime.rs`):
//!   `acquire_driver_handle`, `release_driver_handle`, `runtime_configuration`,
//!   `fault_injection_rule_hit_count`
//!
//! Items (`documents/items.rs`):
//!   `create_item`, `upsert_item`, `replace_item`, `delete_item`, `read_item`,
//!   `patch_item`
//!
//! Queries and feeds (`documents/query.rs`, `wire/item_feed.rs`):
//!   `query_items`, `read_all_items`, `fetch_page_with_cursor`, and the
//!   `ItemFeedCursor` class
//!
//! Feed ranges (`documents/feed_range.rs`, `feed_range_subset.rs`):
//!   `read_feed_ranges`, `feed_range_from_partition_key`, `is_feed_range_subset`
//!
//! Throughput offers (`documents/offers.rs`):
//!   `read_offer`, `replace_offer`
//!
//! Databases (`documents/databases.rs`):
//!   `create_database`, `read_database`, `delete_database`, `list_databases`,
//!   `query_databases`
//!
//! Containers (`documents/containers.rs`):
//!   `create_container`, `read_container`, `replace_container`,
//!   `delete_container`, `list_containers`, `query_containers`,
//!   `get_container_metadata`
//!
//! Diagnostics and settings (`wire/`):
//!   `operation_count`, `attempt_count`, `retry_count`,
//!   `request_settings_schema`
//! `x-ms-activity-id` and `x-ms-session-token` are forwarded to the
//! driver's typed operation fields. `responsePayloadOnWriteDisabled`
//! is pulled out into the typed `OperationOptions::content_response_on_write`
//! field. Every other per-request header (intended-collection-rid,
//! indexing directive, pre/post triggers, priority, throughput bucket,
//! plus any already-`x-ms-...`-named entry) is pushed through the
//! driver's `OperationOptions::with_custom_headers`, which forwards them unchanged, so
//! it lands on the wire.

mod credential;
mod documents;
mod feed_range_subset;
#[cfg(test)]
#[path = "../query_plan_binary.rs"]
mod query_plan_binary;
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
    add_pyfn!(m, wire::settings::request_settings_schema);
    m.add_class::<wire::item_feed::ItemFeedCursor>()?;
    add_pyfn!(m, wire::item_feed::fetch_page_with_cursor);
    add_pyfn!(m, wire::item_feed::fetch_page_with_cursor_async);
    add_pyfn!(m, runtime::acquire_driver_handle);
    add_pyfn!(m, runtime::runtime_configuration);
    add_pyfn!(m, runtime::release_driver_handle);
    add_pyfn!(m, runtime::fault_injection_rule_hit_count);
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
    add_pyfn!(m, documents::read_database);
    add_pyfn!(m, documents::delete_database);
    add_pyfn!(m, documents::list_databases);
    add_pyfn!(m, documents::query_databases);
    add_pyfn!(m, documents::create_container);
    add_pyfn!(m, documents::list_containers);
    add_pyfn!(m, documents::query_containers);
    add_pyfn!(m, documents::read_container);
    add_pyfn!(m, documents::delete_container);
    add_pyfn!(m, documents::replace_container);
    add_pyfn!(m, documents::get_container_metadata);
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
    add_pyfn!(m, documents::read_database_async);
    add_pyfn!(m, documents::delete_database_async);
    add_pyfn!(m, documents::list_databases_async);
    add_pyfn!(m, documents::query_databases_async);
    add_pyfn!(m, documents::create_container_async);
    add_pyfn!(m, documents::list_containers_async);
    add_pyfn!(m, documents::query_containers_async);
    add_pyfn!(m, documents::read_container_async);
    add_pyfn!(m, documents::delete_container_async);
    add_pyfn!(m, documents::replace_container_async);
    add_pyfn!(m, documents::get_container_metadata_async);
    // Proof of which backend actually ran: a counter incremented inside the binding on
    // every operation, so the perf harness can prove the Rust path actually ran
    // (not just that COSMOS_BACKEND said so). See wire::BINDING_OP_COUNT.
    add_pyfn!(m, wire::operation_count);
    // Per-attempt wire-diagnostics counters: total attempts and driver-issued
    // retries/failovers/hedges combined from each response's DiagnosticsContext.
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
        "DriverResponseError",
        m.py().get_type_bound::<wire::DriverResponseError>(),
    )?;
    m.add(
        "UnsupportedQueryFeatureError",
        m.py()
            .get_type_bound::<wire::UnsupportedQueryFeatureError>(),
    )?;
    m.add("__version__", env!("CARGO_PKG_VERSION"))?;
    m.add(
        "__python_commit__",
        env!("AZURE_COSMOS_BUILD_PYTHON_COMMIT"),
    )?;
    m.add(
        "__rust_driver_commit__",
        env!("AZURE_COSMOS_BUILD_RUST_DRIVER_COMMIT"),
    )?;
    Ok(())
}
