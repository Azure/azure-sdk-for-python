use pyo3::prelude::*;
use pyo3::types::{PyDict, PyList};
use azure_data_cosmos::CosmosClient as RustCosmosClient;
use azure_data_cosmos::PartitionKey as RustPartitionKey;
use azure_data_cosmos::ItemOptions;
use std::sync::Arc;
use std::collections::HashMap;
use serde_json::Value;
use crate::exceptions::map_error;
use crate::utils::{py_object_to_json, empty_headers_dict};
use once_cell::sync::Lazy;
use tokio::runtime::Runtime;

// Global Tokio runtime - reused across all operations for better performance
static TOKIO_RUNTIME: Lazy<Runtime> = Lazy::new(|| {
    tokio::runtime::Builder::new_multi_thread()
        .enable_all()
        .build()
        .expect("Failed to create Tokio runtime")
});

#[pyclass(subclass)]
pub struct ContainerClient {
    cosmos_client: Arc<RustCosmosClient>,
    database_id: String,
    container_id: String,
    partition_key_path: Option<String>,  // e.g., "/pk" or "/category"
}

impl ContainerClient {
    pub fn new(cosmos_client: Arc<RustCosmosClient>, database_id: String, container_id: String) -> Self {
        Self {
            cosmos_client,
            database_id,
            container_id,
            partition_key_path: None,
        }
    }

    pub fn with_partition_key_path(cosmos_client: Arc<RustCosmosClient>, database_id: String, container_id: String, partition_key_path: String) -> Self {
        Self {
            cosmos_client,
            database_id,
            container_id,
            partition_key_path: Some(partition_key_path),
        }
    }
}

#[pymethods]
impl ContainerClient {
    /// Create a new item
    /// Accepts either a dict or a JSON string for the body
    /// Returns tuple of (item_dict, headers_dict)
    #[pyo3(signature = (body, **_kwargs))]
    pub fn create_item<'py>(
        &self,
        py: Python<'py>,
        body: &'py PyAny,
        _kwargs: Option<&PyDict>,
    ) -> PyResult<(&'py PyDict, &'py PyDict)> {
        let container = self.cosmos_client
            .database_client(&self.database_id)
            .container_client(&self.container_id);
        
        // Convert Python object (dict or string) to JSON using hybrid approach
        let item_value = py_object_to_json(py, body)?;
        
        // Extract partition key from body or kwargs
        let partition_key = if let Ok(dict) = body.downcast::<PyDict>() {
            self.extract_partition_key(py, dict, _kwargs)?
        } else {
            // If body is a string, partition key must come from kwargs
            self.extract_partition_key_from_kwargs(_kwargs)?
        };
        
        // Execute and get both headers and body
        let (header_map, value) = TOKIO_RUNTIME.block_on(async move {
            // Enable content response on write to get the created item back
            let options = ItemOptions {
                enable_content_response_on_write: true,
                ..Default::default()
            };

            let response = container.create_item(partition_key, item_value, Some(options))
                .await
                .map_err(map_error)?;

            // Extract headers into a HashMap before consuming the body
            let mut headers: HashMap<String, String> = HashMap::new();
            for (name, value) in response.headers().iter() {
                headers.insert(name.as_str().to_string(), value.as_str().to_string());
            }

            // Get the body as JSON - with enable_content_response_on_write, this contains the created item
            let body_value = response.into_body().json::<Value>()
                .map_err(|e| PyErr::new::<pyo3::exceptions::PyValueError, _>(format!("Failed to deserialize response: {}", e)))?;

            Ok::<_, PyErr>((headers, body_value))
        })?;

        // Convert headers to Python dict
        let headers = PyDict::new(py);
        for (key, value) in header_map.iter() {
            headers.set_item(key, value)?;
        }

        let json_str = serde_json::to_string(&value)
            .map_err(|e| PyErr::new::<pyo3::exceptions::PyValueError, _>(format!("JSON error: {}", e)))?;

        let json_module = py.import("json")?;
        let py_dict: &PyDict = json_module.call_method1("loads", (json_str,))?.extract()?;
        Ok((py_dict, headers))
    }

    /// Read an item by ID and partition key
    /// Returns tuple of (item_dict, headers_dict)
    #[pyo3(signature = (item, partition_key, **_kwargs))]
    pub fn read_item<'py>(
        &self,
        py: Python<'py>,
        item: String,
        partition_key: PyObject,
        _kwargs: Option<&PyDict>,
    ) -> PyResult<(&'py PyDict, &'py PyDict)> {
        let container = self.cosmos_client
            .database_client(&self.database_id)
            .container_client(&self.container_id);
        
        let pk = self.python_to_partition_key(py, partition_key)?;
        let item_id = item.clone();
        
        // Execute and get both headers and body
        let (header_map, value) = TOKIO_RUNTIME.block_on(async move {
            let response = container.read_item::<Value>(pk, &item_id, None)
                .await
                .map_err(map_error)?;

            // Extract headers into a HashMap before consuming the body
            let mut headers: HashMap<String, String> = HashMap::new();
            for (name, value) in response.headers().iter() {
                headers.insert(name.as_str().to_string(), value.as_str().to_string());
            }

            // Get the body - read_item always returns the item
            let body_value = response.into_body().json::<Value>()
                .map_err(|e| PyErr::new::<pyo3::exceptions::PyValueError, _>(format!("Failed to deserialize response: {}", e)))?;

            Ok::<_, PyErr>((headers, body_value))
        })?;

        // Convert headers to Python dict
        let headers = PyDict::new(py);
        for (key, value) in header_map.iter() {
            headers.set_item(key, value)?;
        }

        let json_str = serde_json::to_string(&value)
            .map_err(|e| PyErr::new::<pyo3::exceptions::PyValueError, _>(format!("JSON error: {}", e)))?;
        
        let json_module = py.import("json")?;
        let py_dict: &PyDict = json_module.call_method1("loads", (json_str,))?.extract()?;
        Ok((py_dict, headers))
    }

    /// Upsert an item (create or replace)
    /// Returns tuple of (item_dict, headers_dict)
    #[pyo3(signature = (body, **_kwargs))]
    pub fn upsert_item<'py>(
        &self,
        py: Python<'py>,
        body: &'py PyAny,
        _kwargs: Option<&PyDict>,
    ) -> PyResult<(&'py PyDict, &'py PyDict)> {
        let container = self.cosmos_client
            .database_client(&self.database_id)
            .container_client(&self.container_id);
        
        // Convert Python object (dict or string) to JSON using hybrid approach
        let item_value = py_object_to_json(py, body)?;
        
        // Extract partition key from body or kwargs
        let partition_key = if let Ok(dict) = body.downcast::<PyDict>() {
            self.extract_partition_key(py, dict, _kwargs)?
        } else {
            self.extract_partition_key_from_kwargs(_kwargs)?
        };
        
        // Execute and get both headers and body
        let (header_map, value) = TOKIO_RUNTIME.block_on(async move {
            // Enable content response on write to get the upserted item back
            let options = ItemOptions {
                enable_content_response_on_write: true,
                ..Default::default()
            };

            let response = container.upsert_item(partition_key, item_value, Some(options))
                .await
                .map_err(map_error)?;

            // Extract headers into a HashMap before consuming the body
            let mut headers: HashMap<String, String> = HashMap::new();
            for (name, value) in response.headers().iter() {
                headers.insert(name.as_str().to_string(), value.as_str().to_string());
            }

            // Get the body as JSON
            let body_value = response.into_body().json::<Value>()
                .map_err(|e| PyErr::new::<pyo3::exceptions::PyValueError, _>(format!("Failed to deserialize response: {}", e)))?;

            Ok::<_, PyErr>((headers, body_value))
        })?;

        // Convert headers to Python dict
        let headers = PyDict::new(py);
        for (key, value) in header_map.iter() {
            headers.set_item(key, value)?;
        }

        let json_str = serde_json::to_string(&value)
            .map_err(|e| PyErr::new::<pyo3::exceptions::PyValueError, _>(format!("JSON error: {}", e)))?;

        let json_module = py.import("json")?;
        let py_dict: &PyDict = json_module.call_method1("loads", (json_str,))?.extract()?;
        Ok((py_dict, headers))
    }

    /// Replace an item
    /// Returns tuple of (item_dict, headers_dict)
    #[pyo3(signature = (item, body, **_kwargs))]
    pub fn replace_item<'py>(
        &self,
        py: Python<'py>,
        item: String,
        body: &'py PyAny,
        _kwargs: Option<&PyDict>,
    ) -> PyResult<(&'py PyDict, &'py PyDict)> {
        let container = self.cosmos_client
            .database_client(&self.database_id)
            .container_client(&self.container_id);
        
        // Convert Python object (dict or string) to JSON using hybrid approach
        let item_value = py_object_to_json(py, body)?;
        
        // Extract partition key from body or kwargs
        let partition_key = if let Ok(dict) = body.downcast::<PyDict>() {
            self.extract_partition_key(py, dict, _kwargs)?
        } else {
            self.extract_partition_key_from_kwargs(_kwargs)?
        };
        let item_id = item.clone();
        
        // Execute and get both headers and body
        let (header_map, value) = TOKIO_RUNTIME.block_on(async move {
            // Enable content response on write to get the replaced item back
            let options = ItemOptions {
                enable_content_response_on_write: true,
                ..Default::default()
            };

            let response = container.replace_item(partition_key, &item_id, item_value, Some(options))
                .await
                .map_err(map_error)?;

            // Extract headers into a HashMap before consuming the body
            let mut headers: HashMap<String, String> = HashMap::new();
            for (name, value) in response.headers().iter() {
                headers.insert(name.as_str().to_string(), value.as_str().to_string());
            }

            // Get the body as JSON
            let body_value = response.into_body().json::<Value>()
                .map_err(|e| PyErr::new::<pyo3::exceptions::PyValueError, _>(format!("Failed to deserialize response: {}", e)))?;

            Ok::<_, PyErr>((headers, body_value))
        })?;

        // Convert headers to Python dict
        let headers = PyDict::new(py);
        for (key, value) in header_map.iter() {
            headers.set_item(key, value)?;
        }

        let json_str = serde_json::to_string(&value)
            .map_err(|e| PyErr::new::<pyo3::exceptions::PyValueError, _>(format!("JSON error: {}", e)))?;

        let json_module = py.import("json")?;
        let py_dict: &PyDict = json_module.call_method1("loads", (json_str,))?.extract()?;
        Ok((py_dict, headers))
    }

    /// Delete an item
    /// Returns headers_dict
    #[pyo3(signature = (item, partition_key, **_kwargs))]
    pub fn delete_item<'py>(
        &self,
        py: Python<'py>,
        item: String,
        partition_key: PyObject,
        _kwargs: Option<&PyDict>,
    ) -> PyResult<&'py PyDict> {
        let container = self.cosmos_client
            .database_client(&self.database_id)
            .container_client(&self.container_id);
        
        let pk = self.python_to_partition_key(py, partition_key)?;
        let item_id = item.clone();
        
        let header_map = TOKIO_RUNTIME.block_on(async move {
            let response = container.delete_item(pk, &item_id, None)
                .await
                .map_err(map_error)?;

            // Extract headers into a HashMap
            let mut headers: HashMap<String, String> = HashMap::new();
            for (name, value) in response.headers().iter() {
                headers.insert(name.as_str().to_string(), value.as_str().to_string());
            }

            Ok::<_, PyErr>(headers)
        })?;

        // Convert headers to Python dict
        let headers = PyDict::new(py);
        for (key, value) in header_map.iter() {
            headers.set_item(key, value)?;
        }
        Ok(headers)
    }

    /// Query items with SQL
    /// Returns tuple of (list_of_dicts, headers_dict)
    #[pyo3(signature = (query, **kwargs))]
    pub fn query_items<'py>(
        &self,
        py: Python<'py>,
        query: String,
        kwargs: Option<&PyDict>,
    ) -> PyResult<(Vec<&'py PyDict>, &'py PyDict)> {
        let container = self.cosmos_client
            .database_client(&self.database_id)
            .container_client(&self.container_id);
        
        // Extract partition_key from kwargs if provided
        let partition_key_opt = if let Some(kw) = kwargs {
            if let Ok(Some(pk)) = kw.get_item("partition_key") {
                Some(self.python_to_partition_key(py, pk.into())?)
            } else {
                None
            }
        } else {
            None
        };
        
        let items = TOKIO_RUNTIME.block_on(async move {
            let mut result = Vec::new();
            
            // If no partition key is provided, we need to do a cross-partition query
            // For now, if partition_key is not specified, return error asking for it
            let pk = partition_key_opt.ok_or_else(|| {
                PyErr::new::<pyo3::exceptions::PyValueError, _>(
                    "partition_key is required for queries. For cross-partition queries, this will be supported in a future update."
                )
            })?;
            
            let mut stream = container.query_items::<Value>(&query, pk, None).map_err(map_error)?;
            
            use futures::StreamExt;
            while let Some(response) = stream.next().await {
                match response {
                    Ok(item) => {
                        result.push(item);
                    },
                    Err(e) => return Err(map_error(e)),
                }
            }
            
            Ok::<_, PyErr>(result)
        })?;

        let mut py_items = Vec::new();
        for item in items {
            let json_str = serde_json::to_string(&item)
                .map_err(|e| PyErr::new::<pyo3::exceptions::PyValueError, _>(format!("JSON error: {}", e)))?;
            
            let json_module = py.import("json")?;
            let py_dict = json_module.call_method1("loads", (json_str,))?;
            py_items.push(py_dict.extract()?);
        }

        let headers = empty_headers_dict(py);
        Ok((py_items, headers))
    }

    /// Patch an item
    #[pyo3(signature = (_item, _partition_key, _patch_operations, **_kwargs))]
    pub fn patch_item<'py>(
        &self,
        _py: Python<'py>,
        _item: String,
        _partition_key: PyObject,
        _patch_operations: &PyList,
        _kwargs: Option<&PyDict>,
    ) -> PyResult<(&'py PyDict, &'py PyDict)> {
        Err(PyErr::new::<pyo3::exceptions::PyNotImplementedError, _>(
            "patch_item is not yet implemented"
        ))
    }

    /// Read container properties
    /// Returns tuple of (properties_dict, headers_dict)
    #[pyo3(signature = (**_kwargs))]
    pub fn read<'py>(
        &self,
        py: Python<'py>,
        _kwargs: Option<&PyDict>,
    ) -> PyResult<(&'py PyDict, &'py PyDict)> {
        let dict = PyDict::new(py);
        dict.set_item("id", &self.container_id)?;
        let headers = empty_headers_dict(py);
        Ok((dict, headers))
    }

    /// Delete this container
    /// Returns headers_dict
    #[pyo3(signature = (**_kwargs))]
    pub fn delete<'py>(&self, py: Python<'py>, _kwargs: Option<&PyDict>) -> PyResult<&'py PyDict> {
        let container = self.cosmos_client
            .database_client(&self.database_id)
            .container_client(&self.container_id);
        
        TOKIO_RUNTIME.block_on(async move {
            container.delete(None)
                .await
                .map_err(map_error)
        })?;

        Ok(empty_headers_dict(py))
    }

    #[getter]
    pub fn id(&self) -> PyResult<String> {
        Ok(self.container_id.clone())
    }
}

// Helper methods for ContainerClient
impl ContainerClient {
    fn python_to_partition_key(&self, py: Python, pk: PyObject) -> PyResult<RustPartitionKey> {
        if let Ok(s) = pk.extract::<String>(py) {
            Ok(RustPartitionKey::from(s))
        } else if let Ok(i) = pk.extract::<i64>(py) {
            Ok(RustPartitionKey::from(i))
        } else if let Ok(f) = pk.extract::<f64>(py) {
            Ok(RustPartitionKey::from(f))
        } else {
            Err(PyErr::new::<pyo3::exceptions::PyTypeError, _>(
                "Partition key must be string, int, or float"
            ))
        }
    }

    fn extract_partition_key(&self, py: Python, body: &PyDict, kwargs: Option<&PyDict>) -> PyResult<RustPartitionKey> {
        // Try to get partition_key from kwargs first
        if let Some(kw) = kwargs {
            if let Ok(Some(pk)) = kw.get_item("partition_key") {
                return self.python_to_partition_key(py, pk.into());
            }
        }
        
        // If we have a partition key path, use it to extract the value from the body
        if let Some(ref pk_path) = self.partition_key_path {
            // Convert path like "/pk" to field name "pk"
            let field_name = pk_path.trim_start_matches('/');
            if let Ok(Some(value)) = body.get_item(field_name) {
                return self.python_to_partition_key(py, value.into());
            }
        }

        // Fallback: try common partition key field names
        // Note: "pk" should be checked before "id" since "pk" is more commonly the partition key
        let common_pk_fields = ["pk", "partitionKey", "category", "type", "tenantId", "id"];
        for field in &common_pk_fields {
            if let Ok(Some(value)) = body.get_item(field) {
                return self.python_to_partition_key(py, value.into());
            }
        }
        
        Err(PyErr::new::<pyo3::exceptions::PyValueError, _>(
            "Partition key not found in body or kwargs"
        ))
    }
    
    fn extract_partition_key_from_kwargs(&self, kwargs: Option<&PyDict>) -> PyResult<RustPartitionKey> {
        Python::with_gil(|py| {
            if let Some(kw) = kwargs {
                if let Ok(Some(pk)) = kw.get_item("partition_key") {
                    return self.python_to_partition_key(py, pk.into());
                }
            }
            
            Err(PyErr::new::<pyo3::exceptions::PyValueError, _>(
                "Partition key must be provided in kwargs when body is a JSON string"
            ))
        })
    }
}
