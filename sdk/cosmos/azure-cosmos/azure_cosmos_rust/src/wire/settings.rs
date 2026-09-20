// Copyright (c) Microsoft Corporation. All rights reserved.
// Licensed under the MIT License.

use super::request::RequestHeadersAndOptions;
use azure_core::http::headers::{HeaderName, HeaderValue};
use azure_data_cosmos_driver::options::{
    AvailabilityStrategy, ContentResponseOnWrite, EndToEndOperationLatencyPolicy, HedgeThreshold,
    HedgingStrategy,
};
use pyo3::{
    exceptions::{PyTypeError, PyValueError},
    prelude::*,
    types::PyBool,
};
#[cfg(test)]
use pyo3::types::PyDict;
use std::{collections::HashMap, time::Duration};

fn optional<'py, T: FromPyObject<'py>>(obj: &Bound<'py, PyAny>, name: &str) -> PyResult<Option<T>> {
    let value = obj.getattr(name)?;
    if value.is_none() {
        return Ok(None);
    }
    let expected_bool = std::any::type_name::<T>() == "bool";
    if value.is_instance_of::<PyBool>() != expected_bool
        && (expected_bool || value.is_instance_of::<PyBool>())
    {
        return Err(PyTypeError::new_err(format!(
            "invalid type for request setting {name}"
        )));
    }
    value.extract().map(Some)
}

trait WireValue {
    fn wire(self) -> String;
}
impl WireValue for String {
    fn wire(self) -> String {
        self
    }
}
impl WireValue for i64 {
    fn wire(self) -> String {
        self.to_string()
    }
}
impl WireValue for Vec<String> {
    fn wire(self) -> String {
        self.join(",")
    }
}

#[derive(FromPyObject)]
enum IndexingValue {
    Text(String),
    Number(i64),
}
impl WireValue for IndexingValue {
    fn wire(self) -> String {
        match self {
            Self::Text(v) => v,
            Self::Number(v) => v.to_string(),
        }
    }
}

// Boolean casing is a per-header Cosmos contract, not a universal HTTP rule.
// A bool without an explicit encoding fails to compile (no WireValue impl).
macro_rules! header_text {
    ($value:expr, lowercase) => { $value.to_string() };
    ($value:expr, pascal_case) => { (if $value { "True" } else { "False" }).to_owned() };
    ($value:expr) => { $value.wire() };
}

macro_rules! header_group {
    ($reader:ident, $names:ident, {$($field:ident : $ty:ty => $wire:literal $([$encoding:ident])?),* $(,)?}) => {
        const $names: &[&str] = &[$(stringify!($field)),*];
        fn $reader(obj: &Bound<'_, PyAny>, headers: &mut HashMap<HeaderName, HeaderValue>) -> PyResult<()> {
            $(if let Some(value) = optional::<$ty>(obj, stringify!($field))? {
                headers.insert(HeaderName::from_static($wire), HeaderValue::from(header_text!(value $(, $encoding)?)));
            })*
            Ok(())
        }
    };
}

header_group!(item_headers, ITEM_FIELDS, {
    if_match: String => "if-match",
    if_none_match: String => "if-none-match",
    pre_triggers: Vec<String> => "x-ms-documentdb-pre-trigger-include",
    post_triggers: Vec<String> => "x-ms-documentdb-post-trigger-include",
    indexing_directive: IndexingValue => "x-ms-indexing-directive",
    max_staleness_ms: i64 => "x-ms-dedicatedgateway-max-age",
});
header_group!(query_headers, QUERY_FIELDS, {
    max_item_count: i64 => "x-ms-max-item-count",
    continuation: String => "x-ms-continuation",
    is_query: bool => "x-ms-documentdb-isquery" [lowercase],
    enable_cross_partition: bool => "x-ms-documentdb-query-enablecrosspartition" [pascal_case],
    enable_scan: bool => "x-ms-documentdb-query-enable-scan" [pascal_case],
    populate_index_metrics: bool => "x-ms-cosmos-populateindexmetrics" [pascal_case],
    populate_query_metrics: bool => "x-ms-documentdb-populatequerymetrics" [pascal_case],
    populate_query_advice: bool => "x-ms-cosmos-populatequeryadvice" [pascal_case],
    is_query_plan: bool => "x-ms-cosmos-is-query-plan-request" [pascal_case],
    supported_features: String => "x-ms-cosmos-supported-query-features",
    version: String => "x-ms-cosmos-query-version",
    continuation_limit_kb: i64 => "x-ms-documentdb-responsecontinuationtokenlimitinkb",
});
header_group!(resource_headers, RESOURCE_FIELDS, {
    container_rid: String => "x-ms-cosmos-intended-collection-rid",
    offer_throughput: i64 => "x-ms-offer-throughput",
    autoscale_settings: String => "x-ms-cosmos-offer-autopilot-settings",
    offer_type: String => "x-ms-offer-type",
    resource_token_expiry_seconds: i64 => "x-ms-documentdb-expiry-seconds",
    enable_ru_per_minute: bool => "x-ms-offer-is-ru-per-minute-throughput-enabled" [pascal_case],
    disable_ru_per_minute: bool => "x-ms-documentdb-disable-ru-per-minute-usage" [pascal_case],
    enable_script_logging: bool => "x-ms-documentdb-script-enable-logging" [pascal_case],
    populate_partition_statistics: bool => "x-ms-documentdb-populatepartitionstatistics" [pascal_case],
    populate_quota_info: bool => "x-ms-documentdb-populatequotainfo" [pascal_case],
    content_type: String => "content-type",
});

const CORE_FIELDS: &[&str] = &[
    "priority",
    "throughput_bucket",
    "activity_id",
    "correlated_activity_id",
    "session_token",
    "no_response",
    "excluded_locations",
    "hedging",
    "timeout_seconds",
    "consistency_level",
    "item",
    "query",
    "resource",
];

#[pyfunction]
pub(crate) fn _request_settings_schema() -> HashMap<String, Vec<String>> {
    [
        ("RequestSettings", CORE_FIELDS),
        ("ItemSettings", ITEM_FIELDS),
        ("QuerySettings", QUERY_FIELDS),
        ("ResourceSettings", RESOURCE_FIELDS),
        ("HedgingSettings", &["enabled", "threshold_ms"][..]),
        ("BindingPartitionKey", &["kind", "values"][..]),
    ]
    .into_iter()
    .map(|(name, fields)| {
        (
            name.to_owned(),
            fields.iter().map(|s| (*s).to_owned()).collect(),
        )
    })
    .collect()
}

pub(crate) fn validate_request_protocol(prepared: &Bound<'_, PyAny>) -> PyResult<()> {
    let version = prepared.getattr("protocol_version")
        .and_then(|value| value.extract::<u32>())
        .map_err(|_| PyTypeError::new_err(
            "Incompatible request protocol: version 3 with typed partition keys is required; rebuild azure.cosmos._rust",
        ))?;
    if version != 3 {
        return Err(PyValueError::new_err(
            "Incompatible request protocol version",
        ));
    }
    Ok(())
}

pub(crate) fn extract_settings(prepared: &Bound<'_, PyAny>) -> PyResult<RequestHeadersAndOptions> {
    validate_request_protocol(prepared)?;
    let settings = prepared.getattr("settings").map_err(|_| {
        PyTypeError::new_err(
        "Incompatible request protocol: typed settings are required; rebuild azure.cosmos._rust"
    )
    })?;
    if settings.getattr("protocol_version")?.extract::<u32>()? != 3 {
        return Err(PyValueError::new_err(
            "Incompatible request settings protocol version",
        ));
    }

    let mut custom_headers = HashMap::new();
    let mut raw_activity = None;
    let mut raw_session = None;
    for pair in prepared.getattr("headers")?.call_method0("items")?.iter()? {
        let (key, value) = pair?.extract::<(String, String)>()?;
        let name = key.to_ascii_lowercase();
        if name == "x-ms-activity-id" {
            raw_activity = Some(value.clone());
        }
        if name == "x-ms-session-token" {
            raw_session = Some(value.clone());
        }
        custom_headers.insert(HeaderName::from(name), HeaderValue::from(value));
    }
    item_headers(&settings.getattr("item")?, &mut custom_headers)?;
    query_headers(&settings.getattr("query")?, &mut custom_headers)?;
    resource_headers(&settings.getattr("resource")?, &mut custom_headers)?;
    for (field, wire) in [
        ("priority", "x-ms-cosmos-priority-level"),
        (
            "correlated_activity_id",
            "x-ms-cosmos-correlated-activityid",
        ),
        ("consistency_level", "x-ms-consistency-level"),
    ] {
        if let Some(value) = optional::<String>(&settings, field)? {
            if field == "priority" && value != "High" && value != "Low" {
                return Err(PyValueError::new_err("priority must be High or Low"));
            }
            custom_headers.insert(HeaderName::from(wire), HeaderValue::from(value));
        }
    }
    if let Some(bucket) = optional::<u32>(&settings, "throughput_bucket")? {
        custom_headers.insert(
            HeaderName::from_static("x-ms-cosmos-throughput-bucket"),
            HeaderValue::from(bucket.to_string()),
        );
    }
    let activity_header = optional::<String>(&settings, "activity_id")?.or(raw_activity);
    let session_header = optional::<String>(&settings, "session_token")?.or(raw_session);
    custom_headers.remove(&HeaderName::from_static("x-ms-activity-id"));
    custom_headers.remove(&HeaderName::from_static("x-ms-session-token"));
    let no_response = optional::<bool>(&settings, "no_response")?;
    let excluded = optional::<Vec<String>>(&settings, "excluded_locations")?;
    let seconds = optional::<f64>(&settings, "timeout_seconds")?;
    let timeout =
        super::deadline::parse_remaining_timeout(seconds)?.map(EndToEndOperationLatencyPolicy::new);
    let hedging = settings.getattr("hedging")?;
    let availability_strategy = if hedging.is_none() {
        None
    } else {
        let enabled = optional::<bool>(&hedging, "enabled")?
            .ok_or_else(|| PyTypeError::new_err("hedging.enabled is required"))?;
        let threshold = optional::<u64>(&hedging, "threshold_ms")?;
        Some(if enabled {
            let threshold = threshold
                .and_then(|ms| HedgeThreshold::new(Duration::from_millis(ms)))
                .ok_or_else(|| {
                    PyValueError::new_err("Enabled hedging requires positive threshold_ms")
                })?;
            AvailabilityStrategy::Hedging(HedgingStrategy::new(threshold))
        } else {
            if threshold.is_some() {
                return Err(PyValueError::new_err(
                    "Disabled hedging cannot have a threshold",
                ));
            }
            AvailabilityStrategy::Disabled
        })
    };
    Ok(RequestHeadersAndOptions {
        activity_header,
        session_header,
        content_response_on_write: if no_response == Some(true) {
            ContentResponseOnWrite::Disabled
        } else {
            ContentResponseOnWrite::Enabled
        },
        excluded_regions_value: excluded.map(|regions| regions.into_iter().collect()),
        driver_timeout_policy: timeout,
        operation_timeout: None,
        availability_strategy,
        custom_headers,
    })
}

#[cfg(test)]
pub(crate) fn test_settings(py: Python<'_>) -> Bound<'_, PyAny> {
    let namespace = py
        .import_bound("types")
        .unwrap()
        .getattr("SimpleNamespace")
        .unwrap();
    let groups = _request_settings_schema();
    let root = PyDict::new_bound(py);
    for name in CORE_FIELDS {
        root.set_item(name, py.None()).unwrap();
    }
    root.set_item("protocol_version", 3).unwrap();
    for (attribute, name) in [
        ("item", "ItemSettings"),
        ("query", "QuerySettings"),
        ("resource", "ResourceSettings"),
    ] {
        let members = PyDict::new_bound(py);
        for field in &groups[name] {
            members.set_item(field, py.None()).unwrap();
        }
        root.set_item(attribute, namespace.call((), Some(&members)).unwrap())
            .unwrap();
    }
    namespace.call((), Some(&root)).unwrap()
}

#[cfg(test)]
mod tests {
    use super::*;

    fn prepared(py: Python<'_>) -> Bound<'_, PyAny> {
        let kwargs = PyDict::new_bound(py);
        kwargs.set_item("protocol_version", 3).unwrap();
        kwargs.set_item("settings", test_settings(py)).unwrap();
        kwargs.set_item("headers", PyDict::new_bound(py)).unwrap();
        py.import_bound("types")
            .unwrap()
            .getattr("SimpleNamespace")
            .unwrap()
            .call((), Some(&kwargs))
            .unwrap()
    }

    #[test]
    fn readonly_mappings_preserve_header_values_and_typed_precedence() {
        pyo3::prepare_freethreaded_python();
        Python::with_gil(|py| {
            let request = prepared(py);
            let headers = PyDict::new_bound(py);
            headers.set_item("X-CUSTOM", "True").unwrap();
            headers.set_item("X-MS-SESSION-TOKEN", "raw").unwrap();
            headers.set_item("X-MS-ACTIVITY-ID", "activity").unwrap();
            headers.set_item("X-MS-MAX-ITEM-COUNT", "1").unwrap();
            let readonly = py.import_bound("types").unwrap()
                .getattr("MappingProxyType").unwrap().call1((&headers,)).unwrap();
            request.setattr("headers", readonly).unwrap();
            let settings = request.getattr("settings").unwrap();
            settings.setattr("session_token", "typed").unwrap();
            settings.getattr("query").unwrap().setattr("max_item_count", 2).unwrap();
            let result = extract_settings(&request).unwrap();
            assert_eq!(result.session_header.as_deref(), Some("typed"));
            assert_eq!(result.activity_header.as_deref(), Some("activity"));
            assert_eq!(result.custom_headers[&HeaderName::from_static("x-custom")].as_str(), "True");
            assert_eq!(result.custom_headers[&HeaderName::from_static("x-ms-max-item-count")].as_str(), "2");
            assert_eq!(result.custom_headers.len(), 2);
            headers.set_item("x-invalid", 3).unwrap();
            assert!(extract_settings(&request).err().unwrap().is_instance_of::<PyTypeError>(py));
        });
    }

    #[test]
    fn boolean_header_casing_and_override_are_field_specific() {
        pyo3::prepare_freethreaded_python();
        Python::with_gil(|py| {
            for value in [false, true] {
                let request = prepared(py);
                let query = request.getattr("settings").unwrap().getattr("query").unwrap();
                query.setattr("is_query", value).unwrap();
                query.setattr("enable_cross_partition", value).unwrap();
                request.getattr("headers").unwrap().set_item("X-MS-DOCUMENTDB-ISQUERY", "caller").unwrap();
                let result = extract_settings(&request).unwrap();
                assert_eq!(
                    result.custom_headers[&HeaderName::from_static("x-ms-documentdb-isquery")].as_str(),
                    if value { "true" } else { "false" }
                );
                assert_eq!(
                    result.custom_headers[&HeaderName::from_static("x-ms-documentdb-query-enablecrosspartition")].as_str(),
                    if value { "True" } else { "False" }
                );
                assert_eq!(result.custom_headers.len(), 2);
                query.setattr("is_query", 1).unwrap();
                assert!(extract_settings(&request).err().unwrap().is_instance_of::<PyTypeError>(py));
            }
            assert!(extract_settings(&prepared(py)).unwrap().custom_headers.is_empty());
        });
    }

    #[test]
    fn every_service_field_is_read_and_serialized_once() {
        pyo3::prepare_freethreaded_python();
        Python::with_gil(|py| {
            let request = prepared(py);
            let settings = request.getattr("settings").unwrap();
            settings.setattr("priority", "High").unwrap();
            settings.setattr("throughput_bucket", 7).unwrap();
            settings
                .setattr("correlated_activity_id", "correlation")
                .unwrap();
            settings.setattr("consistency_level", "Session").unwrap();
            settings.setattr("activity_id", "activity").unwrap();
            settings.setattr("session_token", "token").unwrap();
            settings.setattr("no_response", true).unwrap();
            settings
                .setattr("excluded_locations", Vec::<String>::new())
                .unwrap();
            settings.setattr("timeout_seconds", 0.25).unwrap();
            for (group, names) in [
                ("item", ITEM_FIELDS),
                ("query", QUERY_FIELDS),
                ("resource", RESOURCE_FIELDS),
            ] {
                let obj = settings.getattr(group).unwrap();
                for field in names {
                    match *field {
                        "pre_triggers" | "post_triggers" => {
                            obj.setattr(*field, vec!["a", "b"]).unwrap()
                        }
                        "indexing_directive"
                        | "max_staleness_ms"
                        | "max_item_count"
                        | "continuation_limit_kb"
                        | "offer_throughput"
                        | "resource_token_expiry_seconds" => obj.setattr(*field, 7).unwrap(),
                        "is_query"
                        | "enable_cross_partition"
                        | "enable_scan"
                        | "populate_index_metrics"
                        | "populate_query_metrics"
                        | "populate_query_advice"
                        | "is_query_plan"
                        | "enable_ru_per_minute"
                        | "disable_ru_per_minute"
                        | "enable_script_logging"
                        | "populate_partition_statistics"
                        | "populate_quota_info" => obj.setattr(*field, true).unwrap(),
                        _ => obj.setattr(*field, "value").unwrap(),
                    }
                }
            }
            let result = extract_settings(&request).unwrap();
            assert_eq!(
                result.custom_headers.len(),
                ITEM_FIELDS.len() + QUERY_FIELDS.len() + RESOURCE_FIELDS.len() + 4
            );
            assert_eq!(result.activity_header.as_deref(), Some("activity"));
            assert_eq!(result.session_header.as_deref(), Some("token"));
            assert!(result.excluded_regions_value.is_some());
            assert!(result.driver_timeout_policy.is_some());
            assert_eq!(
                result.content_response_on_write,
                ContentResponseOnWrite::Disabled
            );
            assert_eq!(
                result.custom_headers
                    [&HeaderName::from_static("x-ms-documentdb-pre-trigger-include")]
                    .as_str(),
                "a,b"
            );
            assert_eq!(
                result.custom_headers[&HeaderName::from_static("x-ms-max-item-count")].as_str(),
                "7"
            );
        });
    }

    #[test]
    fn invalid_values_and_protocols_fail_without_driver_access() {
        pyo3::prepare_freethreaded_python();
        Python::with_gil(|py| {
            for field in [
                "throughput_bucket",
                "timeout_seconds",
                "priority",
                "excluded_locations",
            ] {
                let request = prepared(py);
                request
                    .getattr("settings")
                    .unwrap()
                    .setattr(field, true)
                    .unwrap();
                assert!(extract_settings(&request).is_err(), "{field}");
            }
            let request = prepared(py);
            request
                .getattr("settings")
                .unwrap()
                .setattr("no_response", "false")
                .unwrap();
            assert!(extract_settings(&request).is_err());
            request
                .getattr("settings")
                .unwrap()
                .setattr("protocol_version", 1)
                .unwrap();
            assert!(extract_settings(&request).is_err());
        });
    }

    #[test]
    fn hedging_inheritance_disable_and_enable_are_distinct() {
        pyo3::prepare_freethreaded_python();
        Python::with_gil(|py| {
            let request = prepared(py);
            assert!(extract_settings(&request)
                .unwrap()
                .availability_strategy
                .is_none());
            let hedge = py
                .import_bound("types")
                .unwrap()
                .getattr("SimpleNamespace")
                .unwrap()
                .call0()
                .unwrap();
            hedge.setattr("enabled", false).unwrap();
            hedge.setattr("threshold_ms", py.None()).unwrap();
            request
                .getattr("settings")
                .unwrap()
                .setattr("hedging", &hedge)
                .unwrap();
            assert_eq!(
                extract_settings(&request).unwrap().availability_strategy,
                Some(AvailabilityStrategy::Disabled)
            );
            hedge.setattr("enabled", true).unwrap();
            assert!(extract_settings(&request).is_err());
            hedge.setattr("threshold_ms", 250).unwrap();
            assert!(matches!(
                extract_settings(&request).unwrap().availability_strategy,
                Some(AvailabilityStrategy::Hedging(_))
            ));
        });
    }
}
