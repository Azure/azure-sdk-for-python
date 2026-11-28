// Copyright (c) Microsoft Corporation. All rights reserved.
// Licensed under the MIT License.
//! Parse legacy partition-key header examples for comparison tests.
//! Production binding calls read typed inputs through partition_key_input.rs.
use super::{
    feed_range::{FeedRangePartitionKeyInput, FeedRangePartitionKeySource},
    query::QueryTarget,
    request::{json_value_to_pk_component, partition_key_from_components},
};
use azure_data_cosmos_driver::models::{PartitionKey, PartitionKeyValue};
use pyo3::{exceptions::PyValueError, prelude::*};

pub(super) fn legacy_partition_key_header(header: &str) -> PyResult<PartitionKey> {
    let parsed: Vec<serde_json::Value> = serde_json::from_str(header).map_err(|e| {
        PyValueError::new_err(format!("invalid partition_key_header {header:?}: {e}"))
    })?;

    if parsed.is_empty() {
        return Err(PyValueError::new_err(
            "partition_key_header `[]` (NonePartitionKey / partitionless container) \
             is not yet supported on the Rust path: the driver overloads `PartitionKey::EMPTY` \
             to mean cross-partition query, so emitting it would target the wrong header. \
             Use the legacy backend for partitionless containers until the driver splits \
             those two concepts."
                .to_string(),
        ));
    }
    if parsed.len() > 3 {
        return Err(PyValueError::new_err(format!(
            "partition_key_header has {} components; Cosmos partition keys can have at most 3 levels",
            parsed.len()
        )));
    }

    let mut components: Vec<PartitionKeyValue> = Vec::with_capacity(parsed.len());
    for value in parsed {
        components.push(json_value_to_pk_component(value)?);
    }
    partition_key_from_components(components)
}

pub(super) fn legacy_feed_range_partition_key_header(
    header: &str,
) -> PyResult<FeedRangePartitionKeyInput> {
    let parsed: Vec<serde_json::Value> = serde_json::from_str(header).map_err(|e| {
        PyValueError::new_err(format!("invalid partition_key_header {header:?}: {e}"))
    })?;

    if parsed.len() > 3 {
        return Err(PyValueError::new_err(format!(
            "partition_key_header has {} components; Cosmos partition keys can have at most 3 levels",
            parsed.len()
        )));
    }
    if parsed.is_empty() {
        return Ok(FeedRangePartitionKeyInput {
            partition_key: partition_key_from_components(Vec::new())?,
            source: FeedRangePartitionKeySource::EmptySentinel,
        });
    }
    if parsed.len() == 1 {
        if let serde_json::Value::Array(inner) = &parsed[0] {
            if inner.is_empty() {
                return Ok(FeedRangePartitionKeyInput {
                    partition_key: partition_key_from_components(Vec::new())?,
                    source: FeedRangePartitionKeySource::ExplicitEmptySequence,
                });
            }
        }
    }

    let mut components: Vec<PartitionKeyValue> = Vec::with_capacity(parsed.len());
    for value in parsed {
        components.push(json_value_to_pk_component(value)?);
    }
    Ok(FeedRangePartitionKeyInput {
        partition_key: partition_key_from_components(components)?,
        source: FeedRangePartitionKeySource::Standard,
    })
}

pub(super) fn legacy_query_target_header(header: &str) -> PyResult<QueryTarget> {
    let parsed: Vec<serde_json::Value> = serde_json::from_str(header).map_err(|e| {
        PyValueError::new_err(format!("invalid partition_key_header {header:?}: {e}"))
    })?;

    if parsed.is_empty() {
        return Ok(QueryTarget::CrossPartition);
    }
    if parsed.len() > 3 {
        return Err(PyValueError::new_err(format!(
            "partition_key_header has {} components; Cosmos partition keys can have at most 3 levels",
            parsed.len()
        )));
    }

    let mut components: Vec<PartitionKeyValue> = Vec::with_capacity(parsed.len());
    for value in parsed {
        components.push(json_value_to_pk_component(value)?);
    }
    Ok(QueryTarget::Partition(partition_key_from_components(components)?))
}
