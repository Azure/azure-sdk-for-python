// Copyright (c) Microsoft Corporation. All rights reserved.
// Licensed under the MIT License.

//! Read the typed partition key supplied by the Python wrapper.
//!
//! For an order read, kind="components" and values=("customer-17",) become a
//! Rust driver PartitionKey. This is not JSON parsed from an HTTP header.
//! Other kinds preserve distinctions such as extracting a key from an item
//! body versus querying the full container; each operation checks which it accepts.

use azure_data_cosmos_driver::models::{PartitionKey, PartitionKeyValue};
use pyo3::{
    exceptions::{PyTypeError, PyValueError},
    prelude::*,
    types::{PyBool, PyFloat, PyInt, PyString, PyTuple},
};

use super::feed_range::{FeedRangePartitionKeyInput, FeedRangePartitionKeySource};
use super::query::QueryTarget;
use super::request::partition_key_from_components;

#[derive(Clone, Debug, PartialEq)]
pub(crate) enum BindingPartitionKey {
    Components(PartitionKey),
    Extract,
    CrossPartition,
    EmptySentinel,
    EmptySequence,
}

impl BindingPartitionKey {
    pub(crate) fn into_item_key(self) -> PyResult<Option<PartitionKey>> {
        match self {
            Self::Components(key) => Ok(Some(key)),
            Self::Extract => Ok(None),
            Self::EmptySentinel => Err(PyValueError::new_err(
                "Partitionless container keys are not supported by the Rust driver; use the legacy backend",
            )),
            _ => Err(PyValueError::new_err("An item operation requires partition-key components")),
        }
    }

    pub(super) fn into_query_target(self) -> PyResult<QueryTarget> {
        match self {
            Self::Components(key) => Ok(QueryTarget::Partition(key)),
            Self::CrossPartition => Ok(QueryTarget::CrossPartition),
            _ => Err(PyValueError::new_err(
                "Invalid partition-key scope for a query",
            )),
        }
    }

    pub(super) fn into_feed_range_key(self) -> PyResult<FeedRangePartitionKeyInput> {
        let (partition_key, source) = match self {
            Self::Components(key) => (key, FeedRangePartitionKeySource::Standard),
            Self::EmptySentinel => (
                partition_key_from_components(Vec::new())?,
                FeedRangePartitionKeySource::EmptySentinel,
            ),
            Self::EmptySequence => (
                partition_key_from_components(Vec::new())?,
                FeedRangePartitionKeySource::ExplicitEmptySequence,
            ),
            _ => {
                return Err(PyValueError::new_err(
                    "Invalid partition-key source for feed-range resolution",
                ))
            }
        };
        Ok(FeedRangePartitionKeyInput {
            partition_key,
            source,
        })
    }
}

pub(crate) fn extract_partition_key(prepared: &Bound<'_, PyAny>) -> PyResult<BindingPartitionKey> {
    super::settings::validate_request_protocol(prepared)?;
    let input = prepared.getattr("partition_key").map_err(|_| PyTypeError::new_err(
        "Incompatible partition-key protocol: a typed BindingPartitionKey is required; rebuild azure.cosmos._rust",
    ))?;
    let kind: String = input.getattr("kind")?.extract()?;
    let values = input.getattr("values")?;
    let values = values.downcast::<PyTuple>()?;
    if kind != "components" {
        if !values.is_empty() {
            return Err(PyValueError::new_err(
                "Only component partition keys may carry values",
            ));
        }
        return match kind.as_str() {
            "extract" => Ok(BindingPartitionKey::Extract),
            "cross_partition" => Ok(BindingPartitionKey::CrossPartition),
            "empty_sentinel" => Ok(BindingPartitionKey::EmptySentinel),
            "empty_sequence" => Ok(BindingPartitionKey::EmptySequence),
            _ => Err(PyValueError::new_err("Unknown partition-key input kind")),
        };
    }
    if !(1..=3).contains(&values.len()) {
        return Err(PyValueError::new_err(
            "Partition keys require one to three components",
        ));
    }
    let mut components = Vec::with_capacity(values.len());
    for value in values.iter() {
        let component = if value.is_none() {
            PartitionKeyValue::NULL
        } else if value.is(&value.py().Ellipsis()) {
            PartitionKeyValue::UNDEFINED
        } else if value.is_instance_of::<PyBool>() {
            PartitionKeyValue::from(value.extract::<bool>()?)
        } else if value.is_instance_of::<PyString>() {
            PartitionKeyValue::from(value.extract::<String>()?)
        } else if value.is_instance_of::<PyInt>() || value.is_instance_of::<PyFloat>() {
            let number: f64 = value.extract()?;
            if !number.is_finite() {
                return Err(PyValueError::new_err(
                    "Partition-key numbers must be finite",
                ));
            }
            PartitionKeyValue::try_from(number)
                .map_err(|error| PyValueError::new_err(error.to_string()))?
        } else {
            return Err(PyTypeError::new_err(
                "Unsupported partition-key component type",
            ));
        };
        components.push(component);
    }
    Ok(BindingPartitionKey::Components(partition_key_from_components(
        components,
    )?))
}

#[cfg(test)]
/// Convert legacy header examples into typed inputs for tests, not production requests.
pub(crate) fn test_partition_key<'py>(py: Python<'py>, header: Option<&str>) -> Bound<'py, PyAny> {
    use pyo3::types::PyDict;
    use serde_json::Value;
    let (kind, values) = match header {
        None => ("extract", Vec::new()),
        Some("[]") | Some("") => ("cross_partition", Vec::new()),
        Some("[[]]") => ("empty_sequence", Vec::new()),
        Some(header) => {
            let values: Vec<Value> = serde_json::from_str(header).unwrap();
            let values = values
                .into_iter()
                .map(|value| match value {
                    Value::Null => py.None(),
                    Value::Bool(value) => value.into_py(py),
                    Value::Number(value) => value.as_f64().unwrap().into_py(py),
                    Value::String(value) => value.into_py(py),
                    Value::Object(value) if value.is_empty() => py.Ellipsis(),
                    other => panic!("Invalid legacy test key: {other}"),
                })
                .collect();
            ("components", values)
        }
    };
    let kwargs = PyDict::new_bound(py);
    kwargs.set_item("kind", kind).unwrap();
    kwargs
        .set_item("values", PyTuple::new_bound(py, values))
        .unwrap();
    py.import_bound("types")
        .unwrap()
        .getattr("SimpleNamespace")
        .unwrap()
        .call((), Some(&kwargs))
        .unwrap()
}

#[cfg(test)]
mod tests {
    use super::super::legacy_partition_key::legacy_partition_key_header;
    use super::*;
    use pyo3::types::PyDict;

    fn request<'py>(py: Python<'py>, key: Bound<'py, PyAny>) -> Bound<'py, PyAny> {
        let kwargs = PyDict::new_bound(py);
        kwargs.set_item("protocol_version", 3).unwrap();
        kwargs.set_item("partition_key", key).unwrap();
        py.import_bound("types")
            .unwrap()
            .getattr("SimpleNamespace")
            .unwrap()
            .call((), Some(&kwargs))
            .unwrap()
    }

    #[test]
    fn native_scalars_match_legacy_routing_keys() {
        pyo3::prepare_freethreaded_python();
        Python::with_gil(|py| {
            let cases: Vec<(PyObject, &str)> = vec![
                (py.None(), "[null]"),
                (py.Ellipsis(), "[{}]"),
                (true.into_py(py), "[true]"),
                (false.into_py(py), "[false]"),
                (1_i64.into_py(py), "[1]"),
                (0_i64.into_py(py), "[0]"),
                (9007199254740993_u64.into_py(py), "[9007199254740993]"),
                (
                    u128::MAX.into_py(py),
                    "[340282366920938463463374607431768211455]",
                ),
                (0.1_f64.into_py(py), "[0.1]"),
                (0.8455124082255701_f64.into_py(py), "[0.8455124082255701]"),
                (1.2345678901234567_f64.into_py(py), "[1.2345678901234567]"),
                (f64::MIN_POSITIVE.into_py(py), "[2.2250738585072014e-308]"),
                (f64::from_bits(1).into_py(py), "[5e-324]"),
                (f64::MAX.into_py(py), "[1.7976931348623157e308]"),
                ((-0.0_f64).into_py(py), "[-0.0]"),
                (1.25.into_py(py), "[1.25]"),
                ("customer-17".into_py(py), r#"["customer-17"]"#),
                ("\u{4e2d}\u{1f600}".into_py(py), r#"["\u4e2d\ud83d\ude00"]"#),
            ];
            for (value, legacy) in cases {
                let key = test_partition_key(py, Some("[null]"));
                key.setattr("values", PyTuple::new_bound(py, [value]))
                    .unwrap();
                let actual = extract_partition_key(&request(py, key))
                    .unwrap()
                    .into_item_key()
                    .unwrap()
                    .unwrap();
                let expected = legacy_partition_key_header(legacy).unwrap();
                assert_eq!(actual, expected, "{legacy}");
            }
        });
    }

    #[test]
    fn source_states_are_not_interchangeable() {
        assert!(BindingPartitionKey::CrossPartition.into_item_key().is_err());
        assert!(BindingPartitionKey::EmptySentinel.into_item_key().is_err());
        assert!(BindingPartitionKey::EmptySequence
            .into_query_target()
            .is_err());
        assert!(BindingPartitionKey::Extract
            .into_item_key()
            .unwrap()
            .is_none());
        assert!(matches!(
            BindingPartitionKey::CrossPartition
                .into_query_target()
                .unwrap(),
            QueryTarget::CrossPartition
        ));
        assert!(matches!(
            BindingPartitionKey::EmptySentinel
                .into_feed_range_key()
                .unwrap()
                .source,
            FeedRangePartitionKeySource::EmptySentinel
        ));
        assert!(matches!(
            BindingPartitionKey::EmptySequence
                .into_feed_range_key()
                .unwrap()
                .source,
            FeedRangePartitionKeySource::ExplicitEmptySequence
        ));
    }

    #[test]
    fn malformed_values_and_old_protocol_fail_before_driver_work() {
        pyo3::prepare_freethreaded_python();
        Python::with_gil(|py| {
            for value in [
                f64::NAN.into_py(py),
                f64::INFINITY.into_py(py),
                PyDict::new_bound(py).into_any().unbind(),
            ] {
                let key = test_partition_key(py, Some("[null]"));
                key.setattr("values", PyTuple::new_bound(py, [value]))
                    .unwrap();
                assert!(extract_partition_key(&request(py, key)).is_err());
            }
            let key = test_partition_key(py, Some("[null]"));
            key.setattr("values", PyTuple::empty_bound(py)).unwrap();
            assert!(extract_partition_key(&request(py, key)).is_err());
            let request = request(py, test_partition_key(py, None));
            request.setattr("protocol_version", 2).unwrap();
            assert!(extract_partition_key(&request).is_err());
        });
    }
}
