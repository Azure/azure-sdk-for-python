# The MIT License (MIT)
# Copyright (c) Microsoft Corporation. All rights reserved.
"""Offline checks of workload timing, report populations and result completeness."""

import asyncio
import importlib
import json
import math
import os
from pathlib import Path
import shutil
import subprocess
import sys

import pytest

WORKLOADS = Path(__file__).resolve().parents[1] / "workloads"
STAMP = "20260919-120000000"


@pytest.fixture
def modules(monkeypatch):
    monkeypatch.syspath_prepend(str(WORKLOADS))
    return {name: importlib.import_module(name) for name in (
        "perf_stats", "perf_results", "perf_validate", "latency_report",
        "mixed_report", "coldstart_report", "crt_split_report", "perf_reporter",
        "perf_config", "perf_driver_commit_gate", "workload_utils",
    )}


class Rows:
    def __init__(self, rows=()):
        self.rows = list(rows)

    def query_items(self, *args, **kwargs):
        return self.rows

    def upsert_item(self, row):
        self.rows.append(row)


def measurement(modules, **changes):
    stats = modules["perf_stats"].Stats()
    stats.record("ReadItem", 1)
    stats.record("ReadItem", 2)
    summary = stats.drain_all()[0][0]
    return {
        **summary, "workload_id": f"baseline-read-rust-{STAMP}",
        "record_type": "measurement", "process_id": "process-1",
        "window_id": "window-1", "window_index": 1,
        "window_seconds": 60.0, "elapsed_seconds": 60.0,
        "driver_commit": "a" * 40, "config_backend": "rust",
        "runtime_backend": "AsyncRustBinding", "rust_execute_calls": 2,
        "binding_calls": 2, "attempt_calls": 2, "retry_calls": 0,
        "throttled_429": 0, "config_arrival_rate": 250,
        "config_concurrency": 1, "config_num_clients": 1,
        "config_use_sync": False, "config_proxy_enabled": False,
        **changes,
    }


def completion(row, **changes):
    return {
        "record_type": "completion", "workload_id": row["workload_id"],
        "process_id": row["process_id"], "window_count": 1,
        "summary_count": 1, "total_count": row["count"],
        "total_errors": row["errors"], **changes,
    }


def test_terminal_throttles_not_limited_by_error_detail_buffer(modules):
    stats = modules["perf_stats"].Stats()
    for _ in range(2005):
        stats.record_error("ReadItem", "throttled", "", 429)
    summaries, errors = stats.drain_all()
    assert summaries[0]["throttled_429"] == summaries[0]["errors"] == 2005
    assert len(errors) == 2000
    assert stats.drain_all() == ([], [])


@pytest.mark.parametrize("value", [float("nan"), float("inf"), -1])
@pytest.mark.parametrize("method", ["record", "record_ru", "record_server_ms"])
def test_stats_reject_invalid_measurements(modules, method, value):
    with pytest.raises(ValueError):
        getattr(modules["perf_stats"].Stats(), method)("ReadItem", value)


def test_latency_ignores_error_completion_and_cleanup_rows(modules):
    row = measurement(modules)
    error = {"record_type": "error", "workload_id": row["workload_id"], "error_message": "failed"}
    cleanup = measurement(modules, operation="CreateCleanupDelete", count=0, errors=1, hist_b64=None)
    cells, provenance = modules["latency_report"]._aggregate(
        Rows([row, error, completion(row), cleanup]), "baseline-", STAMP)
    cell = cells[("read", "rust")]
    assert cell["count"] == 2 and cell["errors"] == 0
    assert cell["window_s"] == 60 and cell["hist"].total_count == 2
    assert provenance == (["a" * 40], 0, 1)


def test_missing_histogram_is_not_a_fast_p99(modules):
    row = measurement(modules, hist_b64=None)
    cells, _ = modules["latency_report"]._aggregate(Rows([row]), "baseline-", STAMP)
    assert math.isnan(modules["latency_report"]._pctile_ms(cells[("read", "rust")], 99))


def test_wrong_histogram_sample_count_fails(modules):
    with pytest.raises(ValueError, match="samples"):
        modules["latency_report"]._aggregate(Rows([measurement(modules, count=99)]), "baseline-", STAMP)


def test_missing_retry_evidence_cannot_cancel_positive_counts(modules):
    row = measurement(modules, retry_calls=-1)
    next_row = measurement(modules, retry_calls=1, window_id="window-2", elapsed_seconds=120)
    cells, _ = modules["latency_report"]._aggregate(Rows([row, next_row]), "baseline-", STAMP)
    assert cells[("read", "rust")]["retry_calls"] is None


def test_ru_average_uses_header_sample_counts_not_success_counts(modules):
    rows = [
        measurement(modules, ru_sum=10, ru_count=1, mean_ru=10),
        measurement(modules, ru_sum=6, ru_count=2, mean_ru=3),
    ]
    cells, _ = modules["latency_report"]._aggregate(Rows(rows), "baseline-", STAMP)
    assert cells[("read", "rust")]["ru_weighted"] == 16
    assert cells[("read", "rust")]["ru_count"] == 3


def test_mixed_throughput_counts_shared_window_once(modules):
    read = measurement(modules, workload_id=f"mixed-blend-rust-{STAMP}")
    create = {**read, "operation": "CreateItem"}
    per_op, blended, _ = modules["mixed_report"]._aggregate(Rows([read, create]), "mixed-", STAMP)
    assert blended["rust"]["count"] == 4
    assert blended["rust"]["window_s"] == 60
    assert len(per_op) == 2


def test_zero_success_error_window_needs_no_histogram(modules):
    row = measurement(modules, count=0, errors=1, hist_b64=None)
    cells, _ = modules["latency_report"]._aggregate(Rows([row]), "baseline-", STAMP)
    assert cells[("read", "rust")]["no_hist_windows"] == 0
    assert math.isnan(modules["latency_report"]._pctile_ms(cells[("read", "rust")], 99))


def test_cold_samples_deduplicate_process_windows(modules):
    row = measurement(modules, workload_id=f"cold-read-rust-{STAMP}",
                      cold_first_ms=20, cold_first_n_ms=[20, 5])
    later = {**row, "window_id": "window-2", "cold_first_n_ms": [20, 5, 2]}
    cells, _, _ = modules["coldstart_report"]._aggregate(Rows([row, later]), "cold-", STAMP)
    assert cells[("rust", "read")] == {"firsts": [20], "curves": [[20, 5, 2]]}


def test_cold_first_success_does_not_hide_failed_first_call(modules):
    row = measurement(modules, workload_id=f"cold-read-rust-{STAMP}", errors=1, cold_first_ms=20)
    with pytest.raises(ValueError, match="first success"):
        modules["coldstart_report"]._aggregate(Rows([row]), "cold-", STAMP)


def test_nearest_rank_percentile(modules):
    assert modules["coldstart_report"]._pct(list(range(1, 11)), 50) == 5


@pytest.mark.parametrize("value", ["unknown", "", "branch-main", "none", "xyz12345"])
def test_invalid_commit_labels_fail_every_report_gate(modules, value):
    assert not modules["perf_driver_commit_gate"].decide([value], 0, 1)[0]


def test_partial_unknown_binding_or_wrong_runtime_does_not_pass(modules):
    first = measurement(modules)
    unknown = measurement(modules, binding_calls=-1, elapsed_seconds=120, window_id="window-2")
    validator = modules["perf_validate"]
    assert not validator.check_backend_execution(Rows([first, unknown]), "baseline-", STAMP)[0]
    wrong = measurement(modules, runtime_backend="AsyncLegacyBackend")
    assert not validator.check_backend_execution(Rows([wrong]), "baseline-", STAMP)[0]


def test_legacy_actual_class_name_is_accepted(modules):
    row = measurement(modules, config_backend="core-python", runtime_backend="AsyncLegacyBackend",
                      rust_execute_calls=0, binding_calls=0)
    assert modules["perf_validate"].check_backend_execution(Rows([row]), "baseline-", STAMP)[0]


@pytest.mark.parametrize("name", ["RustBackend", "AsyncRustBackend", "RustBinding", "AsyncRustBinding"])
def test_historical_and_current_rust_class_labels_are_accepted(modules, name):
    row = measurement(modules, runtime_backend=name)
    assert modules["perf_validate"].check_backend_execution(Rows([row]), "baseline-", STAMP)[0]


def test_profiler_reads_private_process_counters(modules):
    counters = importlib.import_module("perf_backend_counters")
    from azure.cosmos import _rust
    for kind in ("operation", "attempt", "retry"):
        expected = getattr(_rust, f"_debug_{kind}_count")()
        assert getattr(counters, f"binding_{kind}_count")() == expected


def test_final_missing_window_and_entire_cell_fail(modules):
    row = measurement(modules)
    validator = modules["perf_validate"]
    assert validator.check_completion(Rows([row, completion(row)]), "baseline-", STAMP)[0]
    assert not validator.check_completion(Rows([row]), "baseline-", STAMP)[0]
    assert not validator.check_completion(
        Rows([row, completion(row, window_count=2, summary_count=2, total_count=4)]),
        "baseline-", STAMP)[0]
    assert not validator.check_completion(
        Rows([row, completion(row)]), "baseline-", STAMP,
        [row["workload_id"], f"baseline-read-core-python-{STAMP}"])[0]


def test_empty_data_does_not_pass_quality_or_backend_gate(modules):
    rows = Rows([{"record_type": "completion"}])
    assert not modules["perf_validate"].check_quality(rows, "", "", ["rust"])[0]
    assert not modules["perf_validate"].check_backend_execution(rows, "", "")[0]


def test_reporter_failure_warning_detected(modules, tmp_path):
    (tmp_path / "cell.log").write_text("PerfReporter final flush failed: network error\n")
    assert not modules["perf_validate"].check_warnings(str(tmp_path))[0]


def test_mixed_continuity_deduplicates_windows(modules):
    row = measurement(modules)
    other = {**row, "operation": "CreateItem"}
    ok, lines = modules["perf_validate"].check_continuity(Rows([row, other]), "baseline-", STAMP, 60)
    assert ok and "rows=1" in lines[0]


def test_reporter_emits_fractional_timeout_and_completion(modules, monkeypatch):
    monkeypatch.setenv("COSMOS_REQUEST_TIMEOUT", "1.5")
    stats = modules["perf_stats"].Stats()
    config = {"report_interval": 60, "workload_id": f"baseline-read-rust-{STAMP}",
              "commit_sha": "b" * 40, "driver_commit": "a" * 40}
    reporter = modules["perf_reporter"].PerfReporter(stats, config)
    reporter._container = Rows()
    stats.record("ReadItem", 1)
    reporter.stop()
    row, final = reporter._container.rows
    assert row["config_request_timeout"] == 1.5
    assert final["record_type"] == "completion" and final["total_count"] == 1
    assert row["process_id"] == final["process_id"]


def test_reporter_failed_write_fails_stop(modules):
    class Broken(Rows):
        def upsert_item(self, row):
            raise OSError("sink unavailable")
    stats = modules["perf_stats"].Stats()
    reporter = modules["perf_reporter"].PerfReporter(
        stats, {"report_interval": 60, "workload_id": "test", "commit_sha": "x", "driver_commit": "y"})
    reporter._container = Broken()
    stats.record("ReadItem", 1)
    with pytest.raises(RuntimeError, match="incomplete"):
        reporter.stop()


def test_failed_sampling_cannot_be_reported_as_zero_memory(modules, monkeypatch):
    reporter_module = modules["perf_reporter"]
    stats = modules["perf_stats"].Stats()
    reporter = reporter_module.PerfReporter(
        stats, {"report_interval": 60, "workload_id": "test", "commit_sha": "x", "driver_commit": "y"})
    reporter._container = Rows()
    def unavailable():
        raise OSError("memory sampling unavailable")
    monkeypatch.setattr(reporter._process, "memory_info", unavailable)
    stats.record("ReadItem", 1)
    with pytest.raises(RuntimeError, match="incomplete"):
        reporter.stop()
    assert reporter._container.rows == []


def test_reporter_startup_failure_is_sticky(modules, monkeypatch):
    module = modules["perf_reporter"]
    reporter = module.PerfReporter(modules["perf_stats"].Stats(), {})
    monkeypatch.setattr(module, "_get_cpu_percent", lambda process: (_ for _ in ()).throw(OSError("denied")))
    reporter._run()
    assert isinstance(reporter._failure, OSError)


def test_mixed_quality_does_not_hide_a_failing_operation(modules):
    good = measurement(modules)
    failed = {**good, "operation": "CreateItem", "count": 0, "errors": 1, "hist_b64": None}
    assert not modules["perf_validate"].check_quality(Rows([good, failed]), "baseline-", STAMP, ["rust"])[0]


def test_fractional_counts_are_rejected(modules):
    with pytest.raises(ValueError, match="integers"):
        list(modules["perf_results"].summary_rows([measurement(modules, count=1.5)]))


@pytest.mark.parametrize("name", ["latency_report", "mixed_report", "coldstart_report",
                                 "scale_verdict", "scaleout_report", "leak_verdict"])
def test_report_cli_rejects_no_measurements(modules, monkeypatch, name):
    module = importlib.import_module(name)
    monkeypatch.setattr(module, "_connect", lambda: Rows([{"record_type": "completion"}]))
    monkeypatch.setattr(sys, "argv", [name, "--prefix", "test-", "--stamp", STAMP])
    with pytest.raises(SystemExit) as result:
        module.main()
    assert result.value.code != 0


@pytest.mark.parametrize("value", ["nan", "inf", "-1"])
@pytest.mark.parametrize("flag", ["--expected-rps", "--max-p99-ms"])
def test_latency_cli_rejects_invalid_threshold_before_connecting(modules, monkeypatch, value, flag):
    module = modules["latency_report"]
    monkeypatch.setattr(module, "_connect", lambda: pytest.fail("Invalid threshold reached the results account"))
    monkeypatch.setattr(sys, "argv", ["latency_report", flag, value])
    with pytest.raises(SystemExit) as result:
        module.main()
    assert result.value.code == 2


def test_fractional_mix_is_sampled_without_rounding_rare_operation_away(modules, monkeypatch):
    utils = modules["workload_utils"]
    def choose(operations, weights, k):
        assert operations == ["read", "patch"] and weights == [99.5, 0.5] and k == 1
        return ["patch"]
    monkeypatch.setattr(utils.random, "choices", choose)
    assert utils._mix_counts({"read": 99.5, "patch": 0.5}, 1) == {"patch": 1}


def test_fixed_rate_instrumentation_failure_propagates(modules):
    utils = modules["workload_utils"]
    class BrokenStats(modules["perf_stats"].Stats):
        def record(self, *args, **kwargs):
            raise ValueError("cannot record latency")
        def record_error(self, *args, **kwargs):
            raise ValueError("cannot record errors")
    async def run():
        stop = asyncio.Event()
        class Container:
            async def read_item(self, *args, **kwargs):
                return {}
        await utils.run_fixed_rate(Container(), [], BrokenStats(), ["read"], 1000, 1, stop)
    with pytest.raises(RuntimeError, match="instrumentation"):
        asyncio.run(run())


def test_mixed_unknown_throttles_remain_unknown(modules):
    row = measurement(modules, workload_id=f"mixed-blend-rust-{STAMP}")
    del row["throttled_429"]
    _, blended, _ = modules["mixed_report"]._aggregate(Rows([row]), "mixed-", STAMP)
    assert blended["rust"]["throttled_429"] is None


def test_cargo_provenance_uses_resolved_git_revision(modules, monkeypatch):
    provenance = importlib.import_module("perf_provenance")
    def metadata(command, **kwargs):
        assert command == ["cargo", "metadata", "--locked", "--offline", "--format-version", "1"]
        return json.dumps({"packages": [{
            "name": "azure_data_cosmos_driver",
            "source": "git+https://example.invalid/driver?rev=short#" + "a" * 40,
        }]})
    monkeypatch.setattr(provenance.subprocess, "check_output", metadata)
    assert provenance.driver_commit() == "a" * 40


@pytest.mark.parametrize("source", [None, "path+local", "registry+crates.io", "git+url#short"])
def test_cargo_provenance_rejects_unidentified_source(modules, monkeypatch, source):
    provenance = importlib.import_module("perf_provenance")
    monkeypatch.setattr(provenance.subprocess, "check_output", lambda *args, **kwargs:
                        json.dumps({"packages": [{"name": "azure_data_cosmos_driver", "source": source}]}))
    with pytest.raises(ValueError, match="locked Git"):
        provenance.driver_commit()


def test_source_fingerprint_catches_uncommitted_edits(modules, monkeypatch, tmp_path):
    provenance = importlib.import_module("perf_provenance")
    monkeypatch.setattr(provenance, "PACKAGE_ROOT", tmp_path)
    source = tmp_path / "azure" / "cosmos" / "client.py"
    source.parent.mkdir(parents=True)
    source.write_text("value = 1\n")
    before = provenance.source_digest()
    assert before == provenance.source_digest()
    source.write_text("value = 2\n")
    assert provenance.source_digest() != before


def test_manifest_escapes_values_and_excludes_credentials(modules, monkeypatch, tmp_path):
    manifest = importlib.import_module("perf_manifest")
    monkeypatch.setattr(manifest, "driver_commit", lambda: "a" * 40)
    monkeypatch.setattr(manifest, "source_digest", lambda: "b" * 64)
    monkeypatch.setattr(manifest, "extension_details", lambda: {"rust_extension_sha256": "c" * 64})
    monkeypatch.setattr(manifest.subprocess, "check_output", lambda *args, **kwargs: 'value "with quotes"')
    monkeypatch.setenv("COSMOS_DATABASE", 'db"quoted')
    monkeypatch.setenv("COSMOS_KEY", "synthetic-key-must-not-be-written")
    monkeypatch.setenv("RESULTS_COSMOS_KEY", "synthetic-results-key-must-not-be-written")
    manifest.write_manifest(tmp_path, STAMP, "test")
    text = (tmp_path / f"manifest-{STAMP}.json").read_text()
    assert json.loads(text)["account"]["database"] == 'db"quoted'
    assert "synthetic-key" not in text and "synthetic-results-key" not in text


@pytest.mark.parametrize("memory", [None, 0, -1, float("nan"), float("inf")])
def test_leak_report_rejects_unavailable_memory(modules, monkeypatch, memory):
    module = importlib.import_module("leak_verdict")
    row = measurement(modules, workload_id=f"leak-read-rust-{STAMP}", memory_bytes=memory)
    monkeypatch.setattr(module, "_connect", lambda: Rows([row]))
    monkeypatch.setattr(sys, "argv", ["leak_verdict", "--stamp", STAMP])
    with pytest.raises(ValueError, match="RSS"):
        module.main()


def bash_executable():
    git_bash = Path(r"C:\Program Files\Git\bin\bash.exe")
    bash = str(git_bash) if os.name == "nt" and git_bash.is_file() else shutil.which("bash")
    if not bash:
        pytest.skip("Bash is required for offline launcher checks")
    return bash


@pytest.mark.parametrize("script,verdict", [
    ("profiling_prove_transport.sh", "TRANSPORT VERDICT: gateway_v2 -- stubbed evidence"),
    ("profiling_prove_topology.sh", "TOPOLOGY VERDICT: advertised -- stubbed evidence"),
])
@pytest.mark.parametrize("python_rc,tee_rc,expected", [(0, 0, 0), (1, 0, 2), (0, 3, 2)])
def test_proof_scripts_fail_on_crash_or_log_loss(tmp_path, script, verdict, python_rc, tee_rc, expected):
    shutil.copyfile(WORKLOADS / script, tmp_path / script)
    (tmp_path / "profiling_common.sh").write_text(
        "profiling_load_env() { return 0; }\n"
        "profiling_load_session() { return 0; }\n"
        "python3() { printf '%s\\n' \"$PROOF_TEXT\"; return \"$PYTHON_RC\"; }\n"
        "tee() { cat > \"$1\"; return \"$TEE_RC\"; }\n",
        encoding="utf-8",
    )
    env = {**os.environ, "ARTIFACTS": tmp_path.as_posix(), "RUN_ID": STAMP,
           "COSMOS_URI": "https://example.invalid", "COSMOS_DATABASE": "db", "COSMOS_CONTAINER": "container",
           "COSMOS_PARTITION_KEY": "id", "PROOF_TEXT": verdict, "PYTHON_RC": str(python_rc), "TEE_RC": str(tee_rc)}
    result = subprocess.run([bash_executable(), script], cwd=tmp_path, env=env,
                            capture_output=True, text=True, timeout=15)
    assert result.returncode == expected, result.stdout + result.stderr


def test_throughput_launcher_keeps_earlier_child_failure(tmp_path):
    script = "run_throughput_sweep.sh"
    shutil.copyfile(WORKLOADS / script, tmp_path / script)
    (tmp_path / "perf_env.sh").write_text(
        "export COSMOS_DATABASE=scale_db COSMOS_CONTAINER=scale_cont PERF_REPORT_INTERVAL=300\n"
        "perf_single_operation_shape() { :; }\n"
        "perf_create_log_dir() { mkdir -p \"$1\"; }\n"
        "perf_require_positive() { :; }\n"
        "write_run_manifest() { :; }\n"
        "perf_check_run() { :; }\n"
        "python3() { :; }\n"
        "calls=0\n"
        "timeout() { calls=$((calls+1)); echo \"$calls\" > calls.txt; "
        "if [[ \"$calls\" == 1 ]]; then return 17; fi; return 0; }\n",
        encoding="utf-8",
    )
    result = subprocess.run([bash_executable(), script, "1", "read"], cwd=tmp_path,
                            env={**os.environ, "CONCURRENCY_LEVELS": "1"},
                            capture_output=True, text=True, timeout=15)
    assert (tmp_path / "calls.txt").read_text().strip() == "2"
    assert result.returncode == 1, result.stdout + result.stderr


def test_duplicate_processes_cannot_reuse_one_workload_id(modules):
    row = measurement(modules)
    second = {**row, "process_id": "process-2", "window_id": "other-window"}
    ok, lines = modules["perf_validate"].check_completion(
        Rows([row, second, completion(row), completion(second)]), "baseline-", STAMP, [row["workload_id"]])
    assert not ok and any("reused" in line for line in lines)


def test_wrong_python_sdk_checkout_is_rejected(modules, monkeypatch, tmp_path):
    import azure.cosmos as sdk
    provenance = importlib.import_module("perf_provenance")
    monkeypatch.setattr(sdk, "__file__", str(tmp_path / "__init__.py"))
    with pytest.raises(ValueError, match="outside the selected checkout"):
        provenance.extension_details()


def test_existing_run_directory_is_not_reused(tmp_path):
    target = tmp_path / "run"
    target.mkdir()
    marker = target / "evidence.txt"
    marker.write_text("preserve")
    result = subprocess.run(
        [bash_executable(), "-c", 'source "$1"; perf_create_log_dir "$2"', "test",
         (WORKLOADS / "perf_env.sh").as_posix(), target.as_posix()],
        env={**os.environ, "COSMOS_KEY": "synthetic-offline-key"},
        capture_output=True, text=True, timeout=15,
    )
    assert result.returncode != 0 and marker.read_text() == "preserve"


@pytest.mark.parametrize("name,prefix,middle", [
    ("latency_report", "baseline-", "read-rust"),
    ("mixed_report", "mixed-", "blend-rust"),
    ("coldstart_report", "cold-", "read-rust-r1"),
    ("scale_verdict", "sweep-", "read-rust-c1"),
    ("scaleout_report", "scaleout-", "read-rust-c1-N1-r1-p1"),
    ("leak_verdict", "leak-", "read-rust"),
])
def test_report_cli_accepts_valid_measurement_population(modules, monkeypatch, name, prefix, middle):
    module = importlib.import_module(name)
    rows = [measurement(
        modules, workload_id=f"{prefix}{middle}-{STAMP}", window_id=f"window-{i}", window_index=i,
        elapsed_seconds=600 + i * 60, memory_bytes=100_000_000, system_cpu_percent=10,
        ru_sum=2, ru_count=2, cold_first_ms=1, cold_first_n_ms=[1, 2],
    ) for i in range(1, 4)]
    rows.append(completion(rows[0], window_count=3, summary_count=3, total_count=6))
    monkeypatch.setattr(module, "_connect", lambda: Rows(rows))
    monkeypatch.setattr(sys, "argv", [name, "--prefix", prefix, "--stamp", STAMP])
    with pytest.raises(SystemExit) as result:
        module.main()
    assert result.value.code == 0


def test_read_preparation_does_not_generate_write_body(modules, monkeypatch):
    utils = modules["workload_utils"]
    monkeypatch.setattr(utils, "create_random_item", lambda: pytest.fail("Read generated a write body"))
    keys = utils.get_existing_random_keys()
    assert set(keys) == {"id", "pk"}


def test_fixed_rate_keeps_lateness_over_five_seconds(modules, monkeypatch):
    utils = modules["workload_utils"]
    monkeypatch.setattr(utils, "WORKLOAD_MIX", {})
    clock_reads = iter([0])
    monkeypatch.setattr(utils.time, "perf_counter_ns", lambda: next(clock_reads, 6_000_000_000))
    stats = modules["perf_stats"].Stats()
    async def run():
        stop = asyncio.Event()
        class Container:
            async def read_item(self, *args, **kwargs):
                stop.set()
                return {}
        await utils.run_fixed_rate(Container(), [], stats, ["read"], 1, 1, stop)
    asyncio.run(run())
    assert stats.first_ms_snapshot()["ReadItem"] == [6000]


def fixed_rate_row(modules, *, delay_ms=20, sdk_ms=5, failed=False, **changes):
    stats = modules["perf_stats"].Stats()
    if failed:
        stats.record_error("ReadItem", "failed", "", 503,
                           delay_before_call_ms=delay_ms, sdk_call_ms=sdk_ms)
    else:
        stats.record("ReadItem", delay_ms + sdk_ms,
                     delay_before_call_ms=delay_ms, sdk_call_ms=sdk_ms)
    summary = stats.drain_all()[0][0]
    return measurement(modules, **{
        **summary, "measurement_version": 2, "duration_kind": "total",
        "config_max_inflight": 10, "window_seconds": 0.004,
        **changes,
    })


def schedule_record(**changes):
    return {
        "schedule_id": "schedule-1", "rate": 250, "max_inflight": 10,
        "peak_inflight": 1, "scheduled_count": 1, "launched_count": 1,
        "not_launched_count": 0, "limit_wait_count": 0, "limit_wait_ms": 0.0,
        "scheduling_seconds": 0.004, **changes,
    }


@pytest.mark.parametrize("failed", [False, True])
def test_fixed_rate_records_delay_sdk_and_total_per_outcome(modules, monkeypatch, failed):
    utils = modules["workload_utils"]
    times = iter([60_000_000, 65_000_000])
    monkeypatch.setattr(utils.time, "perf_counter_ns", lambda: next(times))
    stats = modules["perf_stats"].Stats()

    async def call(**kwargs):
        if failed:
            raise RuntimeError("injected")
        return {"id": "test-42"}

    result = asyncio.run(utils._fixed_rate_call_async("ReadItem", stats, 40_000_000, call))
    assert result == (None if failed else {"id": "test-42"})
    row = stats.drain_all()[0][0]
    outcome = "failure" if failed else "success"
    assert row["count"] == int(not failed) and row["errors"] == int(failed)
    assert set(row["fixed_rate_timings"]) == {outcome}
    for name, value in (("delay_before_call", 20), ("sdk_call", 5), ("total", 25)):
        series = row["fixed_rate_timings"][outcome][name]
        assert series["count"] == 1 and series["max_observed_ms"] == value
        hist = modules["latency_report"].HdrHistogram.decode(series["hist_b64"])
        assert hist.get_value_at_percentile(99) / 1000 == pytest.approx(value, rel=0.001)
    assert stats.drain_all() == ([], [])


def test_total_histogram_is_not_sum_of_component_percentiles(modules):
    stats = modules["perf_stats"].Stats()
    stats.record("ReadItem", 100, delay_before_call_ms=95, sdk_call_ms=5)
    stats.record("ReadItem", 100, delay_before_call_ms=5, sdk_call_ms=95)
    group = stats.drain_all()[0][0]["fixed_rate_timings"]["success"]
    tails = {name: modules["latency_report"].HdrHistogram.decode(series["hist_b64"]).get_value_at_percentile(99)
             / 1000 for name, series in group.items()}
    assert tails["total"] == pytest.approx(100, rel=0.001)
    assert tails["delay_before_call"] + tails["sdk_call"] > 180


def test_fixed_rate_timing_and_schedule_survive_reporter_persistence(modules, monkeypatch):
    monkeypatch.setenv("WORKLOAD_ARRIVAL_RATE", "250")
    monkeypatch.setenv("WORKLOAD_MAX_INFLIGHT", "10")
    monkeypatch.setenv("WORKLOAD_NUM_CLIENTS", "1")
    monkeypatch.setenv("WORKLOAD_USE_SYNC", "false")
    stats = modules["perf_stats"].Stats()
    reporter = modules["perf_reporter"].PerfReporter(
        stats, {"report_interval": 60, "workload_id": f"baseline-read-rust-{STAMP}",
                "commit_sha": "b" * 40, "driver_commit": "a" * 40})
    reporter._container = Rows()
    stats.record("ReadItem", 25, delay_before_call_ms=20, sdk_call_ms=5)
    stats.record_schedule(schedule_record())
    reporter.stop()
    row, done = reporter._container.rows
    assert row["duration_kind"] == "total"
    assert row["fixed_rate_timings"]["success"]["sdk_call"]["max_observed_ms"] == 5
    assert done["fixed_rate_schedules"] == [schedule_record()]
    assert modules["perf_validate"].check_completion(Rows([row, done]), "baseline-", STAMP)[0]


def test_ten_slots_hold_eleventh_call_and_stop_drains_only_launched_work(modules, monkeypatch):
    utils = modules["workload_utils"]
    monkeypatch.setattr(utils, "WORKLOAD_MIX", {})
    clock = {"now": 20_000_000, "first": True}

    def now():
        if clock["first"]:
            clock["first"] = False
            return 0
        return clock["now"]

    monkeypatch.setattr(utils.time, "perf_counter_ns", now)
    stats = modules["perf_stats"].Stats()
    launched = []

    async def run():
        stop = asyncio.Event()
        release = asyncio.Event()
        ten_started = asyncio.Event()

        class Container:
            async def read_item(self, *args, **kwargs):
                launched.append(1)
                if len(launched) == 10:
                    ten_started.set()
                await release.wait()
                clock["now"] = 100_000_000
                return {}

        async def stop_at_limit(slots, stop_event):
            await ten_started.wait()
            clock["now"] = 40_000_000
            stop.set()
            release.set()
            return False

        monkeypatch.setattr(utils, "_wait_for_launch_slot", stop_at_limit)
        await utils.run_fixed_rate(Container(), [], stats, ["read"], 1000, 10, stop)

    asyncio.run(run())
    schedule = stats.schedule_snapshot()[0]
    assert len(launched) == schedule["launched_count"] == schedule["peak_inflight"] == 10
    assert schedule["scheduled_count"] == 40
    assert schedule["not_launched_count"] == 30
    assert schedule["limit_wait_count"] == 1
    assert schedule["limit_wait_ms"] == 20
    assert schedule["scheduling_seconds"] == 0.04  # excludes the 100-ms drain endpoint
    assert stats.drain_all()[0][0]["count"] == 10


@pytest.mark.parametrize("cancel", [False, True])
def test_waiting_for_capacity_stops_without_leaking_slot_or_task(modules, cancel):
    utils = modules["workload_utils"]

    async def run():
        slots = asyncio.Semaphore(1)
        await slots.acquire()
        stop = asyncio.Event()
        waiter = asyncio.create_task(utils._wait_for_launch_slot(slots, stop))
        await asyncio.sleep(0)
        if cancel:
            waiter.cancel()
            with pytest.raises(asyncio.CancelledError):
                await waiter
        else:
            stop.set()
            assert await waiter is False
        slots.release()
        await asyncio.wait_for(slots.acquire(), timeout=1)
        assert slots.locked()
        assert len(asyncio.all_tasks()) == 1

    asyncio.run(run())


def test_slot_is_returned_when_stop_and_capacity_arrive_together(modules):
    async def run():
        slots = asyncio.Semaphore(1)
        stop = asyncio.Event()
        stop.set()
        assert await modules["workload_utils"]._wait_for_launch_slot(slots, stop) is False
        assert not slots.locked()
    asyncio.run(run())


def test_overflow_is_reported_instead_of_a_clipped_p99(modules, capsys):
    row = fixed_rate_row(modules, delay_ms=70_000, sdk_ms=5)
    report = modules["latency_report"]
    cells, _ = report._aggregate(Rows([row]), "baseline-", STAMP)
    cell = cells[("read", "rust")]
    assert math.isnan(report._pctile_ms(cell, 99))
    report._print_fixed_rate_details(cell)
    output = capsys.readouterr().out
    assert "max_observed=70005.000" in output and "overflow=1" in output
    assert "p99=nan" in output


def test_unknown_old_overflow_evidence_cannot_hide_known_clipping(modules):
    old = measurement(modules)
    del old["latency_overflow_count"]
    clipped = fixed_rate_row(modules, delay_ms=70_000, sdk_ms=1)
    report = modules["latency_report"]
    for rows in ([old, clipped], [clipped, old]):
        cell = report._aggregate(Rows(rows), "baseline-", STAMP)[0][("read", "rust")]
        assert cell["latency_overflow_unknown"] and cell["latency_overflow_count"] == 1
        assert math.isnan(report._pctile_ms(cell, 99))


def test_component_histograms_pool_across_reporting_windows(modules):
    first = fixed_rate_row(modules, delay_ms=1, sdk_ms=2)
    second = fixed_rate_row(modules, delay_ms=20, sdk_ms=5,
                            window_index=2, window_id="window-2", elapsed_seconds=120)
    done = completion(first, window_count=2, summary_count=2, total_count=2, fixed_rate_schedules=[
        schedule_record(scheduled_count=2, launched_count=2)])
    cell = modules["latency_report"]._aggregate(Rows([first, second, done]), "baseline-", STAMP)[0][("read", "rust")]
    for name in ("delay_before_call", "sdk_call", "total"):
        assert cell["timings"]["success"][name]["hist"].total_count == 2
    assert cell["schedule"]["launched_count"] == 2


def test_missing_one_clients_schedule_is_rejected(modules):
    row = fixed_rate_row(modules, config_num_clients=2)
    done = completion(row, fixed_rate_schedules=[schedule_record()])
    with pytest.raises(ValueError, match="client schedules"):
        modules["perf_validate"].check_completion(Rows([row, done]), "baseline-", STAMP)


def test_multiple_clients_schedules_reconcile_with_process_totals(modules):
    first = fixed_rate_row(modules, config_num_clients=2)
    second = {**first, "window_id": "window-2", "window_index": 2, "elapsed_seconds": 120}
    done = completion(first, window_count=2, summary_count=2, total_count=2, fixed_rate_schedules=[
        schedule_record(), schedule_record(schedule_id="schedule-2")])
    assert modules["perf_validate"].check_completion(Rows([first, second, done]), "baseline-", STAMP)[0]
    cell = modules["latency_report"]._aggregate(Rows([first, second, done]), "baseline-", STAMP)[0][("read", "rust")]
    assert cell["schedule"]["scheduled_count"] == 2


def test_waiting_for_capacity_resumes_and_releases_exactly_one_slot(modules):
    async def run():
        slots = asyncio.Semaphore(1)
        await slots.acquire()
        waiter = asyncio.create_task(modules["workload_utils"]._wait_for_launch_slot(slots, asyncio.Event()))
        await asyncio.sleep(0)
        slots.release()
        assert await waiter is True
        assert slots.locked()
        slots.release()
        await slots.acquire()
        assert slots.locked()
        assert len(asyncio.all_tasks()) == 1
    asyncio.run(run())


@pytest.mark.parametrize("missing", ["timings", "schedule", "overflow"])
def test_older_rows_never_invent_new_measurements(modules, missing, capsys):
    row = fixed_rate_row(modules)
    done = completion(row, fixed_rate_schedules=[schedule_record()])
    if missing == "timings":
        del row["fixed_rate_timings"]
    elif missing == "schedule":
        del done["fixed_rate_schedules"]
    else:
        del row["latency_overflow_count"]
    report = modules["latency_report"]
    cell = report._aggregate(Rows([row, done]), "baseline-", STAMP)[0][("read", "rust")]
    print(report._fmt_cell("read", "rust", cell))
    report._print_fixed_rate_details(cell)
    output = capsys.readouterr().out
    assert "unavailable" in output or "incomplete" in output


@pytest.mark.parametrize("issue", ["none", "wait", "unlaunched", "missing", "overflow"])
def test_point_read_gate_requires_unconstrained_complete_timing(modules, monkeypatch, issue):
    row = fixed_rate_row(modules, delay_ms=1, sdk_ms=1)
    schedule = schedule_record()
    if issue == "wait":
        schedule.update(limit_wait_count=1, limit_wait_ms=0.5)
    elif issue == "unlaunched":
        schedule.update(scheduled_count=2, not_launched_count=1)
    elif issue == "overflow":
        row = fixed_rate_row(modules, delay_ms=70_000, sdk_ms=1)
    done = completion(row, fixed_rate_schedules=[schedule])
    if issue == "missing":
        del done["fixed_rate_schedules"]
    report = modules["latency_report"]
    monkeypatch.setattr(report, "_connect", lambda: Rows([row, done]))
    monkeypatch.setattr(sys, "argv", [
        "latency_report", "--run-id", STAMP, "--point-read-gate", "--gate-backends", "rust"])
    with pytest.raises(SystemExit) as result:
        report.main()
    assert result.value.code == (0 if issue == "none" else 1)


def test_mixed_fixed_rate_schedule_is_counted_once(modules):
    read = fixed_rate_row(modules, workload_id=f"mixed-blend-rust-{STAMP}")
    patch = {**read, "operation": "PatchItem"}
    done = completion(read, summary_count=2, total_count=2, fixed_rate_schedules=[
        schedule_record(scheduled_count=2, launched_count=2)])
    per_op, blended, _ = modules["mixed_report"]._aggregate(Rows([read, patch, done]), "mixed-", STAMP)
    assert blended["rust"]["schedule"]["launched_count"] == 2
    assert blended["rust"]["window_s"] == read["window_seconds"]
    assert blended["rust"]["timings"]["success"]["sdk_call"]["hist"].total_count == 2
    assert per_op[("rust", "read")]["timings"]["success"]["sdk_call"]["hist"].total_count == 1


def test_timing_population_mismatch_is_rejected(modules):
    row = fixed_rate_row(modules)
    row["fixed_rate_timings"]["success"]["sdk_call"]["count"] = 2
    with pytest.raises(ValueError, match="population"):
        modules["latency_report"]._aggregate(Rows([row]), "baseline-", STAMP)


def test_schedule_population_mismatch_is_rejected(modules):
    row = fixed_rate_row(modules)
    done = completion(row, fixed_rate_schedules=[schedule_record(scheduled_count=2, launched_count=2)])
    with pytest.raises(ValueError, match="Launched"):
        modules["perf_validate"].check_completion(Rows([row, done]), "baseline-", STAMP)


def test_total_and_sdk_call_durations_cannot_be_pooled(modules):
    fixed = fixed_rate_row(modules)
    waiting = measurement(modules, config_arrival_rate=0)
    with pytest.raises(ValueError, match="Cannot combine"):
        modules["latency_report"]._aggregate(Rows([fixed, waiting]), "baseline-", STAMP)


def test_delete_setup_failure_is_not_a_successful_delete(modules):
    utils = modules["workload_utils"]
    stats = modules["perf_stats"].Stats()
    class Container:
        async def create_item(self, *args, **kwargs):
            raise RuntimeError("setup failed")
        async def delete_item(self, *args, **kwargs):
            pytest.fail("Delete issued after setup failed")
    asyncio.run(utils.delete_item_concurrently(Container(), [], 1, stats))
    summary = stats.drain_all()[0][0]
    assert summary["operation"] == "DeleteSetupCreate" and summary["errors"] == 1


def test_straddling_warmup_window_is_excluded(modules):
    assert not modules["perf_results"].post_warmup(
        {"elapsed_seconds": 610, "window_seconds": 60}, 600)
    assert modules["perf_results"].post_warmup(
        {"elapsed_seconds": 660, "window_seconds": 60}, 600)
