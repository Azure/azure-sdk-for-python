// Copyright (c) Microsoft Corporation. All rights reserved.
// Licensed under the MIT License.

//! Compare two feed ranges without a service-backend request.
//!
//! The customer app asks whether the child feed range is entirely inside the
//! parent. This binding module reads their JSON body, converts both ranges to
//! the form expected by FeedRange, and calls the Rust driver's local
//! FeedRange::is_subset_of method. It does not access Python objects or acquire
//! a CosmosDriver object.
//!
//! The bound conversion preserves the legacy Python Range.to_normalized_range
//! arithmetic, including its exclusive-start adjustment. It is not a new
//! interval rule. `wire/feed_range.rs` handles waiting and calls the response
//! converter in `wire/response.rs`; the Python wrapper constructs BackendResponse.

use serde::Deserialize;

use azure_data_cosmos_driver::models::{EffectivePartitionKey, FeedRange};

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

/// Turn one hex character into its 0-15 value, rejecting anything that is not a
/// hex digit.
fn hex_char_value(byte: u8) -> Result<u8, String> {
    match byte {
        b'0'..=b'9' => Ok(byte - b'0'),
        b'a'..=b'f' => Ok(byte - b'a' + 10),
        b'A'..=b'F' => Ok(byte - b'A' + 10),
        other => Err(format!(
            "effective partition key has a non-hex character: {:?}",
            other as char
        )),
    }
}

/// Decode a hex effective-partition-key string into its raw bytes. The string
/// must have an even number of characters (two hex digits per byte); this
/// matches the legacy Python helper's even-length requirement.
fn effective_partition_key_to_bytes(hex: &str) -> Result<Vec<u8>, String> {
    let chars = hex.as_bytes();
    if chars.len() % 2 != 0 {
        return Err(
            "effective partition key hex must have an even number of characters".to_string(),
        );
    }
    let mut out = Vec::with_capacity(chars.len() / 2);
    for pair in chars.chunks_exact(2) {
        out.push((hex_char_value(pair[0])? << 4) | hex_char_value(pair[1])?);
    }
    Ok(out)
}

/// Encode raw bytes back into an upper-case hex effective-partition-key string.
fn bytes_to_effective_partition_key(bytes: &[u8]) -> String {
    const HEX_DIGITS: &[u8; 16] = b"0123456789ABCDEF";
    let mut out = String::with_capacity(bytes.len() * 2);
    for &byte in bytes {
        out.push(HEX_DIGITS[(byte >> 4) as usize] as char);
        out.push(HEX_DIGITS[(byte & 0x0F) as usize] as char);
    }
    out
}

/// Add or subtract one from an effective partition key, treating the hex string
/// as a big-endian number over its bytes. This is the exact arithmetic the
/// legacy Python `add_to_effective_partition_key` performs: for `+1`, walk from the
/// last byte and increment the first byte below 255 (setting trailing 255 bytes
/// to 0 as carries); for `-1`, decrement the first non-zero byte (setting
/// trailing 0 bytes to 255 as borrows).
fn add_to_effective_partition_key(hex: &str, increment: bool) -> Result<String, String> {
    let mut bytes = effective_partition_key_to_bytes(hex)?;
    if increment {
        for byte in bytes.iter_mut().rev() {
            if *byte < 255 {
                *byte += 1;
                break;
            }
            *byte = 0;
        }
    } else {
        for byte in bytes.iter_mut().rev() {
            if *byte != 0 {
                *byte -= 1;
                break;
            }
            *byte = 255;
        }
    }
    Ok(bytes_to_effective_partition_key(&bytes))
}

/// Normalize one feed range to `[min, max)` bounds, matching the legacy Python
/// `Range.to_normalized_range`. The bounds are upper-cased first (the Python
/// parser upper-cases min/max). A range that is already `[min, max)` (min
/// inclusive, max exclusive) is returned as-is; otherwise an inclusive min is
/// left alone but an exclusive min steps back by one, and an inclusive max steps
/// forward by one while an exclusive max is left alone.
fn normalize_feed_range_bounds(range: &RangeDict) -> Result<(String, String), String> {
    let min = range.min.to_ascii_uppercase();
    let max = range.max.to_ascii_uppercase();
    if range.is_min_inclusive && !range.is_max_inclusive {
        return Ok((min, max));
    }
    let normalized_min = if range.is_min_inclusive {
        min
    } else {
        add_to_effective_partition_key(&min, false)?
    };
    let normalized_max = if range.is_max_inclusive {
        add_to_effective_partition_key(&max, true)?
    } else {
        max
    };
    Ok((normalized_min, normalized_max))
}

/// Build a driver `FeedRange` from a normalized `[min, max)` bound pair.
fn feed_range_from_normalized_bounds(min: String, max: String) -> Result<FeedRange, String> {
    FeedRange::new(
        EffectivePartitionKey::from(min),
        EffectivePartitionKey::from(max),
    )
    .map_err(|e| format!("invalid feed range bounds: {e}"))
}

/// Parse both feed ranges and compare them using the Rust driver's local method.
/// For example, the range [40, 60) is inside [20, 80): the lower bound is
/// included and the upper bound is excluded. The response converter elsewhere
/// puts this example's result into `{"IsSubset":true}` body bytes.
pub(crate) fn compute_is_feed_range_subset(body_bytes: &[u8]) -> Result<bool, String> {
    let parsed: IsFeedRangeSubsetBody = serde_json::from_slice(body_bytes).map_err(|e| {
        format!("is_feed_range_subset body must be JSON with 'parent' and 'child' feed ranges: {e}")
    })?;
    let (parent_min, parent_max) = normalize_feed_range_bounds(&parsed.parent.range)?;
    let (child_min, child_max) = normalize_feed_range_bounds(&parsed.child.range)?;
    let parent = feed_range_from_normalized_bounds(parent_min, parent_max)?;
    let child = feed_range_from_normalized_bounds(child_min, child_max)?;
    Ok(child.is_subset_of(&parent))
}

#[cfg(test)]
mod tests {
    use super::{add_to_effective_partition_key, compute_is_feed_range_subset};

    // ---- EPK +/-1 arithmetic --------------------------------------------------
    //
    // These pin the byte carry/borrow rules against the legacy Python
    // `add_to_effective_partition_key`, which the normalization step depends on.

    #[test]
    fn epk_plus_one_increments_last_byte() {
        assert_eq!(add_to_effective_partition_key("3F", true).unwrap(), "40");
        assert_eq!(add_to_effective_partition_key("3E", false).unwrap(), "3D");
    }

    #[test]
    fn epk_plus_one_carries_over_trailing_ff() {
        // 0x3FFF + 1 -> the last byte wraps 0xFF -> 0x00 and the carry lands on
        // the next byte: 0x40, 0x00.
        assert_eq!(
            add_to_effective_partition_key("3FFF", true).unwrap(),
            "4000"
        );
        // All-0xFF wraps to all-0x00 (the carry off the front is dropped, matching
        // legacy `binascii.hexlify` of the truncated byte array).
        assert_eq!(add_to_effective_partition_key("FF", true).unwrap(), "00");
    }

    #[test]
    fn epk_minus_one_borrows_over_trailing_zero() {
        // 0x4000 - 1 -> the last byte borrows 0x00 -> 0xFF and the borrow lands on
        // the next byte: 0x3F, 0xFF.
        assert_eq!(
            add_to_effective_partition_key("4000", false).unwrap(),
            "3FFF"
        );
        // All-zero borrows to all-0xFF.
        assert_eq!(add_to_effective_partition_key("00", false).unwrap(), "FF");
    }

    #[test]
    fn epk_arithmetic_on_empty_string_is_a_noop() {
        // The full-range minimum is the empty string; +/-1 on an empty byte array
        // is a no-op on both backends (the loop has nothing to touch).
        assert_eq!(add_to_effective_partition_key("", true).unwrap(), "");
        assert_eq!(add_to_effective_partition_key("", false).unwrap(), "");
    }

    #[test]
    fn epk_arithmetic_rejects_odd_length_and_non_hex() {
        // Matches legacy `bytearray.fromhex`, which requires even-length hex.
        assert!(add_to_effective_partition_key("3", true).is_err());
        assert!(add_to_effective_partition_key("GG", true).is_err());
    }

    // ---- end-to-end compute ---------------------------------------------------

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
    fn subset_normalizes_inclusive_exclusive_bounds() {
        // parent (3F,7F] normalizes to [3E,80); child [3F,7F) stays. Child is
        // fully inside, so this is a subset -- and it exercises both the -1 (min)
        // and +1 (max) normalization steps.
        let body = subset_body(
            &range_dict("3F", "7F", false, true),
            &range_dict("3F", "7F", true, false),
        );
        assert!(compute_is_feed_range_subset(body.as_bytes()).unwrap());
    }

    #[test]
    fn subset_uppercases_lowercase_hex_bounds() {
        // Lowercase in, subset still computed correctly (bounds are upper-cased
        // exactly like the legacy parser).
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
