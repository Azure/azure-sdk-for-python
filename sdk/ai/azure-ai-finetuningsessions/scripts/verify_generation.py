# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.
"""Emit twice in temporary directories and compare the checked-in generated SDK.

Only supported maintained hooks are supplied to each fresh emission. All other
runtime files must be emitter output. Full assembled runtime equality, including
the hooks, is checked separately from the immutable Loom API/behavior comparison.

This check never updates the package, installs dependencies, or changes Git state.
Run with --spec-repo pointing to the public azure-rest-api-specs working tree.
Use --toolchain for an isolated installation of the SDK repository's shared
eng/emitter-package.json and eng/emitter-package-lock.json. Their location is
discovered above this package, or selected with --sdk-repo. Outside an SDK
checkout, eng/generation contains an archived shared pair, not an active package
override. Without --toolchain, node_modules beside the selected manifest is used.
Only temporary build inputs and outputs are written; sources are not rewritten.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import tempfile

PACKAGE = Path(__file__).resolve().parent.parent
GENERATION = PACKAGE / "eng/generation"
MODULE = Path("azure/ai/finetuningsessions")
PROJECT = Path("specification/ai-foundry/data-plane/Foundry/src/sdk-python-azure-ai-finetuningsessions")
HANDWRITTEN_MODULES = {"_client_options.py", "_exceptions.py", "_logging_setup.py", "_operation_compat.py"}
MAINTAINED_MODULES = HANDWRITTEN_MODULES | {
    "_patch.py", "aio/_patch.py", "models/_patch.py", "operations/_patch.py", "aio/operations/_patch.py"
}
HASH_NORMALIZATION = "CRLF-to-LF"


def normalized_bytes(path: Path) -> bytes:
    """Ignore Windows checkout line endings, not generated content differences."""
    return path.read_bytes().replace(b"\r\n", b"\n")


def toolchain_paths(sdk_repo: Path | None = None, *, package: Path = PACKAGE) -> tuple[Path, Path]:
    """Prefer the public SDK checkout's central pair; never a package-local pin."""
    package = package.resolve()
    if sdk_repo is not None:
        directory = sdk_repo.resolve() / "eng"
    else:
        directory = package / "eng/generation"
        for parent in package.parents:
            # A standalone reference repository can contain unrelated tooling.
            # Only discover central SDK tooling above the SDK's sdk/ tree.
            if package.relative_to(parent).parts[0] == "sdk" and (parent / "eng/emitter-package.json").is_file():
                directory = parent / "eng"
                break
    paths = directory / "emitter-package.json", directory / "emitter-package-lock.json"
    for path in paths:
        if not path.is_file():
            raise RuntimeError(f"Missing shared generation input {path}; supply --sdk-repo or archive the shared pair.")
    return paths


def locked_tool_versions(manifest_path: Path, lock_path: Path) -> dict[str, str]:
    """Resolve every shared direct dependency from lock packages, not npm ranges."""
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    lock = json.loads(lock_path.read_text(encoding="utf-8"))
    packages = lock.get("packages", {})
    root = packages.get("")
    if lock.get("lockfileVersion") not in (2, 3) or not isinstance(root, dict):
        raise RuntimeError("The shared npm lock must contain a root packages entry (lockfile version 2 or 3).")
    if manifest.get("name") != root.get("name"):
        raise RuntimeError("Shared emitter manifest and lock root names disagree.")
    dependencies = {}
    for section in ("dependencies", "devDependencies"):
        declared = manifest.get(section, {})
        if declared != root.get(section, {}):
            raise RuntimeError(f"Shared emitter manifest/lock {section} disagree; update them together.")
        for name, requirement in declared.items():
            if name in dependencies and dependencies[name] != requirement:
                raise RuntimeError(f"Conflicting shared dependency declarations for {name}.")
            dependencies[name] = requirement
    if not dependencies:
        raise RuntimeError("The shared emitter manifest declares no generation dependencies.")
    versions = {}
    for name in sorted(dependencies):
        version = packages.get(f"node_modules/{name}", {}).get("version")
        if not isinstance(version, str) or not version:
            raise RuntimeError(f"No exact locked package version for {name}.")
        versions[name] = version
    return versions


def toolchain_fingerprints(sdk_repo: Path | None = None) -> dict[str, str]:
    """Provenance hashes cover full file bytes after CRLF-to-LF normalization only.

    Record these manifest_sha256, lockfile_sha256 and hash_normalization fields
    under provenance.toolchain. JSON ordering and whitespace remain significant.
    """
    manifest, lock = toolchain_paths(sdk_repo)
    locked_tool_versions(manifest, lock)
    return {
        "manifest_sha256": hashlib.sha256(normalized_bytes(manifest)).hexdigest(),
        "lockfile_sha256": hashlib.sha256(normalized_bytes(lock)).hexdigest(),
        "hash_normalization": HASH_NORMALIZATION,
    }


TOOL_VERSIONS = locked_tool_versions(*toolchain_paths())


def generated_files(package: Path) -> dict[str, bytes]:
    result = {}
    for path in (package / MODULE).rglob("*"):
        if not path.is_file() or "__pycache__" in path.parts or path.name == "_patch.py":
            continue
        # Exclude only the explicitly maintained custom modules, not files based
        # on a mutable generated-code banner. Missing and orphaned files fail.
        if path.relative_to(package / MODULE).as_posix() in HANDWRITTEN_MODULES:
            continue
        result[path.relative_to(package).as_posix()] = normalized_bytes(path)
    for name in ("_metadata.json", "apiview-properties.json"):
        if (package / name).is_file():
            result[name] = normalized_bytes(package / name)
    return result


def source_hashes(spec_repo: Path) -> dict[str, str]:
    root = spec_repo / PROJECT.parent
    paths = [root / PROJECT.name, root / "session-finetuning", root / "common"]
    return {
        path.relative_to(spec_repo).as_posix(): hashlib.sha256(normalized_bytes(path)).hexdigest()
        for directory in paths
        for path in sorted(directory.rglob("*"))
        if path.is_file() and path.suffix in {".tsp", ".yaml"}
    }


def package_hashes(package: Path = PACKAGE) -> dict[str, str]:
    """Ensure the check did not rewrite generated OR handwritten package files."""
    return {
        path.relative_to(package).as_posix(): hashlib.sha256(normalized_bytes(path)).hexdigest()
        for path in (package / MODULE).rglob("*")
        if path.is_file() and "__pycache__" not in path.parts
    }


def check_tools(toolchain: Path, sdk_repo: Path | None = None) -> None:
    shared_manifest, shared_lock = toolchain_paths(sdk_repo)
    versions = locked_tool_versions(shared_manifest, shared_lock)
    # Isolated npm installations rename the shared pair to package*.json.
    # Reject edited installation inputs even when node_modules was not updated.
    installed_inputs = toolchain / "package.json", toolchain / "package-lock.json"
    if any(path.exists() for path in installed_inputs):
        for installed, shared in zip(installed_inputs, (shared_manifest, shared_lock)):
            if not installed.is_file() or normalized_bytes(installed) != normalized_bytes(shared):
                raise RuntimeError(f"Installed toolchain input {installed} differs from the shared {shared.name}.")
    for name, expected in versions.items():
        manifest = toolchain / "node_modules" / name / "package.json"
        if not manifest.exists():
            raise RuntimeError(f"Missing generation dependency {name}; install the pinned tooling first.")
        actual = json.loads(manifest.read_text(encoding="utf-8"))["version"]
        if actual != expected:
            raise RuntimeError(f"Expected {name} {expected}, found {actual}; do not compare different toolchains.")


def check_provenance(spec_repo: Path, sdk_repo: Path | None = None) -> None:
    """Reject a stale checked-in provenance claim rather than silently updating it."""
    provenance = json.loads((GENERATION / "provenance.json").read_text(encoding="utf-8"))
    tooling = toolchain_fingerprints(sdk_repo)
    source = source_hashes(spec_repo)
    source_fingerprint = hashlib.sha256(json.dumps(source, sort_keys=True).encode()).hexdigest()
    generated = {name: hashlib.sha256(value).hexdigest() for name, value in generated_files(PACKAGE).items()}
    actual = {
        "source": source_fingerprint,
        "generated": hashlib.sha256(json.dumps(generated, sort_keys=True).encode()).hexdigest(),
        "runtime": hashlib.sha256(json.dumps(package_hashes(), sort_keys=True).encode()).hexdigest(),
        "manifest": tooling["manifest_sha256"],
        "lock": tooling["lockfile_sha256"],
        "hash_normalization": tooling["hash_normalization"],
        "archived_manifest": hashlib.sha256(normalized_bytes(GENERATION / "emitter-package.json")).hexdigest(),
        "archived_lock": hashlib.sha256(normalized_bytes(GENERATION / "emitter-package-lock.json")).hexdigest(),
    }
    expected = {
        "source": provenance["typespec"]["source_fingerprint_sha256"],
        "generated": provenance["assembly"]["generated_inventory_fingerprint_sha256"],
        "runtime": provenance["assembly"]["runtime_fingerprint_sha256"],
        "manifest": provenance["toolchain"].get("manifest_sha256"),
        "lock": provenance["toolchain"]["lockfile_sha256"],
        "hash_normalization": provenance["toolchain"].get("hash_normalization"),
        "archived_manifest": provenance["toolchain"].get("manifest_sha256"),
        "archived_lock": provenance["toolchain"]["lockfile_sha256"],
    }
    if actual != expected:
        raise RuntimeError(f"Generation provenance is stale: expected={expected}; actual={actual}")


def emit(spec_repo: Path, output: Path, toolchain: Path | None = None) -> dict[str, bytes]:
    toolchain = (toolchain or toolchain_paths()[0].parent).resolve()
    # Keep a complete local input snapshot under the selected toolchain so
    # package resolution cannot accidentally mix pnpm and old npm libraries.
    with tempfile.TemporaryDirectory(prefix="finetuning-inputs-", dir=toolchain, ignore_cleanup_errors=True) as directory:
        inputs = Path(directory)
        for folder in (PROJECT.name, "session-finetuning", "common"):
            source = spec_repo / PROJECT.parent / folder
            shutil.copytree(source, inputs / folder, ignore=shutil.ignore_patterns("node_modules", "tsp-output"))
        # Seed only explicit customization inputs. The emitter's documented
        # _patch.py preservation is verified, not simulated by copying a
        # completed SDK over the generated output afterward.
        for relative in sorted(MAINTAINED_MODULES):
            path = PACKAGE / MODULE / relative
            if not path.is_file():
                raise RuntimeError(f"Missing maintained generation hook: {relative}")
            destination = output / MODULE / relative
            destination.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(path, destination)
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
        "--option",
        "@azure-tools/typespec-python.generate-packaging-files=false",
        "--warn-as-error",
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
    parser.add_argument("--sdk-repo", type=Path, help="SDK checkout containing the authoritative eng/emitter-package*.json")
    args = parser.parse_args()
    spec_repo = args.spec_repo.resolve()
    toolchain = (args.toolchain or toolchain_paths(args.sdk_repo)[0].parent).resolve()
    check_tools(toolchain, args.sdk_repo)
    check_provenance(spec_repo, args.sdk_repo)
    before_source = source_hashes(spec_repo)
    before_package = package_hashes()
    with tempfile.TemporaryDirectory(prefix="finetuning-generation-", ignore_cleanup_errors=True) as directory:
        first_path, second_path = Path(directory) / "first", Path(directory) / "second"
        first = emit(spec_repo, first_path, toolchain)
        second = emit(spec_repo, second_path, toolchain)
        unstable = differences(first, second)
        drift = differences(first, generated_files(PACKAGE))
        if unstable or drift:
            raise RuntimeError(f"Non-repeatable files: {unstable}\nSDK generation drift: {drift}")
        if package_hashes(first_path) != before_package or package_hashes(second_path) != before_package:
            raise RuntimeError("The complete regenerated runtime or a maintained customization changed.")
    if before_source != source_hashes(spec_repo) or before_package != package_hashes():
        raise RuntimeError("Source or package files changed during verification.")
    print(f"PASS: {len(first)} generated files and the complete customized runtime match two independent emissions.")
    fingerprint = hashlib.sha256(json.dumps(before_source, sort_keys=True).encode()).hexdigest()
    print(f"TypeSpec working-tree fingerprint: {fingerprint}")


if __name__ == "__main__":
    main()
