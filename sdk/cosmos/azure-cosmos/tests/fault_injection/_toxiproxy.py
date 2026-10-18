# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.
"""Owned loopback Toxiproxy process for installed-emulator routing tests."""

import copy
from concurrent.futures import ThreadPoolExecutor
from contextlib import contextmanager
import hashlib
import json
import math
import os
from pathlib import Path
import re
import socket
import subprocess
import threading
import time
from urllib.error import URLError
from urllib.parse import urlsplit
from urllib.request import ProxyHandler, Request, build_opener

from azure.core.exceptions import ServiceRequestError, ServiceResponseError
from azure.cosmos import exceptions
from fault_injection._delayed_create import emit
from fault_injection._regional_routing import assert_destination, emulator_endpoints
from fault_injection._tcp_observer import TcpObserver

VERSION = "2.13.0"
SERVER_SHA256 = "04b710eefd7690c89f7cc67289e3e14618f1ff3c26e4a5f752a34a879b895bab"
REGION = "West US"
READ_TIMEOUT = 3
CUTOFF_BYTES = 20000


def proxy_transfers(text, name):
    """Read completed-link counters from the pinned server's metrics output."""
    result = {}
    for line in text.splitlines():
        match = re.fullmatch(
            r"toxiproxy_proxy_(received|sent)_bytes_total\{([^}]+)\} (\S+)", line
        )
        if match is None:
            continue
        transfer, raw_labels, value = match.groups()
        labels = dict(re.findall(r'(\w+)="([^"]*)"', raw_labels))
        if labels.get("proxy") != name:
            continue
        key = labels["direction"] + "_" + transfer
        assert key not in result, "Duplicate proxy byte counter"
        result[key] = float(value)
    assert set(result) == {
        "upstream_received",
        "upstream_sent",
        "downstream_received",
        "downstream_sent",
    }, "Missing completed-link byte counters"
    assert all(
        math.isfinite(value) and value >= 0 for value in result.values()
    ), "Invalid byte counter"
    return result


def assert_warmed_connections(before, after):
    assert before["accepted"], "No warmed proxy connection"
    assert any(
        client + "downstream" not in before["closed_links"]
        for client in before["accepted"]
    ), "All warmed downstream connections were already closed"
    assert (
        after["accepted"] == before["accepted"]
    ), "A new connection could have stalled during TLS setup"


def assert_stall_outcome(error, elapsed, transfers):
    assert isinstance(
        error, exceptions.CosmosClientTimeoutError
    ), "Expected the SDK operation timeout"
    assert (
        math.isfinite(elapsed) and READ_TIMEOUT - 0.5 <= elapsed < READ_TIMEOUT + 3
    ), "Read did not end around its operation budget"
    assert transfers["upstream_received"] >= transfers["upstream_sent"] > 0
    assert (
        transfers["downstream_received"] > transfers["downstream_sent"] > 0
    ), "No downstream bytes were discarded after the successful warm reads"


def assert_latency_outcome(error, elapsed, response_after_start, delay_ms, records):
    assert delay_ms in (0, 500, 5000), "Unexpected latency case"
    assert (
        math.isfinite(elapsed) and 0 <= elapsed < READ_TIMEOUT + 0.5
    ), "Read did not respect its operation budget"
    assert math.isfinite(response_after_start) and 0 <= response_after_start < min(
        elapsed, READ_TIMEOUT / 2
    ), "Returning traffic arrived too late to isolate the proxy delay"
    if delay_ms > READ_TIMEOUT * 1000:
        assert isinstance(
            error, exceptions.CosmosClientTimeoutError
        ), "Expected the SDK operation timeout, not a transport failure"
        assert elapsed >= READ_TIMEOUT - 0.5, "Read ended before its operation budget"
    else:
        assert error is None, "Delay within the budget must not fail the read"
        assert elapsed < READ_TIMEOUT, "Successful read exhausted its operation budget"
        assert (
            len(records) == 1 and records[0]["status"] == 200
        ), "Expected one successful read attempt, not retry recovery"
        assert (
            elapsed - response_after_start >= delay_ms / 1000 - 0.05
        ), "Elapsed setup or emulator time does not prove downstream delay"
    return elapsed - response_after_start


def assert_bandwidth_outcome(
    error, elapsed, progress, baseline_bytes, rate_kbps, records
):
    assert rate_kbps in (0, 64, 16), "Unexpected bandwidth case"
    assert math.isfinite(elapsed) and 0 < elapsed < READ_TIMEOUT + 0.5
    assert baseline_bytes >= 64000, "Warm response was too small for the bandwidth test"
    first, last = (
        progress["first_response_after_start"],
        progress["last_response_after_start"],
    )
    assert 0 <= progress["first_request_after_start"] <= first <= last <= elapsed
    assert first < 0.5, "Forwarding started too late to prove continuing progress"
    forwarded = progress["response_bytes"]
    assert forwarded > 0
    if rate_kbps == 16:
        assert isinstance(
            error, exceptions.CosmosClientTimeoutError
        ), "Expected the original SDK operation timeout despite forwarding progress"
        assert READ_TIMEOUT - 0.5 <= elapsed
        assert baseline_bytes / (rate_kbps * 1000) > READ_TIMEOUT + 0.5
        assert forwarded < baseline_bytes * 0.95, "The response was not partial"
        assert last >= elapsed - 0.4, "Forwarding stopped well before the timeout"
        assert progress["forwarding_span"] >= READ_TIMEOUT - 0.75
    else:
        assert error is None and elapsed < READ_TIMEOUT
        assert len(records) == 1 and records[0]["status"] == 200
        assert baseline_bytes * 0.95 <= forwarded <= baseline_bytes * 1.05
        assert not progress[
            "reconnects_after_start"
        ], "Successful read changed connection"
    if rate_kbps:
        assert (
            progress["response_events"] >= 3
        ), "Missing repeated downstream forwarding"
        assert progress["forwarding_span"] >= 0.5, "Bytes arrived in one burst"
        assert (
            0 <= progress["largest_response_gap"] <= 0.4
        ), "Traffic stalled between deliveries"
        duration = last - progress["first_request_after_start"]
        observed_rate = forwarded / duration
        assert (
            rate_kbps * 1000 * 0.75 <= observed_rate <= rate_kbps * 1000 * 1.25
        ), "Observed forwarding does not match the configured bandwidth limit"
        return observed_rate
    return None


@contextmanager
def response_fault(proxy, kind, attributes, active, **evidence):
    proxy.assert_enabled()
    path = "/proxies/" + proxy.name + "/toxics"
    assert proxy.request(path) == []
    if not active:
        yield
        proxy.assert_enabled()
        assert proxy.request(path) == []
        return
    configuration = {
        "name": "response-" + kind,
        "type": kind,
        "stream": "downstream",
        "toxicity": 1.0,
        "attributes": attributes,
    }
    created = proxy.request(path, configuration)
    try:
        assert all(created[key] == value for key, value in configuration.items())
        emit("proxy_" + kind + "_added", name=proxy.name, configuration=configuration)
        yield
    finally:
        # Pinned server buffer draining can wait five seconds on a closed consumer.
        removal_started = time.monotonic()
        proxy.request(path + "/" + configuration["name"], method="DELETE", timeout=10)
        assert proxy.request(path) == []
        proxy.assert_enabled()
        emit(
            "proxy_" + kind + "_removed",
            name=proxy.name,
            elapsed=time.monotonic() - removal_started,
            **evidence,
        )


def assert_read_outcome(
    returned, error, elapsed, records, endpoint, item, must_fail, transport_retry=False
):
    assert (
        math.isfinite(elapsed) and 0 <= elapsed < READ_TIMEOUT + 3
    ), "Read exceeded its bounded verification window"
    expected = urlsplit(endpoint)
    for record in records:
        actual = urlsplit(record["endpoint"])
        assert (actual.scheme, actual.hostname, actual.port) == (
            expected.scheme,
            expected.hostname,
            expected.port,
        ), "Read bypassed the proxy endpoint"
        assert not any(
            entry["applied"] for entry in record["evaluations"]
        ), "A driver rule injected an item failure instead of a network interruption"
    if must_fail:
        assert returned is None and isinstance(
            error,
            (
                ServiceRequestError,
                ServiceResponseError,
                exceptions.CosmosHttpResponseError,
                exceptions.CosmosClientTimeoutError,
            ),
        ), "Read bypassed the disabled proxy or failed for an unexpected reason"
        if isinstance(error, exceptions.CosmosHttpResponseError):
            assert error.status_code in (
                408,
                503,
            ), "Unexpected non-network service failure"
    else:
        assert error is None, f"Proxy read failed: {error}"
        assert {field: returned[field] for field in item} == item
        if transport_retry:
            assert (
                elapsed < READ_TIMEOUT
            ), "Recovered read exhausted its original operation budget"
            assert (
                len(records) == 2
            ), "Expected one failed read attempt followed by one successful retry"
            assert (records[0]["status"], records[0]["sub_status"]) == (
                503,
                20003,
            ), "Expected the diagnostic pipeline's transport-generated failure"
            assert_destination(records[1:], endpoint, 200)
        else:
            assert_destination(records, endpoint, 200)


def proxy_account(account, endpoint):
    emulator_endpoints(endpoint)
    result = copy.deepcopy(account)
    location = {"name": REGION, "databaseAccountEndpoint": endpoint}
    result["readableLocations"] = [location.copy()]
    result["writableLocations"] = [location.copy()]
    result["enableMultipleWriteLocations"] = False
    result["enablePerPartitionFailoverBehavior"] = False
    result.pop("thinClientReadableLocations", None)
    result.pop("thinClientWritableLocations", None)
    return result


def account_rule(rule_id, account):
    return {
        "id": rule_id,
        "operation_type": "MetadataReadDatabaseAccount",
        "status_code": 200,
        "response_body": json.dumps(account).encode("utf-8"),
        "probability": 1.0,
    }


def verify_server(path):
    path = Path(path)
    if not path.is_file():
        raise FileNotFoundError(
            "Set TOXIPROXY_SERVER to the installed v2.13.0 Windows x64 server"
        )
    if hashlib.sha256(path.read_bytes()).hexdigest() != SERVER_SHA256:
        raise ValueError(
            "Toxiproxy server does not match the pinned v2.13.0 Windows x64 checksum"
        )
    return path


class OwnedProxy:
    def __init__(self, server, endpoint, name, directory, observe=False):
        self.server = verify_server(server)
        emulator_endpoints(endpoint)
        parsed = urlsplit(endpoint)
        self.upstream = f"127.0.0.1:{parsed.port or 443}"
        self.name = name
        self.directory = Path(directory)
        self.process = None
        self.log = None
        self.proxy = None
        self.opener = build_opener(ProxyHandler({}))
        self.observer = TcpObserver(parsed.port or 443) if observe else None
        self.sdk_observer = None

    def request(self, path, body=None, method=None, *, timeout=2):
        request = Request(
            self.api + path,
            data=None if body is None else json.dumps(body).encode("utf-8"),
            headers={
                "User-Agent": "CosmosToxiproxyTests/1.0",
                "Content-Type": "application/json",
            },
            method=method,
        )
        with self.opener.open(request, timeout=timeout) as response:
            payload = response.read()
        return json.loads(payload) if payload else None

    def start(self):
        if self.observer is not None:
            self.observer.start()
            self.upstream = f"127.0.0.1:{self.observer.port}"
        with socket.socket() as reservation:
            reservation.bind(("127.0.0.1", 0))
            port = reservation.getsockname()[1]
        self.api = f"http://127.0.0.1:{port}"
        self.directory.mkdir(parents=True, exist_ok=True)
        self.log = (self.directory / "server.log").open("wb")
        environment = {
            key: value
            for key, value in os.environ.items()
            if key.upper() not in ("TOXIPROXY_AUTH_TOKEN", "TOXIPROXY_URL")
        }
        self.process = subprocess.Popen(
            [
                str(self.server),
                "-host",
                "127.0.0.1",
                "-port",
                str(port),
                "-proxy-metrics",
            ],
            env=environment,
            stdout=self.log,
            stderr=subprocess.STDOUT,
        )
        deadline = time.monotonic() + 10
        while True:
            if self.process.poll() is not None:
                raise RuntimeError(
                    f"Toxiproxy exited at startup; see {self.directory / 'server.log'}"
                )
            try:
                version = self.request("/version")
                break
            except URLError:
                if time.monotonic() >= deadline:
                    raise
                time.sleep(0.05)
        assert version == {"version": VERSION}
        assert self.request("/proxies") == {}, "Unexpected pre-existing proxy state"
        self.proxy = self.request(
            "/proxies",
            {
                "name": self.name,
                "listen": "127.0.0.1:0",
                "upstream": self.upstream,
                "enabled": True,
            },
        )
        assert self.process.poll() is None, "Owned server exited during route creation"
        assert self.proxy["listen"].startswith("127.0.0.1:")
        self.endpoint = "https://" + self.proxy["listen"] + "/"
        self.sdk_endpoint = self.endpoint
        emit(
            "proxy_started",
            name=self.name,
            pid=self.process.pid,
            endpoint=self.endpoint,
            upstream=self.upstream,
            version=VERSION,
        )
        return self

    def observe_sdk_side(self):
        assert self.sdk_observer is None
        assert not self.connection_state()[
            "accepted"
        ], "Observe before warming connections"
        self.sdk_observer = TcpObserver(urlsplit(self.endpoint).port)
        self.sdk_observer.start()
        self.sdk_endpoint = f"https://127.0.0.1:{self.sdk_observer.port}/"
        emit(
            "proxy_sdk_observer_started",
            name=self.name,
            endpoint=self.sdk_endpoint,
            upstream=self.endpoint,
        )

    def assert_enabled(self):
        route = self.request("/proxies/" + self.name)
        assert route["enabled"] is True, "Response fault must not disable the route"
        assert route["listen"] == self.proxy["listen"]
        assert self.process.poll() is None

    def add_response_stall(self):
        self.assert_enabled()
        assert self.request("/proxies/" + self.name + "/toxics") == []
        configuration = {
            "name": "response-stall",
            "type": "timeout",
            "stream": "downstream",
            "toxicity": 1.0,
            "attributes": {"timeout": 0},
        }
        created = self.request("/proxies/" + self.name + "/toxics", configuration)
        assert all(created[key] == value for key, value in configuration.items())
        emit("proxy_stall_added", name=self.name, configuration=configuration)

    def remove_response_stall(self):
        self.request(
            "/proxies/" + self.name + "/toxics/response-stall", method="DELETE"
        )
        assert self.request("/proxies/" + self.name + "/toxics") == []
        self.assert_enabled()
        emit("proxy_stall_removed", name=self.name)

    def response_latency(self, delay_ms):
        assert delay_ms in (0, 500, 5000), "Unexpected latency case"
        return response_fault(
            self,
            "latency",
            {"latency": delay_ms, "jitter": 0},
            delay_ms > 0,
            delay_ms=delay_ms,
        )

    def response_bandwidth(self, rate_kbps):
        assert rate_kbps in (0, 64, 16), "Unexpected bandwidth case"
        return response_fault(
            self,
            "bandwidth",
            {"rate": rate_kbps},
            rate_kbps > 0,
            rate_kbps=rate_kbps,
        )

    def prepare_reset(self):
        assert self.observer is not None
        assert not self.connection_state()[
            "accepted"
        ], "Install reset socket settings before opening connections"
        assert self.request("/proxies/" + self.name + "/toxics") == []
        configuration = {
            "name": "single-reset",
            "type": "reset_peer",
            "stream": "downstream",
            "toxicity": 0.0,
            "attributes": {"timeout": 0},
        }
        created = self.request("/proxies/" + self.name + "/toxics", configuration)
        assert all(created[key] == value for key, value in configuration.items())
        emit("proxy_reset_prepared", name=self.name, configuration=configuration)

    def remove_reset(self):
        self.request("/proxies/" + self.name + "/toxics/single-reset", method="DELETE")
        assert self.request("/proxies/" + self.name + "/toxics") == []
        self.assert_enabled()
        removed = time.monotonic()
        emit("proxy_reset_removed", name=self.name, removed_at=removed)
        return removed

    def single_reset(self, identity):
        def arm():
            enabled = self.request(
                "/proxies/" + self.name + "/toxics/single-reset",
                {"toxicity": 1.0},
                method="POST",
            )
            assert enabled["toxicity"] == 1.0

        return self._single_interruption(
            self.observer,
            identity,
            "reset",
            "single-reset",
            ("ConnectionResetError", "upstream", "recv"),
            arm,
            self.remove_reset,
        )

    def remove_cutoff(self):
        self.request(
            "/proxies/" + self.name + "/toxics/single-cutoff",
            method="DELETE",
            timeout=10,
        )
        assert self.request("/proxies/" + self.name + "/toxics") == []
        self.assert_enabled()
        removed = time.monotonic()
        emit("proxy_cutoff_removed", name=self.name, removed_at=removed)
        return removed

    def single_cutoff(self, identity, cutoff_bytes=CUTOFF_BYTES):
        assert self.sdk_observer is not None
        assert cutoff_bytes == CUTOFF_BYTES

        def arm():
            self.assert_enabled()
            path = "/proxies/" + self.name + "/toxics"
            assert self.request(path) == []
            configuration = {
                "name": "single-cutoff",
                "type": "limit_data",
                "stream": "downstream",
                "toxicity": 1.0,
                "attributes": {"bytes": cutoff_bytes},
            }
            created = self.request(path, configuration)
            assert all(created[key] == value for key, value in configuration.items())
            emit("proxy_cutoff_added", name=self.name, configuration=configuration)

        return self._single_interruption(
            self.sdk_observer,
            identity,
            "cutoff",
            "single-cutoff",
            ("downstream_eof", "downstream", "recv"),
            arm,
            self.remove_cutoff,
        )

    @contextmanager
    def _single_interruption(
        self, observer, identity, kind, toxic_name, expected_close, arm, remove
    ):
        stop = threading.Event()
        state = {}
        observer.new_connections.clear()

        def restore():
            deadline = time.monotonic() + READ_TIMEOUT
            while not stop.is_set():
                connection = observer.snapshot()[identity]
                if connection["closed_at"] is not None:
                    assert (
                        connection["end_reason"],
                        connection["end_direction"],
                        connection["end_operation"],
                    ) == expected_close, (
                        "Established connection closed without the intended fault"
                    )
                    state[kind + "_at"] = connection["closed_at"]
                    state["removed_at"] = remove()
                    observer.new_connections.set()
                    return
                assert (
                    time.monotonic() < deadline
                ), "No interruption observed on the warmed connection"
                stop.wait(0.001)
            raise AssertionError("Read finished before the interruption was observed")

        try:
            arm()
            state["armed_at"] = time.monotonic()
            emit(
                "proxy_" + kind + "_armed", name=self.name, connection=identity, **state
            )
            with ThreadPoolExecutor(
                max_workers=1, thread_name_prefix="cosmos-" + kind + "-removal"
            ) as executor:
                removal = executor.submit(restore)
                try:
                    yield state
                finally:
                    try:
                        removal.result(timeout=READ_TIMEOUT + 1)
                    finally:
                        stop.set()
                        observer.new_connections.set()
        finally:
            try:
                remaining = self.request("/proxies/" + self.name + "/toxics")
                if any(toxic["name"] == toxic_name for toxic in remaining):
                    remove()
            finally:
                observer.new_connections.set()

    def connection_state(self):
        accepted, closed = [], []
        for line in (
            (self.directory / "server.log").read_text(encoding="utf-8").splitlines()
        ):
            event = json.loads(line)
            if event.get("name") != self.name:
                continue
            if event.get("message") == "Accepted client":
                accepted.append(event["client"])
            if event.get("method") == "write" and event.get("message", "").startswith(
                "RemoveConnection "
            ):
                closed.append(event["link"])
        return {"accepted": accepted, "closed_links": closed}

    def completed_transfers(self):
        # v2.13.0 updates counters when each copy loop exits, before logging link removal.
        deadline = time.monotonic() + 5
        while True:
            state = self.connection_state()
            expected = {
                client + direction
                for client in state["accepted"]
                for direction in ("upstream", "downstream")
            }
            if expected and expected.issubset(state["closed_links"]):
                break
            assert (
                time.monotonic() < deadline
            ), "Stalled connections did not finish closing"
            time.sleep(0.02)
        request = Request(
            self.api + "/metrics", headers={"User-Agent": "CosmosToxiproxyTests/1.0"}
        )
        with self.opener.open(request, timeout=2) as response:
            metrics = response.read().decode("utf-8")
        result = proxy_transfers(metrics, self.name)
        emit(
            "proxy_completed_transfers",
            name=self.name,
            transfers=result,
            connections=state,
        )
        return result

    def set_enabled(self, enabled):
        assert self.process.poll() is None, "Owned Toxiproxy server exited"
        self.proxy = self.request(
            "/proxies/" + self.name, {"enabled": enabled}, method="PATCH"
        )
        assert self.proxy["enabled"] is enabled
        assert self.proxy["listen"] + "/" == self.endpoint.removeprefix("https://")
        if not enabled:
            with socket.socket() as probe:
                probe.settimeout(1)
                assert (
                    probe.connect_ex(("127.0.0.1", urlsplit(self.endpoint).port)) != 0
                ), "Disabled proxy still accepts connections"
        emit("proxy_enabled", name=self.name, enabled=enabled)

    def close(self):
        try:
            if self.proxy is not None and self.process.poll() is None:
                self.request("/proxies/" + self.name, method="DELETE")
                assert self.request("/proxies") == {}
        finally:
            try:
                if self.process is not None:
                    if self.process.poll() is None:
                        self.process.terminate()
                    try:
                        self.process.wait(timeout=10)
                    except subprocess.TimeoutExpired:
                        self.process.kill()
                        self.process.wait(timeout=10)
                        raise
                    emit("proxy_process_stopped", name=self.name, pid=self.process.pid)
                    with socket.socket() as probe:
                        probe.settimeout(1)
                        assert (
                            probe.connect_ex(("127.0.0.1", urlsplit(self.api).port))
                            != 0
                        ), "Management listener remained after owned server shutdown"
            finally:
                try:
                    if self.sdk_observer is not None:
                        self.sdk_observer.close()
                        emit("proxy_sdk_observer_stopped", name=self.name)
                finally:
                    try:
                        if self.observer is not None:
                            self.observer.close()
                            emit("proxy_observer_stopped", name=self.name)
                    finally:
                        if self.log is not None:
                            self.log.close()
