// Copyright (c) Microsoft Corporation. All rights reserved.
// Licensed under the MIT License.

//! Shared request and response translation between Python and the Rust driver.
//! Operation-specific execution lives in the sibling operation modules; shared
//! helpers cover the following boundaries:
//!
//!   * Request (down): look up the rust driver by handle, parse the container
//!     link and partition key where needed, combine typed settings with prepared
//!     headers, and build driver operation options. Driver-backed runners execute
//!     on the binding's shared Tokio runtime.
//!   * Reply (up): turn the driver's response -- or an error that still carries a
//!     wire response, like a 404/409 -- into the 5-tuple `BackendResponse` the
//!     Python parser reads. Header conversion uses the driver's `to_raw_headers`,
//!     not an unmodified HTTP header collection. Response-less driver errors can
//!     become the typed error Python converts to `ServiceResponseError`; local
//!     validation and binding timeouts have separate error paths.
//!
//! These helpers centralize common conversions; operation-specific handling such
//! as metadata tuples and retained-cursor continuation headers remains separate.
//!
//! Terminology (consistent with `factory.py`, `rust.py`, `credential.rs`,
//! `documents/`, `runtime.rs`, and the Python `_backend` / `_helpers`
//! package docs):
//!
//!   * binding = this compiled `_rust` extension.
//!   * rust driver = the `CosmosDriver` driver. It owns connection pooling,
//!     request signing, and choosing which region to talk to.
//!   * shared Tokio runtime = the binding-owned process-wide executor that
//!     runs the driver's work.
//!   * driver handle = the string naming which rust driver a client uses.
//!   * legacy = the Python implementation that predates the rust driver. It
//!     is being removed.
//!   * item = one stored record. The service calls these documents on the
//!     wire, so the JSON keys stay `Documents`, but prose says item.
//!   * envelope = the JSON wrapper the service puts a feed in, such as
//!     `{"Documents":[...]}` or `{"Offers":[...]}`. The name of the wrapper
//!     for a given feed is carried as `envelope_name`.
//!   * point operation = an operation on a single item, found by its id and
//!     partition key. As opposed to a query or a feed, which return many.

use std::sync::Arc;

use pyo3::exceptions::PyRuntimeError;
use pyo3::prelude::*;

use azure_data_cosmos_driver::driver::CosmosDriver;

use crate::runtime::drivers;

// Extracted sub-modules --------------------------------------------------
mod container_metadata;
pub(crate) mod deadline;
mod diagnostics;
mod driver_runner;
mod errors;
mod request;
mod response;

// Public-facing exception re-exports (lib.rs registers these) ------------
pub use errors::{DriverResponseError, DriverTransportError, UnsupportedQueryFeatureError};

// Diagnostics counter re-exports (pub(crate) so lib.rs can register them) ---
pub(crate) use container_metadata::{get_container_metadata, get_container_metadata_async};
pub(crate) use diagnostics::{attempt_count, operation_count, retry_count};

// Request-side re-exports ------------------------------------------------
// pub(crate): documents/mod.rs imports these by explicit crate::wire:: path.
pub(crate) use request::{
    extract_account_prepared_modifiers, extract_body_bytes, extract_common_prepared_inputs,
    extract_container_feed_prepared_inputs, extract_container_point_prepared_inputs,
    extract_create_item_id, extract_database_prepared_inputs,
    extract_read_feed_ranges_force_refresh, extract_required_item_id, RequestHeadersAndOptions,
};
// ---------------------------------------------------------------------------
// Shared singleton-operation runner (sync + async)
// ---------------------------------------------------------------------------

/// Request task cancellation when the owning Rust bridge future drops this guard.
/// Aborting is not proof of immediate completion, connection release, or rollback
/// of requests already sent to the service.
struct AbortOnDrop(tokio::task::AbortHandle);

impl Drop for AbortOnDrop {
    fn drop(&mut self) {
        self.0.abort();
    }
}

/// Clone the cached driver's Arc, or raise if the handle is absent.
/// A shared handle can remain cached after one client closes; the Python wrapper
/// is responsible for rejecting operations on that closed client.
fn lookup_driver(driver_handle: &str) -> PyResult<Arc<CosmosDriver>> {
    drivers()
        .read()
        .get(driver_handle)
        .map(|entry| Arc::clone(&entry.driver))
        .ok_or_else(|| {
            PyRuntimeError::new_err(format!(
                "no driver registered for handle {driver_handle:?}; call acquire_driver_handle first"
            ))
        })
}

// Operation modules ------------------------------------------------------
mod containers;
mod databases;
mod feed_range;
pub(crate) mod item_feed;
mod items;
mod offers;
mod query;
pub(crate) mod settings;

pub(crate) use containers::{
    run_create_container_operation, run_create_container_operation_async,
    run_delete_container_operation, run_delete_container_operation_async,
    run_list_containers_operation, run_list_containers_operation_async,
    run_query_containers_operation, run_query_containers_operation_async,
    run_read_container_operation, run_read_container_operation_async,
    run_replace_container_operation, run_replace_container_operation_async,
};
pub(crate) use databases::{
    run_create_database_operation, run_create_database_operation_async,
    run_delete_database_operation, run_delete_database_operation_async,
    run_list_databases_operation, run_list_databases_operation_async,
    run_query_databases_operation, run_query_databases_operation_async,
    run_read_database_operation, run_read_database_operation_async,
};
pub(crate) use feed_range::{
    run_feed_range_from_partition_key_operation, run_feed_range_from_partition_key_operation_async,
    run_is_feed_range_subset_operation, run_is_feed_range_subset_operation_async,
    run_read_feed_ranges_operation, run_read_feed_ranges_operation_async,
};
pub(crate) use items::{execute_item_operation_async, execute_item_operation_sync};
pub(crate) use offers::{
    run_read_offer_operation, run_read_offer_operation_async, run_replace_offer_operation,
    run_replace_offer_operation_async,
};
pub(crate) use query::{
    run_query_operation, run_query_operation_async, run_read_all_items_operation,
    run_read_all_items_operation_async,
};

#[cfg(test)]
mod tests {
    use super::feed_range::{
        maybe_handle_feed_range_partition_key_special_case, FeedRangeFromPartitionKeyError,
        FeedRangePartitionKeySource,
    };
    use azure_data_cosmos_driver::models::{
        PartitionKeyDefinition, PartitionKeyKind, PartitionKeyVersion,
    };

    // Exercise the sibling feed-range helper from this parent module's tests
    // without exposing it outside the binding.

    #[test]
    fn feed_range_special_case_empty_sentinel_matches_legacy_v2_hashing() {
        let hash_v2 = PartitionKeyDefinition::from("/pk")
            .with_kind(PartitionKeyKind::Hash)
            .with_version(PartitionKeyVersion::V2);
        let payload = maybe_handle_feed_range_partition_key_special_case(
            &hash_v2,
            FeedRangePartitionKeySource::EmptySentinel,
        )
        .expect("v2 hash _Empty should be supported")
        .expect("v2 hash _Empty should short-circuit with payload");
        assert_eq!(payload.min, "00000000000000000000000000000000");
        assert_eq!(payload.max, "00000000000000000000000000000000");
        assert!(payload.is_max_inclusive);
    }

    #[test]
    fn feed_range_special_case_empty_sentinel_v1_matches_legacy_type_error() {
        let hash_v1 = PartitionKeyDefinition::from("/pk")
            .with_kind(PartitionKeyKind::Hash)
            .with_version(PartitionKeyVersion::V1);
        let err = maybe_handle_feed_range_partition_key_special_case(
            &hash_v1,
            FeedRangePartitionKeySource::EmptySentinel,
        )
        .expect_err("v1 hash _Empty should raise legacy type error");
        match err {
            FeedRangeFromPartitionKeyError::LegacyType(message) => {
                assert!(message.contains("Unexpected type for PK component"));
            }
            other => panic!("unexpected error: {other:?}"),
        }
    }

    #[test]
    fn feed_range_special_case_explicit_empty_sequence_matches_legacy_routing() {
        let hash_v2 = PartitionKeyDefinition::from("/pk")
            .with_kind(PartitionKeyKind::Hash)
            .with_version(PartitionKeyVersion::V2);
        let hash_err = maybe_handle_feed_range_partition_key_special_case(
            &hash_v2,
            FeedRangePartitionKeySource::ExplicitEmptySequence,
        )
        .expect_err("hash container should reject explicit empty sequence");
        match hash_err {
            FeedRangeFromPartitionKeyError::LegacyAttribute(message) => {
                assert!(message.contains("'int' object has no attribute 'upper'"));
            }
            other => panic!("unexpected error: {other:?}"),
        }

        let multihash_v2 = PartitionKeyDefinition::new(vec!["/a".into(), "/b".into()])
            .with_kind(PartitionKeyKind::MultiHash)
            .with_version(PartitionKeyVersion::V2);
        let passthrough = maybe_handle_feed_range_partition_key_special_case(
            &multihash_v2,
            FeedRangePartitionKeySource::ExplicitEmptySequence,
        )
        .expect("multihash explicit empty sequence should not error");
        assert!(passthrough.is_none());
    }

    // AbortOnDrop cancellation safety ------------------------------------
    //
    // For this yielding/sleeping task, dropping the guard produces a cancelled
    // join result and leaves the completion flag unset. This does not exercise
    // Python cancellation, blocking callbacks, network cleanup, or service work.

    #[tokio::test]
    async fn abort_on_drop_aborts_in_flight_task() {
        use std::sync::{
            atomic::{AtomicBool, Ordering},
            Arc,
        };

        let completed = Arc::new(AtomicBool::new(false));
        let completed_clone = Arc::clone(&completed);

        let join = tokio::spawn(async move {
            // Supply a cancellation point if the task is polled before abort.
            tokio::task::yield_now().await;
            tokio::time::sleep(std::time::Duration::from_secs(60)).await;
            completed_clone.store(true, Ordering::SeqCst);
        });

        let guard = super::AbortOnDrop(join.abort_handle());

        // Give the task a chance to start and reach its first yield point.
        tokio::task::yield_now().await;

        // Request cancellation, then await the join result below.
        drop(guard);

        let result = join.await;
        assert!(result.unwrap_err().is_cancelled());
        assert!(!completed.load(Ordering::SeqCst));
    }
}

#[cfg(test)]
mod legacy_partition_key;
pub(crate) mod partition_key;
