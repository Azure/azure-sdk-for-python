// Copyright (c) Microsoft Corporation. All rights reserved.
// Licensed under the MIT License.

//! Execute account-level throughput offer operations using the Rust driver.
//!
//! Reading throughput queries offers and returns an Offers list in body bytes.
//! Replacing throughput targets an offer resource id and returns one offer
//! record. Neither helper resolves an item container or partition key.

use std::sync::atomic::Ordering;
use std::sync::Arc;

use pyo3::exceptions::{PyRuntimeError, PyTimeoutError};
use pyo3::prelude::*;
use pyo3::types::PyTuple;

use azure_core::http::headers::{HeaderName, HeaderValue};
use azure_data_cosmos_driver::{
    diagnostics::DiagnosticsContext,
    driver::CosmosDriver,
    error::CosmosError,
    models::{ActivityId, CosmosOperation, CosmosResponse, SessionToken},
    options::{ContentResponseOnWrite, PlanOptions},
};

use super::deadline::{parse_remaining_timeout, with_timeout};
use super::diagnostics::BINDING_OP_COUNT;
use super::request::{build_operation_options, RequestHeadersAndOptions};
use super::response::{
    tuple_from_offer_feed_result, tuple_from_result, tuple_from_result_with_attempts,
    with_attempt_diagnostics,
};
use super::{lookup_driver, AbortOnDrop};
use crate::runtime::require_runtime_context;

/// Complete the offer query and return its binding response tuple.
/// Wait on the calling thread with Python's global interpreter lock (GIL) released.
pub(crate) fn run_get_throughput_operation<'py>(
    py: Python<'py>,
    driver_handle: &crate::runtime::DriverHandle,
    modifiers: RequestHeadersAndOptions,
    body_bytes: Vec<u8>,
    op_name: &str,
    timeout_seconds: Option<f64>,
    include_attempts: bool,
) -> PyResult<Bound<'py, PyTuple>> {
    let timeout = parse_remaining_timeout(timeout_seconds)?;
    BINDING_OP_COUNT.fetch_add(1, Ordering::Relaxed);
    let driver = lookup_driver(driver_handle)?;
    let runtime_ctx = require_runtime_context(op_name)?;

    let timed = with_timeout(
        timeout,
        run_get_throughput_future(driver, modifiers, body_bytes),
    );
    let response_result = py
        .allow_threads(|| runtime_ctx.tokio_rt.block_on(timed))
        .map_err(|error| PyTimeoutError::new_err(format!("Offer read timed out: {error}")))?;
    offer_read_tuple(py, response_result, include_attempts)
}

/// Async sibling of `run_get_throughput_operation`.
pub(crate) fn run_get_throughput_operation_async<'py>(
    py: Python<'py>,
    driver_handle: &crate::runtime::DriverHandle,
    modifiers: RequestHeadersAndOptions,
    body_bytes: Vec<u8>,
    op_name: &str,
    timeout_seconds: Option<f64>,
    include_attempts: bool,
) -> PyResult<Bound<'py, PyAny>> {
    let timeout = parse_remaining_timeout(timeout_seconds)?;
    BINDING_OP_COUNT.fetch_add(1, Ordering::Relaxed);
    let driver = lookup_driver(driver_handle)?;
    let runtime_ctx = require_runtime_context(op_name)?;

    let timed = with_timeout(
        timeout,
        run_get_throughput_future(driver, modifiers, body_bytes),
    );
    let join = runtime_ctx.tokio_rt.spawn(timed);
    let abort_guard = AbortOnDrop(join.abort_handle());

    pyo3_async_runtimes::tokio::future_into_py(py, async move {
        let _abort_guard = abort_guard;
        let response_result = join
            .await
            .map_err(|join_error| {
                if join_error.is_cancelled() {
                    PyRuntimeError::new_err(
                        "cosmos async operation was cancelled before it completed",
                    )
                } else {
                    PyRuntimeError::new_err(format!(
                        "cosmos async operation task failed: {join_error}"
                    ))
                }
            })?
            .map_err(|error| PyTimeoutError::new_err(format!("Offer read timed out: {error}")))?;
        Python::with_gil(|py| {
            offer_read_tuple(py, response_result, include_attempts)
                .map(|tuple| tuple.into_any().unbind())
        })
    })
}

/// Replace the named offer and return its binding response tuple.
/// Wait on the calling thread with the GIL released; the body contains one record.
pub(crate) fn run_replace_throughput_operation<'py>(
    py: Python<'py>,
    driver_handle: &crate::runtime::DriverHandle,
    modifiers: RequestHeadersAndOptions,
    offer_id: String,
    body_bytes: Vec<u8>,
    op_name: &str,
    timeout_seconds: Option<f64>,
    include_attempts: bool,
) -> PyResult<Bound<'py, PyTuple>> {
    let timeout = parse_remaining_timeout(timeout_seconds)?;
    BINDING_OP_COUNT.fetch_add(1, Ordering::Relaxed);
    let driver = lookup_driver(driver_handle)?;
    let runtime_ctx = require_runtime_context(op_name)?;

    let timed = with_timeout(
        timeout,
        run_replace_throughput_future(driver, modifiers, offer_id, body_bytes),
    );
    let response_result = py
        .allow_threads(|| runtime_ctx.tokio_rt.block_on(timed))
        .map_err(|error| {
            PyTimeoutError::new_err(format!("Throughput replacement timed out: {error}"))
        })?;
    if include_attempts {
        tuple_from_result_with_attempts(py, response_result)
    } else {
        tuple_from_result(py, response_result)
    }
}

/// Async sibling of `run_replace_throughput_operation`.
pub(crate) fn run_replace_throughput_operation_async<'py>(
    py: Python<'py>,
    driver_handle: &crate::runtime::DriverHandle,
    modifiers: RequestHeadersAndOptions,
    offer_id: String,
    body_bytes: Vec<u8>,
    op_name: &str,
    timeout_seconds: Option<f64>,
    include_attempts: bool,
) -> PyResult<Bound<'py, PyAny>> {
    let timeout = parse_remaining_timeout(timeout_seconds)?;
    BINDING_OP_COUNT.fetch_add(1, Ordering::Relaxed);
    let driver = lookup_driver(driver_handle)?;
    let runtime_ctx = require_runtime_context(op_name)?;

    let timed = with_timeout(
        timeout,
        run_replace_throughput_future(driver, modifiers, offer_id, body_bytes),
    );
    let join = runtime_ctx.tokio_rt.spawn(timed);
    let abort_guard = AbortOnDrop(join.abort_handle());

    pyo3_async_runtimes::tokio::future_into_py(py, async move {
        let _abort_guard = abort_guard;
        let response_result = join
            .await
            .map_err(|join_error| {
                if join_error.is_cancelled() {
                    PyRuntimeError::new_err(
                        "cosmos async operation was cancelled before it completed",
                    )
                } else {
                    PyRuntimeError::new_err(format!(
                        "cosmos async operation task failed: {join_error}"
                    ))
                }
            })?
            .map_err(|error| {
                PyTimeoutError::new_err(format!("Throughput replacement timed out: {error}"))
            })?;
        Python::with_gil(|py| {
            let result = if include_attempts {
                tuple_from_result_with_attempts(py, response_result)
            } else {
                tuple_from_result(py, response_result)
            };
            result.map(|tuple| tuple.into_any().unbind())
        })
    })
}
struct OfferReadResult {
    responses: Vec<CosmosResponse>,
    error: Option<CosmosError>,
}

impl OfferReadResult {
    fn into_result(self) -> Result<Vec<CosmosResponse>, CosmosError> {
        match self.error {
            Some(error) => Err(error),
            None => Ok(self.responses),
        }
    }
}

fn offer_read_tuple<'py>(
    py: Python<'py>,
    result: OfferReadResult,
    include_attempts: bool,
) -> PyResult<Bound<'py, PyTuple>> {
    if !include_attempts {
        return tuple_from_offer_feed_result(py, result.into_result());
    }
    let mut sources: Vec<_> = result
        .responses
        .iter()
        .map(CosmosResponse::diagnostics)
        .collect();
    let mut complete = true;
    if let Some(error) = &result.error {
        match error.diagnostics() {
            Some(diagnostics) => sources.push(diagnostics),
            None => complete = false,
        }
    }
    let diagnostics = DiagnosticsContext::aggregate_sub_operations(&sources).map(Arc::new);
    with_attempt_diagnostics(
        py,
        tuple_from_offer_feed_result(py, result.into_result()),
        diagnostics,
        complete,
    )
}

/// Build query_offers against the account using the prepared query body.
/// Add default query `Content-Type` and `x-ms-documentdb-isquery` markers only if
/// absent from custom headers. The prepared container-recreate guard header is
/// also supplied through those custom headers; this helper does not enforce it.
async fn run_get_throughput_future(
    driver: Arc<CosmosDriver>,
    modifiers: RequestHeadersAndOptions,
    body_bytes: Vec<u8>,
) -> OfferReadResult {
    let account = driver.account().clone();
    let mut op = CosmosOperation::query_offers(account).with_body(body_bytes);

    if let Some(activity) = modifiers.activity_header.as_ref() {
        op = op.with_activity_id(ActivityId::from(activity.clone()));
    }
    if let Some(session) = modifiers.session_header.as_ref() {
        op = op.with_session_token(SessionToken::from(session.clone()));
    }

    let mut custom_headers = modifiers.custom_headers;
    custom_headers
        .entry(HeaderName::from_static("content-type"))
        .or_insert_with(|| HeaderValue::from("application/query+json".to_string()));
    custom_headers
        .entry(HeaderName::from_static("x-ms-documentdb-isquery"))
        .or_insert_with(|| HeaderValue::from("true".to_string()));

    let options = build_operation_options(
        None,
        modifiers.excluded_regions_value,
        modifiers.driver_timeout_policy,
        modifiers.availability_strategy,
        custom_headers,
    );
    let mut responses = Vec::new();
    let result: Result<(), CosmosError> = async {
        let mut plan = driver
            .plan_operation(op, &options, None, &PlanOptions::default())
            .await?;
        while let Some(response) = driver
            .execute_plan(&mut plan, None, options.clone())
            .await?
        {
            responses.push(response);
        }
        Ok(())
    }
    .await;
    OfferReadResult {
        responses,
        error: result.err(),
    }
}

/// Build replace_throughput using the offer resource id and prepared replacement body.
/// Pass through custom headers, including any container-recreate guard. The
/// Rust driver handles signing and execution; this helper does not enforce the guard.
async fn run_replace_throughput_future(
    driver: Arc<CosmosDriver>,
    modifiers: RequestHeadersAndOptions,
    offer_id: String,
    body_bytes: Vec<u8>,
) -> Result<CosmosResponse, CosmosError> {
    let account = driver.account().clone();
    let mut op = CosmosOperation::replace_offer(account, offer_id).with_body(body_bytes);

    if let Some(activity) = modifiers.activity_header.as_ref() {
        op = op.with_activity_id(ActivityId::from(activity.clone()));
    }
    if let Some(session) = modifiers.session_header.as_ref() {
        op = op.with_session_token(SessionToken::from(session.clone()));
    }

    // Request response content because replace_throughput reads the returned
    // offer. Override the extracted no-response setting here; this option alone
    // does not guarantee that a service response contains a body.
    let content_response = Some(ContentResponseOnWrite::Enabled);
    let options = build_operation_options(
        content_response,
        modifiers.excluded_regions_value,
        modifiers.driver_timeout_policy,
        modifiers.availability_strategy,
        modifiers.custom_headers,
    );
    driver.execute_singleton_operation(op, options).await
}

#[cfg(test)]
mod tests {
    use super::*;
    use std::collections::HashMap;

    use azure_core::http::{StatusCode, Url};
    use azure_data_cosmos_driver::{
        fault_injection::{
            CustomResponse, CustomResponseBuilder, FaultInjectionResultBuilder, FaultInjectionRule,
            FaultInjectionRuleBuilder,
        },
        in_memory_emulator::{InMemoryEmulatorHttpClient, VirtualAccountConfig, VirtualRegion},
        models::AccountReference,
        options::DriverOptions,
    };
    use pyo3::types::PyBytes;

    fn page(
        status: StatusCode,
        body: &str,
        continuation: Option<&str>,
        charge: &str,
    ) -> CustomResponse {
        let mut response = CustomResponseBuilder::new(status)
            .with_header("x-ms-request-charge", charge.to_owned())
            .with_header("etag", format!("page-{charge}"))
            .with_body(body.as_bytes().to_vec());
        if let Some(token) = continuation {
            response = response.with_header("x-ms-continuation", token.to_owned());
        }
        response.build()
    }

    async fn setup(
        pages: Vec<CustomResponse>,
    ) -> (Arc<CosmosDriver>, Vec<Arc<FaultInjectionRule>>) {
        pyo3::prepare_freethreaded_python();
        let url = Url::parse("https://offers.emulator.local").unwrap();
        let emulator = Arc::new(InMemoryEmulatorHttpClient::new(
            VirtualAccountConfig::new(vec![VirtualRegion::new("East US", url.clone())]).unwrap(),
        ));
        let rules: Vec<_> = pages
            .into_iter()
            .enumerate()
            .map(|(index, response)| {
                let rule = Arc::new(
                    FaultInjectionRuleBuilder::new(
                        format!("offer-page-{index}"),
                        FaultInjectionResultBuilder::new()
                            .with_custom_response(response)
                            .build(),
                    )
                    .with_hit_limit(1)
                    .build(),
                );
                rule.disable();
                rule
            })
            .collect();
        let runtime = emulator
            .runtime_builder_with_fault_rules(rules.clone())
            .build()
            .await
            .unwrap();
        let driver = runtime
            .create_driver(
                DriverOptions::builder(AccountReference::with_account_key(url, "ZW11bGF0b3Ita2V5"))
                    .build(),
            )
            .await
            .unwrap();
        for rule in &rules {
            rule.enable();
        }
        (driver, rules)
    }

    fn modifiers() -> RequestHeadersAndOptions {
        RequestHeadersAndOptions {
            activity_header: None,
            session_header: None,
            content_response_on_write: ContentResponseOnWrite::Enabled,
            excluded_regions_value: None,
            driver_timeout_policy: None,
            operation_timeout: None,
            availability_strategy: None,
            read_consistency_strategy: None,
            patch_strategy: None,
            custom_headers: HashMap::new(),
        }
    }

    #[tokio::test]
    async fn drains_empty_and_nonempty_offer_pages_and_keeps_final_headers() {
        let (driver, rules) = setup(vec![
            page(StatusCode::Ok, r#"{"Offers":[]}"#, Some("second"), "1"),
            page(StatusCode::Ok, r#"{"Offers":[{"id":"a","content":{"offerThroughput":4000}}]}"#, Some("third"), "2"),
            page(StatusCode::Ok, r#"{"Offers":[{"id":"b","content":{"offerAutopilotSettings":{"maxThroughput":10000}}}]}"#, None, "3"),
        ]).await;
        let result = run_get_throughput_future(
            driver,
            modifiers(),
            br#"{"query":"SELECT * FROM c"}"#.to_vec(),
        )
        .await;
        assert!(rules.iter().all(|rule| rule.hit_count() == 1));
        Python::with_gil(|py| {
            let response = offer_read_tuple(py, result, false).unwrap();
            let bytes = response.get_item(3).unwrap();
            let body: serde_json::Value =
                serde_json::from_slice(bytes.downcast::<PyBytes>().unwrap().as_bytes()).unwrap();
            assert_eq!(body["Offers"].as_array().unwrap().len(), 2);
            assert_eq!(body["Offers"][0]["content"]["offerThroughput"], 4000);
            assert_eq!(
                body["Offers"][1]["content"]["offerAutopilotSettings"]["maxThroughput"],
                10000
            );
            let headers = response.get_item(2).unwrap();
            assert_eq!(
                headers
                    .get_item("etag")
                    .unwrap()
                    .extract::<String>()
                    .unwrap(),
                "page-3"
            );
            assert_eq!(
                headers
                    .get_item("x-ms-request-charge")
                    .unwrap()
                    .extract::<String>()
                    .unwrap(),
                "3"
            );
        });
    }

    #[tokio::test]
    async fn replacement_returns_manual_and_autoscale_content_with_attempts() {
        for body in [
            r#"{"id":"AAAAAA==","content":{"offerThroughput":500}}"#,
            r#"{"id":"AAAAAA==","content":{"offerAutopilotSettings":{"maxThroughput":10000}}}"#,
        ] {
            let (driver, rules) = setup(vec![page(StatusCode::Ok, body, None, "2")]).await;
            let result = run_replace_throughput_future(
                driver,
                modifiers(),
                "AAAAAA==".to_owned(),
                body.as_bytes().to_vec(),
            )
            .await;
            assert_eq!(rules[0].hit_count(), 1);
            Python::with_gil(|py| {
                let envelope = tuple_from_result_with_attempts(py, result).unwrap();
                let response = envelope.get_item(0).unwrap();
                assert_eq!(response.get_item(0).unwrap().extract::<u16>().unwrap(), 200);
                let bytes = response.get_item(3).unwrap();
                let actual: serde_json::Value =
                    serde_json::from_slice(bytes.downcast::<PyBytes>().unwrap().as_bytes())
                        .unwrap();
                assert_eq!(
                    actual,
                    serde_json::from_str::<serde_json::Value>(body).unwrap()
                );
                assert!(!envelope.get_item(1).unwrap().is_none());
            });
        }
    }

    #[tokio::test]
    async fn replacement_service_failure_keeps_status_and_headers() {
        let (driver, rules) = setup(vec![page(
            StatusCode::Forbidden,
            r#"{"code":"Forbidden","message":"denied"}"#,
            None,
            "2",
        )])
        .await;
        let result = run_replace_throughput_future(
            driver,
            modifiers(),
            "AAAAAA==".to_owned(),
            br#"{"id":"AAAAAA==","content":{"offerThroughput":500}}"#.to_vec(),
        )
        .await;
        assert!(result.is_err());
        assert_eq!(rules[0].hit_count(), 1);
        Python::with_gil(|py| {
            let envelope = tuple_from_result_with_attempts(py, result).unwrap();
            let response = envelope.get_item(0).unwrap();
            assert_eq!(response.get_item(0).unwrap().extract::<u16>().unwrap(), 403);
            assert_eq!(
                response
                    .get_item(2)
                    .unwrap()
                    .get_item("etag")
                    .unwrap()
                    .extract::<String>()
                    .unwrap(),
                "page-2",
            );
        });
    }

    #[tokio::test]
    async fn later_offer_failure_does_not_return_partial_success() {
        let (driver, rules) = setup(vec![
            page(
                StatusCode::Ok,
                r#"{"Offers":[{"id":"a"}]}"#,
                Some("second"),
                "1",
            ),
            page(
                StatusCode::Forbidden,
                r#"{"code":"Forbidden","message":"second page denied"}"#,
                None,
                "2",
            ),
        ])
        .await;
        let result = run_get_throughput_future(
            driver,
            modifiers(),
            br#"{"query":"SELECT * FROM c"}"#.to_vec(),
        )
        .await;
        assert!(result.error.is_some());
        assert!(rules.iter().all(|rule| rule.hit_count() == 1));
        Python::with_gil(|py| {
            let response = offer_read_tuple(py, result, false).unwrap();
            assert_eq!(response.get_item(0).unwrap().extract::<u16>().unwrap(), 403);
            assert_eq!(
                response
                    .get_item(2)
                    .unwrap()
                    .get_item("etag")
                    .unwrap()
                    .extract::<String>()
                    .unwrap(),
                "page-2"
            );
        });
    }

    #[tokio::test]
    async fn empty_final_offer_page_is_a_complete_empty_result() {
        let (driver, rules) =
            setup(vec![page(StatusCode::Ok, r#"{"Offers":[]}"#, None, "1")]).await;
        let result = run_get_throughput_future(
            driver,
            modifiers(),
            br#"{"query":"SELECT * FROM c"}"#.to_vec(),
        )
        .await;
        assert_eq!(rules[0].hit_count(), 1);
        Python::with_gil(|py| {
            let response = offer_read_tuple(py, result, false).unwrap();
            let bytes = response.get_item(3).unwrap();
            let body: serde_json::Value =
                serde_json::from_slice(bytes.downcast::<PyBytes>().unwrap().as_bytes()).unwrap();
            assert_eq!(body, serde_json::json!({"Offers":[]}));
        });
    }

    #[tokio::test]
    async fn malformed_later_offer_page_cannot_be_partial_success() {
        let (driver, _) = setup(vec![
            page(
                StatusCode::Ok,
                r#"{"Offers":[{"id":"a"}]}"#,
                Some("second"),
                "1",
            ),
            page(StatusCode::Ok, r#"{"Offers":"invalid"}"#, None, "2"),
        ])
        .await;
        let result = run_get_throughput_future(
            driver,
            modifiers(),
            br#"{"query":"SELECT * FROM c"}"#.to_vec(),
        )
        .await;
        Python::with_gil(|py| match result.into_result() {
            Err(_) => {}
            Ok(responses) => assert!(tuple_from_offer_feed_result(py, Ok(responses)).is_err()),
        });
    }

    #[tokio::test]
    async fn offer_attempts_include_completed_pages_before_success_or_failure() {
        for final_status in [StatusCode::Ok, StatusCode::Forbidden] {
            let (driver, rules) = setup(vec![
                page(StatusCode::Ok, r#"{"Offers":[]}"#, Some("second"), "1"),
                page(
                    final_status,
                    if final_status == StatusCode::Ok {
                        r#"{"Offers":[{"id":"a"}]}"#
                    } else {
                        r#"{"code":"Forbidden","message":"denied"}"#
                    },
                    None,
                    "2",
                ),
            ])
            .await;
            let result = run_get_throughput_future(
                driver,
                modifiers(),
                br#"{"query":"SELECT * FROM c"}"#.to_vec(),
            )
            .await;
            assert!(rules.iter().all(|rule| rule.hit_count() == 1));
            let sources: Vec<_> = result
                .responses
                .iter()
                .map(CosmosResponse::diagnostics)
                .chain(result.error.iter().filter_map(CosmosError::diagnostics))
                .collect();
            let total: usize = sources.iter().map(|source| source.request_count()).sum();
            assert!(total >= 2);
            Python::with_gil(|py| {
                let envelope = offer_read_tuple(py, result, true).unwrap();
                let response = envelope.get_item(0).unwrap();
                assert_eq!(
                    response.get_item(0).unwrap().extract::<u16>().unwrap(),
                    u16::from(final_status)
                );
                assert_eq!(
                    response
                        .get_item(2)
                        .unwrap()
                        .get_item("etag")
                        .unwrap()
                        .extract::<String>()
                        .unwrap(),
                    "page-2"
                );
                assert_eq!(
                    response
                        .get_item(2)
                        .unwrap()
                        .get_item("x-ms-request-charge")
                        .unwrap()
                        .extract::<String>()
                        .unwrap(),
                    "2"
                );
                let payload = envelope.get_item(1).unwrap();
                assert_eq!(
                    payload
                        .get_item("request_count")
                        .unwrap()
                        .extract::<usize>()
                        .unwrap(),
                    total
                );
                let attempts = payload.get_item("attempts").unwrap();
                assert_eq!(attempts.len().unwrap(), total);
                assert_eq!(
                    attempts
                        .get_item(total - 1)
                        .unwrap()
                        .get_item("driver_status_code")
                        .unwrap()
                        .extract::<u16>()
                        .unwrap(),
                    u16::from(final_status)
                );
            });
        }
    }

    #[tokio::test]
    async fn offer_error_without_final_diagnostics_retains_partial_attempts() {
        let (driver, _) = setup(vec![page(StatusCode::Ok, r#"{"Offers":[]}"#, None, "1")]).await;
        let mut result = run_get_throughput_future(
            driver,
            modifiers(),
            br#"{"query":"SELECT * FROM c"}"#.to_vec(),
        )
        .await;
        assert!(!result.responses.is_empty());
        result.error = Some(
            CosmosError::builder()
                .with_message("missing final diagnostics")
                .build(),
        );
        Python::with_gil(|py| {
            let error = offer_read_tuple(py, result, true).unwrap_err();
            assert!(error.is_instance_of::<super::super::errors::_DriverTransportError>(py));
            let payload = error
                .value_bound(py)
                .getattr("_cosmos_attempt_payload")
                .unwrap();
            assert!(!payload
                .get_item("complete")
                .unwrap()
                .extract::<bool>()
                .unwrap());
            assert!(
                payload
                    .get_item("request_count")
                    .unwrap()
                    .extract::<usize>()
                    .unwrap()
                    > 0
            );
        });
    }
}
