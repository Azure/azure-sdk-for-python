use pyo3::prelude::*;
use pyo3::types::PyDict;
use serde_json::Value;
use std::collections::HashMap;
use pythonize::depythonize;
use azure_core::http::Response;
use azure_core::http::headers::{HeaderName, HeaderValue};

/// Convert Python object (dict or string) to serde_json::Value
/// Hybrid approach: accepts both PyDict (PyO3 native serialization) and String (direct serde parsing)
pub fn py_object_to_json(_py: Python, obj: &PyAny) -> PyResult<Value> {
    // Fast path: if it's already a JSON string, parse directly with serde
    if let Ok(json_str) = obj.extract::<String>() {
        return serde_json::from_str(&json_str)
            .map_err(|e| PyErr::new::<pyo3::exceptions::PyValueError, _>(
                format!("Invalid JSON string: {}", e)
            ));
    }
    
    // Compatible path: if it's a dict, use PyO3's native serialization (faster than Python's json.dumps)
    if let Ok(dict) = obj.downcast::<PyDict>() {
        return depythonize(dict)
            .map_err(|e| PyErr::new::<pyo3::exceptions::PyValueError, _>(
                format!("Failed to serialize dict: {}", e)
            ));
    }
    
    // Fallback: try to depythonize any Python object
    depythonize(obj)
        .map_err(|e| PyErr::new::<pyo3::exceptions::PyValueError, _>(
            format!("Failed to serialize Python object: {}", e)
        ))
}

/// Convert Python dict to serde_json::Value (legacy function, kept for compatibility)
pub fn py_dict_to_json(_py: Python, dict: &PyDict) -> PyResult<Value> {
    depythonize(dict)
        .map_err(|e| PyErr::new::<pyo3::exceptions::PyValueError, _>(format!("Invalid JSON: {}", e)))
}

/// Convert serde_json::Value to Python dict
pub fn json_to_py_dict(py: Python, value: &Value) -> PyResult<PyObject> {
    let json_str = serde_json::to_string(value)
        .map_err(|e| PyErr::new::<pyo3::exceptions::PyValueError, _>(format!("JSON serialization error: {}", e)))?;
    
    let json_module = py.import("json")?;
    json_module.call_method1("loads", (json_str,))?.extract()
}

/// Convert Python kwargs to options
pub fn extract_kwargs(kwargs: Option<&PyDict>) -> HashMap<String, Value> {
    let mut options = HashMap::new();
    
    if let Some(kw) = kwargs {
        for (key, value) in kw.iter() {
            if let Ok(key_str) = key.extract::<String>() {
                // Extract common option types
                if let Ok(val) = value.extract::<String>() {
                    options.insert(key_str, Value::String(val));
                } else if let Ok(val) = value.extract::<i64>() {
                    options.insert(key_str, Value::Number(val.into()));
                } else if let Ok(val) = value.extract::<bool>() {
                    options.insert(key_str, Value::Bool(val));
                }
            }
        }
    }
    
    options
}

/// Extract response headers from a HashMap and convert to Python dict
/// This is used when we have headers as a HashMap<String, String>
pub fn headers_to_py_dict<'py>(py: Python<'py>, headers: &HashMap<String, String>) -> PyResult<&'py PyDict> {
    let dict = PyDict::new(py);
    for (key, value) in headers.iter() {
        dict.set_item(key, value)?;
    }
    Ok(dict)
}

/// Create an empty headers dict (used when headers are not available)
pub fn empty_headers_dict<'py>(py: Python<'py>) -> &'py PyDict {
    PyDict::new(py)
}

/// Extract response headers from Azure SDK Response and convert to Python dict
/// This extracts all headers from the HTTP response
pub fn extract_response_headers<'py, T>(py: Python<'py>, response: &Response<T>) -> PyResult<&'py PyDict> {
    let dict = PyDict::new(py);

    // Iterate over all headers in the response
    for (name, value) in response.headers().iter() {
        let header_name: &HeaderName = name;
        let header_value: &HeaderValue = value;
        dict.set_item(header_name.as_str(), header_value.as_str())?;
    }

    Ok(dict)
}

