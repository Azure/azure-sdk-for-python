# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.
"""Loopback-only byte observation; never decrypt or retain network payloads."""

import copy
from contextlib import contextmanager
import select
import socket
import threading
import time


class TcpObserver:
    def __init__(self, upstream_port):
        self.upstream = ("127.0.0.1", upstream_port)
        self.listener = None
        self.thread = None
        self.workers = []
        self.stop = threading.Event()
        self.lock = threading.Lock()
        self.changed = threading.Condition(self.lock)
        self.forwarding = set()
        self.connections = {}
        self.errors = []
        self.new_connections = threading.Event()
        self.new_connections.set()
        self._callback = None
        self._callbacks_running = 0

    @contextmanager
    def forwarding_callback(self, callback):
        """Unregister before waiting for callbacks already running outside the lock."""
        with self.changed:
            assert self._callback is None and self._callbacks_running == 0
            self._callback = callback
        try:
            yield
        finally:
            with self.changed:
                self._callback = None
                if not self.changed.wait_for(lambda: self._callbacks_running == 0, timeout=5):
                    raise TimeoutError("Observer forwarding callback did not stop")

    def start(self):
        self.listener = socket.socket()
        self.listener.bind(("127.0.0.1", 0))
        self.listener.listen()
        self.listener.settimeout(0.1)
        self.port = self.listener.getsockname()[1]
        self.thread = threading.Thread(target=self._accept, name="cosmos-byte-observer")
        self.thread.start()
        return self

    def _accept(self):
        try:
            while not self.stop.is_set():
                try:
                    client, peer = self.listener.accept()
                except socket.timeout:
                    continue
                with self.lock:
                    identity = str(len(self.connections) + 1)
                    self.connections[identity] = {
                        "peer": f"{peer[0]}:{peer[1]}",
                        "accepted_at": time.monotonic(),
                        "closed_at": None,
                        "end_reason": None,
                        "end_direction": None,
                        "end_operation": None,
                        "forwarding_started_at": None,
                        "events": [],
                    }
                worker = threading.Thread(
                    target=self._forward,
                    args=(identity, client),
                    name="cosmos-byte-observer-" + identity,
                )
                self.workers.append(worker)
                worker.start()
        except OSError as error:
            with self.lock:
                self.errors.append(f"accept: {type(error).__name__}: {error}")

    def _forward(self, identity, client):
        upstream = None
        reason = "observer_stopped"
        direction, operation = None, "connect"
        try:
            assert self.new_connections.wait(timeout=3), "Replacement connection was not released"
            client.settimeout(2)
            upstream = socket.create_connection(self.upstream, timeout=2)
            with self.lock:
                self.connections[identity]["forwarding_started_at"] = time.monotonic()
            while not self.stop.is_set():
                readable, _, _ = select.select([client, upstream], [], [], 0.1)
                for source in readable:
                    destination = upstream if source is client else client
                    direction = "upstream" if source is client else "downstream"
                    operation = "recv"
                    payload = source.recv(65536)
                    if not payload:
                        reason = direction + "_eof"
                        return
                    event = {
                        "direction": direction,
                        "bytes": len(payload),
                        "at": time.monotonic(),
                    }
                    with self.changed:
                        callback = self._callback
                        if callback is not None:
                            self._callbacks_running += 1
                    if callback is not None:
                        try:
                            callback(identity, direction)
                        except Exception as error:
                            with self.lock:
                                self.errors.append(f"forwarding callback: {type(error).__name__}: {error}")
                            reason = "forwarding_callback_error"
                            return
                        finally:
                            with self.changed:
                                self._callbacks_running -= 1
                                self.changed.notify_all()
                    operation = "send"
                    with self.changed:
                        self.forwarding.add(identity)
                    try:
                        destination.sendall(payload)
                        del payload
                        with self.lock:
                            self.connections[identity]["events"].append(event)
                    finally:
                        with self.changed:
                            self.forwarding.remove(identity)
                            self.changed.notify_all()
        except (ConnectionResetError, ConnectionAbortedError, BrokenPipeError) as error:
            reason = type(error).__name__
        except OSError as error:
            reason = type(error).__name__
            with self.lock:
                self.errors.append(f"connection {identity}: {type(error).__name__}: {error}")
        except AssertionError as error:
            reason = "observer_gate_timeout"
            with self.lock:
                self.errors.append(f"connection {identity}: {error}")
        finally:
            client.close()
            if upstream is not None:
                upstream.close()
            with self.lock:
                self.connections[identity]["closed_at"] = time.monotonic()
                self.connections[identity]["end_reason"] = reason
                self.connections[identity]["end_direction"] = direction
                self.connections[identity]["end_operation"] = operation

    def snapshot(self):
        with self.changed:
            # A receiver can finish before sendall returns and its event is published.
            if not self.changed.wait_for(lambda: not self.forwarding, timeout=3):
                raise TimeoutError("Observer did not finish recording forwarded traffic")
            assert not self.errors, f"Traffic observer failed: {self.errors}"
            return copy.deepcopy(self.connections)

    def close(self):
        self.stop.set()
        self.new_connections.set()
        try:
            if self.thread is not None:
                self.thread.join(timeout=5)
                assert not self.thread.is_alive(), "Observer accept thread did not stop"
            for worker in self.workers:
                worker.join(timeout=5)
                assert not worker.is_alive(), "Observer connection thread did not stop"
            self.snapshot()
        finally:
            if self.listener is not None:
                self.listener.close()


def exchange_events(before, after, identity):
    assert identity in before and identity in after, "The measured read did not use a known connection"
    original = before[identity]
    current = after[identity]
    assert original["closed_at"] is None, "The selected connection was already closed"
    assert original["accepted_at"] == current["accepted_at"] and original["peer"] == current["peer"]
    count = len(original["events"])
    assert current["events"][:count] == original["events"], "Observer history changed"
    return current["events"][count:]


def warmed_connection(before, after):
    active = [
        identity
        for identity, connection in after.items()
        if len(connection["events"]) > len(before.get(identity, {}).get("events", []))
    ]
    assert len(active) == 1, "Warm read traffic was not isolated to one connection"
    (identity,) = active
    events = exchange_events(before, after, identity)
    assert {event["direction"] for event in events} == {"upstream", "downstream"}
    assert after[identity]["closed_at"] is None, "Warm read connection did not remain open"
    return identity


def assert_response_exchange(before, after, identity, started, finished):
    events = exchange_events(before, after, identity)
    assert events, "No traffic on the warmed order-read connection"
    assert all(
        event["bytes"] > 0 and started <= event["at"] <= finished for event in events
    ), "Traffic was outside the measured read"
    upstream = [event for event in events if event["direction"] == "upstream"]
    downstream = [event for event in events if event["direction"] == "downstream"]
    assert upstream and downstream, "Missing request or returning response traffic on the warmed connection"
    assert upstream[0]["at"] <= downstream[0]["at"], "Response traffic preceded the measured request"
    reconnects = [connection["accepted_at"] for key, connection in after.items() if key not in before]
    assert all(
        accepted > downstream[0]["at"] for accepted in reconnects
    ), "A new connection appeared before response traffic on the warmed connection"
    return {
        "connection": identity,
        "request_bytes": sum(event["bytes"] for event in upstream),
        "response_bytes": sum(event["bytes"] for event in downstream),
        "first_request_after_start": upstream[0]["at"] - started,
        "first_response_after_start": downstream[0]["at"] - started,
        "reconnects_after_start": [accepted - started for accepted in reconnects],
    }


def assert_reset_connection(before, after, identity, started, finished):
    events = exchange_events(before, after, identity)
    closed = after[identity]
    assert (closed["end_reason"], closed["end_direction"], closed["end_operation"]) == (
        "ConnectionResetError",
        "upstream",
        "recv",
    ), "Expected a TCP reset received from Toxiproxy, not EOF"
    assert started <= closed["closed_at"] <= finished, "Reset outside the measured read"
    assert all(started <= event["at"] <= closed["closed_at"] for event in events)
    assert {event["direction"] for event in events} == {
        "upstream",
        "downstream",
    }, "Missing request/returning traffic on the established connection before reset"
    return {
        "connection": identity,
        "reset_after_start": closed["closed_at"] - started,
        "request_bytes": sum(event["bytes"] for event in events if event["direction"] == "upstream"),
        "response_bytes": sum(event["bytes"] for event in events if event["direction"] == "downstream"),
    }


def forwarding_progress(before, after, identity, started, finished):
    result = assert_response_exchange(before, after, identity, started, finished)
    events = exchange_events(before, after, identity)
    times = [event["at"] for event in events if event["direction"] == "downstream"]
    assert times == sorted(times), "Forwarding observations are out of order"
    result.update(
        response_events=len(times),
        last_response_after_start=times[-1] - started,
        forwarding_span=times[-1] - times[0],
        largest_response_gap=max((right - left for left, right in zip(times, times[1:])), default=0),
    )
    return result


def assert_cutoff_connection(before, after, identity, started, finished, cutoff_bytes, baseline_bytes):
    result = assert_response_exchange(before, after, identity, started, finished)
    closed = after[identity]
    assert (closed["end_reason"], closed["end_direction"], closed["end_operation"]) == (
        "downstream_eof",
        "downstream",
        "recv",
    ), "Expected end-of-stream from the proxy after partial forwarding, not a reset"
    assert (
        closed["closed_at"] is not None and started <= closed["closed_at"] <= finished
    ), "Cutoff outside the measured read"
    events = exchange_events(before, after, identity)
    assert all(event["at"] <= closed["closed_at"] for event in events)
    assert 0 < cutoff_bytes < baseline_bytes, "Cutoff does not truncate the response"
    assert result["response_bytes"] == cutoff_bytes, "Forwarded byte count missed the cutoff"
    result["closed_after_start"] = closed["closed_at"] - started
    return result


def assert_persistent_cutoffs(before, after, identity, started, finished, cutoff_bytes, baseline_bytes):
    first = assert_cutoff_connection(before, after, identity, started, finished, cutoff_bytes, baseline_bytes)
    cutoffs = []
    for key, connection in after.items():
        if key in before or connection["accepted_at"] > finished:
            continue
        forwarded_at = connection["forwarding_started_at"]
        assert (
            forwarded_at is not None and forwarded_at <= finished
        ), "Replacement connection did not forward during the read"
        assert started <= connection["accepted_at"] <= forwarded_at
        events = [event for event in connection["events"] if event["at"] <= finished]
        assert all(event["at"] >= forwarded_at and event["bytes"] > 0 for event in events)
        returned = sum(event["bytes"] for event in events if event["direction"] == "downstream")
        assert returned <= cutoff_bytes, "Replacement traffic exceeded the active cutoff"
        closed_at = connection["closed_at"]
        if closed_at is None or closed_at > finished:
            continue
        if (
            connection["end_reason"],
            connection["end_direction"],
            connection["end_operation"],
        ) != ("downstream_eof", "downstream", "recv"):
            continue
        assert all(event["at"] <= closed_at for event in events)
        assert returned == cutoff_bytes, "Replacement EOF did not match the byte cutoff"
        assert any(event["direction"] == "upstream" for event in events)
        cutoffs.append(
            {
                "connection": key,
                "forwarded_bytes": returned,
                "forwarding_started_at": forwarded_at,
                "closed_at": closed_at,
            }
        )
    assert cutoffs, "No replacement connection experienced the persistent cutoff"
    return {"first": first, "replacement_cutoffs": cutoffs}
