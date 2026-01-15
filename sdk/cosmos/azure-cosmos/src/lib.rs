use pyo3::prelude::*;

mod client;
mod database;
mod container;
mod exceptions;
mod types;
mod utils;

use client::CosmosClient;
use database::DatabaseClient;
use container::ContainerClient;

/// Azure Cosmos DB Python SDK - Rust native extension
#[pymodule]
fn _rust(_py: Python, m: &PyModule) -> PyResult<()> {
    // Register classes
    m.add_class::<CosmosClient>()?;
    m.add_class::<DatabaseClient>()?;
    m.add_class::<ContainerClient>()?;
    
    // Register exceptions
    exceptions::register_exceptions(m)?;
    
    Ok(())
}
