// Copyright (c) Microsoft Corporation. All rights reserved.
// Licensed under the MIT License.

//! Shared request and response translation between Python and the Rust driver.
//! Operation-specific execution lives in `databases`, `items`, `query`,
//! `feed_range`, and `offers`; this module owns the behavior all five families need:
//!
//!   * Request (down): look up the rust driver by handle, parse the container
//!     link and partition key, sort the customer's headers into the fields the
//!     driver takes as typed options vs. a plain header pass-through, build the
//!     operation options, then run the operation on the shared Tokio runtime.
//!   * Reply (up): turn the driver's response -- or an error that still carries a
//!     wire response, like a 404/409 -- into the 5-tuple `BackendResponse` the
//!     Python parser reads; copy every response header into a Python dict keyed by
//!     the real `x-ms-...` wire names; and map a response-less failure to a typed
//!     error the Python layer converts to `ServiceResponseError`.
//!
//! Keeping this behavior here prevents operation families from implementing
//! header mapping, error mapping, and response conversion differently.
//!
//! Terminology (consistent with `factory.py`, `rust.py`, `credential.rs`,
//! `documents/`, `runtime.rs`): binding = this compiled `_rust` extension; rust
//! driver = the `CosmosDriver` engine; shared Tokio runtime = the one process-wide
//! Tokio thread pool that runs the driver's work; driver handle = the string
//! naming which rust driver a client uses.

use std::sync::Arc;

use pyo3::exceptions::PyRuntimeError;
use pyo3::prelude::*;

use azure_data_cosmos_driver::driver::CosmosDriver;

use crate::runtime::drivers;

// ── Extracted sub-modules ────────────────────────────────────────────────────
mod container_metadata;
mod diagnostics;
mod driver_runner;
mod errors;
mod request;
mod response;

// ── Public-facing exception re-exports (lib.rs registers these) ──────────────
pub use errors::{DriverTransportError, UnsupportedQueryFeatureError};

// ── Diagnostics counter re-exports (pub(crate) so lib.rs can register them) ──
pub(crate) use container_metadata::{resolve_container_metadata, resolve_container_metadata_async};
pub(crate) use diagnostics::{attempt_count, operation_count, retry_count};

// ── Request-side re-exports ───────────────────────────────────────────────────
// pub(crate): documents/mod.rs imports these by explicit crate::wire:: path.
pub(crate) use request::{
    extract_account_prepared_modifiers, extract_body_bytes, extract_common_prepared_inputs,
    extract_container_feed_prepared_inputs, extract_container_point_prepared_inputs,
    extract_create_item_id, extract_database_prepared_inputs,
    extract_read_feed_ranges_force_refresh, extract_required_item_id, OpModifiers,
};
// ---------------------------------------------------------------------------
// Shared singleton-operation runner (sync + async)
// ---------------------------------------------------------------------------

/// Abort a spawned operation when its Python awaitable is dropped before completion.
struct AbortOnDrop(tokio::task::AbortHandle);

impl Drop for AbortOnDrop {
    fn drop(&mut self) {
        self.0.abort();
    }
}

/// Look up the cached driver for a client handle, or raise if `init_client`
/// has not run yet (or the client was already closed).
fn lookup_driver(handle: &str) -> PyResult<Arc<CosmosDriver>> {
    drivers()
        .read()
        .get(handle)
        .map(|entry| Arc::clone(&entry.driver))
        .ok_or_else(|| {
            PyRuntimeError::new_err(format!(
                "no driver registered for handle {handle:?}; call init_client first"
            ))
        })
}

// ── Operation modules ─────────────────────────────────────────────────────────
mod containers;
mod databases;
mod feed_range;
mod items;
mod offers;
mod query;

pub(crate) use containers::{
    run_create_container_operation, run_create_container_operation_async,
    run_list_containers_operation, run_list_containers_operation_async,
    run_query_containers_operation, run_query_containers_operation_async,
    run_read_container_operation, run_read_container_operation_async,
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
pub(crate) use items::{run_item_operation, run_item_operation_async};
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

    // The three tests below exercise `feed_range.rs`'s
    // `maybe_handle_feed_range_partition_key_special_case`, which is not
    // part of the feed_range module's public API. They live here (in the
    // parent module's test block) so they can reach the function through
    // the private `#[cfg(test)]` import above without widening its visibility
    // in feed_range.rs.

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

    // ── AbortOnDrop cancellation safety ──────────────────────────────────────
    //
    // Proves that dropping the guard aborts a spawned task: the join returns
    // `is_cancelled()` and the task's body never reaches the line after the
    // sleep, so the flag stays false.

    #[tokio::test]
    async fn abort_on_drop_aborts_in_flight_task() {
        use std::sync::{
            atomic::{AtomicBool, Ordering},
            Arc,
        };

        let completed = Arc::new(AtomicBool::new(false));
        let completed_clone = Arc::clone(&completed);

        let join = tokio::spawn(async move {
            // Yield to ensure the task is scheduled before we drop the guard.
            tokio::task::yield_now().await;
            tokio::time::sleep(std::time::Duration::from_secs(60)).await;
            completed_clone.store(true, Ordering::SeqCst);
        });

        let guard = super::AbortOnDrop(join.abort_handle());

        // Give the task a chance to start and reach its first yield point.
        tokio::task::yield_now().await;

        // Dropping the guard aborts the task.
        drop(guard);

        let result = join.await;
        assert!(result.unwrap_err().is_cancelled());
        assert!(!completed.load(Ordering::SeqCst));
    }
}
