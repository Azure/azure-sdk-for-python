# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.
"""Emit twice in temporary directories and compare the checked-in generated SDK.

This check never updates the package, installs dependencies, or changes Git state.
Run with --spec-repo pointing to the public azure-rest-api-specs working tree.
Both emissions use that tree's installed, pinned TypeSpec libraries.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import subprocess
import tempfile


PACKAGE = Path(__file__).resolve().parent
MODULE = Path("azure/ai/finetuning_sessions")
PROJECT = Path("specification/ai-foundry/data-plane/Foundry/src/sdk-python-azure-ai-finetuning-sessions")
TOOL_VERSIONS = json.loads((PACKAGE / "emitter-package.json").read_text(encoding="utf-8"))["dependencies"]
HANDWRITTEN_MODULES = {"_client_options.py", "_exceptions.py", "_logging_setup.py"}


def normalized_bytes(path: Path) -> bytes:
    """Ignore Windows checkout line endings, not generated content differences."""
    return path.read_bytes().replace(b"\r\n", b"\n")


def generated_files(package: Path) -> dict[str, bytes]:
    result = {}
    for path in (package / MODULE).rglob("*"):
        if not path.is_file() or "__pycache__" in path.parts or path.name == "_patch.py":
            continue
        if path.suffix != ".py" and path.name != "py.typed":
            continue
        # Exclude only the explicitly maintained custom modules, not files based
        # on a mutable generated-code banner. Missing and orphaned files fail.
        if path.relative_to(package / MODULE).as_posix() in HANDWRITTEN_MODULES:
            continue
        result[path.relative_to(package).as_posix()] = normalized_bytes(path)
    for name in ("_metadata.json", "apiview-properties.json"):
        result[name] = normalized_bytes(package / name)
    return result


def source_hashes(spec_repo: Path) -> dict[str, str]:
    root = spec_repo / PROJECT.parent
    paths = [root / "sdk-python-azure-ai-finetuning-sessions", root / "session-finetuning", root / "common"]
    return {
        path.relative_to(spec_repo).as_posix(): hashlib.sha256(normalized_bytes(path)).hexdigest()
        for directory in paths
        for path in sorted(directory.rglob("*"))
        if path.is_file() and path.suffix in {".tsp", ".yaml"}
    }


def package_hashes() -> dict[str, str]:
    """Ensure the check did not rewrite generated OR handwritten package files."""
    return {
        path.relative_to(PACKAGE).as_posix(): hashlib.sha256(path.read_bytes()).hexdigest()
        for path in (PACKAGE / MODULE).rglob("*")
        if path.is_file() and "__pycache__" not in path.parts
    }


def check_tools(spec_repo: Path) -> None:
    for name, expected in TOOL_VERSIONS.items():
        manifest = spec_repo / "node_modules" / name / "package.json"
        if not manifest.exists():
            raise RuntimeError(f"Missing generation dependency {name}; install the pinned tooling first.")
        actual = json.loads(manifest.read_text(encoding="utf-8"))["version"]
        if actual != expected:
            raise RuntimeError(f"Expected {name} {expected}, found {actual}; do not compare different toolchains.")


def emit(spec_repo: Path, output: Path) -> dict[str, bytes]:
    command = [
        "node", str(spec_repo / "node_modules/@typespec/compiler/cmd/tsp.js"),
        "compile", str(spec_repo / PROJECT / "client.tsp"),
        "--config", str(spec_repo / PROJECT / "tspconfig.yaml"),
        "--option", f"@azure-tools/typespec-python.emitter-output-dir={output.as_posix()}",
        "--pretty", "false",
    ]
    completed = subprocess.run(command, cwd=spec_repo, capture_output=True, text=True, encoding="utf-8", errors="replace")
    if completed.returncode:
        raise RuntimeError(completed.stdout + completed.stderr)
    warnings = [line for line in (completed.stdout + completed.stderr).splitlines() if "Found " in line]
    print(f"Emitted {output.name}: {'; '.join(warnings) or 'no diagnostics'}")
    return generated_files(output)


def differences(expected: dict[str, bytes], actual: dict[str, bytes]) -> list[str]:
    return [name for name in sorted(expected.keys() | actual.keys()) if expected.get(name) != actual.get(name)]


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--spec-repo", type=Path, required=True)
    args = parser.parse_args()
    spec_repo = args.spec_repo.resolve()
    check_tools(spec_repo)
    before_source = source_hashes(spec_repo)
    before_package = package_hashes()
    with tempfile.TemporaryDirectory(prefix="finetuning-generation-") as directory:
        first = emit(spec_repo, Path(directory) / "first")
        second = emit(spec_repo, Path(directory) / "second")
        unstable = differences(first, second)
        drift = differences(first, generated_files(PACKAGE))
        if unstable or drift:
            raise RuntimeError(f"Non-repeatable files: {unstable}\nSDK generation drift: {drift}")
    if before_source != source_hashes(spec_repo) or before_package != package_hashes():
        raise RuntimeError("Source or package files changed during verification.")
    print(f"PASS: {len(first)} generated files match two independent emissions; handwritten files unchanged.")
    fingerprint = hashlib.sha256(json.dumps(before_source, sort_keys=True).encode()).hexdigest()
    print(f"TypeSpec working-tree fingerprint: {fingerprint}")


if __name__ == "__main__":
    main()