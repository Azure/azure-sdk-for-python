use pyo3::prelude::*;
use pyo3::types::{PyDict, PyString};
use azure_data_cosmos::CosmosClient as RustCosmosClient;
use azure_core::credentials::Secret;
use std::sync::Arc;
use tokio::runtime::Runtime;
use crate::database::DatabaseClient;
use crate::exceptions::map_error;

#[pyclass]
pub struct CosmosClient {
    client: Arc<RustCosmosClient>,
    runtime: Arc<Runtime>,
}

#[pymethods]
impl CosmosClient {
    #[new]
    #[pyo3(signature = (url, credential=None, **kwargs))]
    pub fn new(
        url: String,
        credential: Option<PyObject>,
        kwargs: Option<&PyDict>,
    ) -> PyResult<Self> {
        let runtime = Arc::new(Runtime::new().map_err(|e| {
            PyErr::new::<pyo3::exceptions::PyRuntimeError, _>(format!("Failed to create runtime: {}", e))
        })?);

        let client = if let Some(cred) = credential {
            Python::with_gil(|py| {
                if let Ok(key_str) = cred.extract::<String>(py) {
                    // Key-based authentication
                    let secret = Secret::new(key_str);
                    RustCosmosClient::with_key(&url, secret, None)
                        .map_err(map_error)
                } else {
                    Err(PyErr::new::<pyo3::exceptions::PyValueError, _>(
                        "Credential must be a string key"
                    ))
                }
            })?
        } else {
            return Err(PyErr::new::<pyo3::exceptions::PyValueError, _>(
                "Credential is required"
            ));
        };

        Ok(CosmosClient {
            client: Arc::new(client),
            runtime,
        })
    }

    pub fn get_database_client(&self, database: String) -> DatabaseClient {
        DatabaseClient::new(
            self.client.clone(),
            self.runtime.clone(),
            database,
        )
    }

    pub fn create_database(&self, id: String, kwargs: Option<&PyDict>) -> PyResult<PyObject> {
        let client = self.client.clone();
        let result = self.runtime.block_on(async move {
            client.create_database(&id, None)
                .await
                .map_err(map_error)
        })?;

        // Extract response body
        let body = self.runtime.block_on(async move {
            result.into_body().await.map_err(map_error)
        })?;

        // Convert to Python dict
        Python::with_gil(|py| {
            let json_str = serde_json::to_string(&body).map_err(|e| {
                PyErr::new::<pyo3::exceptions::PyValueError, _>(format!("Serialization error: {}", e))
            })?;
            crate::utils::json_to_py_dict(py, &json_str)
        })
    }

    pub fn delete_database(&self, database: String, kwargs: Option<&PyDict>) -> PyResult<()> {
        let db_client = self.client.database_client(&database);
        self.runtime.block_on(async move {
            db_client.delete(None)
                .await
                .map_err(map_error)?;
            Ok(())
        })
    }

    pub fn list_databases(&self, kwargs: Option<&PyDict>) -> PyResult<Vec<PyObject>> {
        let client = self.client.clone();
        let pager = client.query_databases("SELECT * FROM c", None)
            .map_err(map_error)?;

        let mut results = Vec::new();
        let runtime = self.runtime.clone();

        runtime.block_on(async move {
            use azure_core::Pageable;
            let items = pager.into_stream();
            use futures::StreamExt;
            
            let mut pinned_items = Box::pin(items);
            while let Some(page_result) = pinned_items.next().await {
                let page = page_result.map_err(map_error)?;
                for db in page.databases {
                    let json_str = serde_json::to_string(&db).map_err(|e| {
                        PyErr::new::<pyo3::exceptions::PyValueError, _>(format!("Serialization error: {}", e))
                    })?;
                    Python::with_gil(|py| {
                        results.push(crate::utils::json_to_py_dict(py, &json_str)?);
                        Ok::<(), PyErr>(())
                    })?;
                }
            }
            Ok::<(), PyErr>(())
        })?;

        Ok(results)
    }

    fn __enter__<'py>(&'py self, _py: Python<'py>) -> PyResult<&'py Self> {
        Ok(self)
    }

    #[pyo3(signature = (_exc_type=None, _exc_val=None, _exc_tb=None))]
    fn __exit__(
        &self,
        _exc_type: Option<PyObject>,
        _exc_val: Option<PyObject>,
        _exc_tb: Option<PyObject>,
    ) -> PyResult<bool> {
        Ok(false)
    }
}
