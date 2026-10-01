# The MIT License (MIT)
# Copyright (c) Microsoft Corporation. All rights reserved.
"""Offline checks of workload timing, report populations and result completeness."""

import asyncio
from concurrent.futures import ThreadPoolExecutor
import importlib
import json
import math
import os
from pathlib import Path
import shutil
import subprocess
import sys
import threading

import pytest

WORKLOADS = Path(__file__).resolve().parents[1] / "workloads"
STAMP = "20260919-120000000"


@pytest.fixture
def modules(monkeypatch):
    monkeypatch.syspath_prepend(str(WORKLOADS))
    return {name: importlib.import_module(name) for name in (
        "perf_stats", "perf_results", "perf_validate", "latency_report",
        "mixed_report", "coldstart_report", "client_service_duration_report", "perf_reporter",
        "perf_reporting_config", "perf_driver_commit_gate", "workload_utils",
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
        "runtime_backend": "AsyncBindingAdapter", "rust_execute_calls": 2,
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


@pytest.mark.parametrize("histogram,method", [
    ("success", "get_mean_value"),
    ("success", "get_value_at_percentile"),
    ("success", "encode"),
    ("server", "encode"),
    ("component", "encode"),
])
def test_stats_recording_continues_during_window_serialization(modules, monkeypatch, histogram, method):
    stats_module = modules["perf_stats"]
    monkeypatch.setattr(stats_module.time, "time", lambda: 1000.0)

    def record_window(stats, later=False):
        sdk_ms = 60_001 if later else 7
        stats.record_ru("ReadItem", 2 if later else 1)
        stats.record_server_ms("ReadItem", 4 if later else 2)
        stats.record("ReadItem", 3 + sdk_ms, delay_before_call_ms=3, sdk_call_ms=sdk_ms)
        stats.record_error("ReadItem", "throttled", "details", 429,
                           delay_before_call_ms=4, sdk_call_ms=5)
        stats.record("WriteItem", 2)
        stats.record_error("DeleteItem", "missing", "", 404)

    reference = stats_module.Stats()
    record_window(reference)
    expected_first = reference.drain_all()
    record_window(reference, later=True)
    expected_second = reference.drain_all()
    stats = stats_module.Stats()
    record_window(stats)
    stats.record_loop_lag(12)
    stats.record_schedule({"launched": 1})
    selected = {
        "success": stats._histograms["ReadItem"],
        "server": stats._server_histograms["ReadItem"],
        "component": stats._timings[("ReadItem", "success")]["sdk_call"]["hist"],
    }[histogram]
    original = getattr(selected, method)
    entered = threading.Event()
    release = threading.Event()

    def blocked(*args, **kwargs):
        entered.set()
        assert release.wait(10), "Test did not release histogram serialization"
        return original(*args, **kwargs)

    monkeypatch.setattr(selected, method, blocked)
    with ThreadPoolExecutor(max_workers=2) as pool:
        draining = pool.submit(stats.drain_all)
        try:
            assert entered.wait(5), "Reporter did not reach histogram serialization"
            # This must finish while the old window is still blocked, not merely
            # after serialization completes and releases the old recording lock.
            writing = pool.submit(record_window, stats, True)
            writing.result(timeout=2)
            assert not draining.done()
        finally:
            release.set()
        assert draining.result(timeout=5) == expected_first
    assert stats.drain_all() == expected_second
    assert stats.drain_all() == ([], [])
    assert stats.first_ms_snapshot() == {"ReadItem": [10, 60_004], "WriteItem": [2, 2]}
    assert stats.drain_loop_lag() == 12
    assert stats.schedule_snapshot() == [{"launched": 1}]


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


@pytest.mark.parametrize("backend", ["rust", "core-python"])
def test_latency_labels_explain_counter_and_charge_coverage(modules, backend):
    row = measurement(modules, workload_id=f"baseline-read-{backend}-{STAMP}",
                      config_backend=backend, ru_sum=2, ru_count=1)
    report = modules["latency_report"]
    cells, _ = report._aggregate(Rows([row]), "baseline-", STAMP)
    text = report._fmt_cell("read", backend, cells[("read", backend)])
    assert "RU/sample=" in text and "ru_samples=1" in text
    assert "terminal_429=" in text and "recorded_non_initial=" in text
    assert "RU/op=" not in text and "retries=" not in text
    if backend == "core-python":
        assert "recorded_non_initial= n/a" in text


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


@pytest.mark.parametrize("name", ["BindingAdapter", "AsyncBindingAdapter", "RustBinding", "AsyncRustBinding"])
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


def test_cargo_build_details_use_resolved_git_revision(modules, monkeypatch):
    build_details = importlib.import_module("perf_build_details")
    def metadata(command, **kwargs):
        assert command == ["cargo", "metadata", "--locked", "--offline", "--format-version", "1"]
        return json.dumps({"packages": [{
            "name": "azure_data_cosmos_driver",
            "source": "git+https://example.invalid/driver?rev=short#" + "a" * 40,
        }]})
    monkeypatch.setattr(build_details.subprocess, "check_output", metadata)
    assert build_details.driver_commit() == "a" * 40


@pytest.mark.parametrize("source", [None, "path+local", "registry+crates.io", "git+url#short"])
def test_cargo_build_details_reject_unidentified_source(modules, monkeypatch, source):
    build_details = importlib.import_module("perf_build_details")
    monkeypatch.setattr(build_details.subprocess, "check_output", lambda *args, **kwargs:
                        json.dumps({"packages": [{"name": "azure_data_cosmos_driver", "source": source}]}))
    with pytest.raises(ValueError, match="locked Git"):
        build_details.driver_commit()


@pytest.mark.parametrize("relative_path", [
    "azure/cosmos/client.py",
    "tests/workloads/profiling_config.env.template",
    "tests/workloads/workload_config_helpers.py",
])
def test_source_fingerprint_catches_uncommitted_edits(modules, monkeypatch, tmp_path, relative_path):
    build_details = importlib.import_module("perf_build_details")
    monkeypatch.setattr(build_details, "PACKAGE_ROOT", tmp_path)
    source = tmp_path / relative_path
    source.parent.mkdir(parents=True)
    source.write_text("value = 1\n")
    before = build_details.source_digest()
    assert before == build_details.source_digest()
    source.write_text("value = 2\n")
    assert build_details.source_digest() != before


@pytest.mark.parametrize("profiling_session_id", [None, STAMP, "20260918-120000000"])
def test_manifest_escapes_values_and_excludes_credentials(modules, monkeypatch, tmp_path, profiling_session_id):
    manifest = importlib.import_module("perf_manifest")
    monkeypatch.setattr(manifest, "driver_commit", lambda: "a" * 40)
    monkeypatch.setattr(manifest, "source_digest", lambda: "b" * 64)
    monkeypatch.setattr(manifest, "extension_details", lambda: {"rust_extension_sha256": "c" * 64})
    monkeypatch.setattr(manifest.subprocess, "check_output", lambda *args, **kwargs: 'value "with quotes"')
    monkeypatch.setenv("COSMOS_DATABASE", 'db"quoted')
    monkeypatch.setenv("COSMOS_KEY", "synthetic-key-must-not-be-written")
    monkeypatch.setenv("RESULTS_COSMOS_KEY", "synthetic-results-key-must-not-be-written")
    monkeypatch.setenv("PROFILING_CONFIG_PATH", "/home/test/profiling_config.env")
    monkeypatch.setenv("PROFILING_CONFIG_SHA256", "d" * 64)
    monkeypatch.delenv("PROFILING_SESSION_ID", raising=False)
    if profiling_session_id:
        monkeypatch.setenv("PROFILING_SESSION_ID", profiling_session_id)
    manifest.write_manifest(tmp_path, STAMP, "test")
    text = (tmp_path / f"manifest-{STAMP}.json").read_text()
    assert json.loads(text)["account"]["database"] == 'db"quoted'
    record = json.loads(text)
    assert record["stamp"] == STAMP
    assert record["build"]["python_executable"] == sys.executable
    assert record["build"]["python_environment"] == sys.prefix
    assert record.get("profiling_session_id") == profiling_session_id
    assert ("profiling_session_id" in record) == (profiling_session_id is not None)
    assert record["configuration"] == {
        "path": "/home/test/profiling_config.env", "sha256": "d" * 64,
    }
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


def fake_profiling_environment(tmp_path, name="venvs/perfdrill"):
    activate = tmp_path / name / "bin" / "activate"
    activate.parent.mkdir(parents=True)
    activate.write_text(
        'export VIRTUAL_ENV="$(cd -- "$(dirname "${BASH_SOURCE[0]}")/.." && pwd -P)"\n'
        'export PATH="$VIRTUAL_ENV/bin:$PATH"\n',
        encoding="utf-8",
    )
    interpreter = activate.with_name("python3")
    interpreter.write_text(
        '#!/usr/bin/env bash\nexec "$PROFILING_TEST_PYTHON" "$@"\n', encoding="utf-8",
    )
    interpreter.chmod(0o755)
    return activate


def embedded_python(script, index=0):
    heredoc = (WORKLOADS / script).read_text(encoding="utf-8").split("<<'PY'")[index + 1]
    return heredoc.split("\n", 1)[1].split("\nPY", 1)[0]


@pytest.mark.parametrize("selection", ["default", "candidate"])
def test_profiling_environment_selection_survives_child_processes(tmp_path, selection):
    shutil.copyfile(WORKLOADS / "profiling_common.sh", tmp_path / "profiling_common.sh")
    for name in ("venvs/perfdrill", "candidate environment"):
        fake_profiling_environment(tmp_path, name)
    selected = "venvs/perfdrill" if selection == "default" else "candidate environment"
    command = (
        'export HOME="$PWD"\nunset PROFILING_VENV\n'
        'export VIRTUAL_ENV="$HOME/unrelated-active-environment"\n'
        'source ./profiling_common.sh\n'
    )
    if selection == "candidate":
        command += 'PROFILING_VENV="$PWD/candidate environment"\n'
    command += (
        'profiling_activate_python || exit $?\n'
        f'[[ "$VIRTUAL_ENV" -ef "$PWD/{selected}" ]] || exit 3\n'
        '[[ "$PROFILING_VENV" == "$VIRTUAL_ENV" ]] || exit 4\n'
        "bash --noprofile --norc -c 'source ./profiling_common.sh; "
        'profiling_activate_python || exit $?; '
        f'[[ "$VIRTUAL_ENV" -ef "$PWD/{selected}" ]]\'\n'
    )
    result = subprocess.run([bash_executable(), "-c", command], cwd=tmp_path,
                            capture_output=True, text=True, timeout=15)
    assert result.returncode == 0, result.stdout + result.stderr


@pytest.mark.parametrize("defect", [
    "empty", "relative", "missing", "interpreter", "failed", "wrong", "unset", "wrong_path",
])
def test_profiling_environment_selection_fails_without_falling_back(tmp_path, defect):
    shutil.copyfile(WORKLOADS / "profiling_common.sh", tmp_path / "profiling_common.sh")
    activate = fake_profiling_environment(tmp_path, "candidate")
    scripts = {
        "failed": "return 1\n",
        "wrong": 'export VIRTUAL_ENV="$HOME"\n',
        "unset": "unset VIRTUAL_ENV\n",
        "wrong_path": 'export VIRTUAL_ENV="$HOME/candidate"\n',
    }
    if defect in scripts:
        activate.write_text(scripts[defect], encoding="utf-8")
    elif defect == "missing":
        activate.unlink()
    elif defect == "interpreter":
        activate.with_name("python3").unlink()
    selected = {"empty": '""', "relative": '"candidate"'}.get(defect, '"$PWD/candidate"')
    command = (
        'export HOME="$PWD"\nsource ./profiling_common.sh\n'
        'export VIRTUAL_ENV="$HOME/previous-environment"\n'
        f'PROFILING_VENV={selected}\nprofiling_activate_python\n'
    )
    result = subprocess.run([bash_executable(), "-c", command], cwd=tmp_path,
                            capture_output=True, text=True, timeout=15)
    assert result.returncode == 2, result.stdout + result.stderr
    assert "ERROR:" in result.stderr


@pytest.mark.parametrize("field", ["python_executable", "python_environment"])
@pytest.mark.parametrize("matching", [False, True])
def test_session_validation_checks_the_recorded_python_environment(
    modules, monkeypatch, tmp_path, field, matching
):
    details = importlib.import_module("perf_build_details")
    extension = {
        "rust_extension_sha256": "a" * 64,
        "rust_extension_python_commit": "b" * 40,
        "rust_extension_driver_commit": "c" * 40,
    }
    current = {"python_executable": sys.executable, "python_environment": sys.prefix}
    monkeypatch.setattr(details, "extension_details", lambda: extension)
    monkeypatch.setattr(details, "source_digest", lambda: "d" * 64)
    manifest = {
        "stamp": STAMP, "phase": "read-baseline",
        "account": {"uri": "https://example.invalid", "database": "db", "container": "items"},
        "build": {"source_sha256": "d" * 64, **extension,
                  field: current[field] if matching else "different-environment"},
    }
    path = tmp_path / "manifest.json"
    path.write_text(json.dumps(manifest), encoding="utf-8")
    monkeypatch.setattr(sys, "argv", [
        "-", str(path), STAMP, "read-baseline", "https://example.invalid", "db", "items",
    ])
    code = compile(embedded_python("profiling_common.sh", index=1), "session-validation", "exec")
    if matching:
        exec(code, {})
    else:
        with pytest.raises(SystemExit) as error:
            exec(code, {})
        assert error.value.code == 1


@pytest.mark.parametrize("saved_name", ["PROFILING_SESSION_ID", "RUN_ID", "both", "missing", "conflicting"])
@pytest.mark.parametrize("manifest_id", [None, STAMP, "20260918-120000000"])
@pytest.mark.parametrize("configuration_hash", [None, "same", "changed"])
@pytest.mark.parametrize("saved_names", ["current", "legacy", "conflicting"])
def test_profiling_session_identifier_restore(tmp_path, saved_name, manifest_id, configuration_hash, saved_names):
    shutil.copyfile(WORKLOADS / "profiling_common.sh", tmp_path / "profiling_common.sh")
    folder = tmp_path / "session"
    folder.mkdir()
    settings = ['export PROFILING_SESSION_DIR="$PWD/session"', 'export PROFILING_SESSION_LABEL="point-read-profile"']
    if saved_names == "legacy":
        settings = ['export ARTIFACTS="$PWD/session"', 'export PERF_PHASE="point-read-profile"']
    elif saved_names == "conflicting":
        settings.append('export PERF_PHASE="other-label"')
    if saved_name in ("PROFILING_SESSION_ID", "both", "conflicting"):
        settings.append(f'export PROFILING_SESSION_ID="{STAMP}"')
    if saved_name in ("RUN_ID", "both", "conflicting"):
        old_id = "20260918-120000000" if saved_name == "conflicting" else STAMP
        settings.append(f'export RUN_ID="{old_id}"')
    (folder / "session.env").write_text("\n".join(settings) + "\n", encoding="utf-8")
    extension = {
        "rust_extension_sha256": "a" * 64,
        "rust_extension_python_commit": "b" * 40,
        "rust_extension_driver_commit": "c" * 40,
    }
    manifest = {
        "stamp": STAMP, "phase": "point-read-profile",
        "account": {"uri": "https://example.invalid", "database": "db", "container": "items"},
        "build": {"source_sha256": "d" * 64, **extension},
    }
    if manifest_id is not None:
        manifest["profiling_session_id"] = manifest_id
    if configuration_hash is not None:
        manifest["configuration"] = {"sha256": configuration_hash}
    (folder / f"manifest-{STAMP}.json").write_text(json.dumps(manifest), encoding="utf-8")
    (tmp_path / "perf_build_details.py").write_text(
        f"def source_digest(): return {'d' * 64!r}\n"
        f"def extension_details(): return {extension!r}\n", encoding="utf-8",
    )
    before = {path.name: path.read_bytes() for path in folder.iterdir()}
    env = {**os.environ, "PROFILING_TEST_PYTHON": Path(sys.executable).as_posix(),
           "COSMOS_URI": "https://example.invalid", "COSMOS_DATABASE": "db", "COSMOS_CONTAINER": "items",
           "RUN_ID": "stale-parent-id", "PROFILING_SESSION_ID": STAMP,
           "PROFILING_CONFIG_SHA256": "same"}
    command = (
        'source ./profiling_common.sh\n'
        'python3() { "$PROFILING_TEST_PYTHON" "$@"; }\n'
        'profiling_verify_extension_build() { return 0; }\n'
        'ARTIFACTS="stale-parent-directory"\nPERF_PHASE="stale-parent-label"\n'
        'profiling_load_session "$PWD/session" || exit $?\n'
        '[[ ! -v ARTIFACTS && ! -v PERF_PHASE ]] || exit 3\n'
        'printf "loaded=%s\\n" "$PROFILING_SESSION_ID"\n'
        'python3 -c \'import os; print("exported=" + os.environ["PROFILING_SESSION_ID"])\'\n'
    )
    result = subprocess.run([bash_executable(), "-c", command], cwd=tmp_path, env=env,
                            capture_output=True, text=True, timeout=15)
    valid = (saved_name not in ("missing", "conflicting") and manifest_id in (None, STAMP)
             and configuration_hash in (None, "same") and saved_names != "conflicting")
    if valid:
        assert result.returncode == 0, result.stdout + result.stderr
        assert f"loaded={STAMP}" in result.stdout and f"exported={STAMP}" in result.stdout
    else:
        assert result.returncode != 0, result.stdout + result.stderr
        assert "ERROR:" in result.stderr
    assert before == {path.name: path.read_bytes() for path in folder.iterdir()}


def test_profiling_session_creation_uses_explicit_identifier(tmp_path):
    shutil.copyfile(WORKLOADS / "profiling_create_session.sh", tmp_path / "profiling_create_session.sh")
    (tmp_path / "profiling_common.sh").write_text(
        "profiling_validate_phase() { return 0; }\n"
        "profiling_load_env() { return 0; }\n"
        "profiling_verify_extension_build() { return 0; }\n"
        "profiling_load_session() { source \"$1/session.env\"; }\n"
        'python3() { "$PROFILING_TEST_PYTHON" "$@"; }\n'
        'write_run_manifest() { python3 write-manifest.py "$@"; }\n',
        encoding="utf-8",
    )
    (tmp_path / "write-manifest.py").write_text(
        "import json, os, pathlib, sys\n"
        "folder, stamp, phase = sys.argv[1:]\n"
        "record = {'stamp': stamp, 'phase': phase, "
        "'profiling_session_id': os.environ['PROFILING_SESSION_ID'], 'build': {"
        "'git_commit': 'a'*40, 'rust_driver_commit': 'b'*40, "
        "'rust_extension_path': 'test.so', 'rust_extension_python_commit': 'a'*40, "
        "'rust_extension_driver_commit': 'b'*40, 'rust_extension_has_operation_counter': 'True'}}\n"
        "(pathlib.Path(folder) / f'manifest-{stamp}.json').write_text(json.dumps(record))\n",
        encoding="utf-8",
    )
    env = {**os.environ, "PROFILING_TEST_PYTHON": Path(sys.executable).as_posix(),
           "COSMOS_DATABASE": "db", "COSMOS_CONTAINER": "items", "RUN_ID": "old-parent"}
    result = subprocess.run([bash_executable(), "profiling_create_session.sh", "test"], cwd=tmp_path,
                            env=env, capture_output=True, text=True, timeout=15)
    assert result.returncode == 0, result.stdout + result.stderr
    folder, = (tmp_path / "artifacts").iterdir()
    manifest_path, = folder.glob("manifest-*.json")
    manifest = json.loads(manifest_path.read_text())
    identifier = manifest["profiling_session_id"]
    assert manifest["stamp"] == identifier and folder.name == f"test-{identifier}"
    settings = (folder / "session.env").read_text()
    assert f'export PROFILING_SESSION_ID="{identifier}"' in settings
    assert "PROFILING_SESSION_DIR=" in settings and "PROFILING_SESSION_LABEL=" in settings
    assert not any(name in settings for name in ("RUN_ID", "ARTIFACTS", "PERF_PHASE"))
    assert f"profiling_session_id={identifier}" in (folder / "run.txt").read_text()
    assert f"--profiling-session-id {identifier}" in result.stdout


@pytest.mark.parametrize("name", ["latency_report", "client_service_duration_report", "perf_validate"])
@pytest.mark.parametrize("flag", ["--profiling-session-id", "--run-id", "--stamp"])
def test_profiling_report_identifier_selects_existing_rows(modules, monkeypatch, name, flag):
    module = modules[name]
    selections = []

    class SelectedRows(Rows):
        def query_items(self, query, **kwargs):
            assert "ENDSWITH" in query
            assert kwargs["parameters"][-1]["value"] == STAMP
            selections.append(kwargs["parameters"][-1]["value"])
            return []

    monkeypatch.setattr(module, "_connect", lambda: SelectedRows())
    monkeypatch.setattr(sys, "argv", [name, flag, STAMP])
    with pytest.raises(SystemExit) as exc:
        module.main()
    assert exc.value.code != 0  # No measurements, rather than an argument or selector failure.
    assert selections


@pytest.mark.parametrize("name", ["latency_report", "client_service_duration_report", "perf_validate"])
def test_profiling_report_rejects_conflicting_identifier_flags(modules, monkeypatch, name):
    def unexpected_connection():
        pytest.fail("Conflicting identifiers must fail before contacting the results container")

    module = modules[name]
    monkeypatch.setattr(module, "_connect", unexpected_connection)
    monkeypatch.setattr(sys, "argv", [
        name, "--profiling-session-id", STAMP, "--run-id", "20260918-120000000"])
    with pytest.raises(SystemExit) as exc:
        module.main()
    assert exc.value.code == 2


def test_build_check_accepts_current_counter_exports(monkeypatch):
    import types
    import azure.cosmos as sdk

    extension = types.SimpleNamespace(
        __file__="synthetic-extension",
        _debug_operation_count=lambda: 0,
        _debug_attempt_count=lambda: 0,
        _debug_retry_count=lambda: 0,
    )
    monkeypatch.setattr(sdk, "_rust", extension, raising=False)
    exec(compile(embedded_python("profiling_build_extension.sh"), "build-check", "exec"), {})


@pytest.mark.parametrize("paths", [["/partition_key"], ["/id"], [], ["/partition_key", "/id"], None])
def test_target_checks_results_container_schema(monkeypatch, paths):
    import azure.cosmos as sdk
    from azure.cosmos.exceptions import CosmosResourceNotFoundError

    closed = []

    class Client:
        def __init__(self, uri, key, **kwargs):
            assert (uri, key, kwargs) == (
                "https://results.invalid", "synthetic-key", {"_backend": "core-python"})

        def get_database_client(self, database):
            assert database == "results-db"
            return self

        def get_container_client(self, container):
            assert container == "results"
            return self

        def read(self):
            if paths is None:
                raise CosmosResourceNotFoundError(status_code=404, message="missing results container")
            return {"partitionKey": {"paths": paths}}

        def close(self):
            closed.append(True)

    monkeypatch.setattr(sdk, "CosmosClient", Client)
    for name, value in {"URI": "https://results.invalid", "KEY": "synthetic-key",
                        "DATABASE": "results-db", "CONTAINER": "results"}.items():
        monkeypatch.setenv("RESULTS_COSMOS_" + name, value)
    code = compile(embedded_python("profiling_check_target.sh", 1), "results-check", "exec")
    if paths == ["/partition_key"]:
        exec(code, {})
    elif paths is None:
        with pytest.raises(CosmosResourceNotFoundError):
            exec(code, {})
    else:
        with pytest.raises(SystemExit, match="partition-key mismatch"):
            exec(code, {})
    assert closed == [True]


@pytest.mark.parametrize("override", [False, True])
def test_baseline_keeps_validated_target_and_range(tmp_path, override):
    script = "profiling_run_read_baseline.sh"
    shutil.copyfile(WORKLOADS / script, tmp_path / script)
    (tmp_path / "profiling_common.sh").write_text(
        "profiling_load_env() { :; }\n"
        "profiling_load_session() { :; }\n"
        "perf_require_positive() { :; }\n"
        "profiling_require_read_workload() { :; }\n"
        "perf_create_log_dir() { mkdir \"$1\"; }\n"
        "write_run_manifest() { echo \"$WORKLOAD_ARRIVAL_RATE\" > manifest-rate.txt; }\n"
        "perf_check_run() { :; }\n"
        "python3() { printf '%s\\n' \"$*\" > report-arguments.txt; }\n"
        "timeout() { printf '%s\\n' \"$COSMOS_DATABASE/$COSMOS_CONTAINER/"
        "$COSMOS_MAX_ITEM_INDEX/$WORKLOAD_ARRIVAL_RATE\" >> launched.txt; }\n",
        encoding="utf-8",
    )
    env = {**os.environ, "PROFILING_SESSION_ID": STAMP, "PROFILING_SESSION_DIR": tmp_path.as_posix(),
           "COSMOS_DATABASE": "verified-db", "COSMOS_CONTAINER": "verified-container",
           "COSMOS_MAX_ITEM_INDEX": "42", "WORKLOAD_ARRIVAL_RATE": "100",
           "RESULTS_COSMOS_DATABASE": "results-db", "RESULTS_COSMOS_CONTAINER": "results",
           "BASELINE_BACKENDS": "core-python rust", "BASELINE_COMPARISONS": "1"}
    for name in ("BASELINE_DATABASE", "BASELINE_CONTAINER", "BASELINE_READ_RPS"):
        env.pop(name, None)
    if override:
        env["BASELINE_DATABASE"] = "not-verified"
    result = subprocess.run([bash_executable(), script, "1"], cwd=tmp_path, env=env,
                            capture_output=True, text=True, timeout=15)
    if override:
        assert result.returncode != 0
        assert not (tmp_path / "launched.txt").exists()
    else:
        assert result.returncode == 0, result.stdout + result.stderr
        assert (tmp_path / "launched.txt").read_text().splitlines() == [
            "verified-db/verified-container/42/100", "verified-db/verified-container/42/100",
        ]
        assert (tmp_path / "manifest-rate.txt").read_text().strip() == "100"
        assert "--expected-rps 100" in (tmp_path / "report-arguments.txt").read_text()
        assert "--latency-metric sdk-call" in (tmp_path / "report-arguments.txt").read_text()
        assert "--max-p99-ms 4 " in (tmp_path / "report-arguments.txt").read_text()


@pytest.fixture
def baseline_batch(tmp_path):
    folder = tmp_path / "batch workspace"
    folder.mkdir()
    for script in ("profiling_run_read_baseline.sh", "profiling_create_session.sh", "perf_common.sh"):
        shutil.copyfile(WORKLOADS / script, folder / script)
    (folder / "profiling_common.sh").write_text(
        """source ./perf_common.sh
profiling_load_env() { :; }
profiling_validate_phase() { :; }
profiling_require_read_workload() { :; }
profiling_verify_extension_build() {
  if [[ "${BATCH_FAIL_STAGE:-}" == create ]]; then
    echo "ERROR: simulated session creation failure" >&2
    return 1
  fi
}
profiling_load_session() {
  if [[ -f setup-changed.txt ]]; then
    echo "ERROR: simulated changed source/configuration" >&2
    return 1
  fi
  source "$1/session.env"
  if [[ "${BATCH_FAIL_STAGE:-}" == ambiguous && "$PROFILING_SESSION_LABEL" == read-baseline ]]; then
    echo "artifacts=unexpected-second-directory"
  fi
}
write_run_manifest() { python3 write-manifest.py "$@"; }
perf_check_run() {
  echo "$2/$4" >> integrity-calls.txt
  [[ "${BATCH_FAIL_STAGE:-}" != integrity || $(wc -l < integrity-calls.txt) -ne 2 ]]
}
python3() {
  if [[ "$1" == latency_report.py ]]; then
    echo "$*" >> report-calls.txt
    if [[ "${BATCH_FAIL_STAGE:-}" == changed ]]; then touch setup-changed.txt; fi
    [[ "${BATCH_FAIL_STAGE:-}" != report || $(wc -l < report-calls.txt) -ne 2 ]]
  else
    "$PROFILING_TEST_PYTHON" "$@"
  fi
}
timeout() {
  echo "$PROFILING_SESSION_ID/$COSMOS_BACKEND/$COSMOS_DATABASE/$COSMOS_CONTAINER/$COSMOS_MAX_ITEM_INDEX/$WORKLOAD_ARRIVAL_RATE/$*" >> launched.txt
  if [[ "${BATCH_FAIL_STAGE:-}" == interrupt ]]; then kill -TERM "$PPID"; fi
  [[ "${BATCH_FAIL_STAGE:-}" != process || $(wc -l < launched.txt) -ne 3 ]]
}
""", encoding="utf-8")
    (folder / "write-manifest.py").write_text(
        "import json, os, pathlib, sys\n"
        "folder, stamp, phase = sys.argv[1:]\n"
        "record = {'stamp': stamp, 'phase': phase, "
        "'profiling_session_id': os.environ['PROFILING_SESSION_ID'], 'build': {"
        "'git_commit': 'a'*40, 'rust_driver_commit': 'b'*40, "
        "'rust_extension_path': 'test.so', 'rust_extension_python_commit': 'a'*40, "
        "'rust_extension_driver_commit': 'b'*40, 'rust_extension_has_operation_counter': 'True'}}\n"
        "(pathlib.Path(folder) / f'manifest-{stamp}.json').write_text(json.dumps(record))\n",
        encoding="utf-8")
    source = folder / "prepared-session"
    source.mkdir()
    (source / "session.env").write_text(
        f'export PROFILING_SESSION_ID="{STAMP}"\n'
        'export PROFILING_SESSION_DIR="$PWD/prepared-session"\n'
        'export PROFILING_SESSION_LABEL="read-preparation"\n', encoding="utf-8")
    (source / "preparation-completion.txt").write_text("preparation_complete=true\n", encoding="utf-8")
    env = {name: value for name, value in os.environ.items()
           if not name.startswith(("BASELINE_", "PROFILING_", "BATCH_FAIL_"))}
    env.update({
        "PROFILING_SESSION_ID": STAMP, "PROFILING_SESSION_DIR": source.as_posix(),
        "PROFILING_TEST_PYTHON": Path(sys.executable).as_posix(),
        "COSMOS_DATABASE": "verified-db", "COSMOS_CONTAINER": "verified-items",
        "COSMOS_MAX_ITEM_INDEX": "42", "WORKLOAD_ARRIVAL_RATE": "250",
        "RESULTS_COSMOS_DATABASE": "results-db", "RESULTS_COSMOS_CONTAINER": "results",
    })
    return folder, env


def run_baseline_batch(folder, env):
    return subprocess.run(
        [bash_executable(), "profiling_run_read_baseline.sh", "480"],
        cwd=folder, env=env, capture_output=True, text=True, timeout=60)


def read_baseline_batch(folder):
    batch = folder / "prepared-session" / f"baseline-batch-{STAMP}"
    summary = dict(line.split("=", 1) for line in (batch / "batch-summary.env").read_text().splitlines())
    rows = [line.split("\t") for line in (batch / "comparisons.tsv").read_text().splitlines()[1:]]
    return summary, rows


@pytest.mark.parametrize("count,backends", [(None, None), ("2", "rust core-python"), ("3", "rust")])
def test_baseline_batch_isolates_sessions_and_retains_evidence(baseline_batch, count, backends):
    folder, env = baseline_batch
    if count is not None:
        env["BASELINE_COMPARISONS"] = count
    if backends is not None:
        env["BASELINE_BACKENDS"] = backends
    result = run_baseline_batch(folder, env)
    assert result.returncode == 0, result.stdout + result.stderr
    expected = int(count or 5)
    engines = (backends or "core-python rust").split()
    summary, rows = read_baseline_batch(folder)
    assert summary["requested_comparisons"] == summary["completed_comparisons"] == str(expected)
    assert summary["passed_comparisons"] == summary["attempted_comparisons"] == str(expected)
    assert summary["status"] == "passed" and summary["exit_status"] == "0"
    assert summary["duration_seconds_per_backend"] == "480"
    assert len(rows) == expected and len({row[1] for row in rows}) == expected
    assert rows[0][1] == STAMP
    calls = (folder / "launched.txt").read_text().splitlines()
    assert len(calls) == expected * len(engines)
    report_calls = (folder / "report-calls.txt").read_text().splitlines()
    assert len(report_calls) == expected
    assert all("--latency-metric sdk-call" in call for call in report_calls)
    for index, row in enumerate(rows):
        number, identifier, _, status, rc = row
        assert number == str(index + 1) and status == "passed" and rc == "0"
        session = folder / "prepared-session" if index == 0 else folder / "artifacts" / f"read-baseline-{identifier}"
        logs = session / f"light-load-baseline-{identifier}"
        assert (session / "session.env").is_file()
        assert (logs / "baseline-run.log").is_file()
        assert (logs / "latency-report.txt").is_file()
        assert (logs / f"manifest-{identifier}.json").is_file()
        assert (logs / "expected-workloads.txt").read_text().splitlines() == [
            f"baseline-read-{engine}-{identifier}" for engine in engines]
        for offset, engine in enumerate(engines):
            assert calls[index * len(engines) + offset].startswith(
                f"{identifier}/{engine}/verified-db/verified-items/42/250/")
            assert "480s python3 workload.py" in calls[index * len(engines) + offset]
    assert (folder / "prepared-session" / "preparation-completion.txt").read_text() == "preparation_complete=true\n"


@pytest.mark.parametrize("stage,completed", [
    ("process", 2), ("integrity", 2), ("report", 2), ("create", 1), ("changed", 1), ("ambiguous", 1),
])
def test_baseline_batch_stops_after_failure(baseline_batch, stage, completed):
    folder, env = baseline_batch
    env["BATCH_FAIL_STAGE"] = stage
    result = run_baseline_batch(folder, env)
    assert result.returncode != 0, result.stdout + result.stderr
    summary, rows = read_baseline_batch(folder)
    assert summary["requested_comparisons"] == "5"
    assert summary["attempted_comparisons"] == "2"
    assert summary["completed_comparisons"] == str(completed)
    assert summary["passed_comparisons"] == "1" and summary["status"] == "failed"
    assert len(rows) == 2 and rows[0][3] == "passed"
    assert rows[1][3] == ("setup_failed" if completed == 1 else "failed")
    assert len((folder / "launched.txt").read_text().splitlines()) == completed * 2
    assert "ERROR:" in result.stderr + result.stdout


def test_baseline_single_comparison_preserves_original_layout(baseline_batch):
    folder, env = baseline_batch
    env["BASELINE_COMPARISONS"] = "1"
    result = run_baseline_batch(folder, env)
    assert result.returncode == 0, result.stdout + result.stderr
    session = folder / "prepared-session"
    assert (session / f"light-load-baseline-{STAMP}" / "latency-report.txt").is_file()
    assert not (session / f"baseline-batch-{STAMP}").exists()
    assert not (folder / "artifacts").exists()
    assert len((folder / "launched.txt").read_text().splitlines()) == 2


def test_baseline_batch_records_interruption(baseline_batch):
    folder, env = baseline_batch
    env["BATCH_FAIL_STAGE"] = "interrupt"
    result = run_baseline_batch(folder, env)
    assert result.returncode == 143, result.stdout + result.stderr
    summary, rows = read_baseline_batch(folder)
    assert summary["status"] == "failed" and summary["passed_comparisons"] == "0"
    assert summary["attempted_comparisons"] == "1"
    assert len(rows) == 1 and rows[0][3:] == ["interrupted", "143"]


def test_baseline_batch_refuses_existing_evidence(baseline_batch):
    folder, env = baseline_batch
    env["BASELINE_COMPARISONS"] = "2"
    first = run_baseline_batch(folder, env)
    assert first.returncode == 0, first.stdout + first.stderr
    batch = folder / "prepared-session" / f"baseline-batch-{STAMP}"
    before = {path.name: path.read_bytes() for path in batch.iterdir()}
    calls = (folder / "launched.txt").read_bytes()
    second = run_baseline_batch(folder, env)
    assert second.returncode != 0
    assert before == {path.name: path.read_bytes() for path in batch.iterdir()}
    assert calls == (folder / "launched.txt").read_bytes()


@pytest.mark.parametrize("count", ["", "0", "-1", "1.5", "abc", "05", "1+1", "18446744073709551617"])
def test_baseline_rejects_invalid_comparison_count_before_setup(tmp_path, count):
    script = "profiling_run_read_baseline.sh"
    shutil.copyfile(WORKLOADS / script, tmp_path / script)
    result = subprocess.run(
        [bash_executable(), script], cwd=tmp_path,
        env={**os.environ, "BASELINE_COMPARISONS": count},
        capture_output=True, text=True, timeout=15)
    assert result.returncode == 2
    assert "BASELINE_COMPARISONS" in result.stderr
    assert "profiling_common.sh" not in result.stderr


def profiling_config_test_setup(tmp_path):
    template = (WORKLOADS / "profiling_config.env.template").read_text()
    values = {
        "COSMOS_URI": "https://test.invalid/", "COSMOS_DATABASE": "db", "COSMOS_CONTAINER": "items",
        "RESULTS_COSMOS_URI": "https://results.invalid/",
        "RESULTS_COSMOS_DATABASE": "db", "RESULTS_COSMOS_CONTAINER": "results",
    }
    for name, value in values.items():
        template = template.replace(f'export {name}=""', f'export {name}="{value}"')
    config = tmp_path / "profiling_config.env"
    config.write_text(template, encoding="utf-8")
    env = {name: value for name, value in os.environ.items() if not name.startswith(
        ("COSMOS_", "RESULTS_", "WORKLOAD_", "PERF_", "PROFILING_", "BASELINE_", "EXPECT_", "MEMRAY_"))}
    env["PROFILING_TEST_PYTHON"] = Path(sys.executable).as_posix()
    prefix = (
        'set -u\nexport HOME="$PWD"\n'
        f'source "{(WORKLOADS / "profiling_common.sh").as_posix()}"\n'
        'python3() { "$PROFILING_TEST_PYTHON" "$@"; }\n'
    )
    return config, env, prefix


@pytest.mark.parametrize("inherited", [None, "250", "350", ""])
def test_profiling_config_is_authoritative(tmp_path, inherited):
    import hashlib
    config, env, prefix = profiling_config_test_setup(tmp_path)
    if inherited is not None:
        env["WORKLOAD_ARRIVAL_RATE"] = inherited
    result = subprocess.run(
        [bash_executable(), "-c", prefix + 'profiling_load_config || exit $?\n'
         'printf "%s/%s/%s" "$WORKLOAD_ARRIVAL_RATE" "$WORKLOAD_MAX_INFLIGHT" "$PROFILING_CONFIG_SHA256"'],
        cwd=tmp_path, env=env, capture_output=True, text=True, timeout=15)
    if inherited in (None, "250"):
        assert result.returncode == 0, result.stdout + result.stderr
        assert result.stdout == f"250/10000/{hashlib.sha256(config.read_bytes()).hexdigest()}"
    else:
        assert result.returncode == 2
        assert "inherited WORKLOAD_ARRIVAL_RATE conflicts" in result.stderr


@pytest.mark.parametrize("current,legacy,expected", [
    (None, None, True), ("true", None, True), ("false", None, False),
    (None, "true", False), (None, "false", True),
    ("true", "false", True), ("false", "true", False),
    ("true", "true", None), ("false", "false", None),
    ("invalid", None, None), (None, "invalid", None), ("", None, None),
])
def test_lifecycle_python_and_shell_conversion(modules, tmp_path, current, legacy, expected):
    helper = importlib.import_module("workload_config_helpers")
    values = {}
    if current is not None:
        values["WORKLOAD_MANAGE_CLIENT_LIFECYCLE"] = current
    if legacy is not None:
        values["WORKLOAD_SKIP_CLOSE"] = legacy
    if expected is None:
        with pytest.raises(ValueError):
            helper.manage_client_lifecycle(values)
    else:
        assert helper.manage_client_lifecycle(values) is expected
    env = {key: value for key, value in os.environ.items() if key not in (
        "WORKLOAD_MANAGE_CLIENT_LIFECYCLE", "WORKLOAD_SKIP_CLOSE")}
    result = subprocess.run(
        [bash_executable(), "-c",
         f'source "{(WORKLOADS / "perf_common.sh").as_posix()}"\n'
         'perf_resolve_client_lifecycle || exit $?\n'
         '[[ ! -v WORKLOAD_SKIP_CLOSE ]] || exit 3\n'
         'printf "%s" "$WORKLOAD_MANAGE_CLIENT_LIFECYCLE"'],
        cwd=tmp_path, env={**env, **values}, capture_output=True, text=True, timeout=15)
    assert result.returncode == (2 if expected is None else 0), result.stderr
    if expected is not None:
        assert result.stdout == str(expected).lower()
        assert ("deprecated" in result.stderr) == (legacy is not None)


@pytest.mark.parametrize("file_current,file_legacy,inherited_current,inherited_legacy,expected", [
    ("true", None, None, None, "true"), ("false", None, None, None, "false"),
    (None, "false", None, None, "true"), (None, "true", None, None, "false"),
    ("true", "false", None, None, "true"), ("true", "true", None, None, None),
    ("true", None, None, "false", "true"), ("true", None, None, "true", None),
    (None, "false", "true", None, "true"), (None, "false", "false", None, None),
    (None, None, "true", None, None), (None, None, None, "false", None),
    ("true", None, None, "invalid", None), (None, "", None, None, None),
])
def test_lifecycle_config_file_remains_authoritative(
        tmp_path, file_current, file_legacy, inherited_current, inherited_legacy, expected):
    config, env, prefix = profiling_config_test_setup(tmp_path)
    text = config.read_text().replace("export WORKLOAD_MANAGE_CLIENT_LIFECYCLE=true\n", "")
    for name, value in (("WORKLOAD_MANAGE_CLIENT_LIFECYCLE", file_current),
                        ("WORKLOAD_SKIP_CLOSE", file_legacy)):
        if value is not None:
            text += f"\nexport {name}={value}\n"
    config.write_text(text)
    for name, value in (("WORKLOAD_MANAGE_CLIENT_LIFECYCLE", inherited_current),
                        ("WORKLOAD_SKIP_CLOSE", inherited_legacy)):
        if value is not None:
            env[name] = value
    result = subprocess.run(
        [bash_executable(), "-c", prefix + 'profiling_load_config || exit $?\n'
         '[[ ! -v WORKLOAD_SKIP_CLOSE ]] || exit 3\n'
         'printf "%s" "$WORKLOAD_MANAGE_CLIENT_LIFECYCLE"'],
        cwd=tmp_path, env=env, capture_output=True, text=True, timeout=15)
    assert result.returncode == (2 if expected is None else 0), result.stdout + result.stderr
    if expected is not None:
        assert result.stdout == expected


@pytest.mark.parametrize("current,legacy", [
    ("PROFILING_SESSION_DIR", "ARTIFACTS"), ("PROFILING_SESSION_LABEL", "PERF_PHASE"),
    ("PROFILING_CAPTURE_ID", "PROFILE_STAMP"),
    ("PROFILING_CHECK_ITEM_ID", "PROFILING_PROOF_ITEM"),
    ("PROFILING_CHECK_PARTITION_KEY_VALUE", "PROFILING_PROOF_PK"),
])
@pytest.mark.parametrize("current_value", [None, "saved-value", "conflicting-value"])
def test_profiling_deprecated_names_are_explicit(tmp_path, current, legacy, current_value):
    _, env, _ = profiling_config_test_setup(tmp_path)
    env.pop("ARTIFACTS", None)
    env.pop("PROFILE_STAMP", None)
    env[legacy] = "saved-value"
    if current_value is not None:
        env[current] = current_value
    command = (
        f'source "{(WORKLOADS / "profiling_common.sh").as_posix()}" || exit $?\n'
        f'[[ ! -v {legacy} ]] || exit 3\nprintf "%s" "${{{current}}}"'
    )
    result = subprocess.run([bash_executable(), "-c", command], cwd=tmp_path, env=env,
                            capture_output=True, text=True, timeout=15)
    assert result.returncode == (2 if current_value == "conflicting-value" else 0), result.stderr
    if current_value != "conflicting-value":
        assert result.stdout == "saved-value"
        assert "deprecated" in result.stderr


@pytest.mark.parametrize("current,legacy,skip_close", [
    ("true", None, False), ("false", None, True), (None, "false", False), (None, "true", True),
])
def test_reporter_preserves_saved_skip_close_semantics(modules, monkeypatch, current, legacy, skip_close):
    for name, value in (("WORKLOAD_MANAGE_CLIENT_LIFECYCLE", current), ("WORKLOAD_SKIP_CLOSE", legacy)):
        monkeypatch.delenv(name, raising=False)
        if value is not None:
            monkeypatch.setenv(name, value)
    stats = modules["perf_stats"].Stats()
    reporter = modules["perf_reporter"].PerfReporter(
        stats, {"report_interval": 60, "workload_id": "test", "commit_sha": "x", "driver_commit": "y"})
    reporter._container = Rows()
    stats.record("ReadItem", 1)
    reporter.stop()
    assert reporter._container.rows[0]["config_skip_close"] is skip_close


@pytest.mark.parametrize("manage", [True, False])
@pytest.mark.parametrize("read_fails", [True, False])
def test_workload_lifecycle_controls_entry_and_exit(modules, monkeypatch, manage, read_fails):
    from types import SimpleNamespace
    from unittest.mock import AsyncMock

    workload = importlib.import_module("workload")
    calls = []

    class Client:
        def __init__(self, *args, **kwargs):
            calls.append("construct")

        async def __aenter__(self):
            calls.append("enter")
            return self

        async def __aexit__(self, *args):
            calls.append("exit")

        def get_database_client(self, name):
            return self

        def get_container_client(self, name):
            return self

    async def read(*args):
        calls.append("read")
        if read_fails:
            raise RuntimeError("read failed")

    reporter = SimpleNamespace(stop=lambda: calls.append("report"))
    for name, value in {
        "AsyncClient": Client, "WORKLOAD_MANAGE_CLIENT_LIFECYCLE": manage,
        "WORKLOAD_USE_PROXY": False, "WORKLOAD_LOOP_LAG_MONITOR": False,
        "WORKLOAD_ARRIVAL_RATE": 1, "run_fixed_rate": read,
        "_start_reporter": lambda: (object(), reporter),
        "_install_async_stop": lambda event: None,
        "_wrap_backend_for_counting": lambda *args, **kwargs: None,
        "_maybe_freeze_gc": lambda logger: None,
    }.items():
        monkeypatch.setattr(workload, name, value)
    monkeypatch.setattr(workload.asyncio, "sleep", AsyncMock())
    if read_fails:
        with pytest.raises(RuntimeError, match="read failed"):
            asyncio.run(workload.run_workload_async("test", None))
    else:
        asyncio.run(workload.run_workload_async("test", None))
    assert calls == (["construct", "enter", "read", "exit", "report"] if manage
                     else ["construct", "read", "report"])


@pytest.mark.parametrize("invalid", [
    "missing-file", "missing-value", "empty-target", "zero-limit", "negative-rate", "wrong-boolean",
    "BASELINE_READ_RPS", "BASELINE_DATABASE", "BASELINE_CONTAINER", "BASELINE_OPERATIONS",
    "PROFILING_PROOF_DATABASE", "PROFILING_PROOF_CONTAINER", "PROFILING_PROOF_PARTITION_KEY",
    "MEMRAY_ARRIVAL_RATE", "EXPECT_DATABASE",
])
def test_profiling_config_rejects_missing_invalid_and_removed_settings(tmp_path, invalid):
    config, env, prefix = profiling_config_test_setup(tmp_path)
    text = config.read_text()
    if invalid == "missing-file":
        config.rename(tmp_path / "perf_target.env")
    elif invalid == "missing-value":
        config.write_text(text.replace("export WORKLOAD_MAX_INFLIGHT=10000\n", ""))
        env["WORKLOAD_MAX_INFLIGHT"] = "10000"
    elif invalid == "empty-target":
        config.write_text(text.replace('export COSMOS_DATABASE="db"', 'export COSMOS_DATABASE=""'))
    elif invalid == "zero-limit":
        config.write_text(text.replace("WORKLOAD_MAX_INFLIGHT=10000", "WORKLOAD_MAX_INFLIGHT=0"))
    elif invalid == "negative-rate":
        config.write_text(text.replace("WORKLOAD_ARRIVAL_RATE=250", "WORKLOAD_ARRIVAL_RATE=-1"))
    elif invalid == "wrong-boolean":
        config.write_text(text.replace("WORKLOAD_USE_SYNC=false", "WORKLOAD_USE_SYNC=maybe"))
    else:
        env[invalid] = "obsolete"
    result = subprocess.run([bash_executable(), "-c", prefix + "profiling_load_config"],
                            cwd=tmp_path, env=env, capture_output=True, text=True, timeout=15)
    assert result.returncode == 2, result.stdout + result.stderr
    assert "ERROR:" in result.stderr


@pytest.mark.parametrize("arguments,valid", [
    ("", False),
    ("--confirm-target https://wrong.invalid/ db items", False),
    ("--confirm-target https://test.invalid/ other items", False),
    ("--confirm-target https://test.invalid/ db other", False),
    ("--confirm-target https://test.invalid db items", True),
])
def test_target_confirmation_precedes_service_access(tmp_path, arguments, valid):
    _, env, prefix = profiling_config_test_setup(tmp_path)
    result = subprocess.run(
        [bash_executable(), "-c", prefix + 'profiling_load_config || exit $?\n'
         f'profiling_confirm_target {arguments} || exit $?\necho CONTACT_ALLOWED'],
        cwd=tmp_path, env=env, capture_output=True, text=True, timeout=15)
    assert (result.returncode == 0) == valid, result.stdout + result.stderr
    assert ("CONTACT_ALLOWED" in result.stdout) == valid


@pytest.mark.parametrize("setting,value", [
    ("WORKLOAD_OPERATIONS", "patch"), ("WORKLOAD_USE_SYNC", "true"),
    ("WORKLOAD_NUM_CLIENTS", "2"), ("WORKLOAD_ARRIVAL_RATE", "0"),
    ("WORKLOAD_USE_PROXY", "true"), ("WORKLOAD_MANAGE_CLIENT_LIFECYCLE", "false"), ("PERF_ENABLED", "false"),
])
def test_read_workload_does_not_silently_replace_configuration(tmp_path, setting, value):
    config, env, prefix = profiling_config_test_setup(tmp_path)
    config.write_text(config.read_text() + f"\nexport {setting}={value}\n")
    result = subprocess.run(
        [bash_executable(), "-c", prefix + 'profiling_load_config || exit $?\n'
         'profiling_require_read_workload || exit $?\necho LAUNCH_ALLOWED'],
        cwd=tmp_path, env=env, capture_output=True, text=True, timeout=15)
    assert result.returncode == 2
    assert "LAUNCH_ALLOWED" not in result.stdout


@pytest.mark.parametrize("script", ["profiling_check_target.sh", "profiling_prepare_test_items.sh"])
def test_target_scripts_refuse_unconfirmed_destination_before_python(tmp_path, script):
    shutil.copyfile(WORKLOADS / script, tmp_path / script)
    (tmp_path / "profiling_common.sh").write_text(
        "profiling_load_env() { :; }\n"
        "profiling_confirm_target() { echo 'ERROR: target not confirmed' >&2; return 2; }\n"
        "python3() { echo live >> live.txt; }\n", encoding="utf-8")
    result = subprocess.run([bash_executable(), script], cwd=tmp_path,
                            capture_output=True, text=True, timeout=15)
    assert result.returncode == 2
    assert not (tmp_path / "live.txt").exists()


def test_source_update_requires_explicit_commit_before_git(tmp_path):
    script = "profiling_update_source.sh"
    shutil.copyfile(WORKLOADS / script, tmp_path / script)
    (tmp_path / "profiling_common.sh").write_text(
        "git() { echo contacted >> git.txt; }\n", encoding="utf-8")
    result = subprocess.run([bash_executable(), script], cwd=tmp_path,
                            capture_output=True, text=True, timeout=15)
    assert result.returncode == 2
    assert not (tmp_path / "git.txt").exists()


@pytest.mark.parametrize("status_rc", [0, 1, 2])
def test_source_update_selects_exact_commit_without_building(tmp_path, status_rc):
    script = "profiling_update_source.sh"
    shutil.copyfile(WORKLOADS / script, tmp_path / script)
    commit = "a" * 40
    (tmp_path / "profiling_common.sh").write_text(
        'profiling_python_repo() { printf "%s" "$PWD"; }\n'
        f"profiling_repo_is_dirty() {{ return {status_rc}; }}\n"
        'git() { printf "%s\\n" "${*:3}" >> git.txt; '
        f'if [[ "$3" == rev-parse ]]; then echo {commit}; fi; }}\n',
        encoding="utf-8",
    )
    env = {key: value for key, value in os.environ.items() if key != "PROFILING_PYTHON_REF"}
    result = subprocess.run([bash_executable(), script, commit], cwd=tmp_path, env=env,
                            capture_output=True, text=True, timeout=15)
    if status_rc != 1:
        assert result.returncode == 2
        assert not (tmp_path / "git.txt").exists()
    else:
        assert result.returncode == 0, result.stdout + result.stderr
        assert (tmp_path / "git.txt").read_text().splitlines() == [
            f"fetch origin {commit}", f"checkout --detach {commit}", "rev-parse HEAD",
        ]


@pytest.mark.parametrize("preparation_rc", [0, 7])
def test_experiment_preparation_records_session_before_items(tmp_path, preparation_rc):
    script = "profiling_prepare_experiment.sh"
    shutil.copyfile(WORKLOADS / script, tmp_path / script)
    (tmp_path / "profiling_common.sh").write_text(
        "profiling_load_env() { :; }\n"
        "profiling_confirm_target() { echo confirmed >> order.txt; }\n"
        "profiling_load_session() { echo restored >> order.txt; }\n", encoding="utf-8")
    (tmp_path / "profiling_create_session.sh").write_text(
        'echo created >> order.txt\nmkdir evidence\nprintf "artifacts=%s/evidence\\n" "$PWD"\n',
        encoding="utf-8")
    (tmp_path / "profiling_prepare_test_items.sh").write_text(
        'echo prepared >> order.txt\nprintf "%s\\n" "$*" > confirmation.txt\n'
        f"echo preparation-output\nexit {preparation_rc}\n", encoding="utf-8")
    arguments = ["--confirm-target", "https://test.invalid/", "db", "items"]
    env = {key: value for key, value in os.environ.items()
           if key not in ("PROFILING_SKIP_BUILD", "PROFILING_SKIP_SOURCE_UPDATE")}
    result = subprocess.run([bash_executable(), script, *arguments], cwd=tmp_path, env=env,
                            capture_output=True, text=True, timeout=15)
    assert (result.returncode == 0) == (preparation_rc == 0), result.stdout + result.stderr
    assert (tmp_path / "order.txt").read_text().splitlines() == (
        ["confirmed", "created", "restored", "prepared"] + (["restored"] if preparation_rc == 0 else []))
    assert (tmp_path / "confirmation.txt").read_text().strip() == " ".join(arguments)
    assert (tmp_path / "evidence" / "test-item-preparation.log").read_text().strip() == "preparation-output"
    assert (tmp_path / "evidence" / "session-creation.log").is_file()
    assert (tmp_path / "evidence" / "preparation-completion.txt").exists() == (preparation_rc == 0)


@pytest.mark.parametrize("arguments", ["", "first second", "../other"])
def test_activation_requires_explicit_session_before_loading_environment(tmp_path, arguments):
    shutil.copyfile(WORKLOADS / "profiling_load_session.sh", tmp_path / "profiling_load_session.sh")
    (tmp_path / "profiling_common.sh").write_text(
        "profiling_load_env() { echo loaded >> loaded.txt; }\n", encoding="utf-8")
    result = subprocess.run([bash_executable(), "-c", f"source ./profiling_load_session.sh {arguments}"],
                            cwd=tmp_path, capture_output=True, text=True, timeout=15)
    assert result.returncode != 0
    assert "ERROR:" in result.stderr
    assert not (tmp_path / "loaded.txt").exists()


@pytest.mark.parametrize("script", [
    "profiling_run_read_baseline.sh", "profiling_capture_py_spy.sh", "profiling_capture_memray.sh",
])
def test_measurement_scripts_do_not_select_newest_session(tmp_path, script):
    shutil.copyfile(WORKLOADS / script, tmp_path / script)
    (tmp_path / "profiling_common.sh").write_text("", encoding="utf-8")
    (tmp_path / "profiling_load_session.sh").write_text("echo selected >> selected.txt\n", encoding="utf-8")
    env = {key: value for key, value in os.environ.items()
           if key != "PROFILING_SESSION_DIR" and not key.startswith("BASELINE_")}
    invocation = f"bash ./{script}" if script == "profiling_run_read_baseline.sh" else f"source ./{script}"
    result = subprocess.run([bash_executable(), "-c", invocation], cwd=tmp_path, env=env,
                            capture_output=True, text=True, timeout=15)
    assert result.returncode == 2, result.stdout + result.stderr
    assert "intended profiling session" in result.stderr
    assert not (tmp_path / "selected.txt").exists()


@pytest.mark.parametrize("script", ["profiling_capture_py_spy.sh", "profiling_capture_memray.sh"])
def test_captures_preserve_configuration_before_launch(tmp_path, script):
    shutil.copyfile(WORKLOADS / script, tmp_path / script)
    (tmp_path / "profiling_common.sh").write_text(
        "profiling_load_env() { :; }\nprofiling_load_session() { :; }\n"
        "profiling_require_read_workload() { :; }\nperf_require_positive() { :; }\n"
        "py-spy() { :; }\n"
        "python3() { if [[ \"$1\" != -c ]]; then echo launched >> launched.txt; fi; }\n"
        "write_run_manifest() {\n"
        ' printf "%s/%s/%s/%s/%s\\n" "$WORKLOAD_ARRIVAL_RATE" "$WORKLOAD_MAX_INFLIGHT" '
        '"$PERF_REPORT_INTERVAL" "$WORKLOAD_LOOP_LAG_MONITOR" "$WORKLOAD_GC_FREEZE" > settings.txt\n'
        " return 1\n}\n", encoding="utf-8")
    env = {**os.environ, "PROFILING_SESSION_DIR": tmp_path.as_posix(), "WORKLOAD_ARRIVAL_RATE": "123",
           "WORKLOAD_MAX_INFLIGHT": "7", "PERF_REPORT_INTERVAL": "17",
           "WORKLOAD_LOOP_LAG_MONITOR": "true", "WORKLOAD_GC_FREEZE": "true"}
    env.pop("WORKLOAD_PID", None)
    result = subprocess.run([bash_executable(), "-c", f"source ./{script}"], cwd=tmp_path, env=env,
                            capture_output=True, text=True, timeout=15)
    assert result.returncode == 2, result.stdout + result.stderr
    assert (tmp_path / "settings.txt").read_text().strip() == "123/7/17/true/true"
    assert not (tmp_path / "launched.txt").exists()


def test_transport_check_rejects_saved_target_mismatch_before_read(tmp_path):
    script = "profiling_check_rust_transport.sh"
    shutil.copyfile(WORKLOADS / script, tmp_path / script)
    (tmp_path / "profiling_common.sh").write_text(
        "profiling_load_env() { :; }\nprofiling_load_session() { :; }\n"
        "python3() { echo contacted >> contacted.txt; }\n", encoding="utf-8")
    baseline = tmp_path / f"light-load-baseline-{STAMP}"
    baseline.mkdir()
    (baseline / "baseline-target.env").write_text(
        "BASELINE_DATABASE=wrong-db\nBASELINE_CONTAINER=items\nBASELINE_PARTITION_KEY=id\n",
        encoding="utf-8")
    env = {**os.environ, "PROFILING_SESSION_ID": STAMP, "PROFILING_SESSION_DIR": tmp_path.as_posix(),
           "COSMOS_DATABASE": "db", "COSMOS_CONTAINER": "items", "COSMOS_PARTITION_KEY": "id"}
    result = subprocess.run([bash_executable(), script], cwd=tmp_path, env=env,
                            capture_output=True, text=True, timeout=15)
    assert result.returncode == 2, result.stdout + result.stderr
    assert "saved baseline target differs" in result.stderr
    assert not (tmp_path / "contacted.txt").exists()


@pytest.mark.parametrize("environment", ["venvs/perfdrill", "candidate environment"])
def test_build_needs_python_activation_but_not_cosmos_configuration(tmp_path, environment):
    config, env, prefix = profiling_config_test_setup(tmp_path)
    config.unlink()
    fake_profiling_environment(tmp_path, environment)
    prefix += f'PROFILING_VENV="$HOME/{environment}"\n'
    script = "profiling_build_extension.sh"
    shutil.copyfile(WORKLOADS / script, tmp_path / script)
    (tmp_path / "profiling_common.sh").write_text(
        prefix + '\nprofiling_python_repo() { echo "$PWD"; }\n'
        "git() { printf '%040d\\n' 1; }\n"
        'cargo() { echo "cargo $*" >> "$HOME/build.txt"; }\n'
        'maturin() { echo "maturin $*" >> "$HOME/build.txt"; }\n'
        'python3() { if [[ "$1" == - ]]; then cat >/dev/null; else printf "%040d\\n" 2; fi; }\n',
        encoding="utf-8")
    result = subprocess.run([bash_executable(), script], cwd=tmp_path, env=env,
                            capture_output=True, text=True, timeout=15)
    assert result.returncode == 0, result.stdout + result.stderr
    assert "Extension ready" in result.stdout
    commands = (tmp_path / "build.txt").read_text().splitlines()
    assert commands[0].startswith("cargo fetch --locked --manifest-path ")
    assert commands[1] == "maturin develop --release --locked"


@pytest.mark.parametrize("script", ["run_coldstart.sh", "run_docsize.sh", "run_mixed.sh"])
def test_auxiliary_workloads_use_the_selected_environment(tmp_path, script):
    for name in (script, "profiling_common.sh"):
        shutil.copyfile(WORKLOADS / name, tmp_path / name)
    fake_profiling_environment(tmp_path, "candidate environment")
    (tmp_path / "perf_secrets.env").write_text("", encoding="utf-8")
    (tmp_path / "perf_drill_defaults.sh").write_text(
        "perf_single_operation_shape() { :; }\n"
        "perf_require_positive() { :; }\n"
        'perf_create_log_dir() { printf "%s\\n" "$VIRTUAL_ENV" > selected.txt; return 7; }\n',
        encoding="utf-8",
    )
    command = (
        'export HOME="$PWD"\nexport PROFILING_VENV="$HOME/candidate environment"\n'
        f'bash ./{script} 1\n'
    )
    result = subprocess.run([bash_executable(), "-c", command], cwd=tmp_path,
                            capture_output=True, text=True, timeout=15)
    assert result.returncode == 2, result.stdout + result.stderr
    assert (tmp_path / "selected.txt").read_text().strip().endswith("/candidate environment")


def test_build_finds_common_helpers_after_changing_to_package_directory(tmp_path):
    _, env, _ = profiling_config_test_setup(tmp_path)
    activate = fake_profiling_environment(tmp_path)
    activate.write_text(
        activate.read_text() +
        "git() { printf '%040d\\n' 1; }\n"
        "cargo() { :; }\nmaturin() { :; }\n"
        "python3() {\n"
        ' if [[ "$1" == - ]]; then cat >/dev/null; return 0; fi\n'
        ' if [[ ! -f "$1" ]]; then echo "ERROR: helper not found: $1" >&2; return 2; fi\n'
        ' printf "%s\\n" "$1" >> "$HOME/helper-paths.txt"\n'
        " printf '%040d\\n' 2\n}\n", encoding="utf-8")
    scripts = tmp_path / "package" / "tests" / "workloads"
    scripts.mkdir(parents=True)
    for name in ("profiling_build_extension.sh", "profiling_common.sh", "perf_build_details.py"):
        shutil.copyfile(WORKLOADS / name, scripts / name)
    result = subprocess.run(
        [bash_executable(), "-c",
         'export HOME="$(cd "$TEST_HOME" && pwd)"; bash ./profiling_build_extension.sh'],
        cwd=scripts, env={**env, "TEST_HOME": tmp_path.as_posix()},
        capture_output=True, text=True, timeout=15)
    assert result.returncode == 0, result.stdout + result.stderr
    assert "Extension ready" in result.stdout
    assert len((tmp_path / "helper-paths.txt").read_text().splitlines()) == 2


def test_profiling_config_accepts_fractional_timeout(tmp_path):
    config, env, prefix = profiling_config_test_setup(tmp_path)
    config.write_text(config.read_text().replace("COSMOS_REQUEST_TIMEOUT=30", "COSMOS_REQUEST_TIMEOUT=1.5"))
    result = subprocess.run([bash_executable(), "-c", prefix + "profiling_load_config"],
                            cwd=tmp_path, env=env, capture_output=True, text=True, timeout=15)
    assert result.returncode == 0, result.stdout + result.stderr


@pytest.mark.parametrize("rate", ["250", "333"])
def test_credentials_file_cannot_replace_experiment_configuration(tmp_path, rate):
    _, env, prefix = profiling_config_test_setup(tmp_path)
    fake_profiling_environment(tmp_path)
    (tmp_path / "perf_secrets.env").write_text(
        "export COSMOS_KEY=synthetic-test-key\nexport RESULTS_COSMOS_KEY=synthetic-results-key\n"
        f"export WORKLOAD_ARRIVAL_RATE={rate}\n", encoding="utf-8")
    result = subprocess.run(
        [bash_executable(), "-c", prefix + 'stat() { echo 600; }\nprofiling_load_env'],
        cwd=tmp_path, env=env, capture_output=True, text=True, timeout=15)
    assert (result.returncode == 0) == (rate == "250"), result.stdout + result.stderr
    if rate != "250":
        assert "inherited WORKLOAD_ARRIVAL_RATE conflicts" in result.stderr


@pytest.mark.parametrize("force_seed", [False, True])
@pytest.mark.parametrize("readback_rc", [0, 1, 3, 4])
def test_seed_requires_full_readback(tmp_path, force_seed, readback_rc):
    script = "profiling_prepare_test_items.sh"
    shutil.copyfile(WORKLOADS / script, tmp_path / script)
    (tmp_path / "profiling_check_target.sh").write_text("exit 0\n", encoding="utf-8")
    (tmp_path / "profiling_common.sh").write_text(
        "profiling_load_env() { :; }\n"
        "profiling_confirm_target() { :; }\n"
        "checks=0\n"
        "python3() {\n"
        "  if [[ \"$1\" == initial-setup.py ]]; then echo seeded >> calls.txt; return 0; fi\n"
        "  checks=$((checks+1)); echo checked >> calls.txt; cat >/dev/null\n"
        "  if [[ \"$checks\" == 1 && \"$PROFILING_FORCE_SEED\" != 1 ]]; then return 4; fi\n"
        "  return \"$READBACK_RC\"\n"
        "}\n",
        encoding="utf-8",
    )
    env = {**os.environ, "COSMOS_DATABASE": "db", "COSMOS_CONTAINER": "items",
           "COSMOS_MAX_ITEM_INDEX": "2", "READBACK_RC": str(readback_rc),
           "PROFILING_FORCE_SEED": "1" if force_seed else "0"}
    result = subprocess.run([bash_executable(), script], cwd=tmp_path, env=env,
                            capture_output=True, text=True, timeout=15)
    assert (result.returncode == 0) == (readback_rc == 0), result.stdout + result.stderr
    assert (tmp_path / "calls.txt").read_text().splitlines() == (
        ["seeded", "checked"] if force_seed else ["checked", "seeded", "checked"])


@pytest.mark.parametrize("check_rc", [0, 1, 3])
def test_seed_does_not_write_when_probe_passes_or_crashes(tmp_path, check_rc):
    script = "profiling_prepare_test_items.sh"
    shutil.copyfile(WORKLOADS / script, tmp_path / script)
    (tmp_path / "profiling_check_target.sh").write_text("exit 0\n", encoding="utf-8")
    (tmp_path / "profiling_common.sh").write_text(
        "profiling_load_env() { :; }\n"
        "profiling_confirm_target() { :; }\n"
        "python3() {\n"
        "  if [[ \"$1\" == initial-setup.py ]]; then echo seeded >> calls.txt; return 0; fi\n"
        "  echo checked >> calls.txt; cat >/dev/null; return \"$CHECK_RC\"\n"
        "}\n",
        encoding="utf-8",
    )
    env = {**os.environ, "COSMOS_DATABASE": "db", "COSMOS_CONTAINER": "items",
           "COSMOS_MAX_ITEM_INDEX": "2", "CHECK_RC": str(check_rc), "PROFILING_FORCE_SEED": "0"}
    result = subprocess.run([bash_executable(), script], cwd=tmp_path, env=env,
                            capture_output=True, text=True, timeout=15)
    assert (result.returncode == 0) == (check_rc == 0), result.stdout + result.stderr
    assert (tmp_path / "calls.txt").read_text().splitlines() == ["checked"]


@pytest.mark.parametrize("outcome,expected_rc", [("present", 0), ("missing", 4), ("permission", 3)])
def test_data_probe_distinguishes_missing_items_from_failure(monkeypatch, outcome, expected_rc):
    import azure.cosmos as sdk
    from azure.cosmos.exceptions import CosmosHttpResponseError, CosmosResourceNotFoundError

    calls = []
    closed = []

    class Client:
        def __init__(self, uri, key, **kwargs):
            assert kwargs == {"_backend": "core-python"}

        def get_database_client(self, database):
            return self

        def get_container_client(self, container):
            return self

        def read_item(self, item_id, partition_key):
            assert partition_key == item_id
            calls.append(item_id)
            if item_id == "test-1":
                if outcome == "missing":
                    raise CosmosResourceNotFoundError(status_code=404, message="missing item")
                if outcome == "permission":
                    raise CosmosHttpResponseError(status_code=403, message="forbidden")

        def close(self):
            closed.append(True)

    monkeypatch.setattr(sdk, "CosmosClient", Client)
    for name, value in {"URI": "https://test.invalid", "KEY": "synthetic-key",
                        "DATABASE": "db", "CONTAINER": "items", "PARTITION_KEY": "id",
                        "MAX_ITEM_INDEX": "2"}.items():
        monkeypatch.setenv("COSMOS_" + name, value)
    with pytest.raises(SystemExit) as exc:
        exec(compile(embedded_python("profiling_prepare_test_items.sh"), "data-probe", "exec"), {})
    assert exc.value.code == expected_rc
    assert calls == (["test-0", "test-1"] if outcome == "permission" else
                     ["test-0", "test-1", "test-2"])
    assert closed == [True]


@pytest.mark.parametrize("verdict,python_rc,tee_rc,expected", [
    ("TRANSPORT VERDICT: gateway_v2 -- stubbed evidence", 0, 0, 0),
    ("TRANSPORT VERDICT: gateway -- stubbed evidence", 1, 0, 1),
    ("TRANSPORT VERDICT: invalid sample -- stubbed failure", 2, 0, 2),
    ("TRANSPORT VERDICT: gateway_v2 -- stubbed evidence", 1, 0, 2),
    ("TRANSPORT VERDICT: gateway_v2 -- stubbed evidence", 0, 3, 2),
    ("interpreter crashed before a verdict", 1, 0, 2),
])
def test_rust_transport_check_validates_exit_and_evidence(tmp_path, verdict, python_rc, tee_rc, expected):
    script = "profiling_check_rust_transport.sh"
    shutil.copyfile(WORKLOADS / script, tmp_path / script)
    (tmp_path / "profiling_common.sh").write_text(
        "profiling_load_env() { return 0; }\n"
        "profiling_load_session() { return 0; }\n"
        "python3() { [[ \"$COSMOS_BACKEND\" == rust ]] || return 2; "
        "printf '%s\\n' \"$TRANSPORT_TEXT\"; return \"$PYTHON_RC\"; }\n"
        "tee() { cat > \"$1\"; return \"$TEE_RC\"; }\n",
        encoding="utf-8",
    )
    env = {**os.environ, "PROFILING_SESSION_DIR": tmp_path.as_posix(), "PROFILING_SESSION_ID": STAMP,
           "COSMOS_URI": "https://example.invalid", "COSMOS_DATABASE": "db", "COSMOS_CONTAINER": "container",
           "COSMOS_PARTITION_KEY": "id", "TRANSPORT_TEXT": verdict,
           "PYTHON_RC": str(python_rc), "TEE_RC": str(tee_rc)}
    result = subprocess.run([bash_executable(), script], cwd=tmp_path, env=env,
                            capture_output=True, text=True, timeout=15)
    assert result.returncode == expected, result.stdout + result.stderr


@pytest.mark.parametrize("scenario,expected_rc", [
    ("gateway_v2", 0), ("gateway", 1), ("mixed", 2), ("missing", 2),
    ("legacy", 2), ("read_failure", 2), ("no_binding_entry", 2), ("no_requests", 2),
])
def test_rust_transport_check_requires_rust_read_evidence(monkeypatch, capsys, scenario, expected_rc):
    from types import SimpleNamespace
    import azure.cosmos as sdk
    import azure.cosmos.aio as async_sdk
    from azure.cosmos.aio._backend.binding_adapter import AsyncBindingAdapter

    calls = []
    counters = [0, 0, 0]
    diagnostics = {
        "gateway": "transports=[metadata/gateway,data_plane/gateway]",
        "mixed": "transports=[data_plane/gateway,data_plane/gateway_v2]",
        "missing": "transports=[metadata/gateway]",
    }.get(scenario, "transports=[metadata/gateway,data_plane/gateway_v2]")
    runtime_class = "AsyncLegacyBackend" if scenario == "legacy" else AsyncBindingAdapter.__name__

    class Client:
        def __init__(self, uri, key, **kwargs):
            assert (uri, key) == ("https://test.invalid", "synthetic-key")
            assert kwargs == {"preferred_locations": ["West US 2"], "_backend": "rust"}
            self._adapter = type(runtime_class, (), {})()

        async def __aenter__(self):
            return self

        async def __aexit__(self, *args):
            calls.append("closed")

        def get_database_client(self, name):
            assert name == "db"
            return self

        def get_container_client(self, name):
            assert name == "items"
            return self

        async def read_item(self, *, item, partition_key, response_hook):
            assert (item, partition_key) == ("test-42", "test-42")
            calls.append("read")
            if scenario == "read_failure":
                raise RuntimeError("synthetic read failure")
            counters[0] += 0 if scenario == "no_binding_entry" else 1
            counters[1] += 0 if scenario == "no_requests" else 1
            body = {"id": item}
            response_hook({"x-ms-cosmos-sdk-diagnostics": diagnostics}, body)
            return body

    monkeypatch.setattr(async_sdk, "CosmosClient", Client)
    monkeypatch.setattr(sdk, "_rust", SimpleNamespace(
        _debug_operation_count=lambda: counters[0],
        _debug_attempt_count=lambda: counters[1],
        _debug_retry_count=lambda: counters[2],
    ), raising=False)
    for name, value in {"COSMOS_URI": "https://test.invalid", "COSMOS_KEY": "synthetic-key",
                        "COSMOS_DATABASE": "db", "COSMOS_CONTAINER": "items",
                        "COSMOS_PARTITION_KEY": "id", "COSMOS_PREFERRED_LOCATIONS": "West US 2",
                        "PROFILING_CHECK_ITEM_ID": "test-42"}.items():
        monkeypatch.setenv(name, value)
    with pytest.raises(SystemExit) as exc:
        exec(compile(embedded_python("profiling_check_rust_transport.sh"), "rust-transport-check", "exec"), {})
    assert exc.value.code == expected_rc
    assert calls == (["closed"] if scenario == "legacy" else ["read", "closed"])
    expected_verdict = scenario if scenario in {"gateway", "gateway_v2"} else "invalid sample"
    assert f"TRANSPORT VERDICT: {expected_verdict} --" in capsys.readouterr().out


def test_throughput_launcher_keeps_earlier_child_failure(tmp_path):
    script = "run_throughput_sweep.sh"
    shutil.copyfile(WORKLOADS / script, tmp_path / script)
    (tmp_path / "perf_drill_defaults.sh").write_text(
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
    build_details = importlib.import_module("perf_build_details")
    monkeypatch.setattr(sdk, "__file__", str(tmp_path / "__init__.py"))
    with pytest.raises(ValueError, match="outside the selected checkout"):
        build_details.extension_details()


def test_existing_run_directory_is_not_reused(tmp_path):
    target = tmp_path / "run"
    target.mkdir()
    marker = target / "evidence.txt"
    marker.write_text("preserve")
    result = subprocess.run(
        [bash_executable(), "-c", 'source "$1"; perf_create_log_dir "$2"', "test",
         (WORKLOADS / "perf_drill_defaults.sh").as_posix(), target.as_posix()],
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


def test_primary_sdk_latency_pools_components_without_mutating_total(modules):
    rows = [fixed_rate_row(modules, delay_ms=20, sdk_ms=2),
            fixed_rate_row(modules, delay_ms=40, sdk_ms=8)]
    report = modules["latency_report"]
    original = report._aggregate(Rows(rows), "baseline-", STAMP)[0][("read", "rust")]
    selected = report._latency_view(original, "sdk-call")
    assert selected["hist"].total_count == 2
    assert report._mean_ms(selected) == pytest.approx(5, rel=0.001)
    assert report._pctile_ms(selected, 99) == pytest.approx(8, rel=0.001)
    assert report._pctile_ms(original, 99) == pytest.approx(48, rel=0.001)
    assert original["duration_kinds"] == {"total"}
    assert selected["duration_kinds"] == {"sdk_call"}
    assert report._latency_view(original, "total") is original


@pytest.mark.parametrize("missing", ["all", "one"])
def test_primary_sdk_latency_never_falls_back_to_total(modules, missing):
    first = fixed_rate_row(modules)
    del first["fixed_rate_timings"]
    rows = [first] if missing == "all" else [first, fixed_rate_row(modules)]
    report = modules["latency_report"]
    cell = report._aggregate(Rows(rows), "baseline-", STAMP)[0][("read", "rust")]
    selected = report._latency_view(cell, "sdk-call")
    assert math.isnan(report._pctile_ms(selected, 99))
    assert math.isnan(report._mean_ms(selected))
    assert "pooled latency unavailable" in report._fmt_cell("read", "rust", selected)
    assert not math.isnan(report._pctile_ms(cell, 99))


@pytest.mark.parametrize("component", ["delay", "sdk"])
def test_primary_sdk_latency_uses_its_own_overflow_evidence(modules, component):
    row = fixed_rate_row(modules, delay_ms=70_000 if component == "delay" else 1,
                         sdk_ms=70_000 if component == "sdk" else 5)
    report = modules["latency_report"]
    cell = report._aggregate(Rows([row]), "baseline-", STAMP)[0][("read", "rust")]
    assert math.isnan(report._pctile_ms(cell, 99))
    selected = report._latency_view(cell, "sdk-call")
    if component == "sdk":
        assert math.isnan(report._pctile_ms(selected, 99))
    else:
        assert report._pctile_ms(selected, 99) == pytest.approx(5, rel=0.001)


def test_send_and_wait_primary_sdk_latency_preserves_existing_histogram(modules):
    row = measurement(modules, config_arrival_rate=0)
    report = modules["latency_report"]
    cell = report._aggregate(Rows([row]), "baseline-", STAMP)[0][("read", "rust")]
    assert report._latency_view(cell, "sdk-call") is cell
    with pytest.raises(ValueError, match="fixed-rate"):
        report._latency_view(cell, "total")


@pytest.mark.parametrize("metric,expected_exit", [(None, 0), ("sdk-call", 0), ("total", 1)])
def test_report_summary_comparison_and_gate_use_same_latency_metric(
        modules, monkeypatch, capsys, metric, expected_exit):
    rows = []
    for backend, sdk_ms in (("core-python", 7), ("rust", 3)):
        row = fixed_rate_row(
            modules, delay_ms=20, sdk_ms=sdk_ms,
            workload_id=f"baseline-read-{backend}-{STAMP}", config_backend=backend)
        rows.extend([row, completion(row, fixed_rate_schedules=[schedule_record()])])
    report = modules["latency_report"]
    monkeypatch.setattr(report, "_connect", lambda: Rows(rows))
    argv = ["latency_report", "--run-id", STAMP, "--point-read-gate"]
    if metric is not None:
        argv.extend(["--latency-metric", metric])
    monkeypatch.setattr(sys, "argv", argv)
    with pytest.raises(SystemExit) as result:
        report.main()
    assert result.value.code == expected_exit
    output = capsys.readouterr().out
    selected = metric or "sdk-call"
    label = "total" if metric == "total" else "SDK-call"
    assert f"Primary latency metric: {selected}" in output
    assert f"core-python vs rust ({selected}; pooled ms" in output
    assert output.count(f"duration={selected}") == 2
    assert f"rust: {label} p99 <= 4 ms" in output
    rust_line = next(line for line in output.splitlines() if "read     rust" in line)
    assert ("p99= 23.01" if metric == "total" else "p99=  3.00") in rust_line
    assert "success total duration: samples=1 p99=23.007" in output
    assert "success delay before SDK call: samples=1" in output
    assert "limit_waits=0" in output


@pytest.mark.parametrize("sdk_ms", [4.002, 5, 70_000])
def test_sdk_call_gate_rejects_above_target_and_overflow(modules, monkeypatch, capsys, sdk_ms):
    row = fixed_rate_row(modules, delay_ms=0, sdk_ms=sdk_ms)
    report = modules["latency_report"]
    monkeypatch.setattr(report, "_connect", lambda: Rows([
        row, completion(row, fixed_rate_schedules=[schedule_record()])]))
    monkeypatch.setattr(sys, "argv", [
        "latency_report", "--run-id", STAMP, "--point-read-gate", "--gate-backends", "rust"])
    with pytest.raises(SystemExit) as result:
        report.main()
    assert result.value.code == 1
    assert "[FAIL] rust: SDK-call p99 <= 4 ms" in capsys.readouterr().out


@pytest.mark.parametrize("p99,expected_exit", [(3.999, 0), (4.0, 0), (4.001, 1)])
def test_sdk_call_gate_uses_inclusive_unrounded_target(modules, monkeypatch, capsys, p99, expected_exit):
    row = fixed_rate_row(modules, delay_ms=0, sdk_ms=3)
    report = modules["latency_report"]
    monkeypatch.setattr(report, "_connect", lambda: Rows([
        row, completion(row, fixed_rate_schedules=[schedule_record()])]))
    original_pctile = report._pctile_ms
    monkeypatch.setattr(report, "_pctile_ms",
                        lambda cell, percentile: p99 if percentile == 99 else original_pctile(cell, percentile))
    monkeypatch.setattr(sys, "argv", [
        "latency_report", "--run-id", STAMP, "--point-read-gate", "--gate-backends", "rust"])
    with pytest.raises(SystemExit) as result:
        report.main()
    assert result.value.code == expected_exit
    verdict = "PASS" if expected_exit == 0 else "FAIL"
    assert f"[{verdict}] rust: SDK-call p99 <= 4 ms ({p99:.3f} ms)" in capsys.readouterr().out


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
