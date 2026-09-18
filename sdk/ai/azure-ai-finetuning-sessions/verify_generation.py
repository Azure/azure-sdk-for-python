# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.
"""Emit twice in temporary directories and compare the checked-in generated SDK.

This check never updates the package, installs dependencies, or changes Git state.
Run with --spec-repo pointing to the public azure-rest-api-specs working tree.
Use --toolchain for an isolated installation of emitter-package.json, or omit it
to use the spec repository's installed libraries. Only temporary build inputs
and outputs are written; the source tree and SDK package are not rewritten.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import shutil
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


def check_tools(toolchain: Path) -> None:
    for name, expected in TOOL_VERSIONS.items():
        manifest = toolchain / "node_modules" / name / "package.json"
        if not manifest.exists():
            raise RuntimeError(f"Missing generation dependency {name}; install the pinned tooling first.")
        actual = json.loads(manifest.read_text(encoding="utf-8"))["version"]
        if actual != expected:
            raise RuntimeError(f"Expected {name} {expected}, found {actual}; do not compare different toolchains.")


def emit(spec_repo: Path, output: Path, toolchain: Path | None = None) -> dict[str, bytes]:
    toolchain = (toolchain or spec_repo).resolve()
    # Keep a complete local input snapshot under the selected toolchain so
    # package resolution cannot accidentally mix pnpm and old npm libraries.
    with tempfile.TemporaryDirectory(prefix="finetuning-inputs-", dir=toolchain) as directory:
        inputs = Path(directory)
        for folder in (PROJECT.name, "session-finetuning", "common"):
            source = spec_repo / PROJECT.parent / folder
            shutil.copytree(source, inputs / folder, ignore=shutil.ignore_patterns("node_modules", "tsp-output"))
        _compile(inputs / PROJECT.name, output, toolchain)
    return generated_files(output)


def _compile(project: Path, output: Path, toolchain: Path) -> None:
    command = [
        "node",
        str(toolchain / "node_modules/@typespec/compiler/cmd/tsp.js"),
        "compile",
        str(project / "client.tsp"),
        "--config",
        str(project / "tspconfig.yaml"),
        "--option",
        f"@azure-tools/typespec-python.emitter-output-dir={output.as_posix()}",
        "--pretty",
        "false",
    ]
    completed = subprocess.run(
        command, cwd=toolchain, capture_output=True, text=True, encoding="utf-8", errors="replace"
    )
    if completed.returncode:
        raise RuntimeError(completed.stdout + completed.stderr)
    warnings = [line for line in (completed.stdout + completed.stderr).splitlines() if "Found " in line]
    print(f"Emitted {output.name}: {'; '.join(warnings) or 'no diagnostics'}")


def differences(expected: dict[str, bytes], actual: dict[str, bytes]) -> list[str]:
    return [name for name in sorted(expected.keys() | actual.keys()) if expected.get(name) != actual.get(name)]


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--spec-repo", type=Path, required=True)
    parser.add_argument("--toolchain", type=Path, help="Directory containing the pinned generation node_modules")
    args = parser.parse_args()
    spec_repo = args.spec_repo.resolve()
    toolchain = (args.toolchain or spec_repo).resolve()
    check_tools(toolchain)
    before_source = source_hashes(spec_repo)
    before_package = package_hashes()
    with tempfile.TemporaryDirectory(prefix="finetuning-generation-") as directory:
        first = emit(spec_repo, Path(directory) / "first", toolchain)
        second = emit(spec_repo, Path(directory) / "second", toolchain)
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
