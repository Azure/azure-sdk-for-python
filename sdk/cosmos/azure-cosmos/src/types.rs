use pyo3::prelude::*;
use azure_data_cosmos::PartitionKey as RustPartitionKey;

#[derive(Debug, Clone)]
#[pyclass]
pub struct PartitionKey {
    #[pyo3(get, set)]
    pub value: PyObject,
}

#[pymethods]
impl PartitionKey {
    #[new]
    pub fn new(value: PyObject) -> Self {
        Self { value }
    }
}

impl PartitionKey {
    pub fn to_rust_partition_key(&self, py: Python) -> PyResult<RustPartitionKey> {
        // Convert Python value to Rust PartitionKey
        if let Ok(s) = self.value.extract::<String>(py) {
            Ok(RustPartitionKey::from(s))
        } else if let Ok(i) = self.value.extract::<i64>(py) {
            Ok(RustPartitionKey::from(i))
        } else if let Ok(f) = self.value.extract::<f64>(py) {
            Ok(RustPartitionKey::from(f))
        } else {
            Err(PyErr::new::<pyo3::exceptions::PyTypeError, _>(
                "Partition key must be string, int, or float"
            ))
        }
    }
}
