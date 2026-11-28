// Copyright (c) Microsoft Corporation. All rights reserved.
// Licensed under the MIT License.

//! Compare two feed ranges without a service-backend request.
//!
//! The customer app asks whether the child feed range is entirely inside the
//! parent. Compare the original endpoints using the driver's partition-key
//! ordering and retain their inclusion flags. Stepping an endpoint forward or
//! backward can wrap at FF or 00 and cannot preserve variable-width boundaries.
//! This computation does not acquire a driver or contact the service backend.

use serde::Deserialize;

use azure_data_cosmos_driver::models::EffectivePartitionKey;

/// Read parent and child objects from the body supplied by the Python wrapper.
/// Each contains Range with min, max, isMinInclusive, and isMaxInclusive fields.
#[derive(Deserialize)]
struct IsFeedRangeSubsetBody {
    parent: FeedRangeDict,
    child: FeedRangeDict,
}

#[derive(Deserialize)]
struct FeedRangeDict {
    #[serde(rename = "Range")]
    range: RangeDict,
}

#[derive(Deserialize)]
struct RangeDict {
    min: String,
    max: String,
    #[serde(rename = "isMinInclusive")]
    is_min_inclusive: bool,
    #[serde(rename = "isMaxInclusive")]
    is_max_inclusive: bool,
}

fn parse_feed_range_bounds(
    range: &RangeDict,
) -> Result<(EffectivePartitionKey, EffectivePartitionKey), String> {
    let min = EffectivePartitionKey::try_from(range.min.as_str())
        .map_err(|e| format!("invalid feed range minimum: {e}"))?;
    let max = EffectivePartitionKey::try_from(range.max.as_str())
        .map_err(|e| format!("invalid feed range maximum: {e}"))?;
    if min > max {
        return Err("invalid feed range bounds: minimum must not exceed maximum".to_string());
    }
    Ok((min, max))
}

/// Compare endpoints without converting inclusive bounds into exclusive ones.
pub(crate) fn compute_is_feed_range_subset(body_bytes: &[u8]) -> Result<bool, String> {
    let parsed: IsFeedRangeSubsetBody = serde_json::from_slice(body_bytes).map_err(|e| {
        format!("is_feed_range_subset body must be JSON with 'parent' and 'child' feed ranges: {e}")
    })?;
    let parent = parsed.parent.range;
    let child = parsed.child.range;
    let (parent_min, parent_max) = parse_feed_range_bounds(&parent)?;
    let (child_min, child_max) = parse_feed_range_bounds(&child)?;
    if child_min == child_max && !(child.is_min_inclusive && child.is_max_inclusive) {
        return Ok(true);
    }
    if parent_min == parent_max && !(parent.is_min_inclusive && parent.is_max_inclusive) {
        return Ok(false);
    }
    let starts_inside = child_min > parent_min
        || (child_min == parent_min && (!child.is_min_inclusive || parent.is_min_inclusive));
    let ends_inside = child_max < parent_max
        || (child_max == parent_max && (!child.is_max_inclusive || parent.is_max_inclusive));
    Ok(starts_inside && ends_inside)
}

#[cfg(test)]
mod tests {
    use super::compute_is_feed_range_subset;

    fn subset_body(parent: &str, child: &str) -> String {
        format!(r#"{{"parent":{parent},"child":{child}}}"#)
    }

    fn range_dict(min: &str, max: &str, min_inc: bool, max_inc: bool) -> String {
        format!(
            r#"{{"Range":{{"min":"{min}","max":"{max}","isMinInclusive":{min_inc},"isMaxInclusive":{max_inc}}}}}"#
        )
    }

    #[test]
    fn subset_true_when_child_inside_parent() {
        let body = subset_body(
            &range_dict("", "FF", true, false),
            &range_dict("3F", "7F", true, false),
        );
        assert!(compute_is_feed_range_subset(body.as_bytes()).unwrap());
    }

    #[test]
    fn subset_false_when_child_wider_than_parent() {
        let body = subset_body(
            &range_dict("3F", "7F", true, false),
            &range_dict("", "FF", true, false),
        );
        assert!(!compute_is_feed_range_subset(body.as_bytes()).unwrap());
    }

    #[test]
    fn subset_respects_excluded_lower_endpoint() {
        let body = subset_body(
            &range_dict("3F", "7F", false, true),
            &range_dict("3F", "7F", true, false),
        );
        assert!(!compute_is_feed_range_subset(body.as_bytes()).unwrap());
    }

    #[test]
    fn subset_preserves_inclusive_ff_without_wraparound() {
        for max in ["FF", "FFFF"] {
            let parent = range_dict("80", max, true, true);
            for child in [
                parent.clone(),
                range_dict("80", "90", true, false),
                range_dict(max, max, true, true),
            ] {
                let body = subset_body(&parent, &child);
                assert!(compute_is_feed_range_subset(body.as_bytes()).unwrap());
            }
        }
    }

    #[test]
    fn subset_checks_shared_endpoint_flags() {
        for parent_min in [false, true] {
            for parent_max in [false, true] {
                for child_min in [false, true] {
                    for child_max in [false, true] {
                        let body = subset_body(
                            &range_dict("00", "FF", parent_min, parent_max),
                            &range_dict("00", "FF", child_min, child_max),
                        );
                        assert_eq!(
                            compute_is_feed_range_subset(body.as_bytes()).unwrap(),
                            (!child_min || parent_min) && (!child_max || parent_max),
                            "{body}"
                        );
                    }
                }
            }
        }
    }

    #[test]
    fn subset_does_not_expand_variable_width_boundaries() {
        let body = subset_body(
            &range_dict("40", "80", true, true),
            &range_dict("80", "8001", true, false),
        );
        assert!(!compute_is_feed_range_subset(body.as_bytes()).unwrap());
    }

    #[test]
    fn subset_uses_driver_ordering_for_zero_padded_endpoints() {
        let body = subset_body(
            &range_dict("8000", "9000", true, true),
            &range_dict("80", "90", true, true),
        );
        assert!(compute_is_feed_range_subset(body.as_bytes()).unwrap());
    }

    #[test]
    fn subset_distinguishes_empty_ranges_from_points() {
        let empty = range_dict("80", "8000", true, false);
        let point = range_dict("80", "80", true, true);
        let outside = range_dict("90", "A0", true, false);
        assert!(compute_is_feed_range_subset(subset_body(&outside, &empty).as_bytes()).unwrap());
        assert!(!compute_is_feed_range_subset(subset_body(&empty, &point).as_bytes()).unwrap());
        assert!(!compute_is_feed_range_subset(subset_body(&outside, &point).as_bytes()).unwrap());
        assert!(compute_is_feed_range_subset(subset_body(&point, &point).as_bytes()).unwrap());
    }

    #[test]
    fn subset_uppercases_lowercase_hex_bounds() {
        // Hex decoding accepts lowercase bounds without uppercasing the input.
        let body = subset_body(
            &range_dict("", "ff", true, false),
            &range_dict("3f", "7f", true, false),
        );
        assert!(compute_is_feed_range_subset(body.as_bytes()).unwrap());
    }

    #[test]
    fn subset_rejects_inverted_range() {
        // The local computation rejects this reversed range. This test does
        // not exercise Python routing or establish a legacy fallback.
        let body = subset_body(
            &range_dict("7F", "3F", true, false),
            &range_dict("3F", "7F", true, false),
        );
        assert!(compute_is_feed_range_subset(body.as_bytes()).is_err());
    }

    #[test]
    fn subset_rejects_invalid_hex_in_normalized_bounds() {
        for (min, max) in [("3", "7F"), ("GG", "7F"), ("3F", "7"), ("3F", "GG")] {
            let body = subset_body(
                &range_dict("", "FF", true, false),
                &range_dict(min, max, true, false),
            );
            assert!(compute_is_feed_range_subset(body.as_bytes()).is_err());
        }
    }

    #[test]
    fn subset_rejects_malformed_body() {
        // Not JSON at all.
        assert!(compute_is_feed_range_subset(b"not json").is_err());
        // Missing the "child" feed range.
        let body = format!(r#"{{"parent":{}}}"#, range_dict("", "FF", true, false));
        assert!(compute_is_feed_range_subset(body.as_bytes()).is_err());
        // Missing the "Range" wrapper.
        assert!(compute_is_feed_range_subset(br#"{"parent":{},"child":{}}"#).is_err());
    }
}
