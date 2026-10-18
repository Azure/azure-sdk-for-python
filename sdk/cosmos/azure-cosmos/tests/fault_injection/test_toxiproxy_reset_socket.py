# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.
"""Verify genuine resets and exact-byte cutoffs on established connections."""

import os
import socket
import time
import uuid
from urllib.parse import urlsplit

import pytest

from fault_injection._delayed_create import emit
from fault_injection._tcp_observer import (
    assert_cutoff_connection,
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
                and sum(
                    event["bytes"]
                    for event in events
                    if event["direction"] == "downstream"
                )
                >= response_bytes
            ):
                return state
        assert (
            time.monotonic() < deadline
        ), "Observer did not record the completed exchange"
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
            with socket.create_connection(
                ("127.0.0.1", urlsplit(proxy.endpoint).port), timeout=3
            ) as client:
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
                    evidence = assert_reset_connection(
                        before, after, "1", started, time.monotonic()
                    )
                    emit(
                        "proxy_socket_reset_verified",
                        name=proxy.name,
                        client_reset_at=finished,
                        exchange=evidence,
                    )
            with socket.create_connection(
                ("127.0.0.1", urlsplit(proxy.endpoint).port), timeout=3
            ) as recovered:
                upstream, _ = server.accept()
                with upstream:
                    upstream.settimeout(3)
                    recovered.sendall(b"again")
                    assert receive_exact(upstream, 5) == b"again"
                    upstream.sendall(b"ok")
                    assert receive_exact(recovered, 2) == b"ok"
        finally:
            proxy.close()


def test_proxy_cuts_established_socket(tmp_path):
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
            with socket.create_connection(
                ("127.0.0.1", urlsplit(proxy.sdk_endpoint).port), timeout=3
            ) as client:
                upstream, _ = server.accept()
                with upstream:
                    upstream.settimeout(3)
                    client.sendall(b"warm")
                    assert receive_exact(upstream, 4) == b"warm"
                    upstream.sendall(payload)
                    assert receive_exact(client, len(payload)) == payload
                    before = snapshot_after_exchange(
                        proxy.sdk_observer, "1", 2, len(payload)
                    )
                    with proxy.single_cutoff("1") as state:
                        started = time.monotonic()
                        client.sendall(b"read")
                        assert receive_exact(upstream, 4) == b"read"
                        upstream.sendall(payload)
                        assert (
                            receive_exact(client, CUTOFF_BYTES)
                            == payload[:CUTOFF_BYTES]
                        )
                        assert (
                            client.recv(1) == b""
                        ), "Expected EOF after the exact cutoff"
                        eof_at = time.monotonic()
                    evidence = assert_cutoff_connection(
                        before,
                        proxy.sdk_observer.snapshot(),
                        "1",
                        started,
                        time.monotonic(),
                        CUTOFF_BYTES,
                        len(payload),
                    )
            with socket.create_connection(
                ("127.0.0.1", urlsplit(proxy.sdk_endpoint).port), timeout=3
            ) as recovered:
                upstream, _ = server.accept()
                with upstream:
                    upstream.settimeout(3)
                    recovered.sendall(b"again")
                    assert receive_exact(upstream, 5) == b"again"
                    upstream.sendall(payload)
                    assert receive_exact(recovered, len(payload)) == payload
            emit(
                "proxy_socket_cutoff_verified",
                name=proxy.name,
                client_eof_at=eof_at,
                exchange=evidence,
                cutoff_state=state,
                recovered_bytes=len(payload),
            )
        finally:
            proxy.close()
