// Copyright (c) Microsoft Corporation. All rights reserved.
// Licensed under the MIT License.

use azure_data_cosmos_driver::{
    error::{CosmosError, CosmosStatus},
    in_memory_emulator::{InMemoryEmulatorHttpClient, VirtualAccountConfig, VirtualRegion},
    models::{
        AccountReference, CosmosOperation, CosmosResponse, ItemReference, PartitionKey,
        PartitionKeyDefinition,
    },
    options::{
        BinaryEncodingOptions, ContentResponseOnWrite, DriverOptions, OperationOptionsBuilder,
    },
};
use pyo3::prelude::*;
use std::{
    sync::{
        atomic::{AtomicU64, Ordering},
        Arc, OnceLock,
    },
    time::{Duration, Instant},
};

const CAPACITY: usize = 25000;
static CLOCK: OnceLock<Instant> = OnceLock::new();
static ROWS: OnceLock<Vec<[AtomicU64; 5]>> = OnceLock::new();
static HANDLE: OnceLock<crate::runtime::DriverHandle> = OnceLock::new();
static RESPONSE: OnceLock<CosmosResponse> = OnceLock::new();

#[pyfunction]
fn clock() -> u64 {
    CLOCK.get_or_init(Instant::now).elapsed().as_nanos() as u64
}

pub(crate) fn mark(slot: usize, phase: usize) {
    ROWS.get().unwrap()[slot][phase].store(clock(), Ordering::Relaxed);
}

#[pyfunction]
fn row(slot: usize) -> PyResult<Vec<u64>> {
    if slot >= CAPACITY {
        return Err(pyo3::exceptions::PyValueError::new_err(
            "trace capacity exceeded",
        ));
    }
    Ok(ROWS.get().unwrap()[slot]
        .iter()
        .map(|value| value.load(Ordering::Relaxed))
        .collect())
}

#[pyfunction]
fn rows(count: usize) -> PyResult<Vec<Vec<u64>>> {
    if count > CAPACITY {
        return Err(pyo3::exceptions::PyValueError::new_err(
            "trace capacity exceeded",
        ));
    }
    Ok(ROWS.get().unwrap()[..count]
        .iter()
        .map(|row| {
            row.iter()
                .map(|value| value.load(Ordering::Relaxed))
                .collect()
        })
        .collect())
}

#[pyfunction]
fn convert_one(py: Python<'_>) -> PyResult<Bound<'_, pyo3::types::PyTuple>> {
    crate::wire::response::tuple_from_result(py, Ok(RESPONSE.get().unwrap().clone()))
}

#[pyfunction]
fn submit(
    py: Python<'_>,
    slot: usize,
    observed: bool,
    fail: bool,
    delay_ms: u64,
) -> PyResult<Bound<'_, PyAny>> {
    if slot >= CAPACITY {
        return Err(pyo3::exceptions::PyValueError::new_err(
            "trace capacity exceeded",
        ));
    }
    let response = RESPONSE.get().unwrap().clone();
    let prepare = move |_| {
        Ok(async move {
            if delay_ms != 0 {
                tokio::time::sleep(Duration::from_millis(delay_ms)).await;
            } else {
                tokio::task::yield_now().await;
            }
            if fail {
                Err(CosmosError::builder()
                    .with_status(CosmosStatus::new(
                        azure_core::http::StatusCode::RequestTimeout,
                    ))
                    .with_message("offline handoff failure")
                    .build())
            } else {
                Ok(response)
            }
        })
    };
    let handle = HANDLE.get().unwrap();
    if observed {
        crate::wire::driver_runner::run_handoff_observed(
            py,
            handle,
            prepare,
            crate::wire::response::tuple_from_result,
            slot,
        )
    } else {
        crate::wire::driver_runner::run_prepared_driver_operation_async(
            py,
            handle,
            "handoff_experiment",
            prepare,
            crate::wire::response::tuple_from_result,
        )
    }
}

async fn initialize() {
    let url = azure_core::http::Url::parse("https://handoff.emulator.local").unwrap();
    let emulator = Arc::new(InMemoryEmulatorHttpClient::new(
        VirtualAccountConfig::new(vec![VirtualRegion::new("East US", url.clone())]).unwrap(),
    ));
    emulator.store().create_database("sales");
    emulator.store().create_container(
        "sales",
        "orders",
        PartitionKeyDefinition::from("/customerId"),
    );
    let runtime = emulator.runtime_builder().build().await.unwrap();
    let driver = runtime
        .create_driver(
            DriverOptions::builder(AccountReference::with_account_key(url, "ZW11bGF0b3Ita2V5"))
                .with_operation_options(
                    OperationOptionsBuilder::new()
                        .with_binary_encoding(BinaryEncodingOptions::new().with_enabled(false))
                        .with_content_response_on_write(ContentResponseOnWrite::Enabled)
                        .build(),
                )
                .build(),
        )
        .await
        .unwrap();
    let container = driver
        .resolve_container("sales", "orders", Default::default())
        .await
        .unwrap();
    driver
        .execute_singleton_operation(
            CosmosOperation::create_item(ItemReference::from_name(
                &container,
                PartitionKey::from("customer-17"),
                "order-17",
            ))
            .with_body(br#"{"id":"order-17","customerId":"customer-17"}"#.to_vec()),
            Default::default(),
        )
        .await
        .unwrap();
    let response = driver
        .execute_singleton_operation(
            CosmosOperation::read_item(ItemReference::from_name(
                &container,
                PartitionKey::from("customer-17"),
                "order-17",
            )),
            Default::default(),
        )
        .await
        .unwrap();
    assert!(HANDLE
        .set(crate::runtime::DriverHandle::for_handoff_experiment(driver))
        .is_ok());
    assert!(RESPONSE.set(response).is_ok());
}

#[cfg(feature = "handoff-count-allocations")]
mod allocations {
    use std::{
        alloc::{GlobalAlloc, Layout, System},
        sync::atomic::{AtomicBool, AtomicU64, Ordering},
    };
    pub(super) static ENABLED: AtomicBool = AtomicBool::new(false);
    pub(super) static ALLOCS: AtomicU64 = AtomicU64::new(0);
    pub(super) static BYTES: AtomicU64 = AtomicU64::new(0);
    pub(super) static FREES: AtomicU64 = AtomicU64::new(0);
    pub(super) static REALLOCS: AtomicU64 = AtomicU64::new(0);
    pub(super) struct Counting;
    unsafe impl GlobalAlloc for Counting {
        unsafe fn alloc(&self, layout: Layout) -> *mut u8 {
            let pointer = System.alloc(layout);
            if !pointer.is_null() && ENABLED.load(Ordering::Relaxed) {
                ALLOCS.fetch_add(1, Ordering::Relaxed);
                BYTES.fetch_add(layout.size() as u64, Ordering::Relaxed);
            }
            pointer
        }
        unsafe fn alloc_zeroed(&self, layout: Layout) -> *mut u8 {
            let pointer = System.alloc_zeroed(layout);
            if !pointer.is_null() && ENABLED.load(Ordering::Relaxed) {
                ALLOCS.fetch_add(1, Ordering::Relaxed);
                BYTES.fetch_add(layout.size() as u64, Ordering::Relaxed);
            }
            pointer
        }
        unsafe fn dealloc(&self, pointer: *mut u8, layout: Layout) {
            if ENABLED.load(Ordering::Relaxed) {
                FREES.fetch_add(1, Ordering::Relaxed);
            }
            System.dealloc(pointer, layout);
        }
        unsafe fn realloc(&self, pointer: *mut u8, layout: Layout, size: usize) -> *mut u8 {
            let result = System.realloc(pointer, layout, size);
            if !result.is_null() && ENABLED.load(Ordering::Relaxed) {
                REALLOCS.fetch_add(1, Ordering::Relaxed);
                BYTES.fetch_add(size as u64, Ordering::Relaxed);
            }
            result
        }
    }
}

#[cfg(feature = "handoff-count-allocations")]
#[global_allocator]
static ALLOCATOR: allocations::Counting = allocations::Counting;

#[pyfunction]
fn allocation_counts(enable: bool) -> (bool, u64, u64, u64, u64) {
    #[cfg(feature = "handoff-count-allocations")]
    {
        use allocations::*;
        ENABLED.store(enable, Ordering::Relaxed);
        (
            true,
            ALLOCS.load(Ordering::Relaxed),
            BYTES.load(Ordering::Relaxed),
            FREES.load(Ordering::Relaxed),
            REALLOCS.load(Ordering::Relaxed),
        )
    }
    #[cfg(not(feature = "handoff-count-allocations"))]
    {
        let _ = enable;
        (false, 0, 0, 0, 0)
    }
}

#[test]
#[ignore = "isolated offline completion-handoff experiment"]
fn measure_completion_handoff() {
    assert!(!cfg!(debug_assertions), "use --release");
    let mut builder = tokio::runtime::Builder::new_multi_thread();
    builder.worker_threads(2).enable_all();
    pyo3_async_runtimes::tokio::init(builder);
    crate::test_support::prepare_python();
    ROWS.get_or_init(|| {
        (0..CAPACITY)
            .map(|_| std::array::from_fn(|_| AtomicU64::new(0)))
            .collect()
    });
    let _ = clock();
    crate::runtime::runtime_context()
        .tokio_rt
        .block_on(initialize());
    Python::with_gil(|py| {
        let native = pyo3::types::PyModule::new_bound(py, "handoff_native").unwrap();
        native
            .add_function(wrap_pyfunction!(clock, &native).unwrap())
            .unwrap();
        native
            .add_function(wrap_pyfunction!(rows, &native).unwrap())
            .unwrap();
        native
            .add_function(wrap_pyfunction!(row, &native).unwrap())
            .unwrap();
        native
            .add_function(wrap_pyfunction!(submit, &native).unwrap())
            .unwrap();
        native
            .add_function(wrap_pyfunction!(convert_one, &native).unwrap())
            .unwrap();
        native
            .add_function(wrap_pyfunction!(allocation_counts, &native).unwrap())
            .unwrap();
        let script = std::env::var("HANDOFF_SCRIPT").unwrap();
        let code = std::fs::read_to_string(&script).unwrap();
        let module =
            pyo3::types::PyModule::from_code_bound(py, &code, &script, "handoff_measure").unwrap();
        if let Err(error) = module.getattr("run").unwrap().call1((native,)) {
            error.print(py);
            panic!("Python handoff experiment failed");
        }
    });
}
