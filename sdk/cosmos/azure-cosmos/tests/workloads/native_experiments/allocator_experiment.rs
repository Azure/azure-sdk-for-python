// Copyright (c) Microsoft Corporation. All rights reserved.
// Licensed under the MIT License.

use super::*;
use azure_data_cosmos_driver::{
    in_memory_emulator::{InMemoryEmulatorHttpClient, VirtualAccountConfig, VirtualRegion},
    models::{AccountReference, PartitionKeyDefinition, ResponseBody},
    options::{
        BinaryEncodingOptions, ContentResponseOnWrite, DriverOptions, OperationOptionsBuilder,
    },
};
use std::{future::Future, mem::size_of_val, time::Instant};

fn cpu_ns() -> u64 {
    Python::with_gil(|py| {
        py.import_bound("time")
            .unwrap()
            .call_method0("process_time_ns")
            .unwrap()
            .extract()
            .unwrap()
    })
}

fn python_metrics(method: &str) -> serde_json::Value {
    Python::with_gil(|py| {
        let json: String = py
            .import_bound("native_experiment_metrics")
            .unwrap()
            .call_method0(method)
            .unwrap()
            .extract()
            .unwrap();
        serde_json::from_str(&json).unwrap()
    })
}

async fn fixture() -> Arc<CosmosDriver> {
    let url = azure_core::http::Url::parse("https://allocator.emulator.local").unwrap();
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
    driver
}

fn read_future(
    driver: Arc<CosmosDriver>,
) -> impl Future<Output = PyResult<Result<CosmosResponse, CosmosError>>> + Send + 'static {
    let modifiers = RequestHeadersAndOptions {
        activity_header: None,
        session_header: None,
        content_response_on_write: ContentResponseOnWrite::Enabled,
        excluded_regions_value: None,
        driver_timeout_policy: None,
        operation_timeout: None,
        availability_strategy: None,
        read_consistency_strategy: None,
        patch_strategy: None,
        custom_headers: Default::default(),
    };
    let future = with_operation_timeout(
        None,
        execute_item_on_driver(
            driver,
            "sales".to_owned(),
            "orders".to_owned(),
            Some(PartitionKey::from("customer-17")),
            ItemTarget::Name("order-17".to_owned()),
            Vec::new(),
            modifiers,
            false,
            false,
            |item, _| CosmosOperation::read_item(item),
        ),
    );
    let future = super::super::lifecycle::LifecycleFuture::new(future, None).unwrap();
    async move { future.run().await? }
}

async fn reads(driver: &Arc<CosmosDriver>, count: usize, concurrency: usize, expected: &[u8]) {
    let mut pending = Vec::with_capacity(concurrency);
    let mut completed = 0;
    while completed < count {
        for _ in 0..concurrency.min(count - completed) {
            pending.push(tokio::spawn(read_future(driver.clone())));
        }
        for task in pending.drain(..) {
            let response = task.await.unwrap().unwrap().unwrap();
            assert_eq!(u16::from(response.status().status_code()), 200);
            assert_eq!(response.diagnostics().request_count(), 1);
            match response.body() {
                ResponseBody::Bytes(body) => assert_eq!(body.as_ref(), expected),
                _ => panic!("read must return the expected JSON bytes"),
            }
            Python::with_gil(|py| {
                drop(tuple_from_result(py, Ok(response)).unwrap());
            });
            completed += 1;
        }
    }
    assert_eq!(completed, count);
}

#[test]
#[ignore = "isolated allocator experiment; release, one test process per sample"]
fn measure_allocator_native_reads() {
    assert!(!cfg!(debug_assertions), "use --release");
    crate::test_support::prepare_python();
    let python_runtime = python_metrics("python_source_json");
    let iterations: usize = std::env::var("ALLOCATOR_ITERATIONS")
        .unwrap()
        .parse()
        .unwrap();
    let concurrency: usize = std::env::var("ALLOCATOR_CONCURRENCY")
        .unwrap()
        .parse()
        .unwrap();
    assert!((1..=1_000_000).contains(&iterations));
    assert!([1, 8].contains(&concurrency));
    let runtime = tokio::runtime::Builder::new_multi_thread()
        .worker_threads(2)
        .enable_all()
        .build()
        .unwrap();
    let driver = runtime.block_on(fixture());
    let future_size = size_of_val(&read_future(driver.clone()));
    let read = runtime
        .block_on(read_future(driver.clone()))
        .unwrap()
        .unwrap();
    let expected = match read.body() {
        ResponseBody::Bytes(body) => body.to_vec(),
        _ => panic!("expected JSON read"),
    };
    let item: serde_json::Value = serde_json::from_slice(&expected).unwrap();
    assert_eq!(item["id"], "order-17");
    assert_eq!(item["customerId"], "customer-17");
    runtime.block_on(reads(&driver, 512, concurrency, &expected));
    let before = python_metrics("snapshot_json");
    let cpu_start = cpu_ns();
    let start = Instant::now();
    runtime.block_on(reads(&driver, iterations, concurrency, &expected));
    let elapsed_ns = start.elapsed().as_nanos();
    let process_cpu_ns = cpu_ns() - cpu_start;
    let after = python_metrics("snapshot_json");
    println!(
        "ALLOCATOR_BENCHMARK={}",
        serde_json::json!({
            "allocator": if cfg!(feature = "allocator-experiment-mimalloc") { "mimalloc" } else { "system" },
            "iterations": iterations, "concurrency": concurrency, "worker_threads": 2,
            "warmup_operations": 512, "body_bytes": expected.len(),
            "read_future_bytes": future_size, "elapsed_ns": elapsed_ns,
            "process_cpu_ns": process_cpu_ns, "before": before, "after": after,
            "python_runtime": python_runtime,
            "scope": "In-memory emulator plus native item future, Tokio spawn and Python tuple conversion; no asyncio bridge or public Python API; not network latency",
        })
    );
}
