use pyo3::prelude::*;
use pyo3::exceptions::PyException;
use typespec::error::Error as TypeSpecError;

// Define custom exceptions matching the existing Python SDK

pyo3::create_exception!(azure.cosmos.exceptions, CosmosHttpResponseError, PyException);
pyo3::create_exception!(azure.cosmos.exceptions, CosmosResourceNotFoundError, CosmosHttpResponseError);
pyo3::create_exception!(azure.cosmos.exceptions, CosmosResourceExistsError, CosmosHttpResponseError);
pyo3::create_exception!(azure.cosmos.exceptions, CosmosAccessConditionFailedError, CosmosHttpResponseError);

pub fn register_exceptions(m: &PyModule) -> PyResult<()> {
    m.add("CosmosHttpResponseError", m.py().get_type::<CosmosHttpResponseError>())?;
    m.add("CosmosResourceNotFoundError", m.py().get_type::<CosmosResourceNotFoundError>())?;
    m.add("CosmosResourceExistsError", m.py().get_type::<CosmosResourceExistsError>())?;
    m.add("CosmosAccessConditionFailedError", m.py().get_type::<CosmosAccessConditionFailedError>())?;
    Ok(())
}

pub fn map_error(err: TypeSpecError) -> PyErr {
    // Map Rust SDK errors to Python exceptions
    let error_msg = format!("{}", err);
    
    // Check for HTTP status codes in the error
    if error_msg.contains("404") || error_msg.contains("NotFound") {
        CosmosResourceNotFoundError::new_err(error_msg)
    } else if error_msg.contains("409") || error_msg.contains("Conflict") {
        CosmosResourceExistsError::new_err(error_msg)
    } else if error_msg.contains("412") || error_msg.contains("PreconditionFailed") {
        CosmosAccessConditionFailedError::new_err(error_msg)
    } else {
        CosmosHttpResponseError::new_err(error_msg)
    }
}
