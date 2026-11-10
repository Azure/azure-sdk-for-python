# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.
"""Offline safety and interpretation checks for native experiment packaging."""

import importlib
import json
from pathlib import Path

import pytest

WORKLOADS = Path(__file__).resolve().parents[1] / "workloads"


@pytest.fixture(name="tooling")
def fixture_tooling(monkeypatch):
    monkeypatch.syspath_prepend(str(WORKLOADS))
    monkeypatch.syspath_prepend(str(WORKLOADS / "native_experiments"))
    return (
        importlib.import_module("profiling_native_experiments"),
        importlib.import_module("native_experiment_metrics"),
    )


@pytest.fixture(name="package")
def fixture_package(tmp_path):
    root = tmp_path / "package"
    files = {
        "Cargo.toml": '[workspace]\nmembers = ["azure_cosmos_rust"]\n',
        "Cargo.lock": 'version = 4\n\n[[package]]\nname = "azure_cosmos_rust"\nversion = "0.1.0"\n',
        "azure_cosmos_rust/Cargo.toml": (
            '[package]\nname = "azure_cosmos_rust"\nversion = "0.1.0"\n'
            '[dependencies]\npyo3 = { version = "0.22", features = [\n'
            '    "extension-module",\n    "abi3-py310",\n] }\n'
        ),
        "azure_cosmos_rust/src/lib.rs": "mod runtime;\nmod wire;\n",
        "azure_cosmos_rust/src/runtime.rs": "impl DriverHandle {\n}\n",
        "azure_cosmos_rust/src/wire/mod.rs": "mod driver_runner;\nmod response;\n",
        "azure_cosmos_rust/src/wire/driver_runner.rs": (
            "pub(super) type ResponseTupleConverter<R> = R;\n"
            "pub(super) fn run_prepared_driver_operation_async() {}\n"
        ),
        "azure_cosmos_rust/src/wire/response.rs": "pub(super) fn tuple_from_result<'py>() {}\n",
        "azure_cosmos_rust/src/wire/items.rs": "// item operations\n",
        "azure/cosmos/_backend/_async_credential_bridge.py": "# fixture\n",
        "azure/cosmos/__init__.py": "# Python source is fingerprinted, not transplanted\n",
        "tests/create_item/legacy_partition_key_cases.json": "[]\n",
    }
    for name, content in files.items():
        target = root / name
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(content, encoding="utf-8")
    return root


@pytest.mark.parametrize("suite", ["allocator", "handoff"])
def test_experiment_changes_only_copy_and_links_embedded_python(tooling, package, tmp_path, suite):
    runner, _ = tooling
    before = runner.snapshot(package)
    copied, saved = runner.prepare_copy(package, tmp_path / suite)
    runner.instrument(copied, runner.ASSETS, suite, "linux")
    runner.verify_snapshot(package, before)
    assert before == saved
    manifest = (copied / "azure_cosmos_rust" / "Cargo.toml").read_text(encoding="utf-8")
    assert '"extension-module"' not in manifest
    assert '"extension-module"' in (package / "azure_cosmos_rust" / "Cargo.toml").read_text(encoding="utf-8")
    lib = (copied / "azure_cosmos_rust" / "src" / "lib.rs").read_text(encoding="utf-8")
    if suite == "allocator":
        assert '#[cfg(all(test, feature = "allocator-experiment-mimalloc"))]' in lib
        assert "[features]" in manifest
    else:
        assert "#[cfg(test)]\nmod handoff_experiment;" in lib
        assert "handoff-count-allocations = []" in manifest
    (package / "azure" / "cosmos" / "__init__.py").write_text("# changed\n", encoding="utf-8")
    with pytest.raises(RuntimeError, match="source changed"):
        runner.verify_snapshot(package, before)


def test_existing_output_and_in_package_output_are_not_touched(tooling, package, tmp_path):
    runner, _ = tooling
    output = tmp_path / "existing"
    output.mkdir()
    sentinel = output / "keep.txt"
    sentinel.write_text("keep", encoding="utf-8")
    with pytest.raises(FileExistsError):
        runner.prepare_copy(package, output)
    assert sentinel.read_text(encoding="utf-8") == "keep"
    forbidden = package / "new-experiment"
    with pytest.raises(ValueError, match="outside"):
        runner.prepare_copy(package, forbidden)
    assert not forbidden.exists()
    with pytest.raises(ValueError, match="outside"):
        runner.prepare_copy(package, package.parent)


@pytest.mark.parametrize("content", ["no insertion point", "marker and marker"])
def test_source_drift_refuses_ambiguous_patch(tooling, tmp_path, content):
    runner, _ = tooling
    path = tmp_path / "source.rs"
    path.write_text(content, encoding="utf-8")
    with pytest.raises(ValueError, match="exactly one"):
        runner.replace_once(path, "marker", "replacement")
    assert path.read_text(encoding="utf-8") == content


def test_allocator_resolution_preserves_existing_dependencies(tooling, tmp_path):
    runner, _ = tooling
    original = tmp_path / "original.lock"
    current = tmp_path / "current.lock"
    base = (
        'version = 4\n\n[[package]]\nname = "azure_cosmos_rust"\nversion = "0.1.0"\n'
        'dependencies = [\n "pyo3",\n]\n'
        '\n[[package]]\nname = "pyo3"\nversion = "0.22.6"\nchecksum = "original"\n'
    )
    additions = "".join(
        f'\n[[package]]\nname = "{name}"\nversion = "{version}"\n'
        'source = "registry+https://github.com/rust-lang/crates.io-index"\n'
        for name, version in runner.ADDITIONS.items()
    )
    original.write_text(base, encoding="utf-8")
    candidate = base.replace(' "pyo3",', ' "mimalloc",\n "libmimalloc-sys",\n "pyo3",') + additions
    current.write_text(candidate, encoding="utf-8")
    runner.check_dependencies(original, current, "allocator")
    with pytest.raises(ValueError):
        runner.check_dependencies(original, current, "handoff")
    current.write_text(candidate.replace('checksum = "original"', 'checksum = "changed"'), encoding="utf-8")
    with pytest.raises(ValueError, match="metadata changed"):
        runner.check_dependencies(original, current, "allocator")
    current.write_text(candidate.replace('version = "0.22.6"', 'version = "0.23.0"'), encoding="utf-8")
    with pytest.raises(ValueError, match="identity"):
        runner.check_dependencies(original, current, "allocator")


def test_timing_gate_separates_overhead_instability_and_smoke(tooling):
    runner, _ = tooling

    def pairs(controls, observed):
        return [
            {"control": {"process_cpu_ns": control}, "observed": {"process_cpu_ns": observation}}
            for control, observation in zip(controls, observed)
        ]

    stable = pairs([100, 102, 101, 100], [103, 105, 104, 103])
    assert runner.handoff_gate(stable, False)["timing_qualified"]
    assert not runner.handoff_gate(stable, True)["timing_qualified"]
    assert not runner.handoff_gate(pairs([100] * 4, [128] * 4), False)["timing_qualified"]
    assert not runner.handoff_gate(pairs([100, 160, 100, 160], [100, 160, 100, 160]), False)["timing_qualified"]


def test_linux_memory_keeps_resident_and_virtual_memory_distinct(tooling):
    _, metrics = tooling
    snapshot = metrics.linux_memory(
        "Name:\tpython\nVmHWM:\t200 kB\nVmSize:\t900 kB\n",
        "Rss: 150 kB\nPss: 130 kB\nPrivate_Clean: 20 kB\nPrivate_Dirty: 80 kB\n",
    )
    assert snapshot["rss_bytes"] == 150 * 1024
    assert snapshot["virtual_bytes"] == 900 * 1024
    assert snapshot["private_clean_dirty_resident_bytes"] == 100 * 1024
    assert "private_committed_bytes" not in snapshot


@pytest.mark.parametrize(
    "text",
    [
        "Rss: -1 kB",
        "Rss: 12 MB",
        "Rss: 1 kB\nRss: 2 kB",
        "Rss: 12",
        "Pss: 12 kB",
    ],
)
def test_missing_or_malformed_memory_evidence_fails(tooling, text):
    _, metrics = tooling
    with pytest.raises(ValueError):
        metrics.kib_fields(text, ("Rss",))


def test_handoff_concurrency_is_not_silently_ignored(tooling, tmp_path):
    runner, _ = tooling
    output = tmp_path / "output"
    with pytest.raises(SystemExit) as error:
        runner.main(["handoff", "--output-dir", str(output), "--concurrency", "8"])
    assert error.value.code == 2
    assert not output.exists()


@pytest.mark.parametrize(
    "result, error_type",
    [
        (None, ValueError),
        ({"allocator": "system"}, KeyError),
        ({"allocator": "system", "iterations": 1000, "process_cpu_ns": "invalid"}, TypeError),
    ],
)
def test_malformed_sample_persists_failed_status(tooling, package, tmp_path, monkeypatch, result, error_type):
    runner, _ = tooling
    monkeypatch.setattr(runner, "PACKAGE", package)
    monkeypatch.setattr(runner.Experiment, "build", lambda *_args, **_kwargs: tmp_path / "fake-binary")

    def fake_execute(_self, command, name, _timeout, _environment=None):
        log = tmp_path / f"{name}.txt"
        text = "test version" if command[0] in ("cargo", "rustc") else "ALLOCATOR_BENCHMARK=" + json.dumps(result)
        log.write_text(text, encoding="utf-8")
        return log

    monkeypatch.setattr(runner.Experiment, "execute", fake_execute)
    output = tmp_path / "experiment"
    with pytest.raises(error_type):
        runner.main(["allocator", "--output-dir", str(output), "--smoke"])
    summary = json.loads((output / "summary.json").read_text(encoding="utf-8"))
    assert summary["status"] == "failed"
    assert summary["error"]
    assert summary["samples"] == []
