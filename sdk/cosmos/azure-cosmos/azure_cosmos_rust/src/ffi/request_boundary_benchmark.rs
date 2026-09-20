// Copyright (c) Microsoft Corporation. All rights reserved.
// Licensed under the MIT License.

//! Offline measurement of the production extractors, without shipping debug exports.

use super::*;
use std::hint::black_box;

#[pyfunction]
fn extract_read(prepared: &Bound<'_, PyAny>) -> PyResult<()> {
    validate_prepared_operation(prepared, "read_item")?;
    black_box(extract_item_inputs(
        prepared,
        READ_ITEM_ID_REQUIRED,
        READ_ITEM_PARTITION_KEY_REQUIRED,
    )?);
    Ok(())
}

#[pyfunction]
fn extract_create(prepared: &Bound<'_, PyAny>) -> PyResult<()> {
    validate_prepared_operation(prepared, "create_item")?;
    black_box(extract_create_body_inputs(prepared)?);
    Ok(())
}

#[pyfunction]
fn extract_query(prepared: &Bound<'_, PyAny>) -> PyResult<()> {
    validate_prepared_operation(prepared, "query_items")?;
    black_box(extract_body_inputs(prepared)?);
    Ok(())
}

#[test]
#[ignore = "offline microbenchmark; run explicitly with --release --ignored --nocapture"]
fn measure_request_boundary() {
    assert!(!cfg!(debug_assertions), "Use --release for this benchmark");
    let script = std::path::Path::new(env!("CARGO_MANIFEST_DIR"))
        .join("../tests/workloads/benchmark_request_boundary.py");
    let code = std::fs::read_to_string(&script).expect("read boundary benchmark script");
    pyo3::prepare_freethreaded_python();
    Python::with_gil(|py| -> PyResult<()> {
        let module = PyModule::from_code_bound(
            py,
            &code,
            script.to_str().expect("UTF-8 script path"),
            "benchmark_request_boundary",
        )?;
        module.getattr("run")?.call1((
            wrap_pyfunction!(extract_read, &module)?,
            wrap_pyfunction!(extract_create, &module)?,
            wrap_pyfunction!(extract_query, &module)?,
            std::env::current_exe()?.to_string_lossy().as_ref(),
        ))?;
        Ok(())
    })
    .unwrap();
}
