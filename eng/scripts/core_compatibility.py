#!/usr/bin/env python
# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# -------------------------------------------------------------------------
"""Run generated-client compatibility against this checkout's core packages."""

import argparse
import ast
from collections.abc import Iterator, Mapping, Sequence
import configparser
from contextlib import contextmanager
import importlib
import importlib.metadata
import json
import os
from pathlib import Path
import shlex
import shutil
import socket
import subprocess
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
import venv


# Standalone Python emitter 0.38.0, reviewed 2026-10-02; update together with its test contract.
TYPESPEC_REF = "06e398a022bd46bb93d283b1f975ddf005e86729"
NPM_FEED = "https://pkgs.dev.azure.com/azure-sdk/public/_packaging/azure-sdk-for-js/npm/registry/"
CORES = {"azure-core": "azure.core", "azure-mgmt-core": "azure.mgmt.core"}


def run(command: Sequence[str | Path], cwd: Path, env: Mapping[str, str]) -> None:
    subprocess.run([str(arg) for arg in command], cwd=cwd, env=env, check=True)


def feed_environment(environ: Mapping[str, str]) -> dict[str, str]:
    env = dict(environ)
    env.pop("PIP_ISOLATED", None)
    index = urllib.parse.urlsplit(env.get("PIP_INDEX_URL", ""))
    if (
        index.scheme != "https"
        or index.hostname != "pkgs.dev.azure.com"
        or not index.path.startswith("/azure-sdk/")
        or "/_packaging/azure-sdk-for-python" not in index.path
        or not index.path.endswith("/pypi/simple/")
        or not index.username
        or not index.password
    ):
        raise ValueError(
            "An authenticated Azure SDK Python CFS PIP_INDEX_URL is required; run PipAuthenticate."
        )
    env.update(
        PIP_CONFIG_FILE=os.devnull,
        PIP_EXTRA_INDEX_URL="",
        PIP_FIND_LINKS="",
        PIP_DISABLE_PIP_VERSION_CHECK="1",
        UV_DEFAULT_INDEX=env["PIP_INDEX_URL"],
        UV_INDEX_URL=env["PIP_INDEX_URL"],
        UV_INDEX="",
        UV_EXTRA_INDEX_URL="",
        UV_FIND_LINKS="",
        UV_NO_CONFIG="true",
        UV_PYTHON_DOWNLOADS="never",
        UV_NO_MANAGED_PYTHON="true",
        UV_KEYRING_PROVIDER="disabled",
        npm_config_registry=NPM_FEED,
    )
    return env


def redirect_npm_lock(lock_path: Path) -> None:
    """Route locked tarballs through CFS without changing versions or integrity."""
    lock = json.loads(lock_path.read_text(encoding="utf-8"))
    if lock["lockfileVersion"] != 3:
        raise ValueError("Expected the standalone emitter's npm v3 lockfile.")
    for key, package in lock["packages"].items():
        if not key:
            continue
        url = urllib.parse.urlsplit(package.get("resolved", ""))
        if url.scheme != "https" or not (
            url.hostname in ("registry.npmjs.org", "pkgs.dev.azure.com")
            or (url.hostname or "").endswith(".pkgs.visualstudio.com")
        ):
            raise ValueError(
                f"Unexpected locked package origin for {key}; review before updating the upstream pin."
            )
        name = package.get("name", key.rsplit("node_modules/", 1)[-1])
        package["resolved"] = (
            f"{NPM_FEED}{name}/-/{name.rsplit('/', 1)[-1]}-{package['version']}.tgz"
        )
    lock_path.write_text(json.dumps(lock, indent=2) + "\n", encoding="utf-8")


def core_sources(sdk_root: Path) -> dict[str, Path]:
    return {name: sdk_root / "sdk" / "core" / name for name in CORES}


def source_version(source: Path, module: str) -> str:
    version_file = source.joinpath(*module.split("."), "_version.py")
    for node in ast.parse(version_file.read_text(encoding="utf-8")).body:
        if isinstance(node, ast.Assign) and any(
            isinstance(t, ast.Name) and t.id == "VERSION" for t in node.targets
        ):
            version = ast.literal_eval(node.value)
            if not isinstance(version, str):
                raise ValueError(f"VERSION is not a string in {version_file}")
            return version
    raise ValueError(f"No VERSION in {version_file}")


def verify_local_cores(sdk_root: Path) -> None:
    for name, source in core_sources(sdk_root.resolve()).items():
        module = importlib.import_module(CORES[name])
        expected_file = source.joinpath(
            *CORES[name].split("."), "__init__.py"
        ).resolve()
        dist = importlib.metadata.distribution(name)
        direct = json.loads(dist.read_text("direct_url.json") or "{}")
        expected_version = source_version(source, CORES[name])
        if (
            Path(module.__file__).resolve() != expected_file
            or dist.version != expected_version
            or module.__version__ != expected_version
            or direct.get("url") != source.as_uri()
            or not direct.get("dir_info", {}).get("editable")
        ):
            raise RuntimeError(
                f"{name} is not the editable SDK PR source at {source} (loaded {module.__file__})."
            )
        print(f"Verified {name}=={dist.version}: {module.__file__}", flush=True)


def pytest_sessionstart(session: object) -> None:
    # Also runs in every xdist worker, not just the host that launches tox.
    verify_local_cores(Path(os.environ["SDK_CORE_ROOT"]))


def prepare_tox(package: Path, sdk_root: Path, work_dir: Path) -> tuple[Path, Path]:
    tests = package / "tests"
    requirements = tests / "requirements" / "azure.txt"
    lines = requirements.read_text(encoding="utf-8").splitlines()
    core_lines = [
        line for line in lines if line.startswith(("azure-core", "azure-mgmt-core"))
    ]
    if core_lines != ["azure-core>=1.37.0", "azure-mgmt-core==1.6.0"]:
        raise ValueError(
            "Upstream Azure core requirements changed; review the compatibility overlay."
        )
    filtered = work_dir / "azure-requirements.txt"
    filtered.write_text(
        "\n".join(
            (
                f"-r {(requirements.parent / 'base.txt').as_posix()}"
                if line == "-r base.txt"
                else line
            )
            for line in lines
            if line not in core_lines
        )
        + "\n",
        encoding="utf-8",
    )
    constraints = work_dir / "core-constraints.txt"
    constraints.write_text(
        "".join(
            f"{name} @ {source.as_uri()}\n"
            for name, source in core_sources(sdk_root).items()
        ),
        encoding="utf-8",
    )
    config = configparser.ConfigParser(interpolation=None)
    config.read_string(
        (tests / "tox.ini")
        .read_text(encoding="utf-8")
        .replace("{tox_root}", tests.as_posix())
    )
    env = config["testenv:test-azure"]
    expected_commands = (
        f"python {tests.as_posix()}/install_packages.py azure {tests.as_posix()}\n"
        "pytest mock_api/azure mock_api/shared -v -n auto {posargs}"
    )
    if env["commands"].strip() != expected_commands:
        raise ValueError(
            "Upstream test-azure commands changed; review the compatibility overlay."
        )
    fixture = tests / "mock_api" / "conftest.py"
    if fixture.exists():
        raise ValueError(
            "Upstream mock_api conftest changed; review the managed-server overlay."
        )
    # A nearer fixture prevents upstream's fallback from spawning an unowned server.
    fixture.write_text(
        "import pytest\n"
        "from core_compatibility import server_ready\n\n"
        '@pytest.fixture(scope="session", autouse=True)\n'
        "def testserver():\n"
        '    if not server_ready("http://localhost:3000/.admin/health"):\n'
        '        pytest.fail("SDK-managed Spector is not healthy; auto-start is disabled.")\n'
        "    yield\n",
        encoding="utf-8",
    )
    env["deps"] = "\n".join(
        [f"-r {filtered.as_posix()}"]
        + [f"-e {source.as_posix()}" for source in core_sources(sdk_root).values()]
        + [f"-e {(package / 'generator').as_posix()}"]
    )
    config["tox"]["envlist"] = "test-azure"
    config["tox"]["work_dir"] = (work_dir / "tox").as_posix()
    base = config["testenv"]
    base["passenv"] = "\n".join(["PIP_*", "UV_*", "SDK_CORE_ROOT", "PATH"])
    base["setenv"] = (
        f"PYTHONPATH = {Path(__file__).parent.as_posix()}{os.pathsep}{(package / 'generator').as_posix()}\n"
        "FLAVOR = azure\n"
        f"SDK_CORE_ROOT = {sdk_root.as_posix()}\n"
        f"PIP_CONSTRAINT = {constraints.as_posix()}\n"
        f"UV_CONSTRAINT = {constraints.as_posix()}"
    )
    env["setenv"] = "{[testenv]setenv}"
    env["changedir"] = tests.as_posix()
    verify = shlex.join(
        ["python", str(Path(__file__).resolve()), "verify", "--sdk-root", str(sdk_root)]
    )
    env["commands"] = "\n".join(
        [
            verify,
            expected_commands.splitlines()[0],
            verify,
            "python -m pytest -p core_compatibility mock_api/azure mock_api/shared -v -n auto "
            f"--junitxml={shlex.quote(str(work_dir / 'results' / 'generated.xml'))} {{posargs}}",
        ]
    )
    tox_file = work_dir / "tox.ini"
    with tox_file.open("w", encoding="utf-8") as stream:
        config.write(stream)
    return tox_file, constraints


def server_ready(url: str) -> bool:
    try:
        with urllib.request.urlopen(url, timeout=1) as response:
            body = json.load(response)
            return (
                response.status == 200
                and isinstance(body, dict)
                and body.get("server") == "tsp-spector"
            )
    except (urllib.error.URLError, TimeoutError, OSError, json.JSONDecodeError):
        return False


def wait_for_server(process: subprocess.Popen, url: str, timeout: float = 60) -> None:
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        if process.poll() is not None:
            raise RuntimeError(
                f"Spector exited with code {process.returncode}; see spector.log."
            )
        if server_ready(url):
            return
        time.sleep(0.5)
    raise RuntimeError(f"Spector did not become healthy at {url}; see spector.log.")


@contextmanager
def mock_server(
    package: Path, results: Path, env: Mapping[str, str]
) -> Iterator[subprocess.Popen]:
    # Upstream clients/fixtures use port 3000; never reuse or stop someone else's server.
    with socket.socket() as probe:
        probe.bind(("127.0.0.1", 3000))
    specs = package / "node_modules"
    command = [
        "node",
        str(specs / "@typespec" / "spector" / "cmd" / "cli.mjs"),
        "serve",
        str(specs / "@azure-tools" / "azure-http-specs" / "specs"),
        str(specs / "@typespec" / "http-specs" / "specs"),
        "--port",
        "3000",
    ]
    with (results / "spector.log").open("w", encoding="utf-8") as log:
        process = subprocess.Popen(
            command, cwd=package, env=env, stdout=log, stderr=subprocess.STDOUT
        )
        try:
            wait_for_server(process, "http://localhost:3000/.admin/health")
            yield process
            if process.poll() is not None:
                raise RuntimeError("Spector exited during tests; see spector.log.")
        finally:
            if process.poll() is None:
                process.terminate()
                try:
                    process.wait(timeout=10)
                except subprocess.TimeoutExpired:
                    process.kill()
                    process.wait(timeout=10)


def run_legacy(
    python: str | Path, sdk_root: Path, results: Path, env: Mapping[str, str]
) -> None:
    core = core_sources(sdk_root)["azure-core"]
    mgmt = core_sources(sdk_root)["azure-mgmt-core"]
    run(
        [
            python,
            "-m",
            "pip",
            "install",
            "-e",
            core / "tests" / "testserver_tests" / "coretestserver",
            "opentelemetry-sdk~=1.26",
            "trio",
        ],
        core,
        env,
    )
    env = dict(env, PYTHONPATH=str(Path(__file__).parent))
    selections = [
        (
            core,
            [
                "tests/test_rest_request_backcompat.py",
                "tests/test_rest_response_backcompat.py",
                "tests/test_testserver.py",
            ],
            "legacy-core",
        ),
        (
            core,
            [
                "tests/async_tests/test_rest_response_backcompat_async.py",
                "tests/async_tests/test_testserver_async.py",
            ],
            "legacy-core-async",
        ),
        (
            mgmt,
            ["tests/test_arm_polling.py", "tests/asynctests/test_async_arm_polling.py"],
            "legacy-mgmt",
        ),
    ]
    for cwd, files, name in selections:
        run(
            [
                python,
                "-m",
                "pytest",
                "-p",
                "core_compatibility",
                *files,
                "-v",
                f"--junitxml={results / (name + '.xml')}",
            ],
            cwd,
            env,
        )


def run_compatibility(sdk_root: Path, work_dir: Path) -> None:
    sdk_root = sdk_root.resolve()
    work_dir = work_dir.resolve()
    if sys.version_info[:2] != (3, 12):
        raise ValueError("Use Python 3.12, matching the pinned upstream Python CI.")
    env = feed_environment(os.environ)
    work_dir.mkdir(parents=True, exist_ok=False)
    results = work_dir / "results"
    results.mkdir()
    checkout = work_dir / "typespec"
    run(["git", "init", checkout], work_dir, env)
    run(
        ["git", "remote", "add", "origin", "https://github.com/microsoft/typespec.git"],
        checkout,
        env,
    )
    run(["git", "sparse-checkout", "set", "packages/http-client-python"], checkout, env)
    run(["git", "fetch", "--depth=1", "origin", TYPESPEC_REF], checkout, env)
    run(["git", "checkout", "--detach", "FETCH_HEAD"], checkout, env)
    actual_ref = subprocess.check_output(
        ["git", "rev-parse", "HEAD"], cwd=checkout, text=True
    ).strip()
    if actual_ref != TYPESPEC_REF:
        raise RuntimeError(f"Unexpected TypeSpec checkout: {actual_ref}")
    stage = work_dir / "stage"
    stage.mkdir()
    shutil.copy2(checkout / "tsconfig.base.json", stage)
    package = stage / "packages" / "http-client-python"
    shutil.copytree(checkout / "packages" / "http-client-python", package)
    redirect_npm_lock(package / "package-lock.json")
    tox_file, constraints = prepare_tox(package, sdk_root, work_dir)
    env.update(
        SDK_CORE_ROOT=str(sdk_root),
        PIP_CONSTRAINT=str(constraints),
        UV_CONSTRAINT=str(constraints),
        PIP_CACHE_DIR=str(work_dir / "pip-cache"),
        UV_CACHE_DIR=str(work_dir / "uv-cache"),
        AUTOREST_PYTHON_EXE=sys.executable,
    )
    npm = shutil.which("npm")
    if npm is None:
        raise RuntimeError("npm is required (Node.js 24).")
    # Avoid the upstream prepare hook's unrelated lint/type-check dependencies.
    run([npm, "ci", "--ignore-scripts", "--no-audit", "--no-fund"], package, env)
    venv.EnvBuilder(with_pip=True).create(package / "venv")
    run(
        [sys.executable, package / "eng" / "scripts" / "setup" / "install.py"],
        package,
        env,
    )
    python = (
        package / "venv" / ("Scripts/python.exe" if os.name == "nt" else "bin/python")
    )
    if not python.is_file():
        raise RuntimeError(
            "The generator venv is missing; refusing a Pyodide fallback."
        )
    env["PATH"] = str(python.parent) + os.pathsep + env.get("PATH", "")
    run(
        [
            python,
            "-m",
            "pip",
            "install",
            "-r",
            package / "tests" / "requirements" / "base.txt",
        ]
        + [arg for source in core_sources(sdk_root).values() for arg in ("-e", source)],
        package,
        env,
    )
    run([npm, "run", "build"], package, env)
    run([npm, "run", "regenerate", "--", "--flavor=azure"], package, env)
    packages = list(
        (package / "tests" / "generated" / "azure").glob("*/pyproject.toml")
    )
    if not packages:
        raise RuntimeError(
            "Regeneration produced no Azure packages; refusing an empty compatibility run."
        )
    (results / "upstream.json").write_text(
        json.dumps(
            {
                "repository": "microsoft/typespec",
                "commit": actual_ref,
                "generated_packages": len(packages),
            },
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )
    # Spector records the upstream commit when serving specs from the staged copy.
    with mock_server(package, results, dict(env, GIT_DIR=str(checkout / ".git"))):
        run([python, "-m", "tox", "-c", tox_file, "-e", "test-azure"], package, env)
    run_legacy(python, sdk_root, results, env)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    subcommands = parser.add_subparsers(dest="command", required=True)
    verify = subcommands.add_parser("verify")
    verify.add_argument("--sdk-root", required=True, type=Path)
    execute = subcommands.add_parser("run")
    execute.add_argument("--sdk-root", required=True, type=Path)
    execute.add_argument("--work-dir", required=True, type=Path)
    args = parser.parse_args()
    if args.command == "verify":
        verify_local_cores(args.sdk_root)
    else:
        run_compatibility(args.sdk_root, args.work_dir)


if __name__ == "__main__":
    main()
