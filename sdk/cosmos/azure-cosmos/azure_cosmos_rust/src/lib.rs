// Copyright (c) Microsoft Corporation. All rights reserved.
// Licensed under the MIT License.

//! Register the binding functions and types exposed as azure.cosmos._rust.
//!
//! Compiled into one cdylib that Maturin renames to
//! `_rust.{pyd,so}` and drops into `azure/cosmos/`. The
//! Rust driver library is statically linked into that compiled extension. Assets such as
//! QueryPlanInterop are packaged separately.
//!
//! Most operation entry points take a driver handle plus a `PreparedRequest`
//! and return the 5-tuple
//! `(status, sub_status, headers, body, diagnostics)`, which Python builds
//! back into its `BackendResponse` dataclass. Metadata has a separate tuple
//! contract. Feed-range subset checks call the Rust driver's local comparison,
//! not a CosmosDriver service operation.
//!
//! Every operation export has an `_async` twin that returns a Python awaitable
//! instead of a ready result. Runtime creation also has sync and async exports.
//! Acquisition can initialize the default CosmosDriverRuntime,
//! obtain the Tokio runtime, and wait for a CosmosDriver object to be created.
//! It is not merely a driver-cache lookup. See each
//! function for its execution and return-value contract.
//!
//! `azure/cosmos/_rust.pyi` is the complete list of exports, with their
//! parameters; a unit test checks it against the built module. The
//! registrations in `_rust` below show which Rust module defines each export.
//!
//! `wire/settings.rs` validates the request protocol and combines typed settings
//! with prepared headers. Activity/session values become typed operation fields;
//! no-response, timeout, excluded regions, hedging, UTF-8 decoding mode, and
//! throughput control (priority and throughput bucket) become operation options.
//! Other settings become custom headers. Header names are lowercased and typed
//! settings can replace prepared values; operation-specific code may also
//! consume headers, such as PATCH's If-Match precondition.
//!
//! The binding and linked Rust driver are separate responsibilities inside the
//! same compiled extension.


#[cfg(test)]
#[path = "../build_commit.rs"]
mod build_commit;
mod credential;
mod driver_runtime;
mod ffi;
mod feed_range_subset;
#[cfg(test)]
#[path = "../query_plan_binary.rs"]
mod query_plan_binary;
mod runtime;
#[cfg(test)]
mod test_support;
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
    add_pyfn!(m, wire::settings::_request_settings_schema);
    #[cfg(feature = "test-probes")]
    m.add_class::<wire::lifecycle::AsyncOperationProbe>()?;
    m.add_class::<wire::item_feed::ItemFeedCursor>()?;
    m.add_class::<driver_runtime::RuntimeHandle>()?;
    m.add_class::<runtime::DriverHandle>()?;
    add_pyfn!(m, driver_runtime::create_runtime);
    add_pyfn!(m, driver_runtime::create_runtime_async);
    add_pyfn!(m, wire::item_feed::fetch_page_with_cursor);
    add_pyfn!(m, wire::item_feed::fetch_page_with_cursor_async);
    add_pyfn!(m, runtime::acquire_driver_handle);
    add_pyfn!(m, runtime::validate_runtime_configuration);
    add_pyfn!(m, runtime::runtime_configuration);
    add_pyfn!(m, runtime::release_driver_handle);
    #[cfg(feature = "test-probes")]
    {
        add_pyfn!(m, runtime::_debug_fault_injection_rule_hit_count);
        add_pyfn!(m, runtime::_debug_set_fault_injection_rule_enabled);
        add_pyfn!(m, runtime::_debug_cached_account_regions);
    }
    add_pyfn!(m, ffi::create_item);
    add_pyfn!(m, ffi::upsert_item);
    add_pyfn!(m, ffi::replace_item);
    add_pyfn!(m, ffi::delete_item);
    add_pyfn!(m, ffi::read_item);
    add_pyfn!(m, ffi::patch_item);
    add_pyfn!(m, wire::batch::execute_item_batch);
    add_pyfn!(m, ffi::query_items);
    add_pyfn!(m, ffi::read_feed_ranges);
    add_pyfn!(m, ffi::feed_range_from_partition_key);
    add_pyfn!(m, ffi::is_feed_range_subset);
    add_pyfn!(m, ffi::get_throughput);
    add_pyfn!(m, ffi::replace_throughput);
    add_pyfn!(m, ffi::create_database);
    add_pyfn!(m, ffi::read_database);
    add_pyfn!(m, ffi::delete_database);
    add_pyfn!(m, ffi::list_databases);
    add_pyfn!(m, ffi::query_databases);
    add_pyfn!(m, ffi::create_container);
    add_pyfn!(m, ffi::list_containers);
    add_pyfn!(m, ffi::query_containers);
    add_pyfn!(m, ffi::read_container);
    add_pyfn!(m, ffi::delete_container);
    add_pyfn!(m, ffi::replace_container);
    add_pyfn!(m, ffi::get_container_metadata);
    // Async siblings return Python awaitables. Driver-backed paths spawn work
    // rather than reserving a Python worker thread for the full operation.
    add_pyfn!(m, ffi::create_item_async);
    add_pyfn!(m, ffi::upsert_item_async);
    add_pyfn!(m, ffi::replace_item_async);
    add_pyfn!(m, ffi::delete_item_async);
    add_pyfn!(m, ffi::read_item_async);
    add_pyfn!(m, ffi::patch_item_async);
    add_pyfn!(m, wire::batch::execute_item_batch_async);
    add_pyfn!(m, ffi::query_items_async);
    add_pyfn!(m, ffi::read_feed_ranges_async);
    add_pyfn!(m, ffi::feed_range_from_partition_key_async);
    add_pyfn!(m, ffi::is_feed_range_subset_async);
    add_pyfn!(m, ffi::get_throughput_async);
    add_pyfn!(m, ffi::replace_throughput_async);
    add_pyfn!(m, ffi::create_database_async);
    add_pyfn!(m, ffi::read_database_async);
    add_pyfn!(m, ffi::delete_database_async);
    add_pyfn!(m, ffi::list_databases_async);
    add_pyfn!(m, ffi::query_databases_async);
    add_pyfn!(m, ffi::create_container_async);
    add_pyfn!(m, ffi::list_containers_async);
    add_pyfn!(m, ffi::query_containers_async);
    add_pyfn!(m, ffi::read_container_async);
    add_pyfn!(m, ffi::delete_container_async);
    add_pyfn!(m, ffi::replace_container_async);
    add_pyfn!(m, ffi::get_container_metadata_async);
    // Counts instrumented runner entries, not successful operations or network
    // requests. Not every entry point increments it; metadata lookup does not.
    #[cfg(feature = "test-probes")]
    add_pyfn!(m, wire::operation_count);
    // Sum diagnostics passed to record_diagnostics. Attempt totals include the
    // driver's compaction totals; retry counts inspect retained non-initial
    // records. Neither accessor proves complete coverage of a workload.
    #[cfg(feature = "test-probes")]
    add_pyfn!(m, wire::attempt_count);
    #[cfg(feature = "test-probes")]
    add_pyfn!(m, wire::retry_count);
    // Typed transport error the Python backend maps to azure-core's
    // ServiceResponseError (see wire::_DriverTransportError).
    m.add(
        "_DriverTransportError",
        m.py().get_type_bound::<wire::_DriverTransportError>(),
    )?;
    m.add(
        "_DriverResponseError",
        m.py().get_type_bound::<wire::_DriverResponseError>(),
    )?;
    m.add(
        "_UnsupportedQueryFeatureError",
        m.py()
            .get_type_bound::<wire::_UnsupportedQueryFeatureError>(),
    )?;
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
