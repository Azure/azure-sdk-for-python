# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.
import copy
from concurrent.futures import ThreadPoolExecutor
import socket
import threading
import time

import pytest

from fault_injection._tcp_observer import (
    TcpObserver,
    assert_cutoff_connection,
    assert_persistent_cutoffs,
    assert_reset_connection,
    assert_response_exchange,
    forwarding_progress,
    warmed_connection,
)


def connection(events=None, accepted=1, closed=None):
    return {
        "peer": "127.0.0.1:12345",
        "accepted_at": accepted,
        "closed_at": closed,
        "end_reason": None,
        "events": [] if events is None else events,
    }


def traffic(at=2):
    return [
        {"direction": "upstream", "bytes": 100, "at": at},
        {"direction": "downstream", "bytes": 200, "at": at + 0.01},
    ]


def test_isolates_warm_read_and_later_reconnection_rust():
    before = {"1": connection()}
    warm = {"1": connection(traffic())}
    assert warmed_connection(before, warm) == "1"
    after = {
        "1": connection(traffic() + traffic(3), closed=5.9),
        "2": connection(accepted=5.95),
    }
    result = assert_response_exchange(warm, after, "1", 3, 6)
    assert result["request_bytes"] == 100
    assert result["response_bytes"] == 200
    assert result["first_response_after_start"] == pytest.approx(0.01)
    assert result["reconnects_after_start"] == pytest.approx([2.95])


@pytest.mark.parametrize(
    "after",
    [
        {"1": connection()},
        {"2": connection(traffic(), accepted=2)},
        {"1": connection(traffic(), closed=2.1)},
        {"1": connection(traffic()), "2": connection(traffic())},
        {"1": connection(traffic()[:1])},
    ],
)
def test_rejects_missing_unwarmed_or_ambiguous_warm_connection_rust(after):
    with pytest.raises(AssertionError):
        warmed_connection({"1": connection()}, after)


@pytest.mark.parametrize(
    "events",
    [
        [],
        traffic()[:1],
        traffic()[1:],
        traffic(0),
        traffic(5),
        list(
            reversed(
                [
                    {"direction": "upstream", "bytes": 100, "at": 2.1},
                    {"direction": "downstream", "bytes": 200, "at": 2},
                ]
            )
        ),
        [{"direction": "upstream", "bytes": 0, "at": 2}] + traffic()[1:],
    ],
)
def test_rejects_missing_response_wrong_order_or_outside_window_rust(events):
    with pytest.raises(AssertionError):
        assert_response_exchange({"1": connection()}, {"1": connection(events)}, "1", 2, 3)


def test_rejects_new_connection_as_only_fault_traffic_rust():
    before = {"1": connection(traffic())}
    after = copy.deepcopy(before)
    after["2"] = connection(traffic(3), accepted=3)
    with pytest.raises(AssertionError, match="No traffic"):
        assert_response_exchange(before, after, "1", 3, 6)


def test_rejects_reconnect_before_original_response_rust():
    before = {"1": connection()}
    after = {"1": connection(traffic(3)), "2": connection(accepted=3)}
    with pytest.raises(AssertionError, match="before response"):
        assert_response_exchange(before, after, "1", 3, 6)


def test_rejects_changed_connection_history_rust():
    before = {"1": connection(traffic())}
    after = {"1": connection(traffic(3))}
    with pytest.raises(AssertionError, match="history"):
        assert_response_exchange(before, after, "1", 3, 6)


def wait_for_events(observer, count):
    deadline = time.monotonic() + 2
    while True:
        snapshot = observer.snapshot()
        if sum(len(value["events"]) for value in snapshot.values()) >= count:
            return snapshot
        assert time.monotonic() < deadline, "Observer did not record forwarded traffic"
        time.sleep(0.01)


def test_observer_forwards_counts_separate_connections_and_stops_rust():
    with socket.socket() as server:
        server.bind(("127.0.0.1", 0))
        server.listen()
        server.settimeout(2)
        observer = TcpObserver(server.getsockname()[1])
        try:
            observer.start()
            for index in range(2):
                with socket.create_connection(("127.0.0.1", observer.port), timeout=2) as client:
                    upstream, _ = server.accept()
                    with upstream:
                        upstream.settimeout(2)
                        client.sendall(b"request")
                        assert upstream.recv(7) == b"request"
                        upstream.sendall(b"response")
                        assert client.recv(8) == b"response"
                        snapshot = wait_for_events(observer, (index + 1) * 2)
                        events = snapshot[str(index + 1)]["events"]
                        assert [(event["direction"], event["bytes"]) for event in events] == [
                            ("upstream", 7),
                            ("downstream", 8),
                        ]
                        assert all(set(event) == {"direction", "bytes", "at"} for event in events)
            assert len(observer.snapshot()) == 2
        finally:
            observer.close()
        assert not observer.thread.is_alive()
        assert all(not worker.is_alive() for worker in observer.workers)
        with socket.socket() as probe:
            probe.settimeout(1)
            assert probe.connect_ex(("127.0.0.1", observer.port)) != 0


def test_observer_failure_is_not_silently_accepted_rust():
    observer = TcpObserver(8081)
    observer.errors.append("controlled observation failure")
    with pytest.raises(AssertionError, match="observation failure"):
        observer.snapshot()
    with pytest.raises(AssertionError, match="observation failure"):
        observer.close()


def test_snapshot_waits_for_delivered_bytes_to_be_recorded_rust(monkeypatch):
    delivered, release, waiting = threading.Event(), threading.Event(), threading.Event()
    sendall = socket.socket.sendall

    def delayed_send(connection, payload, *args, **kwargs):
        result = sendall(connection, payload, *args, **kwargs)
        if threading.current_thread().name.startswith("cosmos-byte-observer-") and payload == b"response":
            delivered.set()
            assert release.wait(5)
        return result

    with socket.socket() as server:
        server.bind(("127.0.0.1", 0))
        server.listen()
        server.settimeout(2)
        observer = TcpObserver(server.getsockname()[1])
        wait = observer.changed.wait

        def observe_wait(timeout=None):
            waiting.set()
            return wait(timeout)

        monkeypatch.setattr(socket.socket, "sendall", delayed_send)
        monkeypatch.setattr(observer.changed, "wait", observe_wait)
        try:
            observer.start()
            with socket.create_connection(("127.0.0.1", observer.port), timeout=2) as client:
                upstream, _ = server.accept()
                with upstream, ThreadPoolExecutor(max_workers=1) as executor:
                    upstream.sendall(b"response")
                    assert client.recv(8) == b"response" and delivered.wait(2)
                    future = executor.submit(observer.snapshot)
                    try:
                        assert waiting.wait(2) and not future.done()
                    finally:
                        release.set()
                    observed = future.result(timeout=2)
                    assert observed["1"]["events"] == [
                        {"direction": "downstream", "bytes": 8, "at": observed["1"]["events"][0]["at"]}
                    ]
        finally:
            release.set()
            observer.close()


def test_snapshot_wait_is_bounded_rust(monkeypatch):
    observer = TcpObserver(8081)
    wait_for = observer.changed.wait_for
    monkeypatch.setattr(observer.changed, "wait_for", lambda predicate, timeout: wait_for(predicate, 0.01))
    observer.forwarding.add("unfinished")
    try:
        with pytest.raises(TimeoutError, match="recording"):
            observer.snapshot()
    finally:
        observer.forwarding.clear()
        observer.close()


def test_callback_teardown_waits_for_active_call_and_rejects_new_calls_rust(monkeypatch):
    entered, release, registered, finish, waiting = (threading.Event() for _ in range(5))
    calls = []
    with socket.socket() as server:
        server.bind(("127.0.0.1", 0))
        server.listen()
        server.settimeout(2)
        observer = TcpObserver(server.getsockname()[1])
        wait = observer.changed.wait

        def observe_wait(timeout=None):
            waiting.set()
            return wait(timeout)

        def callback(identity, direction):
            calls.append((identity, direction))
            observer.snapshot()
            entered.set()
            assert release.wait(5)

        def registration():
            with observer.forwarding_callback(callback):
                registered.set()
                assert finish.wait(5)

        monkeypatch.setattr(observer.changed, "wait", observe_wait)
        try:
            observer.start()
            with ThreadPoolExecutor(max_workers=1) as executor:
                future = executor.submit(registration)
                try:
                    assert registered.wait(2)
                    with socket.create_connection(("127.0.0.1", observer.port), timeout=2) as client:
                        upstream, _ = server.accept()
                        with upstream:
                            upstream.settimeout(2)
                            client.sendall(b"first")
                            assert entered.wait(2)
                            finish.set()
                            assert waiting.wait(2) and not future.done()
                            with socket.create_connection(("127.0.0.1", observer.port), timeout=2) as second:
                                other, _ = server.accept()
                                with other:
                                    other.settimeout(2)
                                    second.sendall(b"later")
                                    assert other.recv(5) == b"later"
                            release.set()
                            future.result(timeout=2)
                            assert upstream.recv(5) == b"first"
                    assert calls == [("1", "upstream")]
                finally:
                    release.set()
                    finish.set()
        finally:
            release.set()
            observer.close()


def test_callback_failure_remains_visible_without_unhandled_thread_error_rust():
    with socket.socket() as server:
        server.bind(("127.0.0.1", 0))
        server.listen()
        server.settimeout(2)
        observer = TcpObserver(server.getsockname()[1])

        def fail(identity, direction):
            raise ValueError("deliberate callback failure")

        try:
            observer.start()
            with observer.forwarding_callback(fail):
                with socket.create_connection(("127.0.0.1", observer.port), timeout=2) as client:
                    upstream, _ = server.accept()
                    with upstream:
                        client.sendall(b"request")
                        for worker in observer.workers:
                            worker.join(timeout=2)
                            assert not worker.is_alive()
                with pytest.raises(AssertionError, match="deliberate callback failure"):
                    observer.snapshot()
                assert observer.connections["1"]["events"] == []
                assert observer.connections["1"]["end_reason"] == "forwarding_callback_error"
        finally:
            with pytest.raises(AssertionError, match="deliberate callback failure"):
                observer.close()


def test_failed_send_does_not_publish_bytes_rust(monkeypatch):
    sendall = socket.socket.sendall

    def failed_send(connection, payload, *args, **kwargs):
        if threading.current_thread().name.startswith("cosmos-byte-observer-"):
            raise OSError("deliberate send failure")
        return sendall(connection, payload, *args, **kwargs)

    with socket.socket() as server:
        server.bind(("127.0.0.1", 0))
        server.listen()
        server.settimeout(2)
        observer = TcpObserver(server.getsockname()[1])
        monkeypatch.setattr(socket.socket, "sendall", failed_send)
        try:
            observer.start()
            with socket.create_connection(("127.0.0.1", observer.port), timeout=2) as client:
                upstream, _ = server.accept()
                with upstream:
                    client.sendall(b"request")
                    for worker in observer.workers:
                        worker.join(timeout=2)
                        assert not worker.is_alive()
            assert observer.connections["1"]["events"] == [] and not observer.forwarding
            with pytest.raises(AssertionError, match="deliberate send failure"):
                observer.snapshot()
        finally:
            with pytest.raises(AssertionError, match="deliberate send failure"):
                observer.close()


def reset_connection():
    return dict(
        connection(traffic(), closed=2.1),
        end_reason="ConnectionResetError",
        end_direction="upstream",
        end_operation="recv",
    )


def test_reset_evidence_requires_observed_reset_on_warmed_connection_rust():
    result = assert_reset_connection({"1": connection()}, {"1": reset_connection()}, "1", 2, 3)
    assert result["reset_after_start"] == pytest.approx(0.1)
    assert result["request_bytes"] == 100 and result["response_bytes"] == 200


@pytest.mark.parametrize(
    "change",
    [
        {"end_reason": "upstream_eof"},
        {"end_reason": "ConnectionAbortedError"},
        {"end_direction": "downstream"},
        {"end_operation": "send"},
        {"closed_at": 4},
        {"events": traffic()[:1]},
        {"events": traffic(1)},
    ],
)
def test_reset_evidence_rejects_orderly_close_or_wrong_connection_failure_rust(change):
    with pytest.raises(AssertionError):
        assert_reset_connection({"1": connection()}, {"1": dict(reset_connection(), **change)}, "1", 2, 3)


def test_observer_holds_new_connections_until_fault_is_removed_rust():
    with socket.socket() as server:
        server.bind(("127.0.0.1", 0))
        server.listen()
        server.settimeout(0.05)
        observer = TcpObserver(server.getsockname()[1])
        try:
            observer.start()
            observer.new_connections.clear()
            with socket.create_connection(("127.0.0.1", observer.port), timeout=2) as client:
                client.sendall(b"request")
                with pytest.raises(socket.timeout):
                    server.accept()
                released = time.monotonic()
                observer.new_connections.set()
                server.settimeout(2)
                upstream, _ = server.accept()
                with upstream:
                    upstream.settimeout(2)
                    assert upstream.recv(7) == b"request"
                observed = wait_for_events(observer, 1)
                assert observed["1"]["forwarding_started_at"] >= released
        finally:
            observer.close()


def test_forwarding_progress_records_deliveries_on_selected_connection_rust():
    events = traffic() + [{"direction": "downstream", "bytes": 1600, "at": at} for at in (2.11, 2.21, 2.31)]
    progress = forwarding_progress({"1": connection()}, {"1": connection(events)}, "1", 2, 3)
    assert progress["response_events"] == 4
    assert progress["response_bytes"] == 5000
    assert progress["forwarding_span"] == pytest.approx(0.3)
    assert progress["largest_response_gap"] == pytest.approx(0.1)
    assert progress["last_response_after_start"] == pytest.approx(0.31)


def test_forwarding_progress_rejects_reordered_response_events_rust():
    events = traffic() + [
        {"direction": "downstream", "bytes": 100, "at": 2.2},
        {"direction": "downstream", "bytes": 100, "at": 2.1},
    ]
    with pytest.raises(AssertionError, match="out of order"):
        forwarding_progress({"1": connection()}, {"1": connection(events)}, "1", 2, 3)


def test_two_observers_forward_through_both_legs_without_retaining_payloads_rust():
    with socket.socket() as server:
        server.bind(("127.0.0.1", 0))
        server.listen()
        server.settimeout(2)
        upstream_observer = TcpObserver(server.getsockname()[1])
        sdk_observer = None
        try:
            upstream_observer.start()
            sdk_observer = TcpObserver(upstream_observer.port)
            sdk_observer.start()
            with socket.create_connection(("127.0.0.1", sdk_observer.port), timeout=2) as client:
                upstream, _ = server.accept()
                with upstream:
                    upstream.settimeout(2)
                    client.sendall(b"request")
                    assert upstream.recv(7) == b"request"
                    for value in (b"first", b"later", b"final"):
                        upstream.sendall(value)
                        assert client.recv(len(value)) == value
                    for observer in (sdk_observer, upstream_observer):
                        events = wait_for_events(observer, 4)["1"]["events"]
                        assert sum(event["bytes"] for event in events if event["direction"] == "downstream") == 15
                        assert all(set(event) == {"direction", "bytes", "at"} for event in events)
        finally:
            try:
                if sdk_observer is not None:
                    sdk_observer.close()
            finally:
                upstream_observer.close()


def cutoff_connection():
    events = traffic()
    events[1]["bytes"] = 20000
    return dict(
        connection(events, closed=2.02),
        end_reason="downstream_eof",
        end_direction="downstream",
        end_operation="recv",
    )


def test_cutoff_requires_exact_partial_bytes_then_observed_close_rust():
    evidence = assert_cutoff_connection({"1": connection()}, {"1": cutoff_connection()}, "1", 2, 3, 20000, 64000)
    assert evidence["response_bytes"] == 20000
    assert evidence["closed_after_start"] == pytest.approx(0.02)


@pytest.mark.parametrize(
    "change",
    [
        {"end_reason": "ConnectionResetError"},
        {"end_reason": "upstream_eof"},
        {"end_direction": "upstream"},
        {"end_operation": "send"},
        {"closed_at": None},
        {"closed_at": 4},
        {"closed_at": 2.005},
        {"events": traffic()[:1]},
        {"events": traffic()},
        {
            "events": [
                traffic()[0],
                {"direction": "downstream", "bytes": 20001, "at": 2.01},
            ]
        },
    ],
)
def test_cutoff_rejects_wrong_close_missing_data_or_wrong_byte_count_rust(change):
    with pytest.raises(AssertionError):
        assert_cutoff_connection(
            {"1": connection()},
            {"1": dict(cutoff_connection(), **change)},
            "1",
            2,
            3,
            20000,
            64000,
        )


@pytest.mark.parametrize("baseline,cutoff", [(20000, 20000), (10000, 20000), (64000, 0)])
def test_cutoff_rejects_complete_or_empty_transfer_rust(baseline, cutoff):
    with pytest.raises(AssertionError):
        assert_cutoff_connection({"1": connection()}, {"1": cutoff_connection()}, "1", 2, 3, cutoff, baseline)


def persistent_connections():
    replacement = cutoff_connection()
    replacement.update(accepted_at=2.1, forwarding_started_at=2.11, closed_at=2.3)
    replacement["events"] = [
        {"direction": "upstream", "bytes": 100, "at": 2.12},
        {"direction": "downstream", "bytes": 20000, "at": 2.2},
    ]
    return {"1": cutoff_connection(), "2": replacement}


def test_persistent_cutoff_requires_warmed_and_replacement_failures_rust():
    result = assert_persistent_cutoffs({"1": connection()}, persistent_connections(), "1", 2, 3, 20000, 64000)
    assert result["first"]["response_bytes"] == 20000
    assert result["replacement_cutoffs"][0]["connection"] == "2"


@pytest.mark.parametrize(
    "change",
    [
        {"forwarding_started_at": None},
        {"forwarding_started_at": 4},
        {"closed_at": None},
        {"closed_at": 4},
        {"closed_at": 2.15},
        {"end_reason": "ConnectionResetError"},
        {"end_direction": "upstream"},
        {"end_operation": "send"},
        {"events": traffic(2.12)},
        {"events": [{"direction": "downstream", "bytes": 20001, "at": 2.2}]},
        {"events": [{"direction": "downstream", "bytes": 20000, "at": 2.2}]},
    ],
)
def test_persistent_cutoff_rejects_gated_or_unproven_replacement_rust(change):
    after = persistent_connections()
    after["2"].update(change)
    with pytest.raises(AssertionError):
        assert_persistent_cutoffs({"1": connection()}, after, "1", 2, 3, 20000, 64000)


def test_persistent_cutoff_rejects_only_one_interruption_rust():
    with pytest.raises(AssertionError, match="No replacement"):
        assert_persistent_cutoffs({"1": connection()}, {"1": cutoff_connection()}, "1", 2, 3, 20000, 64000)
