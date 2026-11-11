// Copyright (c) Microsoft Corporation. All rights reserved.
// Licensed under the MIT License.

use super::*;
use pyo3::ffi::c_str;
use std::sync::Barrier;

#[test]
fn state_is_lazy_and_reused_within_a_process() {
    let slot = ProcessStateSlot::new();
    let state = slot.get(1);
    assert!(state.runtime.get().is_none());
    assert!(state.transport.get().is_none());
    assert!(std::ptr::eq(state, slot.get(1)));
    assert!(std::ptr::eq(
        state.runtime().unwrap(),
        slot.get(1).runtime().unwrap()
    ));
    assert!(std::ptr::eq(state.transport(), slot.get(1).transport()));
    assert_eq!(
        state
            .runtime()
            .unwrap()
            .block_on(async { tokio::spawn(async { 42 }).await.unwrap() }),
        42
    );
}

#[test]
fn changed_pid_does_not_reuse_resources() {
    let slot = ProcessStateSlot::new();
    let parent = slot.get(1);
    let parent_runtime = parent.runtime().unwrap();
    let parent_transport = parent.transport();
    let child = slot.get(2);
    assert_eq!(child.pid, 2);
    assert!(!std::ptr::eq(parent, child));
    assert!(child.runtime.get().is_none());
    assert!(child.transport.get().is_none());
    assert!(!std::ptr::eq(parent_runtime, child.runtime().unwrap()));
    assert!(!std::ptr::eq(parent_transport, child.transport()));
    assert!(std::ptr::eq(child, slot.get(2)));
}

#[test]
fn concurrent_callers_publish_one_state() {
    let slot = ProcessStateSlot::new();
    let barrier = Barrier::new(8);
    std::thread::scope(|scope| {
        let handles: Vec<_> = (0..8)
            .map(|_| {
                scope.spawn(|| {
                    barrier.wait();
                    slot.get(1) as *const ProcessState as usize
                })
            })
            .collect();
        let states: Vec<_> = handles
            .into_iter()
            .map(|task| task.join().unwrap())
            .collect();
        assert!(states.iter().all(|state| *state == states[0]));
    });
}

#[test]
fn child_does_not_wait_for_parent_initialization() {
    let slot = ProcessStateSlot::new();
    let parent = slot.get(1);
    let initializing = Barrier::new(2);
    let release = Barrier::new(2);
    std::thread::scope(|scope| {
        let worker = scope.spawn(|| {
            parent.runtime.get_or_init(|| {
                initializing.wait();
                release.wait();
                Runtime::new().unwrap()
            });
        });
        initializing.wait();
        let child = slot.get(2);
        let fresh = child.runtime.get().is_none() && child.transport.get().is_none();
        release.wait();
        worker.join().unwrap();
        assert!(fresh);
        assert!(!std::ptr::eq(parent, child));
    });
}

#[test]
fn credentials_and_tokens_are_isolated_even_with_the_same_id() {
    Python::initialize();
    Python::attach(|py| {
        let module = PyModule::from_code(
            py,
            c_str!(
                "def parent(scopes):\n return ('parent-token', 4102444800)\n\
                 def child(scopes):\n return ('child-token', 4102444800)\n"
            ),
            c_str!("process_credentials.py"),
            c_str!("process_credentials"),
        )
        .unwrap();
        let slot = ProcessStateSlot::new();
        let parent = slot
            .get(1)
            .credentials
            .get(module.getattr("parent").unwrap().unbind(), 7);
        let runtime = get_runtime().unwrap();
        let token = runtime
            .block_on(parent.get_token(&["scope"], None))
            .unwrap();
        assert_eq!(token.token.secret(), "parent-token");
        let child = slot
            .get(2)
            .credentials
            .get(module.getattr("child").unwrap().unbind(), 7);
        assert!(!Arc::ptr_eq(&parent, &child));
        let token = runtime.block_on(child.get_token(&["scope"], None)).unwrap();
        assert_eq!(token.token.secret(), "child-token");
        let token = runtime
            .block_on(parent.get_token(&["scope"], None))
            .unwrap();
        assert_eq!(token.token.secret(), "parent-token");
    });
}
