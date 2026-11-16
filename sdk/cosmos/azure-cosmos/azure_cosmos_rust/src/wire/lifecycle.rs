// Copyright (c) Microsoft Corporation. All rights reserved.
// Licensed under the MIT License.

//! Opt-in, per-call evidence that an async item future was dropped.
//! This does not observe detached driver tasks, sockets, or service rollback.

use std::future::Future;
use std::pin::Pin;
use std::sync::atomic::{AtomicU8, Ordering};
use std::sync::Arc;
use std::task::{Context, Poll};

use pyo3::exceptions::PyValueError;
use pyo3::prelude::*;

const CREATED: u8 = 0;
const SCHEDULED: u8 = 1;
const RUNNING: u8 = 2;
const COMPLETED: u8 = 3;
const DROPPED: u8 = 4;

/// Single-use internal test probe; no process-global registry or retained history.
#[pyclass(name = "_AsyncOperationProbe", frozen)]
pub(crate) struct AsyncOperationProbe {
    pub(crate) state: Arc<AtomicU8>,
}

#[pymethods]
impl AsyncOperationProbe {
    #[new]
    fn new() -> Self {
        Self {
            state: Arc::new(AtomicU8::new(CREATED)),
        }
    }

    #[getter]
    fn status(&self) -> &'static str {
        match self.state.load(Ordering::Acquire) {
            CREATED => "created",
            SCHEDULED => "scheduled",
            RUNNING => "running",
            COMPLETED => "completed",
            DROPPED => "dropped",
            _ => unreachable!("invalid operation probe state"),
        }
    }
}

pub(super) enum LifecycleFuture<F: Future> {
    Plain(F),
    Observed(ObservedFuture<F>),
}

impl<F: Future> LifecycleFuture<F> {
    pub(super) fn new(future: F, state: Option<Arc<AtomicU8>>) -> PyResult<Self> {
        match state {
            None => Ok(Self::Plain(future)),
            Some(state) => {
                state
                    .compare_exchange(CREATED, SCHEDULED, Ordering::AcqRel, Ordering::Acquire)
                    .map_err(|_| {
                        PyValueError::new_err("An async operation probe can only be used once")
                    })?;
                Ok(Self::Observed(ObservedFuture {
                    future: Some(Box::pin(future)),
                    state,
                    completed: false,
                }))
            }
        }
    }

    pub(super) async fn run(self) -> F::Output {
        match self {
            Self::Plain(future) => future.await,
            Self::Observed(future) => future.await,
        }
    }
}

pub(super) struct ObservedFuture<F: Future> {
    future: Option<Pin<Box<F>>>,
    state: Arc<AtomicU8>,
    completed: bool,
}

impl<F: Future> Future for ObservedFuture<F> {
    type Output = F::Output;

    fn poll(mut self: Pin<&mut Self>, cx: &mut Context<'_>) -> Poll<Self::Output> {
        self.state.store(RUNNING, Ordering::Release);
        let result = self
            .future
            .as_mut()
            .expect("future exists until drop")
            .as_mut()
            .poll(cx);
        self.completed = result.is_ready();
        result
    }
}

impl<F: Future> Drop for ObservedFuture<F> {
    fn drop(&mut self) {
        // Publish only AFTER the real operation future and its owned state drop.
        drop(self.future.take());
        self.state.store(
            if self.completed { COMPLETED } else { DROPPED },
            Ordering::Release,
        );
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    use std::sync::atomic::AtomicBool;

    struct PendingUntilDropped(Arc<AtomicBool>);
    impl Future for PendingUntilDropped {
        type Output = ();
        fn poll(self: Pin<&mut Self>, _: &mut Context<'_>) -> Poll<()> {
            Poll::Pending
        }
    }
    impl Drop for PendingUntilDropped {
        fn drop(&mut self) {
            self.0.store(true, Ordering::Release);
        }
    }

    #[tokio::test]
    async fn cancellation_publishes_only_after_inner_future_drops() {
        let probe = AsyncOperationProbe::new();
        let inner_dropped = Arc::new(AtomicBool::new(false));
        let future = LifecycleFuture::new(
            PendingUntilDropped(inner_dropped.clone()),
            Some(probe.state.clone()),
        )
        .unwrap();
        let task = tokio::spawn(future.run());
        tokio::task::yield_now().await;
        assert_eq!(probe.status(), "running");
        task.abort();
        assert!(task.await.unwrap_err().is_cancelled());
        assert_eq!(probe.status(), "dropped");
        assert!(inner_dropped.load(Ordering::Acquire));
    }

    #[tokio::test]
    async fn probes_distinguish_completion_and_are_operation_scoped() {
        let first = AsyncOperationProbe::new();
        let second = AsyncOperationProbe::new();
        let future =
            LifecycleFuture::new(std::future::ready(7), Some(first.state.clone())).unwrap();
        assert_eq!(future.run().await, 7);
        assert_eq!(first.status(), "completed");
        assert_eq!(second.status(), "created");
        assert!(LifecycleFuture::new(std::future::ready(0), Some(first.state.clone())).is_err());
    }

    #[test]
    fn dropping_before_poll_still_observes_inner_destruction() {
        let probe = AsyncOperationProbe::new();
        let inner_dropped = Arc::new(AtomicBool::new(false));
        let future = LifecycleFuture::new(
            PendingUntilDropped(inner_dropped.clone()),
            Some(probe.state.clone()),
        )
        .unwrap();
        assert_eq!(probe.status(), "scheduled");
        drop(future.run());
        assert_eq!(probe.status(), "dropped");
        assert!(inner_dropped.load(Ordering::Acquire));
    }
}
