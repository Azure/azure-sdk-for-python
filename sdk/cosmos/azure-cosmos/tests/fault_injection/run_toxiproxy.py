# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.
"""Repeat the pinned, local-only network tests without changing an installation."""

import argparse
import datetime
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[2]
if __package__ in (None, ""):
    sys.path.insert(0, str(ROOT / "tests"))

from fault_injection._process_tree import run_owned_worker
from fault_injection._toxiproxy_config import DRIVER_COMMIT, digest, validate_endpoint, verify_server

SELECTIONS = {
    "unit": [
        "test_toxiproxy_unit.py",
        "test_tcp_observer_unit.py",
        "test_toxiproxy_local_unit.py",
    ],
    "writes": ["test_toxiproxy_write.py", "test_toxiproxy_local_unit.py"],
    "sockets": ["test_toxiproxy_reset_socket.py", "test_toxiproxy_local_unit.py"],
    "full": [
        "test_toxiproxy_route.py",
        "test_toxiproxy_write.py",
        "test_toxiproxy_reset_socket.py",
        "test_toxiproxy_unit.py",
        "test_tcp_observer_unit.py",
        "test_toxiproxy_local_unit.py",
    ],
    "no-opt-in": [
        "test_toxiproxy_route.py",
        "test_toxiproxy_write.py",
        "test_toxiproxy_reset_socket.py",
    ],
}


def worker(argv):
    if sys.stdin.buffer.read(1) != b"1":
        raise RuntimeError("Runner did not establish process-tree ownership")
    base, manifest_path, output = map(Path, argv[:3])
    import azure

    azure.__path__.insert(0, str(base / "azure"))
    from azure.cosmos import _rust
    from test_config import TestConfig
    import pytest

    manifest = json.loads(manifest_path.read_text())
    if Path(_rust.__file__).resolve() != (base / r"azure\cosmos\_rust.pyd").resolve():
        raise RuntimeError("Worker loaded an extension outside the selected snapshot")
    if digest(Path(_rust.__file__)) != manifest["binary_sha256"]:
        raise RuntimeError("Worker extension checksum differs from the selected snapshot")
    if _rust.__rust_driver_commit__ != DRIVER_COMMIT:
        raise RuntimeError("Worker extension does not contain the pinned driver")
    os.environ["ACCOUNT_KEY"] = TestConfig.masterKey
    return pytest.main(
        [
            "-q",
            "-s",
            "-o",
            "pythonpath=tests",
            "--confcutdir=tests\\fault_injection",
            "--basetemp=" + str(output / "temp"),
            "--junitxml=" + str(output / "live.xml"),
            *[str(Path("tests") / "fault_injection" / name) for name in argv[3:]],
        ]
    )


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--sdk-snapshot", type=Path, required=True)
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument("--server", type=Path)
    parser.add_argument("--output", type=Path, required=True, help="A new, nonexistent run directory")
    parser.add_argument("--endpoint", default="https://localhost:8081/")
    parser.add_argument("--selection", choices=SELECTIONS, default="full")
    args = parser.parse_args(argv)
    validate_endpoint(args.endpoint)
    base, manifest_path, output = (
        args.sdk_snapshot.resolve(),
        args.manifest.resolve(),
        args.output.resolve(),
    )
    manifest = json.loads(manifest_path.read_text())
    assert (
        manifest["driver_source"]
        == f"git+https://github.com/Azure/azure-sdk-for-rust?rev={DRIVER_COMMIT}#{DRIVER_COMMIT}"
    )
    assert all(digest(base / path) == value for path, value in manifest["sources"].items()), "Snapshot source drift"
    assert digest(base / r"azure\cosmos\_rust.pyd") == manifest["binary_sha256"], "Snapshot binary drift"
    if args.selection != "no-opt-in":
        if args.server is None:
            raise ValueError("Supply the pinned Windows x64 Toxiproxy executable")
        verify_server(args.server)
    output.mkdir(parents=True, exist_ok=False)
    selection = SELECTIONS[args.selection]
    sources = {str(path.relative_to(ROOT)): digest(path) for path in (ROOT / r"tests\fault_injection").glob("*.py")}
    for path, value in sources.items():
        target = output / "test_sources" / path
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(ROOT / path, target)
        assert digest(target) == value
    shutil.copy2(manifest_path, output / "build.json")
    shared = ROOT / r"azure\cosmos\_rust.pyd"
    shared_before = digest(shared)
    env = os.environ.copy()
    env.pop("ACCOUNT_KEY", None)
    env.pop("TOXIPROXY_SERVER", None)
    env.update(
        ACCOUNT_HOST=args.endpoint,
        AZURE_COSMOS_E2E_BACKGROUND_ACCOUNT_REFRESH_INTERVAL_MS="100",
    )
    if args.selection != "no-opt-in":
        env["TOXIPROXY_SERVER"] = str(args.server.resolve())
    status, timed_out = None, False
    worker_state = {}
    print("RUN_DIRECTORY", output, flush=True)
    try:
        with (output / "live.txt").open("w", encoding="utf-8") as log:
            status = run_owned_worker(
                [
                    sys.executable,
                    str(Path(__file__).resolve()),
                    "--worker",
                    str(base),
                    str(manifest_path),
                    str(output),
                    *selection,
                ],
                cwd=ROOT,
                env=env,
                log=log,
                state=worker_state,
            )
    except subprocess.TimeoutExpired:
        timed_out = True
        raise
    finally:
        record = {
            "date": datetime.datetime.now(datetime.timezone.utc).isoformat(),
            "exit_code": status,
            "outer_timeout": timed_out,
            **worker_state,
            "selection": selection,
            "test_hashes": sources,
            "tests_unchanged": all(digest(ROOT / path) == value for path, value in sources.items()),
            "snapshot_unchanged": all(digest(base / path) == value for path, value in manifest["sources"].items())
            and digest(base / r"azure\cosmos\_rust.pyd") == manifest["binary_sha256"],
            "shared_binary_before": shared_before,
            "shared_binary_after": digest(shared),
            "current_source_drift": [
                path
                for path, value in manifest["sources"].items()
                if not (ROOT / path).is_file() or digest(ROOT / path) != value
            ],
        }
        (output / "run.json").write_text(json.dumps(record, indent=2), encoding="utf-8")
    assert record["tests_unchanged"] and record["snapshot_unchanged"]
    assert record["shared_binary_before"] == record["shared_binary_after"]
    print(json.dumps({"exit_code": status, "output": str(output)}))
    return status


if __name__ == "__main__":
    sys.exit(worker(sys.argv[2:]) if sys.argv[1:2] == ["--worker"] else main())
