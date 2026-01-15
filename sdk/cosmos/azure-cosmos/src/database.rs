use pyo3::prelude::*;
use pyo3::types::PyDict;
use azure_data_cosmos::{CosmosClient as RustCosmosClient, models::{ContainerProperties, PartitionKeyDefinition}};
use std::sync::Arc;
use crate::container::ContainerClient;
use crate::exceptions::map_error;
use crate::utils::empty_headers_dict;
use once_cell::sync::Lazy;
use tokio::runtime::Runtime;

static TOKIO_RUNTIME: Lazy<Runtime> = Lazy::new(|| {
    tokio::runtime::Builder::new_multi_thread()
        .enable_all()
        .build()
        .expect("Failed to create Tokio runtime")
});

#[pyclass(subclass)]
pub struct DatabaseClient {
    cosmos_client: Arc<RustCosmosClient>,
    database_id: String,
}

impl DatabaseClient {
    pub fn new(cosmos_client: Arc<RustCosmosClient>, database_id: String) -> Self {
        Self {
            cosmos_client,
            database_id,
        }
    }
}

#[pymethods]
impl DatabaseClient {
    /// Create a new container
    /// Returns tuple of (ContainerClient, headers_dict)
    #[pyo3(signature = (id, partition_key, **_kwargs))]
    pub fn create_container<'py>(
        &self,
        py: Python<'py>,
        id: String,
        partition_key: &PyDict,
        _kwargs: Option<&PyDict>,
    ) -> PyResult<(ContainerClient, &'py PyDict)> {
        let db_client = self.cosmos_client.database_client(&self.database_id);
        
        // Extract partition key path
        let paths = partition_key.get_item("paths")?
            .ok_or_else(|| PyErr::new::<pyo3::exceptions::PyKeyError, _>("partition_key must have 'paths'"))?;
        let path_list = paths.extract::<Vec<String>>()?;
        let partition_key_path = path_list.get(0)
            .ok_or_else(|| PyErr::new::<pyo3::exceptions::PyValueError, _>("partition_key paths cannot be empty"))?
            .clone();
        
        let container_id = id.clone();
        TOKIO_RUNTIME.block_on(async move {
            let props = ContainerProperties {
                id: container_id.into(),
                partition_key: PartitionKeyDefinition::from(partition_key_path),
                ..Default::default()
            };
            db_client.create_container(props, None)
                .await
                .map_err(map_error)
        })?;

        let headers = empty_headers_dict(py);
        Ok((ContainerClient::new(
            self.cosmos_client.clone(),
            self.database_id.clone(),
            id,
        ), headers))
    }

    /// Get a container client
    pub fn get_container_client(&self, container_id: String) -> PyResult<ContainerClient> {
        Ok(ContainerClient::new(
            self.cosmos_client.clone(),
            self.database_id.clone(),
            container_id,
        ))
    }

    /// Delete a container
    /// Returns headers_dict
    #[pyo3(signature = (container_id, **_kwargs))]
    pub fn delete_container<'py>(
        &self,
        py: Python<'py>,
        container_id: String,
        _kwargs: Option<&PyDict>,
    ) -> PyResult<&'py PyDict> {
        let db_client = self.cosmos_client.database_client(&self.database_id);
        
        TOKIO_RUNTIME.block_on(async move {
            let container = db_client.container_client(&container_id);
            container.delete(None)
                .await
                .map_err(map_error)
        })?;

        Ok(empty_headers_dict(py))
    }

    /// Read database properties
    /// Returns tuple of (properties_dict, headers_dict)
    #[pyo3(signature = (**_kwargs))]
    pub fn read<'py>(
        &self,
        py: Python<'py>,
        _kwargs: Option<&PyDict>,
    ) -> PyResult<(&'py PyDict, &'py PyDict)> {
        let db_client = self.cosmos_client.database_client(&self.database_id);
        
        TOKIO_RUNTIME.block_on(async move {
            db_client.read(None)
                .await
                .map_err(map_error)
        })?;

        let dict = PyDict::new(py);
        dict.set_item("id", &self.database_id)?;
        let headers = empty_headers_dict(py);
        Ok((dict, headers))
    }

    /// List all containers
    /// Returns tuple of (list_of_dicts, headers_dict)
    #[pyo3(signature = (**_kwargs))]
    pub fn list_containers<'py>(
        &self,
        py: Python<'py>,
        _kwargs: Option<&PyDict>,
    ) -> PyResult<(Vec<&'py PyDict>, &'py PyDict)> {
        let db_client = self.cosmos_client.database_client(&self.database_id);
        
        let containers = TOKIO_RUNTIME.block_on(async move {
            let mut result = Vec::new();
            let mut stream = db_client.query_containers("SELECT * FROM containers", None).map_err(map_error)?;
            
            use futures::StreamExt;
            while let Some(response) = stream.next().await {
                match response {
                    Ok(container) => result.push(container),
                    Err(e) => return Err(map_error(e)),
                }
            }
            
            Ok::<_, PyErr>(result)
        })?;

        let mut py_containers = Vec::new();
        for container in containers {
            let dict = PyDict::new(py);
            dict.set_item("id", format!("{:?}", container))?;
            py_containers.push(dict);
        }

        let headers = empty_headers_dict(py);
        Ok((py_containers, headers))
    }

    /// Delete this database
    /// Returns headers_dict
    #[pyo3(signature = (**_kwargs))]
    pub fn delete<'py>(&self, py: Python<'py>, _kwargs: Option<&PyDict>) -> PyResult<&'py PyDict> {
        let db_client = self.cosmos_client.database_client(&self.database_id);
        
        TOKIO_RUNTIME.block_on(async move {
            db_client.delete(None)
                .await
                .map_err(map_error)
        })?;

        Ok(empty_headers_dict(py))
    }

    #[getter]
    pub fn id(&self) -> PyResult<String> {
        Ok(self.database_id.clone())
    }
}
