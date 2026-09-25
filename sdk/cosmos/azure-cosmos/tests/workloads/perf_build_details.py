# The MIT License (MIT)
# Copyright (c) Microsoft Corporation. All rights reserved.
"""Identify the selected Rust driver, source files and loaded compiled extension."""

import argparse
import hashlib
import json
from pathlib import Path
import re
import subprocess

PACKAGE_ROOT = Path(__file__).resolve().parents[2]


def driver_commit():
    metadata = json.loads(subprocess.check_output(
        ["cargo", "metadata", "--locked", "--offline", "--format-version", "1"],
        cwd=PACKAGE_ROOT, text=True,
    ))
    drivers = [p for p in metadata["packages"] if p["name"] == "azure_data_cosmos_driver"]
    if len(drivers) != 1:
        raise ValueError("Expected exactly one resolved Cosmos driver dependency")
    source = drivers[0].get("source") or ""
    match = re.search(r"#([0-9a-f]{40})$", source)
    if not source.startswith("git+") or not match:
        raise ValueError("Profiling build details currently require the locked Git driver; local path overrides need their own build record")
    return match.group(1)


def source_digest():
    """Fingerprint SDK/binding/harness sources, including uncommitted changes."""
    files = set()
    for directory, pattern in (
        ("azure/cosmos", "*.py"), ("azure_cosmos_rust/src", "*.rs"),
        ("tests/workloads", "*.py"), ("tests/workloads", "*.sh"),
    ):
        files.update((PACKAGE_ROOT / directory).rglob(pattern))
    for name in ("Cargo.toml", "Cargo.lock", "pyproject.toml", "azure_cosmos_rust/Cargo.toml",
                 "azure_cosmos_rust/build.rs", "tests/workloads/profiling_config.env.example"):
        path = PACKAGE_ROOT / name
        if path.is_file():
            files.add(path)
    if not files:
        raise ValueError("No profiling source files found")
    digest = hashlib.sha256()
    for path in sorted(files):
        digest.update(path.relative_to(PACKAGE_ROOT).as_posix().encode("utf-8"))
        digest.update(b"\0")
        digest.update(hashlib.sha256(path.read_bytes()).digest())
    return digest.hexdigest()


def extension_details():
    import azure.cosmos as sdk

    sdk_path = Path(sdk.__file__).resolve()
    if sdk_path != (PACKAGE_ROOT / "azure" / "cosmos" / "__init__.py").resolve():
        raise ValueError(f"Python imports azure.cosmos outside the selected checkout: {sdk_path}")
    from azure.cosmos import _rust

    path = Path(_rust.__file__).resolve()
    return {
        "python_sdk_path": str(sdk_path),
        "rust_extension_path": str(path),
        "rust_extension_sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
        "rust_extension_python_commit": getattr(_rust, "__python_commit__", "unknown"),
        "rust_extension_driver_commit": getattr(_rust, "__rust_driver_commit__", "unknown"),
        "rust_extension_has_operation_counter": str(callable(getattr(_rust, "_debug_operation_count", None))),
    }


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("action", choices=["driver-commit", "extension"])
    args = parser.parse_args()
    print(driver_commit() if args.action == "driver-commit" else json.dumps(extension_details()))
