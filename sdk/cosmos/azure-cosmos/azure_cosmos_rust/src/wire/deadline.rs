// Copyright (c) Microsoft Corporation. All rights reserved.
// Licensed under the MIT License.

//! Keep the supplied remaining timeout across waiting and execution.
//!
//! If an order read has 50 ms left and spends 30 ms waiting to start, its future
//! has a deadline 20 ms away, not another 50 ms. A timeout cannot forcibly stop
//! synchronous work or undo work already sent to the service backend.

use std::{future::Future, time::Duration};

use pyo3::{
    exceptions::{PyTimeoutError, PyValueError},
    PyResult,
};
use tokio::time::error::Elapsed;

/// Accept no timeout or a positive finite duration the platform clock can represent.
pub(crate) fn parse_remaining_timeout(seconds: Option<f64>) -> PyResult<Option<Duration>> {
    seconds
        .map(|seconds| {
            let duration = Duration::try_from_secs_f64(seconds).map_err(|_| {
                PyValueError::new_err("timeout_seconds must be finite and positive")
            })?;
            if duration.is_zero() {
                return Err(PyValueError::new_err("timeout_seconds must be positive"));
            }
            if std::time::Instant::now().checked_add(duration).is_none() {
                return Err(PyValueError::new_err(
                    "timeout_seconds exceeds the platform clock range",
                ));
            }
            Ok(duration)
        })
        .transpose()
}

/// Record the deadline now, rather than when the returned future is first polled.
/// If waiting to start uses all remaining time, do not poll the operation at all.
pub(super) fn with_timeout<T>(
    timeout: Option<Duration>,
    operation: impl Future<Output = T>,
) -> impl Future<Output = Result<T, Elapsed>> {
    let deadline = timeout.map(|duration| tokio::time::Instant::now() + duration);
    async move {
        match deadline {
            Some(deadline) if deadline <= tokio::time::Instant::now() => {
                tokio::time::timeout_at(deadline, std::future::pending()).await
            }
            Some(deadline) => tokio::time::timeout_at(deadline, operation).await,
            None => Ok(operation.await),
        }
    }
}

pub(super) fn with_operation_timeout<T>(
    timeout: Option<Duration>,
    operation: impl Future<Output = T>,
) -> impl Future<Output = PyResult<T>> {
    let timed = with_timeout(timeout, operation);
    async move {
        timed.await.map_err(|error| {
            PyTimeoutError::new_err(format!(
                "Item operation timed out during metadata resolution or execution: {error}"
            ))
        })
    }
}

pub(super) fn with_page_timeout<T>(
    timeout: Option<Duration>,
    operation: impl Future<Output = T>,
) -> impl Future<Output = PyResult<T>> {
    let timed = with_timeout(timeout, operation);
    async move {
        timed
            .await
            .map_err(|error| PyTimeoutError::new_err(format!("Page operation timed out: {error}")))
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    use std::sync::{
        atomic::{AtomicBool, Ordering},
        Arc,
    };

    struct Dropped(Arc<AtomicBool>);
    impl Drop for Dropped {
        fn drop(&mut self) {
            self.0.store(true, Ordering::SeqCst);
        }
    }

    #[tokio::test(start_paused = true)]
    async fn one_subsecond_budget_cancels_lookup_and_read_together() {
        let dropped = Arc::new(AtomicBool::new(false));
        let read_started = Arc::new(AtomicBool::new(false));
        let future = {
            let dropped = dropped.clone();
            let read_started = read_started.clone();
            async move {
                let _guard = Dropped(dropped);
                tokio::time::sleep(Duration::from_millis(30)).await;
                read_started.store(true, Ordering::SeqCst);
                tokio::time::sleep(Duration::from_millis(40)).await;
            }
        };
        assert!(with_timeout(Some(Duration::from_millis(50)), future)
            .await
            .is_err());
        assert!(read_started.load(Ordering::SeqCst));
        assert!(dropped.load(Ordering::SeqCst));
    }

    #[tokio::test(start_paused = true)]
    async fn expired_lookup_does_not_start_read() {
        let read_started = AtomicBool::new(false);
        let future = async {
            std::future::pending::<()>().await;
            read_started.store(true, Ordering::SeqCst);
        };
        assert!(with_timeout(Some(Duration::from_millis(1)), future)
            .await
            .is_err());
        assert!(!read_started.load(Ordering::SeqCst));
    }

    #[tokio::test(start_paused = true)]
    async fn scheduling_delay_does_not_restart_budget_or_poll_work() {
        let called = AtomicBool::new(false);
        let timed = with_timeout(Some(Duration::from_millis(1)), async {
            called.store(true, Ordering::SeqCst);
        });
        tokio::time::advance(Duration::from_millis(2)).await;
        assert!(timed.await.is_err());
        assert!(!called.load(Ordering::SeqCst));
    }

    #[tokio::test]
    async fn successful_results_and_service_errors_are_not_rewritten() {
        assert_eq!(
            with_timeout(None, async { Ok::<_, u16>(304) })
                .await
                .unwrap(),
            Ok(304)
        );
        assert_eq!(
            with_timeout(Some(Duration::from_secs(1)), async { Err::<u16, _>(412) })
                .await
                .unwrap(),
            Err(412)
        );
    }

    #[test]
    fn remaining_duration_is_not_rounded_to_the_driver_minimum() {
        assert_eq!(
            parse_remaining_timeout(Some(0.125)).unwrap(),
            Some(Duration::from_millis(125))
        );
    }

    #[tokio::test(start_paused = true)]
    async fn page_deadline_returns_python_timeout_and_drops_pending_work() {
        pyo3::prepare_freethreaded_python();
        let dropped = Arc::new(AtomicBool::new(false));
        let guard = Dropped(dropped.clone());
        let error = with_page_timeout(Some(Duration::from_millis(5)), async move {
            let _guard = guard;
            std::future::pending::<()>().await;
        })
        .await
        .unwrap_err();
        assert!(dropped.load(Ordering::SeqCst));
        pyo3::Python::with_gil(|py| assert!(error.is_instance_of::<PyTimeoutError>(py)));
    }
}
