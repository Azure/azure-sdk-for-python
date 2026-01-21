use pyo3::prelude::*;
use pyo3::types::PyModule;
use typespec::error::Error as TypeSpecError;

/// Get the Python exception classes from azure.cosmos.exceptions module
fn get_cosmos_exceptions(py: Python) -> PyResult<(PyObject, PyObject, PyObject, PyObject)> {
    let exceptions_module = PyModule::import(py, "azure.cosmos.exceptions")?;
    let http_error = exceptions_module.getattr("CosmosHttpResponseError")?.to_object(py);
    let not_found_error = exceptions_module.getattr("CosmosResourceNotFoundError")?.to_object(py);
    let exists_error = exceptions_module.getattr("CosmosResourceExistsError")?.to_object(py);
    let precondition_error = exceptions_module.getattr("CosmosAccessConditionFailedError")?.to_object(py);
    Ok((http_error, not_found_error, exists_error, precondition_error))
}

/// Extract HTTP status code from error message
fn extract_status_code(error_msg: &str) -> Option<u16> {
    // Look for patterns like "StatusCode: 409" or "status_code=409" or just "409:" at the start
    // Also check for explicit HTTP status code patterns
    if error_msg.contains("StatusCode: 409") || error_msg.contains("\"code\":\"Conflict\"") {
        return Some(409);
    }
    if error_msg.contains("StatusCode: 404") || error_msg.contains("\"code\":\"NotFound\"") {
        return Some(404);
    }
    if error_msg.contains("StatusCode: 412") || error_msg.contains("\"code\":\"PreconditionFailed\"") {
        return Some(412);
    }
    None
}

pub fn map_error(err: TypeSpecError) -> PyErr {
    // Map Rust SDK errors to Python exceptions
    let error_msg = format!("{}", err);
    
    Python::with_gil(|py| {
        // Try to get the actual Python exception classes
        match get_cosmos_exceptions(py) {
            Ok((http_error, not_found_error, exists_error, precondition_error)) => {
                // Extract status code from error message
                let status_code = extract_status_code(&error_msg);

                match status_code {
                    Some(409) => {
                        // CosmosResourceExistsError for 409 Conflict
                        match exists_error.call1(py, (409i32, error_msg.clone())) {
                            Ok(exc) => PyErr::from_value(exc.as_ref(py)),
                            Err(_) => PyErr::new::<pyo3::exceptions::PyRuntimeError, _>(error_msg)
                        }
                    }
                    Some(404) => {
                        // CosmosResourceNotFoundError for 404 Not Found
                        match not_found_error.call1(py, (404i32, error_msg.clone())) {
                            Ok(exc) => PyErr::from_value(exc.as_ref(py)),
                            Err(_) => PyErr::new::<pyo3::exceptions::PyRuntimeError, _>(error_msg)
                        }
                    }
                    Some(412) => {
                        // CosmosAccessConditionFailedError for 412 Precondition Failed
                        match precondition_error.call1(py, (412i32, error_msg.clone())) {
                            Ok(exc) => PyErr::from_value(exc.as_ref(py)),
                            Err(_) => PyErr::new::<pyo3::exceptions::PyRuntimeError, _>(error_msg)
                        }
                    }
                    _ => {
                        // Default to CosmosHttpResponseError for other errors
                        match http_error.call1(py, (500i32, error_msg.clone())) {
                            Ok(exc) => PyErr::from_value(exc.as_ref(py)),
                            Err(_) => PyErr::new::<pyo3::exceptions::PyRuntimeError, _>(error_msg)
                        }
                    }
                }
            }
            Err(_) => {
                // Fallback if we can't import the Python module
                PyErr::new::<pyo3::exceptions::PyRuntimeError, _>(error_msg)
            }
        }
    })
}
