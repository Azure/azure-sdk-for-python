# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.
"""Build and run isolated native allocator or completion-handoff experiments."""

import argparse
import hashlib
import json
import os
from pathlib import Path
import platform
import re
import shutil
import statistics
import subprocess
import sys
import sysconfig

PACKAGE = Path(__file__).resolve().parents[2]
ASSETS = Path(__file__).resolve().parent / "native_experiments"
ADDITIONS = {"mimalloc": "0.1.52", "libmimalloc-sys": "0.1.49"}


def sha256(path):
    """Fingerprint source bytes, not just the current Git commit."""
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write_json(path, value):
    """Keep raw records and summaries outside the checkout."""
    path.write_text(json.dumps(value, indent=2), encoding="utf-8")


def replace_once(path, old, new):
    """Refuse source drift instead of silently patching a different code path."""
    text = path.read_text(encoding="utf-8")
    if text.count(old) != 1:
        raise ValueError(f"Expected exactly one experiment insertion point in {path}: {old!r}")
    path.write_text(text.replace(old, new, 1), encoding="utf-8")


def append_source(path, text):
    """Append test-only code in an isolated source tree."""
    with path.open("a", encoding="utf-8") as output:
        output.write("\n" + text + "\n")


def lock_packages(path):
    """Read Cargo-generated package blocks without a Python 3.11 dependency."""
    result = {}
    for block in re.split(r"(?m)^\[\[package\]\]\s*$", path.read_text(encoding="utf-8"))[1:]:
        fields = {}
        for field in ("name", "version", "source"):
            matches = re.findall(rf'(?m)^{field} = "([^"]+)"$', block)
            if len(matches) > 1 or (not matches and field != "source"):
                raise ValueError(f"Malformed Cargo.lock package field: {field}")
            fields[field] = matches[0] if matches else None
        key = (fields["name"], fields["version"], fields["source"])
        if key in result:
            raise ValueError(f"Duplicate Cargo.lock package: {key}")
        result[key] = block.strip()
    if not result:
        raise ValueError(f"No packages in {path}")
    return result


def check_dependencies(original, current, suite):
    """Permit only the two pinned experimental allocator additions."""
    old, new = lock_packages(original), lock_packages(current)
    if old.keys() - new.keys():
        raise ValueError("An existing dependency was removed or changed identity")
    for key, block in old.items():
        candidate = new[key]
        if key[0] == "azure_cosmos_rust" and suite == "allocator":
            candidate = re.sub(r'(?m)^ "(?:mimalloc|libmimalloc-sys)",\n', "", candidate)
        if candidate != block:
            raise ValueError(f"Existing dependency metadata changed: {key}")
    additions = new.keys() - old.keys()
    if suite == "handoff" and additions:
        raise ValueError(f"Unexpected handoff dependencies: {additions}")
    for name, version, source in additions:
        if ADDITIONS.get(name) != version or source != "registry+https://github.com/rust-lang/crates.io-index":
            raise ValueError(f"Unexpected allocator dependency: {(name, version, source)}")


def source_files(package):
    """Include compile-time fixtures and Python sources used by embedded tests."""
    files = [package / "Cargo.toml", package / "Cargo.lock"]
    toolchain = package / "rust-toolchain.toml"
    if toolchain.is_file():
        files.append(toolchain)
    files.extend(
        path
        for path in (package / "azure_cosmos_rust").rglob("*")
        if path.is_file() and not {"target", ".git", "__pycache__"}.intersection(path.relative_to(package).parts)
    )
    files.extend((package / "azure" / "cosmos").rglob("*.py"))
    files.append(package / "tests" / "create_item" / "partition_key_reference_cases.json")
    return sorted(set(files))


def snapshot(package):
    """Record all inputs used by the experiment, including uncommitted changes."""
    return {path.relative_to(package).as_posix(): sha256(path) for path in source_files(package)}


def verify_snapshot(package, expected):
    """Source changes invalidate an experiment; never restore somebody else's edits."""
    actual = snapshot(package)
    if actual != expected:
        changed = sorted(key for key in actual.keys() | expected.keys() if actual.get(key) != expected.get(key))
        raise RuntimeError(f"SDK source changed during experiment: {changed}")


def prepare_copy(package, output):
    """Create a new source-only workspace; never overwrite or delete output."""
    package, output = package.resolve(), output.resolve()
    if output == package or package in output.parents or output in package.parents:
        raise ValueError("Experiment output must be outside the SDK package and its ancestors")
    output.mkdir(parents=True, exist_ok=False)
    before = snapshot(package)
    source = output / "source"
    for name in before:
        # Python runs against the original package; copy only native compile-time inputs.
        if name.startswith("azure/") and name != "azure/cosmos/_backend/_async_credential_bridge.py":
            continue
        destination = source / name
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(package / name, destination)
        if sha256(destination) != before[name]:
            raise RuntimeError(f"Source changed while copying {name}")
    verify_snapshot(package, before)
    write_json(output / "original-source-sha256.json", before)
    return source, before


def add_feature(manifest, declaration):
    """Keep features confined to the copied crate."""
    if "[features]" in manifest.read_text(encoding="utf-8"):
        replace_once(manifest, "[features]", "[features]\n" + declaration)
    else:
        replace_once(manifest, "[dependencies]", "[features]\n" + declaration + "\n\n[dependencies]")


def instrument(source, assets, suite, target_platform):
    """Apply explicit, checked test seams; production files are never edited."""
    crate = source / "azure_cosmos_rust"
    native = crate / "src"
    manifest = crate / "Cargo.toml"
    if target_platform.startswith("linux"):
        # These are embedding test executables, not extension modules.
        replace_once(manifest, '    "extension-module",\n', "")
    if suite == "allocator":
        add_feature(manifest, 'allocator-experiment-mimalloc = ["dep:mimalloc", "dep:libmimalloc-sys"]')
        dependencies = "\n".join(
            f'{name} = {{ version = "={version}", optional = true }}' for name, version in ADDITIONS.items()
        )
        replace_once(manifest, "[dependencies]", "[dependencies]\n" + dependencies)
        append_source(
            native / "lib.rs",
            """
#[cfg(all(test, feature = "allocator-experiment-mimalloc"))]
#[global_allocator]
static EXPERIMENT_ALLOCATOR: mimalloc::MiMalloc = mimalloc::MiMalloc;
""",
        )
        append_source(
            native / "wire" / "items.rs",
            """
#[cfg(test)]
#[path = "allocator_experiment.rs"]
mod allocator_experiment;
""",
        )
        shutil.copy2(assets / "allocator_experiment.rs", native / "wire" / "allocator_experiment.rs")
        return
    add_feature(manifest, "handoff-count-allocations = []")
    append_source(native / "lib.rs", "#[cfg(test)]\nmod handoff_experiment;")
    for module in ("driver_runner", "response"):
        replace_once(native / "wire" / "mod.rs", f"mod {module};", f"pub(crate) mod {module};")
    runner = native / "wire" / "driver_runner.rs"
    for kind, name in (("type", "ResponseTupleConverter"), ("fn", "run_prepared_driver_operation_async")):
        replace_once(runner, f"pub(super) {kind} {name}", f"pub(crate) {kind} {name}")
    replace_once(
        native / "wire" / "response.rs",
        "pub(super) fn tuple_from_result<'py>",
        "pub(crate) fn tuple_from_result<'py>",
    )
    replace_once(
        native / "runtime.rs",
        "impl DriverHandle {",
        """impl DriverHandle {
    #[cfg(test)]
    pub(crate) fn for_handoff_experiment(driver: Arc<CosmosDriver>) -> Self {
        Self {
            key: "offline-handoff-experiment".to_owned(),
            driver,
            fault_rules: HashMap::new(),
            released: AtomicBool::new(true),
        }
    }
""",
    )
    append_source(runner, (assets / "handoff_runner.rs").read_text(encoding="utf-8"))
    shutil.copy2(assets / "handoff_experiment.rs", native / "handoff_experiment.rs")


def handoff_gate(pairs, smoke):
    """Functional success is not timing qualification."""
    overhead = statistics.median(
        (pair["observed"]["process_cpu_ns"] / pair["control"]["process_cpu_ns"] - 1) * 100 for pair in pairs
    )
    controls = [pair["control"]["process_cpu_ns"] for pair in pairs]
    spread = (max(controls) - min(controls)) / statistics.median(controls) * 100
    return {
        "median_observer_cpu_change_percent": overhead,
        "control_cpu_spread_percent": spread,
        "cpu_overhead_limit_percent": 10,
        "control_spread_limit_percent": 10,
        "timing_qualified": not smoke and overhead <= 10 and spread <= 10,
    }


class Experiment:
    """One bounded run with immutable inputs and separate raw artifacts."""

    def __init__(self, args):
        self.args = args
        self.output = args.output_dir.resolve()
        self.source, self.original = prepare_copy(PACKAGE, self.output)
        self.assets = self.output / "assets"
        shutil.copytree(ASSETS, self.assets, ignore=shutil.ignore_patterns("__pycache__"))
        self.environment = {
            **os.environ,
            "PYO3_PYTHON": sys.executable,
            "PYTHONPATH": os.pathsep.join(
                dict.fromkeys(
                    (str(self.assets), str(PACKAGE), sysconfig.get_path("purelib"), sysconfig.get_path("platlib"))
                )
            ),
            "NATIVE_EXPERIMENT_PACKAGE": str(PACKAGE),
            "PYTHONHASHSEED": "0",
            "PYTHONOPTIMIZE": "0",
            "CARGO_TARGET_DIR": str(PACKAGE / "target" if args.reuse_build_cache else self.output / "target"),
            "ALLOCATOR_ITERATIONS": str(args.iterations),
            "ALLOCATOR_CONCURRENCY": str(args.concurrency),
            "HANDOFF_SCRIPT": str(self.assets / "measure_handoff.py"),
            "HANDOFF_ITERATIONS": str(args.iterations),
        }
        if args.toolchain:
            self.environment["RUSTUP_TOOLCHAIN"] = args.toolchain
        self.summary = {
            "status": "in_progress",
            "suite": args.suite,
            "smoke_only": args.smoke,
            "os": platform.platform(),
            "python": sys.version,
            "interpreter": sys.executable,
            "iterations_per_arm": args.iterations,
            "concurrency": args.concurrency,
            "asset_sha256": {p.name: sha256(p) for p in self.assets.iterdir() if p.is_file()},
            "runner_sha256": sha256(Path(__file__)),
            "binary_sha256": {},
            "samples": [],
            "tuning_environment": {
                key: value
                for key, value in self.environment.items()
                if key.startswith("MIMALLOC_") or key in ("PYTHONMALLOC", "PYTHONHASHSEED", "RUSTFLAGS")
            },
            "limitations": [
                "Offline native screening, not live Cosmos or complete Python SDK performance.",
                "Allocator measurements include in-memory emulator work and response conversion.",
                "Handoff uses a cached response; service work and the public Python API are excluded.",
                "Rust allocation requests exclude Python/C allocation and are not retained memory.",
                "Counting binaries must not be used for timing comparisons.",
                "Linux private resident memory is not Windows private committed memory.",
                "Observed handoff phases are descriptive unless timing qualification passes.",
            ],
        }
        self.save()

    def save(self):
        """Persist partial progress without falsely publishing completion."""
        write_json(self.output / "summary.json", self.summary)

    def execute(self, command, name, timeout, environment=None):
        """Retain bounded command output even on failure."""
        stdout, stderr = self.output / f"{name}.stdout.txt", self.output / f"{name}.stderr.txt"
        write_json(self.output / f"{name}.command.json", {"command": command, "timeout_seconds": timeout})
        with stdout.open("x", encoding="utf-8") as out, stderr.open("x", encoding="utf-8") as err:
            result = subprocess.run(
                command,
                cwd=self.source,
                env=environment or self.environment,
                stdout=out,
                stderr=err,
                timeout=timeout,
                check=False,
            )
        if result.returncode:
            raise RuntimeError(f"{name} exited {result.returncode}; see {stdout} and {stderr}")
        return stdout

    def build(self, name, feature=None, resolve=False):
        """Copy test executables into the output directory, never into the SDK."""
        command = ["cargo", "test", "--release", "-p", "azure_cosmos_rust", "--no-run", "--message-format=json"]
        if not resolve:
            command.append("--locked")
        if self.args.offline:
            command.append("--offline")
        if feature:
            command.extend(("--features", feature))
        print(f"Building isolated {name} executable", flush=True)
        log = self.execute(command, f"build-{name}", 1200)
        check_dependencies(PACKAGE / "Cargo.lock", self.source / "Cargo.lock", self.args.suite)
        executables = []
        for line in log.read_text(encoding="utf-8").splitlines():
            if not line.startswith("{"):
                continue
            record = json.loads(line)
            if (
                record.get("reason") == "compiler-artifact"
                and record.get("executable")
                and record.get("profile", {}).get("test")
                and record["target"]["name"] == "azure_cosmos_rust"
            ):
                executables.append(Path(record["executable"]))
        if len(executables) != 1:
            raise RuntimeError(f"Expected one test executable, found {executables}")
        binary = self.output / (name + (".exe" if sys.platform == "win32" else ""))
        shutil.copy2(executables[0], binary)
        self.summary["binary_sha256"][binary.name] = sha256(binary)
        self.save()
        return binary

    def sample(self, name, mode, binary, idle_seconds=None):
        """Run one fresh process and validate the actual requested workload."""
        environment = dict(self.environment)
        allocator = self.args.suite == "allocator"
        test = "measure_allocator_native_reads" if allocator else "measure_completion_handoff"
        prefix = "ALLOCATOR_BENCHMARK=" if allocator else "HANDOFF_RESULT="
        environment.update(HANDOFF_MODE=mode, HANDOFF_OUTPUT=str(self.output / f"{name}.trace.json"))
        if idle_seconds is not None:
            environment["HANDOFF_IDLE_SECONDS"] = str(idle_seconds)
        log = self.execute(
            [str(binary), test, "--ignored", "--nocapture", "--test-threads=1"],
            name,
            180,
            environment,
        )
        records = [
            json.loads(line.split(prefix, 1)[1])
            for line in log.read_text(encoding="utf-8").splitlines()
            if prefix in line
        ]
        if len(records) != 1:
            raise RuntimeError(f"{name}: expected one result, found {len(records)}")
        result = records[0]
        if not isinstance(result, dict):
            raise ValueError(f"{name}: result must be a JSON object")
        expected_count = 0 if mode == "idle" else self.args.iterations
        identity = result.get("allocator") if allocator else result.get("mode")
        if identity != mode or result["iterations"] != expected_count:
            raise RuntimeError(f"{name}: workload identity/count mismatch")
        if mode != "idle" and result["process_cpu_ns"] <= 0:
            raise RuntimeError(f"{name}: invalid CPU accounting")
        if allocator and result["concurrency"] != self.args.concurrency:
            raise RuntimeError(f"{name}: concurrency mismatch")
        result["sample"] = name
        self.summary["samples"].append(result)
        self.save()
        print(f"Completed {name}", flush=True)
        return result

    def allocator(self):
        """Counterbalance allocator order; report screening, not production acceptance."""
        binaries = {
            "system": self.build("system", resolve=True),
            "mimalloc": self.build("mimalloc", "allocator-experiment-mimalloc"),
        }
        pairs = []
        for index in range(self.args.pairs):
            order = ("system", "mimalloc") if index % 2 == 0 else ("mimalloc", "system")
            pair = {mode: self.sample(f"pair-{index + 1:02d}-{mode}", mode, binaries[mode]) for mode in order}
            for field in ("concurrency", "body_bytes", "read_future_bytes", "worker_threads", "warmup_operations"):
                if pair["system"][field] != pair["mimalloc"][field]:
                    raise RuntimeError(f"Allocator arms differ in {field}")
            pairs.append(pair)
        self.summary["median_paired_cpu_change_percent"] = statistics.median(
            (pair["mimalloc"]["process_cpu_ns"] / pair["system"]["process_cpu_ns"] - 1) * 100 for pair in pairs
        )
        self.summary["paired_cpu_changes_percent"] = [
            (pair["mimalloc"]["process_cpu_ns"] / pair["system"]["process_cpu_ns"] - 1) * 100 for pair in pairs
        ]
        self.summary["production_qualified"] = False

    def handoff(self):
        """Keep allocation counting and phase timing in separate executables."""
        timing = self.build("timing")
        counting = self.build("counting", "handoff-count-allocations")
        pairs = []
        for index in range(self.args.pairs):
            order = ("control", "observed") if index % 2 == 0 else ("observed", "control")
            pair = {mode: self.sample(f"pair-{index + 1:02d}-{mode}", mode, timing) for mode in order}
            for field in ("body_bytes", "header_count", "event_loop"):
                if pair["control"][field] != pair["observed"][field]:
                    raise RuntimeError(f"Handoff arms differ in {field}")
            pairs.append(pair)
        self.summary.update(handoff_gate(pairs, self.args.smoke))
        allocation_pairs = []
        orders = (("allocations", "conversion"), ("conversion", "allocations"))
        for index, order in enumerate(orders[:1] if self.args.smoke else orders, 1):
            allocation_pairs.append({mode: self.sample(f"alloc-{index:02d}-{mode}", mode, counting) for mode in order})
        idle_seconds = statistics.median(pair["allocations"]["wall_ns"] / 1e9 for pair in allocation_pairs)
        self.summary["allocation_idle_control"] = self.sample("allocation-idle", "idle", counting, idle_seconds)
        self.summary["allocation_counting_qualified"] = not any(
            self.summary["allocation_idle_control"]["rust_allocation_delta"].values()
        )
        self.summary["additional_async_path_per_operation"] = [
            {
                key: (
                    pair["allocations"]["rust_allocation_delta"][key] - pair["conversion"]["rust_allocation_delta"][key]
                )
                / self.args.iterations
                for key in pair["allocations"]["rust_allocation_delta"]
            }
            for pair in allocation_pairs
        ]

    def run(self):
        """Preserve both failures and source-integrity evidence."""
        try:
            log = self.execute(
                [
                    sys.executable,
                    "-c",
                    "from native_experiment_metrics import python_source_json; print(python_source_json())",
                ],
                "python-source",
                30,
            )
            self.summary["python_source"] = json.loads(log.read_text(encoding="utf-8"))
            instrument(self.source, self.assets, self.args.suite, sys.platform)
            for program in ("rustc", "cargo"):
                log = self.execute([program, "--version"], f"{program}-version", 30)
                self.summary[program] = log.read_text(encoding="utf-8").strip()
            if self.args.suite == "allocator":
                self.allocator()
            else:
                self.handoff()
            verify_snapshot(PACKAGE, self.original)
            for name, expected in self.summary["binary_sha256"].items():
                if sha256(self.output / name) != expected:
                    raise RuntimeError(f"Experiment executable changed: {name}")
            self.summary.update(
                status="completed",
                original_sources_unchanged=True,
                experiment_lock_sha256=sha256(self.source / "Cargo.lock"),
            )
            names = {"azure_data_cosmos_driver", "pyo3", "pyo3-async-runtimes", "tokio", *ADDITIONS}
            self.summary["dependencies"] = [
                {"name": name, "version": version, "source": source}
                for name, version, source in lock_packages(self.source / "Cargo.lock")
                if name in names
            ]
        except (OSError, ValueError, RuntimeError, KeyError, TypeError, subprocess.TimeoutExpired) as error:
            self.summary.update(status="failed", error=str(error))
            raise
        finally:
            self.save()


def main(argv=None):
    """Require a new output directory and explicit opt-in invocation."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("suite", choices=("allocator", "handoff"))
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--toolchain", help="Explicit rustup override; default uses the copied toolchain file")
    parser.add_argument("--iterations", type=int)
    parser.add_argument("--pairs", type=int, default=4, choices=(2, 4, 6, 8))
    parser.add_argument("--concurrency", type=int, default=1, choices=(1, 8))
    parser.add_argument("--offline", action="store_true", help="Do not let Cargo fetch missing dependencies")
    parser.add_argument("--reuse-build-cache", action="store_true", help="Reuse package/target; never install a wheel")
    parser.add_argument("--smoke", action="store_true", help="One short pair; never timing-qualified")
    args = parser.parse_args(argv)
    if not __debug__:
        parser.error("Run without Python -O; correctness assertions must remain enabled")
    if sys.platform != "win32" and not sys.platform.startswith("linux"):
        parser.error("Only Windows and Linux are supported")
    if args.suite == "handoff" and args.concurrency != 1:
        parser.error("The handoff experiment currently requires concurrency=1")
    if args.smoke:
        args.iterations, args.pairs = 1000, 1
    elif args.iterations is None:
        args.iterations = 16384 if args.suite == "allocator" else 5000
    if not 1000 <= args.iterations <= 20000:
        parser.error("--iterations must be between 1000 and 20000")
    experiment = Experiment(args)
    experiment.run()
    print(f"Completed {args.suite}; evidence: {experiment.output / 'summary.json'}")
    if args.suite == "handoff":
        print(f"Timing qualified: {experiment.summary['timing_qualified']}")
        print(f"Allocation counting qualified: {experiment.summary['allocation_counting_qualified']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
