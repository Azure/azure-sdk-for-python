# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.
"""Verify the immutable Loom source oracle, or an explicitly supplied exact snapshot.

The shipping SDK is regenerated plus supported hooks, not a byte-identical copy.
Its acceptance gate is scripts/verify_compatibility.py. This tool preserves the
stronger byte/hash validation for the reference and for archived exact snapshots.
No dependencies are installed and neither repository nor its index is modified.
"""

from __future__ import annotations

import argparse
from contextlib import contextmanager
import hashlib
import json
from pathlib import Path, PurePosixPath
import subprocess
import tempfile
from typing import Iterator

PACKAGE = Path(__file__).resolve().parent.parent
NORMALIZATIONS = (
    ("azure.ai.finetuning_sessions", "azure.ai.finetuningsessions"),
    ("azure/ai/finetuning_sessions", "azure/ai/finetuningsessions"),
    ("azure-ai-finetuning-sessions", "azure-ai-finetuningsessions"),
    ("ai-finetuning-sessions", "ai-finetuningsessions"),
)


def normalized_bytes(path: Path) -> bytes:
    return path.read_bytes().replace(b"\r\n", b"\n")


def renamed_bytes(content: bytes) -> bytes:
    text = content.decode("utf-8").replace("\r\n", "\n")
    for old, new in NORMALIZATIONS:
        text = text.replace(old, new)
    return text.encode("utf-8")


def load_manifest(package: Path = PACKAGE) -> dict:
    manifest = json.loads((package / "eng/generation/reference.json").read_text(encoding="utf-8"))
    if manifest.get("schema_version") != 1 or manifest.get("status") != "loom-preview-snapshot":
        raise ValueError("Unsupported Loom snapshot manifest")
    expected = [{"from": old, "to": new} for old, new in NORMALIZATIONS]
    if manifest.get("normalizations") != expected:
        raise ValueError("Snapshot normalization must be limited to the reviewed package/import rename")
    commit = manifest.get("source_commit", "")
    if len(commit) != 40 or any(char not in "0123456789abcdef" for char in commit):
        raise ValueError("The Loom source must be pinned to a full immutable commit")
    for name in manifest["files"]:
        path = PurePosixPath(name)
        if path.is_absolute() or ".." in path.parts or path.parts[0] not in {"azure", "tests"}:
            raise ValueError(f"Invalid snapshot path: {name}")
    return manifest


def snapshot_files(package: Path) -> dict[str, bytes]:
    return {
        path.relative_to(package).as_posix(): normalized_bytes(path)
        for directory in (package / "azure", package / "tests")
        for path in directory.rglob("*")
        if path.is_file() and not {"__pycache__", ".pytest_cache"}.intersection(path.relative_to(package).parts)
    }


def _git(repo: Path, *args: str) -> bytes:
    return subprocess.check_output(["git", "--no-optional-locks", "-C", str(repo), *args])


def upstream_files(repo: Path, manifest: dict) -> dict[str, bytes]:
    commit, directory = manifest["source_commit"], manifest["source_directory"]
    prefix = directory.rstrip("/") + "/"
    paths = _git(repo, "ls-tree", "-r", "--name-only", commit, "--", directory).decode("utf-8").splitlines()
    result = {}
    for source_path in paths:
        relative = source_path.removeprefix(prefix)
        if not relative.startswith(("azure/", "tests/")):
            continue
        destination = relative.replace("azure/ai/finetuning_sessions/", "azure/ai/finetuningsessions/")
        entry = manifest["files"].get(destination)
        if entry is None or entry["source_path"] != source_path:
            raise ValueError(f"Upstream inventory mismatch: {source_path}")
        source = _git(repo, "show", f"{commit}:{source_path}")
        if hashlib.sha256(source).hexdigest() != entry["source_sha256"]:
            raise ValueError(f"Upstream blob mismatch: {source_path}")
        content = renamed_bytes(source)
        if hashlib.sha256(content).hexdigest() != entry["sha256"]:
            raise ValueError(f"Unexpected transformation: {source_path}")
        result[destination] = content
    if result.keys() != manifest["files"].keys():
        raise ValueError("Manifest does not cover exactly all upstream runtime and test files")
    return result


def verify(package: Path = PACKAGE, loom_repo: Path | None = None) -> dict:
    manifest = load_manifest(package)
    actual = snapshot_files(package)
    expected = manifest["files"]
    missing = sorted(expected.keys() - actual.keys())
    extra = sorted(actual.keys() - expected.keys())
    changed = sorted(
        name
        for name in expected.keys() & actual.keys()
        if hashlib.sha256(actual[name]).hexdigest() != expected[name]["sha256"]
    )
    if missing or extra or changed:
        raise ValueError(f"Loom snapshot drift: missing={missing}; extra={extra}; changed={changed}")
    if loom_repo is not None and upstream_files(loom_repo, manifest) != actual:
        raise ValueError("Public source differs from the name-normalized immutable Loom source")
    return manifest


@contextmanager
def reference_package(loom_repo: Path, package: Path = PACKAGE) -> Iterator[Path]:
    """Materialize only the verified immutable reference for isolated execution."""
    manifest = load_manifest(package)
    contents = upstream_files(loom_repo, manifest)
    with tempfile.TemporaryDirectory(prefix="loom-sdk-reference-") as directory:
        reference = Path(directory)
        for name, content in contents.items():
            path = reference / name
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(content)
        yield reference


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--loom-repo", type=Path, help="Local Git clone containing the pinned upstream Loom commit")
    parser.add_argument("--snapshot", type=Path, help="Verify an archived exact source snapshot (not the regenerated SDK)")
    args = parser.parse_args()
    try:
        if args.snapshot is not None:
            manifest = verify(args.snapshot, args.loom_repo)
        elif args.loom_repo is not None:
            manifest = load_manifest()
            upstream_files(args.loom_repo, manifest)
        else:
            parser.error("--loom-repo or --snapshot is required")
    except (OSError, ValueError, subprocess.CalledProcessError) as exc:
        print(f"FAIL: {exc}")
        return 1
    count = len(manifest["files"])
    print(f"PASS: all {count} reference runtime/test files verified against Loom {manifest['source_commit']}.")
    if args.loom_repo is None:
        print(
            "Checked manifest hashes; use --loom-repo to also verify original Git blobs and complete upstream inventory."
        )
    print("This verifies the immutable source oracle, not generated SDK parity or live-service correctness.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
