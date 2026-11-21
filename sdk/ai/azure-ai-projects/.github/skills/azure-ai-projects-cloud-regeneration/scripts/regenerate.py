# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.

"""Generate a validated azure-ai-projects patch on Actions, or apply its artifact."""

import argparse
import hashlib
import json
import os
from pathlib import Path, PurePosixPath
import re
import shlex
import shutil
import subprocess
import sys
import tempfile
from typing import Sequence

PACKAGE_PATH = "sdk/ai/azure-ai-projects"
PACKAGE_ROOT = Path.cwd().resolve()
CHECKS = (
    ("python", "-m", "compileall", "-q", "azure"),
    (
        "python",
        "-c",
        "import sys; from azpysdk.black import black; "
        "result = black.format_directory(sys.executable, '.', check_only=True); "
        "sys.stdout.buffer.write(result.stdout or b'') if result is not None else None; "
        "sys.stderr.buffer.write(result.stderr or b'') if result is not None else None; "
        "sys.exit(1 if result is None else result.returncode)",
    ),
    ("azpysdk", "pylint", "."),
    ("azpysdk", "mypy", "."),
    ("azpysdk", "devtest", "."),
)


def run(command: Sequence[str | Path], cwd: Path) -> None:
    print(f"+ {shlex.join(str(arg) for arg in command)}", flush=True)
    subprocess.run([str(arg) for arg in command], cwd=cwd, check=True)


def git_output(repo: Path, *args: str) -> bytes:
    return subprocess.check_output(["git", *args], cwd=repo)


def repository_root() -> Path:
    root = Path(git_output(PACKAGE_ROOT, "rev-parse", "--show-toplevel").decode().strip()).resolve()
    if root.joinpath(*PACKAGE_PATH.split("/")).resolve() != PACKAGE_ROOT:
        raise ValueError("This workflow must run from sdk/ai/azure-ai-projects in an SDK checkout.")
    return root


def check_paths(paths: Sequence[str]) -> None:
    for path in paths:
        parts = PurePosixPath(path).parts
        if not path.startswith(f"{PACKAGE_PATH}/") or ".." in parts or "\\" in path:
            raise ValueError(f"Regeneration contains an out-of-package path: {path}")
        if any(part.startswith(".env") for part in parts):
            raise ValueError(f"Regeneration must not transfer environment files: {path}")


def status_paths(status: bytes) -> list[str]:
    records = iter(status.split(b"\0"))
    paths = []
    for record in records:
        if not record:
            continue
        paths.append(record[3:].decode())
        if b"R" in record[:2] or b"C" in record[:2]:
            paths.append(next(records).decode())
    return paths


def patch_paths(numstat: bytes) -> list[str]:
    records = iter(numstat.split(b"\0"))
    paths = []
    for record in records:
        if not record:
            continue
        _, _, path = record.split(b"\t", 2)
        if path:
            paths.append(path.decode())
        else:
            paths.extend((next(records).decode(), next(records).decode()))
    return paths


def preview_patch_paths(repo: Path, patch: Path) -> list[str]:
    with tempfile.TemporaryDirectory(prefix="azure-ai-projects-patch-index-") as temporary:
        environment = {**os.environ, "GIT_INDEX_FILE": str(Path(temporary) / "index")}
        for command in (
            ["git", "read-tree", "HEAD"],
            ["git", "apply", "--cached", "--whitespace=error-all", str(patch)],
        ):
            subprocess.run(
                command, cwd=repo, env=environment, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE
            )
        numstat = subprocess.check_output(
            ["git", "diff", "--cached", "--numstat", "-z", "HEAD"], cwd=repo, env=environment
        )
    return patch_paths(numstat)


def typespec_source(path: Path, commit: str) -> str:
    text = path.read_text(encoding="utf-8")
    pattern = re.compile(r"(?m)^commit:[ \t]*([0-9a-fA-F]{40})[ \t]*$")
    matches = list(pattern.finditer(text))
    if len(matches) != 1:
        raise ValueError("tsp-location.yaml must contain one full, unquoted TypeSpec commit SHA.")
    if commit:
        path.write_text(pattern.sub(f"commit: {commit}", text), encoding="utf-8")
    return commit or matches[0].group(1).lower()


def generate(args: argparse.Namespace) -> None:
    repo = repository_root()
    if git_output(repo, "status", "--porcelain"):
        raise ValueError("Generation requires a clean Actions checkout; preserve existing edits first.")
    output = args.output_dir.resolve()
    if output == repo or repo in output.parents:
        raise ValueError("The artifact directory must be outside the SDK checkout.")
    if output.exists():
        raise ValueError("Use a fresh artifact directory to avoid returning stale results.")
    typespec_source(PACKAGE_ROOT / "tsp-location.yaml", "")
    output.mkdir(parents=True)

    sdk_commit = git_output(repo, "rev-parse", "HEAD").decode().strip()
    cli_dir = repo / "eng" / "common" / "tsp-client"
    cli_name = "@azure-tools/typespec-client-generator-cli"
    cli_version = json.loads((cli_dir / "package.json").read_text())["dependencies"][cli_name]
    emitter_version = json.loads((repo / "eng" / "emitter-package.json").read_text())["dependencies"][
        "@azure-tools/typespec-python"
    ]
    npm = shutil.which("npm")
    if not npm:
        raise RuntimeError("Node.js and npm are required to install the pinned TypeSpec CLI.")
    run([npm, "ci", "--prefix", cli_dir], repo)
    installed = cli_dir / "node_modules" / "@azure-tools" / "typespec-client-generator-cli"
    if json.loads((installed / "package.json").read_text())["version"] != cli_version:
        raise ValueError("The installed TypeSpec CLI does not match the repository pin.")
    run(
        [sys.executable, "-m", "pip", "install", "-r", repo / "eng" / "ci_tools.txt"],
        repo,
    )
    run(
        [
            sys.executable,
            "-m",
            "pip",
            "install",
            "-r",
            "dev_requirements.txt",
            "-e",
            ".",
        ],
        PACKAGE_ROOT,
    )
    run(
        [
            sys.executable,
            "-c",
            "import sys; from ci_tools.environment_exclusions import is_check_enabled, is_typing_ignored; "
            "enabled = all(is_check_enabled('.', check, True) for check in ('pylint', 'mypy')); "
            "sys.exit(0 if enabled and not is_typing_ignored('azure-ai-projects') "
            "else 'The selected SDK revision opts out of required validation.')",
        ],
        PACKAGE_ROOT,
    )

    source_commit = typespec_source(PACKAGE_ROOT / "tsp-location.yaml", args.typespec_commit)
    run(
        ["node", installed / "cmd" / "tsp-client.js", "update", "--debug", "--no-prompt"],
        PACKAGE_ROOT,
    )
    run(
        [
            "pwsh",
            "-NoLogo",
            "-NoProfile",
            "-Command",
            "& { $ErrorActionPreference = 'Stop'; $PSNativeCommandUseErrorActionPreference = $true; "
            "& ./PostEmitter.ps1 }",
        ],
        PACKAGE_ROOT,
    )
    for command in CHECKS:
        run(
            [sys.executable, *command[1:]] if command[0] == "python" else command,
            PACKAGE_ROOT,
        )

    paths = status_paths(git_output(repo, "status", "--porcelain=v1", "--untracked-files=all", "-z"))
    check_paths(paths)
    run(["git", "add", "--intent-to-add", "--", PACKAGE_PATH], repo)
    run(["git", "diff", "--check", "HEAD", "--", PACKAGE_PATH], repo)
    patch = output / "regeneration.patch"
    run(
        [
            "git",
            "diff",
            "--binary",
            "--full-index",
            f"--output={patch}",
            "HEAD",
            "--",
            PACKAGE_PATH,
        ],
        repo,
    )
    checks = [{"command": shlex.join(command), "result": "passed"} for command in CHECKS]
    result = {
        "package": PACKAGE_PATH,
        "sdk_commit": sdk_commit,
        "typespec_commit": source_commit,
        "tsp_client_version": cli_version,
        "emitter_version": emitter_version,
        "python_version": sys.version.split()[0],
        "checks": checks,
        "changed_files": sorted(set(paths)),
        "patch_sha256": hashlib.sha256(patch.read_bytes()).hexdigest(),
    }
    (output / "result.json").write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    if os.environ.get("GITHUB_STEP_SUMMARY"):
        with open(os.environ["GITHUB_STEP_SUMMARY"], "a", encoding="utf-8") as summary:
            summary.write(
                f"## azure-ai-projects regeneration\n\nSDK: `{sdk_commit}`\n\n"
                f"TypeSpec: `{source_commit}`\n\nCLI: `{cli_version}`; emitter: `{emitter_version}`\n\n"
            )
            for check in checks:
                summary.write(f"- `{check['command']}`: passed\n")
            summary.write("\nLive tests, samples, and Sphinx were not run.\n")


def apply(args: argparse.Namespace) -> None:
    repo = repository_root()
    artifact = args.artifact_dir.resolve()
    result = json.loads((artifact / "result.json").read_text(encoding="utf-8"))
    if result["package"] != PACKAGE_PATH:
        raise ValueError("The artifact is not for azure-ai-projects.")
    if result["sdk_commit"] != git_output(repo, "rev-parse", "HEAD").decode().strip():
        raise ValueError("The artifact SDK baseline differs from this checkout; regenerate from the current commit.")
    expected_source = args.typespec_commit or typespec_source(PACKAGE_ROOT / "tsp-location.yaml", "")
    if result["typespec_commit"] != expected_source:
        raise ValueError("The artifact TypeSpec commit differs from the selected source.")
    expected_checks = [{"command": shlex.join(command), "result": "passed"} for command in CHECKS]
    if result["checks"] != expected_checks:
        raise ValueError("The artifact does not contain all required passing validation results.")
    check_paths(result["changed_files"])
    patch = artifact / "regeneration.patch"
    if hashlib.sha256(patch.read_bytes()).hexdigest() != result["patch_sha256"]:
        raise ValueError("The artifact patch digest does not match result.json.")
    if not patch.stat().st_size:
        print("Generation and validation passed; there are no package changes to apply.")
        return
    check_paths(preview_patch_paths(repo, patch))
    run(["git", "diff", "--check", "--", PACKAGE_PATH], repo)
    run(["git", "apply", "--check", "--whitespace=error-all", patch], repo)
    run(["git", "apply", "--whitespace=error-all", patch], repo)
    run(["git", "diff", "--check", "--", PACKAGE_PATH], repo)


def commit_sha(value: str) -> str:
    if value and not re.fullmatch(r"[0-9a-fA-F]{40}", value):
        raise argparse.ArgumentTypeError("Pass a full 40-character TypeSpec commit SHA, or leave it empty.")
    return value.lower()


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    generator = commands.add_parser("generate")
    generator.add_argument("--typespec-commit", type=commit_sha, default="")
    generator.add_argument("--output-dir", type=Path, required=True)
    generator.set_defaults(func=generate)
    receiver = commands.add_parser("apply")
    receiver.add_argument("--artifact-dir", type=Path, required=True)
    receiver.add_argument("--typespec-commit", type=commit_sha, default="")
    receiver.set_defaults(func=apply)
    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
