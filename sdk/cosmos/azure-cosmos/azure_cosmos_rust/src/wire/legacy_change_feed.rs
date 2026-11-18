// Copyright (c) Microsoft Corporation. All rights reserved.
// Licensed under the MIT License.

//! Import complete-key legacy checkpoints through the driver's public opaque
//! server-continuation API. Never construct or edit a driver-issued token.

use azure_data_cosmos_driver::models::{
    ChangeFeedStartFrom, ContinuationToken, CosmosOperation, FeedRange, PartitionKey,
};
use pyo3::{
    exceptions::{PyNotImplementedError, PyValueError},
    PyResult,
};
use serde::Deserialize;

use super::request::{json_value_to_pk_component, partition_key_from_components};

#[derive(Deserialize)]
struct Checkpoint {
    v: String,
    #[serde(rename = "containerRid")]
    rid: String,
    mode: String,
    #[serde(rename = "startFrom")]
    start: Start,
    continuation: Composite,
}

#[derive(Deserialize)]
#[serde(tag = "Type")]
enum Start {
    Beginning,
    Now,
    PointInTime {
        #[serde(rename = "PointInTimeMs")]
        milliseconds: i64,
    },
}

impl Start {
    fn matches(&self, start: Option<&ChangeFeedStartFrom>) -> bool {
        match (self, start) {
            (Self::Beginning, Some(ChangeFeedStartFrom::Beginning))
            | (Self::Now, Some(ChangeFeedStartFrom::Now)) => true,
            (Self::PointInTime { milliseconds }, Some(ChangeFeedStartFrom::PointInTime(time))) => {
                time.unix_timestamp_nanos() / 1_000_000 == i128::from(*milliseconds)
            }
            _ => false,
        }
    }
}

#[derive(Deserialize)]
struct Composite {
    v: String,
    rid: String,
    #[serde(flatten)]
    scope: serde_json::Map<String, serde_json::Value>,
    continuation: Vec<Position>,
}

#[derive(Deserialize)]
struct Position {
    token: String,
    range: Bounds,
}

#[derive(Deserialize)]
struct Bounds {
    min: String,
    max: String,
    #[serde(rename = "isMinInclusive")]
    min_inclusive: bool,
    #[serde(rename = "isMaxInclusive")]
    max_inclusive: bool,
}

fn invalid() -> pyo3::PyErr {
    PyValueError::new_err("Invalid or incompatible legacy change-feed checkpoint.")
}

fn numeric_etag(token: &str) -> bool {
    let value = token
        .strip_prefix('"')
        .and_then(|value| value.strip_suffix('"'))
        .unwrap_or(token);
    !value.is_empty() && value.bytes().all(|byte| byte.is_ascii_digit())
}

pub(super) fn continuation(
    token: String,
    operation: &CosmosOperation,
    partition_key: Option<&PartitionKey>,
) -> PyResult<ContinuationToken> {
    if token.starts_with("c1.") || token.starts_with("c2.") {
        return Ok(ContinuationToken::from_string(token));
    }
    if !operation.is_change_feed() || !operation.is_trivial() {
        return Err(PyNotImplementedError::new_err(
            "Legacy change-feed checkpoints require a complete partition key. \
             The public driver API cannot import per-range progress for this scope; \
             no restart or fallback was performed.",
        ));
    }
    if numeric_etag(&token) {
        if operation.request_headers().full_fidelity_feed {
            return Err(invalid());
        }
        return Ok(ContinuationToken::from_string(token));
    }
    let bytes = azure_core::base64::decode(&token).map_err(|_| invalid())?;
    let checkpoint: Checkpoint = serde_json::from_slice(&bytes).map_err(|_| invalid())?;
    let container = operation.container().ok_or_else(invalid)?;
    if checkpoint.v != "v2"
        || checkpoint.continuation.v != "v2"
        || checkpoint.rid != container.rid()
        || checkpoint.continuation.rid != checkpoint.rid
        || checkpoint.mode
            != if operation.request_headers().full_fidelity_feed {
                "AllVersionsAndDeletes"
            } else {
                "LatestVersion"
            }
        || !checkpoint.start.matches(operation.change_feed_start())
        || checkpoint.continuation.scope.contains_key("Range")
    {
        return Err(invalid());
    }
    let key = checkpoint
        .continuation
        .scope
        .get("PK")
        .ok_or_else(invalid)?;
    let values = match key {
        serde_json::Value::Array(values) => values.clone(),
        value => vec![value.clone()],
    };
    let key = partition_key_from_components(
        values
            .into_iter()
            .map(json_value_to_pk_component)
            .collect::<PyResult<_>>()?,
    )?;
    if Some(&key) != partition_key {
        return Err(invalid());
    }
    if checkpoint.continuation.continuation.is_empty() {
        return Err(invalid());
    }
    let [position] = checkpoint.continuation.continuation.as_slice() else {
        return Err(PyNotImplementedError::new_err(
            "Importing legacy change-feed checkpoints with multiple range positions is not supported.",
        ));
    };
    let range = FeedRange::new(
        position
            .range
            .min
            .as_str()
            .try_into()
            .map_err(|_| invalid())?,
        position
            .range
            .max
            .as_str()
            .try_into()
            .map_err(|_| invalid())?,
    )
    .map_err(|_| invalid())?;
    let point = operation.target().ok_or_else(invalid)?.min_inclusive();
    if point < range.min_inclusive()
        || point > range.max_exclusive()
        || (point == range.min_inclusive() && !position.range.min_inclusive)
        || (point == range.max_exclusive() && !position.range.max_inclusive)
        || position.token.is_empty()
        || position
            .token
            .strip_prefix('c')
            .and_then(|value| value.split_once('.'))
            .is_some_and(|(version, _)| version.parse::<u32>().is_ok())
    {
        return Err(invalid());
    }
    Ok(ContinuationToken::from_string(position.token.clone()))
}
