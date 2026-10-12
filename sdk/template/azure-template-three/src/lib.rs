// Copyright (c) Microsoft Corporation. All rights reserved.
// Licensed under the MIT License.

use pyo3::prelude::*;

#[pyfunction]
fn is_true() -> bool {
    true
}

#[pymodule]
fn _rust(module: &Bound<'_, PyModule>) -> PyResult<()> {
    module.add_function(wrap_pyfunction!(is_true, module)?)?;
    Ok(())
}
