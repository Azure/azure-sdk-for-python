# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.
import copy
import threading
import time
from types import SimpleNamespace

import pytest
from azure.core.exceptions import ServiceRequestError
from azure.cosmos import exceptions
from azure.cosmos._backend.client_config import _prepare_fault_injection_rules
from fault_injection._toxiproxy import (
    OwnedProxy,
    account_rule,
    assert_bandwidth_outcome,
    assert_latency_outcome,
    assert_persistent_cutoff_outcome,
    assert_read_outcome,
    assert_stall_outcome,
    assert_warmed_connections,
    proxy_account,
    proxy_transfers,
    verify_server,
)

ENDPOINT = "https://127.0.0.1:12345/"
ITEM = {"id": "order-42", "pk": "customer-17"}


def records(endpoint=ENDPOINT, applied=False, status=200):
    return [
        {
            "endpoint": endpoint,
            "status": status,
            "evaluations": [{"rule_id": "account", "applied": applied}],
        }
    ]


@pytest.mark.parametrize(
    "error,elapsed,expected",
    [
        (exceptions.CosmosClientTimeoutError(), 3.01, "operation_timeout"),
        (ServiceRequestError("closed"), 0.5, "terminal_transport_failure"),
    ],
)
def test_persistent_cutoff_classifies_bounded_failure_rust(error, elapsed, expected):
    attempts = [dict(record, sub_status=20003) for record in records(status=503)] * 2
    assert assert_persistent_cutoff_outcome(error, elapsed, attempts) == expected


@pytest.mark.parametrize(
    "error,elapsed,pairs",
    [
        (None, 0.1, [(503, 20003), (200, 0)]),
        (ValueError("bad setup"), 0.1, [(503, 20003)] * 2),
        (exceptions.CosmosClientTimeoutError(), 1, [(503, 20003)] * 2),
        (exceptions.CosmosClientTimeoutError(), 3.5, [(503, 20003)] * 2),
        (exceptions.CosmosClientTimeoutError(), float("nan"), [(503, 20003)] * 2),
        (ServiceRequestError("late"), 3.1, [(503, 20003)] * 2),
        (ServiceRequestError("early"), 0.1, []),
        (ServiceRequestError("early"), 0.1, [(503, 20003)]),
        (ServiceRequestError("early"), 0.1, [(503, 20014)] * 2),
        (ServiceRequestError("early"), 0.1, [(503, 20003), (429, 0)]),
        (exceptions.CosmosHttpResponseError(408), 3.01, [(503, 20003)] * 2),
    ],
)
def test_persistent_cutoff_rejects_wrong_classification_or_budget_rust(error, elapsed, pairs):
    with pytest.raises(AssertionError):
        assert_persistent_cutoff_outcome(
            error,
            elapsed,
            [{"status": status, "sub_status": sub} for status, sub in pairs],
        )


@pytest.mark.parametrize("failure", [None, "body", "remove", "configuration"])
@pytest.mark.parametrize("active", [False, True])
def test_persistent_fault_leaves_gates_open_until_cleanup_rust(active, failure, monkeypatch):
    monkeypatch.setattr("fault_injection._toxiproxy.emit", lambda *args, **kwargs: None)
    gate = threading.Event()
    gate.set()
    observer = SimpleNamespace(new_connections=gate)
    toxics, deleted = [], []

    def request(path, body=None, method=None, *, timeout=2):
        assert gate.is_set()
        if body is not None:
            assert body == {
                "name": "response-limit_data",
                "type": "limit_data",
                "stream": "downstream",
                "toxicity": 1.0,
                "attributes": {"bytes": 20000},
            }
            toxics.append(body.copy())
            return dict(body, stream="upstream") if failure == "configuration" else body
        if method == "DELETE":
            assert timeout == 10 and path.endswith("/response-limit_data")
            deleted.append(path)
            toxics.clear()
            if failure == "remove":
                raise TimeoutError("removal failed")
        return toxics.copy()

    proxy = SimpleNamespace(
        name="owned",
        sdk_observer=observer,
        observer=observer,
        request=request,
        assert_enabled=lambda: None,
    )

    def exercise():
        with OwnedProxy.persistent_cutoff(proxy, active):
            assert gate.is_set() and bool(toxics) is active and not deleted
            if failure == "body":
                raise RuntimeError("read failed")

    expected = {
        "body": RuntimeError,
        "remove": TimeoutError,
        "configuration": AssertionError,
    }
    if failure == "body" or (active and failure in ("remove", "configuration")):
        with pytest.raises(expected[failure]):
            exercise()
    else:
        exercise()
    assert gate.is_set() and not toxics and len(deleted) == int(active)


def test_topology_copies_account_and_removes_direct_routes_rust():
    original = {
        "readableLocations": [{"name": "South Central US", "databaseAccountEndpoint": "direct"}],
        "writableLocations": [{"name": "South Central US", "databaseAccountEndpoint": "direct"}],
        "thinClientReadableLocations": [{"databaseAccountEndpoint": "thin-direct"}],
        "thinClientWritableLocations": [{"databaseAccountEndpoint": "thin-direct"}],
        "enableMultipleWriteLocations": True,
        "enablePerPartitionFailoverBehavior": True,
        "unrelated": {"preserved": True},
    }
    before = copy.deepcopy(original)
    result = proxy_account(original, ENDPOINT)
    expected = [{"name": "West US", "databaseAccountEndpoint": ENDPOINT}]
    assert result["readableLocations"] == result["writableLocations"] == expected
    assert "thinClientReadableLocations" not in result
    assert "thinClientWritableLocations" not in result
    assert result["enableMultipleWriteLocations"] is False
    assert result["enablePerPartitionFailoverBehavior"] is False
    assert result["unrelated"] == original["unrelated"]
    result["unrelated"]["preserved"] = False
    assert original == before


@pytest.mark.parametrize(
    "endpoint",
    [
        "https://cloud.documents.azure.com/",
        "http://127.0.0.1:12345/",
        "https://user:password@127.0.0.1:12345/",
        "https://127.0.0.1:12345/path",
    ],
)
def test_topology_rejects_nonlocal_or_invalid_destination_rust(endpoint):
    with pytest.raises(ValueError):
        proxy_account({}, endpoint)


def test_only_account_metadata_is_synthetic_rust():
    rule = account_rule("account-only", proxy_account({}, ENDPOINT))
    (prepared,) = _prepare_fault_injection_rules([rule])
    assert prepared.operation_type == "MetadataReadDatabaseAccount"
    assert prepared.status_code == 200
    assert prepared.probability == 1
    assert prepared.hit_limit is None


def test_success_and_network_failure_are_distinct_rust():
    assert_read_outcome(ITEM.copy(), None, 0.01, records(), ENDPOINT, ITEM, False)
    assert_read_outcome(None, ServiceRequestError("offline"), 1, [], ENDPOINT, ITEM, True)
    assert_read_outcome(None, exceptions.CosmosClientTimeoutError(), 3, [], ENDPOINT, ITEM, True)


@pytest.mark.parametrize(
    "returned,error",
    [
        (ITEM, None),
        (None, None),
        (None, ValueError("bad setup")),
        (None, exceptions.CosmosHttpResponseError(401)),
        (None, exceptions.CosmosHttpResponseError(429)),
    ],
)
def test_disabled_route_rejects_success_and_unrelated_failure_rust(returned, error):
    with pytest.raises(AssertionError):
        assert_read_outcome(returned, error, 1, [], ENDPOINT, ITEM, True)


@pytest.mark.parametrize(
    "attempts",
    [
        [],
        records("https://127.0.0.1:8081/"),
        records(applied=True),
        records(status=503),
    ],
)
def test_success_requires_real_proxy_attempt_rust(attempts):
    with pytest.raises(AssertionError):
        assert_read_outcome(ITEM, None, 0.01, attempts, ENDPOINT, ITEM, False)


@pytest.mark.parametrize("elapsed", [-1, 6, float("inf"), float("nan")])
def test_rejects_unbounded_or_invalid_elapsed_rust(elapsed):
    with pytest.raises(AssertionError):
        assert_read_outcome(None, ServiceRequestError("offline"), elapsed, [], ENDPOINT, ITEM, True)


def test_rejects_unverified_executable_rust(tmp_path):
    with pytest.raises(FileNotFoundError):
        verify_server(tmp_path / "missing.exe")
    fake = tmp_path / "fake.exe"
    fake.write_bytes(b"not the official server")
    with pytest.raises(ValueError, match="checksum"):
        verify_server(fake)


def transfers():
    return {
        "upstream_received": 400,
        "upstream_sent": 400,
        "downstream_received": 1000,
        "downstream_sent": 700,
    }


def metrics(name="owned"):
    return "\n".join(
        f'toxiproxy_proxy_{transfer}_bytes_total{{direction="{direction}",listener="127.0.0.1:12345",'
        f'proxy="{name}",upstream="127.0.0.1:8081"}} {value}'
        for key, value in transfers().items()
        for direction, transfer in [key.split("_")]
    )


def test_completed_transfer_metrics_select_only_owned_proxy_rust():
    assert proxy_transfers("# HELP comment\n" + metrics("other") + "\n" + metrics(), "owned") == transfers()


@pytest.mark.parametrize(
    "text",
    [
        metrics("other"),
        metrics().replace(" 1000", " NaN"),
        metrics().replace(" 1000", " -1"),
        metrics() + "\n" + metrics(),
    ],
)
def test_transfer_metrics_reject_missing_invalid_or_duplicate_counters_rust(text):
    with pytest.raises(AssertionError):
        proxy_transfers(text, "owned")


def test_stall_requires_sdk_timeout_and_dropped_response_bytes_rust():
    assert_stall_outcome(exceptions.CosmosClientTimeoutError(), 3.01, transfers())
    connections = {"accepted": ["127.0.0.1:1234"], "closed_links": []}
    assert_warmed_connections(connections, copy.deepcopy(connections))


@pytest.mark.parametrize(
    "error,elapsed",
    [
        (None, 3),
        (ServiceRequestError("TLS failed"), 3),
        (exceptions.CosmosHttpResponseError(408), 3),
        (exceptions.CosmosClientTimeoutError(), 1),
        (exceptions.CosmosClientTimeoutError(), 10),
        (exceptions.CosmosClientTimeoutError(), float("nan")),
    ],
)
def test_stall_rejects_wrong_timeout_or_budget_rust(error, elapsed):
    with pytest.raises(AssertionError):
        assert_stall_outcome(error, elapsed, transfers())


@pytest.mark.parametrize(
    "field,value",
    [
        ("downstream_received", 700),
        ("downstream_received", 500),
        ("downstream_sent", 0),
        ("upstream_sent", 0),
        ("upstream_sent", 401),
    ],
)
def test_stall_rejects_missing_or_inconsistent_network_evidence_rust(field, value):
    actual = transfers()
    actual[field] = value
    with pytest.raises(AssertionError):
        assert_stall_outcome(exceptions.CosmosClientTimeoutError(), 3, actual)


@pytest.mark.parametrize(
    "before,after",
    [
        ({"accepted": [], "closed_links": []}, {"accepted": [], "closed_links": []}),
        (
            {"accepted": ["old"], "closed_links": ["olddownstream"]},
            {"accepted": ["old"], "closed_links": ["olddownstream"]},
        ),
        (
            {"accepted": ["old"], "closed_links": []},
            {"accepted": ["old", "new"], "closed_links": []},
        ),
    ],
)
def test_stall_rejects_unwarmed_or_new_connections_rust(before, after):
    with pytest.raises(AssertionError):
        assert_warmed_connections(before, after)


def reset_attempts():
    failed = records(status=503)[0]
    failed["sub_status"] = 20003
    return [failed, records()[0]]


def test_reset_retry_requires_transport_failure_then_success_rust():
    assert_read_outcome(ITEM, None, 0.1, reset_attempts(), ENDPOINT, ITEM, False, transport_retry=True)


@pytest.mark.parametrize(
    "attempts",
    [
        records(),
        reset_attempts() + records(),
        [dict(reset_attempts()[0], status=408), records()[0]],
        [dict(reset_attempts()[0], sub_status=20011), records()[0]],
        [dict(reset_attempts()[0], sub_status=20014), records()[0]],
        [dict(reset_attempts()[0], endpoint="https://127.0.0.1:8081/"), records()[0]],
        [reset_attempts()[0], records(status=503)[0]],
    ],
)
def test_reset_retry_rejects_missing_extra_or_unrelated_attempts_rust(attempts):
    with pytest.raises(AssertionError):
        assert_read_outcome(ITEM, None, 0.1, attempts, ENDPOINT, ITEM, False, transport_retry=True)


def test_reset_retry_does_not_accept_a_late_success_rust():
    with pytest.raises(AssertionError, match="budget"):
        assert_read_outcome(
            ITEM,
            None,
            3.1,
            reset_attempts(),
            ENDPOINT,
            ITEM,
            False,
            transport_retry=True,
        )


@pytest.mark.parametrize(
    "delay_ms,error,elapsed,attempts",
    [
        (0, None, 0.01, records()),
        (500, None, 0.51, records()),
        (5000, exceptions.CosmosClientTimeoutError(), 3.01, []),
    ],
)
def test_latency_outcome_requires_delay_and_original_budget_rust(delay_ms, error, elapsed, attempts):
    assert assert_latency_outcome(error, elapsed, 0.005, delay_ms, attempts) == (elapsed - 0.005)


@pytest.mark.parametrize(
    "delay_ms,error,elapsed,response_after_start,attempts",
    [
        (500, None, 0.01, 0.005, records()),
        (500, None, 0.9, 0.6, records()),
        (500, None, 3.01, 0.005, records()),
        (500, exceptions.CosmosClientTimeoutError(), 0.51, 0.005, []),
        (500, None, 0.51, 0.005, []),
        (500, None, 0.51, 0.005, records() * 2),
        (500, None, 0.51, 0.005, records(status=503)),
        (500, None, 0.51, -0.005, records()),
        (500, None, 0.51, 0.6, records()),
        (500, None, 0.51, float("nan"), records()),
        (500, None, float("nan"), 0.005, records()),
        (500, None, float("inf"), 0.005, records()),
        (5000, None, 3.01, 0.005, records()),
        (5000, ServiceRequestError("connection timeout"), 3.01, 0.005, []),
        (5000, exceptions.CosmosHttpResponseError(408), 3.01, 0.005, []),
        (5000, exceptions.CosmosClientTimeoutError(), 0.51, 0.005, []),
        (5000, exceptions.CosmosClientTimeoutError(), 3.6, 0.005, []),
        (5000, exceptions.CosmosClientTimeoutError(), 3.01, 2, []),
        (5000, exceptions.CosmosClientTimeoutError(), -1, 0.005, []),
        (3000, None, 0.51, 0.005, records()),
    ],
)
def test_latency_rejects_unproven_delay_and_wrong_deadline_rust(delay_ms, error, elapsed, response_after_start, attempts):
    with pytest.raises(AssertionError):
        assert_latency_outcome(error, elapsed, response_after_start, delay_ms, attempts)


@pytest.mark.parametrize("delay_ms", [0, 500, 5000])
@pytest.mark.parametrize("body_fails", [False, True])
def test_latency_configuration_and_cleanup_rust(delay_ms, body_fails, monkeypatch):
    calls, toxics = [], []
    monkeypatch.setattr("fault_injection._toxiproxy.emit", lambda *args, **kwargs: None)

    def request(path, data=None, method=None, *, timeout=2):
        calls.append((path, data, method))
        assert path.startswith("/proxies/owned/toxics")
        if method == "DELETE":
            assert path == "/proxies/owned/toxics/response-latency"
            assert timeout == 10
            toxics.clear()
        elif data is not None:
            assert timeout == 2
            toxics.append(copy.deepcopy(data))
            return copy.deepcopy(data)
        return copy.deepcopy(toxics)

    proxy = SimpleNamespace(name="owned", request=request, assert_enabled=lambda: None)

    def exercise():
        with OwnedProxy.response_latency(proxy, delay_ms):
            assert toxics == (
                [
                    {
                        "name": "response-latency",
                        "type": "latency",
                        "stream": "downstream",
                        "toxicity": 1.0,
                        "attributes": {"latency": delay_ms, "jitter": 0},
                    }
                ]
                if delay_ms
                else []
            )
            if body_fails:
                raise RuntimeError("read assertion failed")

    if body_fails:
        with pytest.raises(RuntimeError, match="read assertion"):
            exercise()
    else:
        exercise()
    assert toxics == []
    assert sum(method == "DELETE" for _, _, method in calls) == (1 if delay_ms else 0)


@pytest.mark.parametrize("mismatch", [False, True])
def test_latency_surfaces_removal_failure_or_configuration_mismatch_rust(mismatch, monkeypatch):
    monkeypatch.setattr("fault_injection._toxiproxy.emit", lambda *args, **kwargs: None)
    deleted = []

    def request(path, data=None, method=None, *, timeout=2):
        if method == "DELETE":
            deleted.append(path)
            if not mismatch:
                raise TimeoutError("bounded management cleanup expired")
        if data is not None:
            return dict(data, stream="upstream") if mismatch else data
        return []

    proxy = SimpleNamespace(name="owned", request=request, assert_enabled=lambda: None)
    entered = False
    with pytest.raises(AssertionError if mismatch else TimeoutError):
        with OwnedProxy.response_latency(proxy, 5000):
            entered = True
    assert entered is not mismatch, "Mismatched server configuration reached the read"
    assert deleted == ["/proxies/owned/toxics/response-latency"]


def bandwidth_progress(rate):
    last = {0: 0.02, 64: 1.025, 16: 2.9}[rate]
    first = 0.01 if rate == 0 else 0.1
    return {
        "first_request_after_start": 0.001,
        "first_response_after_start": first,
        "last_response_after_start": last,
        "response_bytes": 46400 if rate == 16 else 65000,
        "response_events": 29 if rate == 16 else 11,
        "forwarding_span": last - first,
        "largest_response_gap": 0.1,
        "reconnects_after_start": [],
    }


@pytest.mark.parametrize("rate", [0, 64, 16])
def test_bandwidth_requires_complete_success_or_timeout_despite_progress_rust(rate):
    progress = bandwidth_progress(rate)
    observed = assert_bandwidth_outcome(
        exceptions.CosmosClientTimeoutError() if rate == 16 else None,
        3.01 if rate == 16 else progress["last_response_after_start"] + 0.01,
        progress,
        65000,
        rate,
        [] if rate == 16 else records(),
    )
    if rate:
        assert rate * 750 < observed < rate * 1250
    else:
        assert observed is None


@pytest.mark.parametrize(
    "change",
    [
        {"response_events": 1},
        {"forwarding_span": 0},
        {"forwarding_span": 1.5},
        {"largest_response_gap": 1},
        {"largest_response_gap": float("nan")},
        {"first_response_after_start": 1},
        {"first_request_after_start": 1},
        {"last_response_after_start": 2},
        {"last_response_after_start": 4},
        {"response_bytes": 65000},
        {"response_bytes": 10000},
        {"response_bytes": 0},
    ],
)
def test_bandwidth_rejects_stall_burst_setup_or_unrelated_progress_rust(change):
    with pytest.raises(AssertionError):
        assert_bandwidth_outcome(
            exceptions.CosmosClientTimeoutError(),
            3.01,
            dict(bandwidth_progress(16), **change),
            65000,
            16,
            [],
        )


@pytest.mark.parametrize(
    "rate,error,elapsed,baseline,attempts",
    [
        (16, None, 3.01, 65000, records()),
        (16, ServiceRequestError("closed"), 3.01, 65000, []),
        (16, exceptions.CosmosClientTimeoutError(), 4, 65000, []),
        (16, exceptions.CosmosClientTimeoutError(), float("nan"), 65000, []),
        (16, exceptions.CosmosClientTimeoutError(), 3.01, 30000, []),
        (64, exceptions.CosmosClientTimeoutError(), 3.01, 65000, []),
        (64, None, 3.01, 65000, records()),
        (64, None, 1.1, 65000, []),
        (64, None, 1.1, 65000, records() * 2),
        (64, None, 1.1, 65000, records(status=503)),
    ],
)
def test_bandwidth_rejects_wrong_outcomes_and_unbounded_wait_rust(rate, error, elapsed, baseline, attempts):
    with pytest.raises(AssertionError):
        assert_bandwidth_outcome(error, elapsed, bandwidth_progress(rate), baseline, rate, attempts)


@pytest.mark.parametrize("rate", [0, 64, 16])
@pytest.mark.parametrize("body_fails", [False, True])
def test_bandwidth_configuration_and_cleanup_rust(rate, body_fails, monkeypatch):
    toxics, deleted = [], []
    monkeypatch.setattr("fault_injection._toxiproxy.emit", lambda *args, **kwargs: None)

    def request(path, data=None, method=None, *, timeout=2):
        if method == "DELETE":
            assert path == "/proxies/owned/toxics/response-bandwidth" and timeout == 10
            toxics.clear()
            deleted.append(path)
        elif data is not None:
            toxics.append(copy.deepcopy(data))
            return copy.deepcopy(data)
        return copy.deepcopy(toxics)

    proxy = SimpleNamespace(name="owned", request=request, assert_enabled=lambda: None)

    def exercise():
        with OwnedProxy.response_bandwidth(proxy, rate):
            assert toxics == (
                [
                    {
                        "name": "response-bandwidth",
                        "type": "bandwidth",
                        "stream": "downstream",
                        "toxicity": 1.0,
                        "attributes": {"rate": rate},
                    }
                ]
                if rate
                else []
            )
            if body_fails:
                raise RuntimeError("read assertion failed")

    if body_fails:
        with pytest.raises(RuntimeError, match="read assertion"):
            exercise()
    else:
        exercise()
    assert not toxics
    assert len(deleted) == (1 if rate else 0)


@pytest.mark.parametrize("failure", [None, "body", "close", "remove", "configuration"])
def test_single_cutoff_gates_replacements_and_surfaces_failures_rust(failure, monkeypatch):
    monkeypatch.setattr("fault_injection._toxiproxy.emit", lambda *args, **kwargs: None)
    gate = threading.Event()
    gate.set()
    observed = {
        "closed_at": None,
        "end_reason": "downstream_eof",
        "end_direction": "downstream",
        "end_operation": "recv",
    }
    observer = SimpleNamespace(new_connections=gate, snapshot=lambda: {"warm": observed.copy()})
    proxy = object.__new__(OwnedProxy)
    proxy.name = "owned"
    proxy.sdk_observer = observer
    proxy.assert_enabled = lambda: None
    toxics, removed = [], []

    def request(path, body=None, method=None, *, timeout=2):
        if body is not None:
            assert not gate.is_set(), "Replacement forwarding was not gated before arming"
            assert body == {
                "name": "single-cutoff",
                "type": "limit_data",
                "stream": "downstream",
                "toxicity": 1.0,
                "attributes": {"bytes": 20000},
            }
            toxics.append(body.copy())
            return dict(body, stream="upstream") if failure == "configuration" else body
        if method == "DELETE":
            assert path == "/proxies/owned/toxics/single-cutoff" and timeout == 10
            removed.append(time.monotonic())
            toxics.clear()
            if failure == "remove":
                raise TimeoutError("cutoff removal failed")
        return toxics.copy()

    proxy.request = request
    entered = []

    def exercise():
        with proxy.single_cutoff("warm") as state:
            entered.append(True)
            assert not gate.is_set()
            if failure == "close":
                observed["end_reason"] = "ConnectionResetError"
            observed["closed_at"] = time.monotonic()
            if failure == "body":
                raise RuntimeError("read failed")
        assert state["cutoff_at"] <= state["removed_at"]
        assert removed[0] <= state["removed_at"]

    if failure is None:
        exercise()
    else:
        error = {
            "body": RuntimeError,
            "close": AssertionError,
            "remove": TimeoutError,
            "configuration": AssertionError,
        }[failure]
        with pytest.raises(error):
            exercise()
    assert bool(entered) is (failure != "configuration")
    assert gate.is_set() and removed and not toxics


def test_recovered_read_rejects_a_partial_receipt_rust():
    expected = dict(ITEM, receipt="complete receipt")
    with pytest.raises(AssertionError):
        assert_read_outcome(
            dict(ITEM, receipt="complete"),
            None,
            0.1,
            reset_attempts(),
            ENDPOINT,
            expected,
            False,
            transport_retry=True,
        )
