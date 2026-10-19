# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.
"""Verify genuine resets and exact-byte cutoffs on established connections."""

import os
from contextlib import ExitStack
import socket
import time
import uuid
from urllib.parse import urlsplit

import pytest

from fault_injection._delayed_create import emit
from fault_injection._tcp_observer import (
    assert_cutoff_connection,
    assert_persistent_cutoffs,
    assert_reset_connection,
)
from fault_injection._toxiproxy import CUTOFF_BYTES, OwnedProxy

pytestmark = pytest.mark.skipif(
    not os.environ.get("TOXIPROXY_SERVER"),
    reason="Opt-in pinned Toxiproxy socket verification",
)


def receive_exact(connection, size):
    result = b""
    while len(result) < size:
        part = connection.recv(size - len(result))
        assert part, "Unexpected orderly connection close"
        result += part
    return result


def snapshot_after_exchange(observer, identity, count, response_bytes=0):
    deadline = time.monotonic() + 2
    while True:
        state = observer.snapshot()
        if identity in state:
            events = state[identity]["events"]
            if (
                len(events) >= count
                and sum(event["bytes"] for event in events if event["direction"] == "downstream") >= response_bytes
            ):
                return state
        assert time.monotonic() < deadline, "Observer did not record the completed exchange"
        time.sleep(0.001)


def test_proxy_resets_established_socket(tmp_path):
    with socket.socket() as server:
        server.bind(("127.0.0.1", 0))
        server.listen()
        server.settimeout(3)
        proxy = OwnedProxy(
            os.environ["TOXIPROXY_SERVER"],
            f"https://127.0.0.1:{server.getsockname()[1]}/",
            "cosmos-reset-socket-" + uuid.uuid4().hex,
            tmp_path,
            observe=True,
        )
        try:
            proxy.start()
            proxy.prepare_reset()
            with socket.create_connection(("127.0.0.1", urlsplit(proxy.endpoint).port), timeout=3) as client:
                upstream, _ = server.accept()
                with upstream:
                    upstream.settimeout(3)
                    client.sendall(b"warm")
                    assert receive_exact(upstream, 4) == b"warm"
                    upstream.sendall(b"ready")
                    assert receive_exact(client, 5) == b"ready"
                    before = snapshot_after_exchange(proxy.observer, "1", 2)
                    with proxy.single_reset("1"):
                        started = time.monotonic()
                        client.sendall(b"read")
                        assert receive_exact(upstream, 4) == b"read"
                        upstream.sendall(b"reply")
                        with pytest.raises(ConnectionResetError):
                            client.recv(5)
                        finished = time.monotonic()
                    after = proxy.observer.snapshot()
                    # The upstream-leg reset may be recorded just after the client observes its reset.
                    evidence = assert_reset_connection(before, after, "1", started, time.monotonic())
                    emit(
                        "proxy_socket_reset_verified",
                        name=proxy.name,
                        client_reset_at=finished,
                        exchange=evidence,
                    )
            with socket.create_connection(("127.0.0.1", urlsplit(proxy.endpoint).port), timeout=3) as recovered:
                upstream, _ = server.accept()
                with upstream:
                    upstream.settimeout(3)
                    recovered.sendall(b"again")
                    assert receive_exact(upstream, 5) == b"again"
                    upstream.sendall(b"ok")
                    assert receive_exact(recovered, 2) == b"ok"
        finally:
            proxy.close()


@pytest.mark.parametrize("persistent", [False, True], ids=["single", "persistent"])
def test_proxy_cuts_established_socket(tmp_path, persistent):
    payload = bytes(range(256)) * 250
    with socket.socket() as server:
        server.bind(("127.0.0.1", 0))
        server.listen()
        server.settimeout(3)
        proxy = OwnedProxy(
            os.environ["TOXIPROXY_SERVER"],
            f"https://127.0.0.1:{server.getsockname()[1]}/",
            "cosmos-cutoff-socket-" + uuid.uuid4().hex,
            tmp_path,
            observe=True,
        )
        try:
            proxy.start()
            proxy.observe_sdk_side()
            with socket.create_connection(("127.0.0.1", urlsplit(proxy.sdk_endpoint).port), timeout=3) as client:
                upstream, _ = server.accept()
                with upstream:
                    upstream.settimeout(3)
                    client.sendall(b"warm")
                    assert receive_exact(upstream, 4) == b"warm"
                    upstream.sendall(payload)
                    assert receive_exact(client, len(payload)) == payload
                    before = snapshot_after_exchange(proxy.sdk_observer, "1", 2, len(payload))
                    fault = proxy.persistent_cutoff() if persistent else proxy.single_cutoff("1")
                    with fault as state:
                        started = time.monotonic()
                        client.sendall(b"read")
                        assert receive_exact(upstream, 4) == b"read"
                        upstream.sendall(payload)
                        assert receive_exact(client, CUTOFF_BYTES) == payload[:CUTOFF_BYTES]
                        assert client.recv(1) == b"", "Expected EOF after the exact cutoff"
                        eof_at = time.monotonic()
                        if persistent:
                            for _ in range(2):
                                with socket.create_connection(
                                    ("127.0.0.1", urlsplit(proxy.sdk_endpoint).port),
                                    timeout=3,
                                ) as replacement:
                                    replacement_upstream, _ = server.accept()
                                    with replacement_upstream:
                                        replacement_upstream.settimeout(3)
                                        replacement.sendall(b"read")
                                        assert receive_exact(replacement_upstream, 4) == b"read"
                                        replacement_upstream.sendall(payload)
                                        assert receive_exact(replacement, CUTOFF_BYTES) == payload[:CUTOFF_BYTES]
                                        assert replacement.recv(1) == b""
                            deadline = time.monotonic() + 2
                            while True:
                                observed = proxy.sdk_observer.snapshot()
                                if len(observed) == 3 and all(c["closed_at"] is not None for c in observed.values()):
                                    break
                                assert time.monotonic() < deadline, "Cutoff closures were not recorded"
                                time.sleep(0.001)
                            repeated = assert_persistent_cutoffs(
                                before,
                                observed,
                                "1",
                                started,
                                time.monotonic(),
                                CUTOFF_BYTES,
                                len(payload),
                            )
                            assert len(repeated["replacement_cutoffs"]) == 2
                    evidence = assert_cutoff_connection(
                        before,
                        proxy.sdk_observer.snapshot(),
                        "1",
                        started,
                        time.monotonic(),
                        CUTOFF_BYTES,
                        len(payload),
                    )
            with socket.create_connection(("127.0.0.1", urlsplit(proxy.sdk_endpoint).port), timeout=3) as recovered:
                upstream, _ = server.accept()
                with upstream:
                    upstream.settimeout(3)
                    recovered.sendall(b"again")
                    assert receive_exact(upstream, 5) == b"again"
                    upstream.sendall(payload)
                    assert receive_exact(recovered, len(payload)) == payload
            emit(
                ("proxy_socket_persistent_cutoff_verified" if persistent else "proxy_socket_cutoff_verified"),
                name=proxy.name,
                client_eof_at=eof_at,
                exchange=evidence,
                cutoff_state=state,
                repeated_cutoffs=repeated if persistent else None,
                recovered_bytes=len(payload),
            )
        finally:
            proxy.close()


@pytest.mark.parametrize("failure", ["body", "removal"])
def test_owned_routes_isolate_faults_and_clean_up_after_failure(tmp_path, monkeypatch, failure):
    payload = bytes(range(256)) * 250
    proxies = []
    with socket.socket() as server:
        server.bind(("127.0.0.1", 0))
        server.listen()
        server.settimeout(3)

        def exchange(proxy, expected_size):
            with socket.create_connection(("127.0.0.1", urlsplit(proxy.sdk_endpoint).port), timeout=3) as client:
                upstream, _ = server.accept()
                with upstream:
                    upstream.settimeout(3)
                    client.sendall(b"read")
                    assert receive_exact(upstream, 4) == b"read"
                    upstream.sendall(payload)
                    assert receive_exact(client, expected_size) == payload[:expected_size]
                    if expected_size < len(payload):
                        assert client.recv(1) == b""

        expected_error = RuntimeError if failure == "body" else TimeoutError
        with pytest.raises(expected_error, match="deliberate") as raised:
            with ExitStack() as cleanup:
                for label in ("a", "b"):
                    directory = tmp_path / label
                    directory.mkdir()
                    proxy = OwnedProxy(
                        os.environ["TOXIPROXY_SERVER"],
                        f"https://127.0.0.1:{server.getsockname()[1]}/",
                        "cosmos-isolation-" + uuid.uuid4().hex,
                        directory,
                        observe=True,
                    )
                    cleanup.callback(proxy.close)
                    proxies.append(proxy)
                    proxy.start()
                    proxy.observe_sdk_side()
                    exchange(proxy, len(payload))
                affected, unaffected = proxies
                assert affected.process.pid != unaffected.process.pid
                assert affected.api != unaffected.api and affected.sdk_endpoint != unaffected.sdk_endpoint
                if failure == "removal":
                    request = affected.request

                    def fail_removal(path, body=None, method=None, **kwargs):
                        if method == "DELETE" and path.endswith("/response-limit_data"):
                            raise TimeoutError("deliberate removal failure")
                        return request(path, body, method, **kwargs)

                    monkeypatch.setattr(affected, "request", fail_removal)
                with affected.persistent_cutoff():
                    exchange(affected, CUTOFF_BYTES)
                    exchange(unaffected, len(payload))
                    assert len(affected.request("/proxies/" + affected.name + "/toxics")) == 1
                    assert unaffected.request("/proxies/" + unaffected.name + "/toxics") == []
                    emit(
                        "proxy_isolation_observed",
                        failure=failure,
                        affected=affected.name,
                        unaffected=unaffected.name,
                        cutoff_bytes=CUTOFF_BYTES,
                        unaffected_bytes=len(payload),
                    )
                    raise RuntimeError("deliberate body failure")
        if failure == "removal":
            assert isinstance(raised.value.__context__, RuntimeError)
        for proxy in proxies:
            assert proxy.process.poll() is not None
            assert not proxy.observer.thread.is_alive() and not proxy.sdk_observer.thread.is_alive()
            with socket.socket() as probe:
                probe.settimeout(1)
                assert probe.connect_ex(("127.0.0.1", urlsplit(proxy.sdk_endpoint).port)) != 0
        emit(
            "proxy_failure_cleanup_verified",
            failure=failure,
            owned_pids=[proxy.process.pid for proxy in proxies],
            original_error_visible=True,
            removal_error_visible=failure == "removal",
        )
