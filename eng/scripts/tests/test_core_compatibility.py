# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# -------------------------------------------------------------------------
import configparser
import base64
import hashlib
import importlib.util
import importlib.metadata
import json
import os
from pathlib import Path
import subprocess
import sys
from unittest.mock import Mock
import zipfile

import pytest
import yaml
from packaging.requirements import Requirement


ROOT = Path(__file__).resolve().parents[3]
SPEC = importlib.util.spec_from_file_location(
    "core_compatibility", ROOT / "eng" / "scripts" / "core_compatibility.py"
)
compat = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(compat)
FEED = "https://build:test-token@pkgs.dev.azure.com/azure-sdk/public/_packaging/azure-sdk-for-python/pypi/simple/"


@pytest.fixture
def upstream(tmp_path):
    package = tmp_path / "package with spaces"
    requirements = package / "tests" / "requirements"
    requirements.mkdir(parents=True)
    (package / "tests/mock_api").mkdir()
    (requirements / "azure.txt").write_text(
        "-r base.txt\nazure-core>=1.37.0\nazure-mgmt-core==1.6.0\ngeojson>=3.0.0\n"
    )
    (package / "tests" / "tox.ini").write_text(
        "[tox]\nrequires = tox-uv\nenvlist = test-{azure,unbranded}\n"
        "[testenv]\ndeps = -r {tox_root}/requirements/base.txt\n"
        "passenv = PIP_INDEX_URL\nsetenv = PYTHONPATH = {tox_root}/../generator\n"
        "[testenv:test-azure]\nsetenv = {[testenv]setenv}\n"
        "deps =\n    {[testenv]deps}\n    -r {tox_root}/requirements/azure.txt\n    -e {tox_root}/../generator\n"
        "commands =\n    python {tox_root}/install_packages.py azure {tox_root}\n"
        "    pytest mock_api/azure mock_api/shared -v -n auto {posargs}\n"
    )
    return package


def test_feed_environment_closes_secondary_indexes():
    env = compat.feed_environment(
        {
            "PIP_INDEX_URL": FEED,
            "PIP_EXTRA_INDEX_URL": "https://example.test/",
            "UV_INDEX": "https://example.test/",
        }
    )
    assert env["PIP_INDEX_URL"] == FEED
    assert env["UV_DEFAULT_INDEX"] == FEED
    assert (
        env["UV_INDEX"] == env["PIP_EXTRA_INDEX_URL"] == env["UV_EXTRA_INDEX_URL"] == ""
    )
    assert env["PIP_CONFIG_FILE"] == compat.os.devnull
    assert env["PIP_FIND_LINKS"] == env["UV_FIND_LINKS"] == ""
    assert env["UV_PYTHON_DOWNLOADS"] == "never"
    assert env["npm_config_registry"] == compat.NPM_FEED


@pytest.mark.parametrize(
    "index",
    [
        "",
        "https://pypi.org/simple/",
        FEED.replace("build:test-token@", ""),
        FEED + "extra",
    ],
)
def test_feed_environment_rejects_missing_auth_or_wrong_feed(index):
    with pytest.raises(ValueError, match="authenticated"):
        compat.feed_environment({"PIP_INDEX_URL": index})


def test_npm_lock_preserves_versions_and_integrities(tmp_path):
    path = tmp_path / "package-lock.json"
    package = {
        "version": "1.0.0",
        "integrity": "sha512-original",
        "resolved": "https://registry.npmjs.org/a/-/a-1.0.0.tgz",
    }
    path.write_text(
        json.dumps(
            {
                "lockfileVersion": 3,
                "packages": {"": {}, "node_modules/@scope/a": package},
            }
        )
    )
    compat.redirect_npm_lock(path)
    actual = json.loads(path.read_text())["packages"]["node_modules/@scope/a"]
    assert actual["resolved"] == compat.NPM_FEED + "@scope/a/-/a-1.0.0.tgz"
    assert actual["version"] == package["version"]
    assert actual["integrity"] == package["integrity"]


def test_npm_lock_rejects_unreviewed_origin(tmp_path):
    path = tmp_path / "package-lock.json"
    path.write_text(
        json.dumps(
            {
                "lockfileVersion": 3,
                "packages": {"node_modules/a": {"resolved": "git+ssh://host/a"}},
            }
        )
    )
    with pytest.raises(ValueError, match="Unexpected locked"):
        compat.redirect_npm_lock(path)


def test_overlay_injects_both_local_cores_and_guards_actual_environment(
    upstream, tmp_path
):
    sdk = (tmp_path / "sdk checkout").resolve()
    config_path, constraints = compat.prepare_tox(upstream, sdk, tmp_path)
    config = configparser.ConfigParser(interpolation=None)
    config.read(config_path)
    azure = config["testenv:test-azure"]
    assert f"-e {(sdk / 'sdk/core/azure-core').as_posix()}" in azure["deps"]
    assert f"-e {(sdk / 'sdk/core/azure-mgmt-core').as_posix()}" in azure["deps"]
    assert "-e " + (upstream / "generator").as_posix() in azure["deps"]
    assert config["testenv"]["setenv"].count(str(constraints.as_posix())) == 2
    assert "SDK_CORE_ROOT" in config["testenv"]["setenv"]
    commands = azure["commands"].strip().splitlines()
    assert "verify --sdk-root" in commands[0]
    assert "install_packages.py azure" in commands[1]
    assert commands[2] == commands[0]
    assert "-p core_compatibility mock_api/azure mock_api/shared" in commands[3]
    assert "-n auto" in commands[3]
    assert "{posargs}" in commands[3]
    filtered = (tmp_path / "azure-requirements.txt").read_text()
    assert "azure-core" not in filtered and "azure-mgmt-core" not in filtered
    assert "-r " + (upstream / "tests/requirements/base.txt").as_posix() in filtered
    assert "geojson>=3.0.0" in filtered
    assert "azure-core @ file:" in constraints.read_text()
    assert "azure-mgmt-core @ file:" in constraints.read_text()
    fixture = (upstream / "tests/mock_api/conftest.py").read_text()
    assert "SDK-managed Spector is not healthy" in fixture
    assert "subprocess" not in fixture


@pytest.mark.parametrize("file", ["requirements/azure.txt", "tox.ini"])
def test_overlay_fails_on_upstream_contract_drift(upstream, tmp_path, file):
    path = upstream / "tests" / file
    path.write_text(
        path.read_text()
        .replace("1.6.0", "1.7.0")
        .replace("pytest mock_api", "pytest changed mock_api")
    )
    with pytest.raises(ValueError, match="Upstream"):
        compat.prepare_tox(upstream, tmp_path, tmp_path)


def test_overlay_refuses_to_overwrite_an_upstream_fixture(upstream, tmp_path):
    fixture = upstream / "tests/mock_api/conftest.py"
    fixture.write_text("# Upstream fixture\n")
    with pytest.raises(ValueError, match="conftest changed"):
        compat.prepare_tox(upstream, tmp_path, tmp_path)
    assert fixture.read_text() == "# Upstream fixture\n"


def test_verify_checks_distribution_and_import_provenance(monkeypatch, tmp_path):
    sdk = tmp_path.resolve()
    modules = {}
    distributions = {}
    for name, source in compat.core_sources(sdk).items():
        module_name = compat.CORES[name]
        folder = source.joinpath(*module_name.split("."))
        folder.mkdir(parents=True)
        (folder / "_version.py").write_text('VERSION = "9.1.0b1"\n')
        modules[module_name] = Mock(
            __file__=str(folder / "__init__.py"), __version__="9.1.0b1"
        )
        dist = Mock(version="9.1.0b1")
        dist.read_text.return_value = json.dumps(
            {"url": source.as_uri(), "dir_info": {"editable": True}}
        )
        distributions[name] = dist
    monkeypatch.setattr(compat.importlib, "import_module", modules.__getitem__)
    monkeypatch.setattr(
        compat.importlib.metadata, "distribution", distributions.__getitem__
    )
    compat.verify_local_cores(sdk)
    modules["azure.mgmt.core"].__file__ = str(tmp_path / "released/__init__.py")
    with pytest.raises(RuntimeError, match="azure-mgmt-core"):
        compat.verify_local_cores(sdk)
    modules["azure.mgmt.core"].__file__ = str(
        compat.core_sources(sdk)["azure-mgmt-core"] / "azure/mgmt/core/__init__.py"
    )
    distributions["azure-mgmt-core"].version = "1.6.0"
    with pytest.raises(RuntimeError, match="azure-mgmt-core"):
        compat.verify_local_cores(sdk)
    distributions["azure-mgmt-core"].version = "9.1.0b1"
    distributions["azure-mgmt-core"].read_text.return_value = None
    with pytest.raises(RuntimeError, match="azure-mgmt-core"):
        compat.verify_local_cores(sdk)


def test_pytest_guard_checks_each_worker(monkeypatch, tmp_path):
    monkeypatch.setenv("SDK_CORE_ROOT", str(tmp_path))
    verify = Mock()
    monkeypatch.setattr(compat, "verify_local_cores", verify)
    compat.pytest_sessionstart(Mock())
    verify.assert_called_once_with(tmp_path)


def test_run_propagates_command_failure(monkeypatch, tmp_path):
    failed = Mock(side_effect=subprocess.CalledProcessError(17, ["npm"]))
    monkeypatch.setattr(compat.subprocess, "run", failed)
    with pytest.raises(subprocess.CalledProcessError) as error:
        compat.run(["npm", "ci"], tmp_path, {})
    assert error.value.returncode == 17
    assert failed.call_args.kwargs["check"] is True


def test_health_requires_spector_identity(monkeypatch):
    response = Mock(status=200)
    response.__enter__ = Mock(return_value=response)
    response.__exit__ = Mock(return_value=False)
    response.read.return_value = b'{"server":"tsp-spector"}'
    monkeypatch.setattr(compat.urllib.request, "urlopen", Mock(return_value=response))
    assert compat.server_ready("http://localhost/health")
    response.read.return_value = b'{"server":"unrelated"}'
    assert not compat.server_ready("http://localhost/health")
    response.read.return_value = b"[]"
    assert not compat.server_ready("http://localhost/health")


def test_server_startup_failure_and_timeout(monkeypatch):
    exited = Mock()
    exited.poll.return_value = 7
    exited.returncode = 7
    with pytest.raises(RuntimeError, match="exited with code 7"):
        compat.wait_for_server(exited, "http://localhost")
    alive = Mock()
    alive.poll.return_value = None
    monkeypatch.setattr(compat, "server_ready", Mock(return_value=False))
    with pytest.raises(RuntimeError, match="did not become healthy"):
        compat.wait_for_server(alive, "http://localhost", timeout=0)


@pytest.mark.parametrize("failure", [False, True])
def test_mock_server_cleanup_on_success_and_test_failure(
    monkeypatch, tmp_path, failure
):
    process = Mock()
    process.poll.return_value = None
    start = Mock(return_value=process)
    probe = Mock()
    probe.__enter__ = Mock(return_value=probe)
    probe.__exit__ = Mock(return_value=False)
    monkeypatch.setattr(compat.socket, "socket", Mock(return_value=probe))
    monkeypatch.setattr(compat.subprocess, "Popen", start)
    monkeypatch.setattr(compat, "wait_for_server", Mock())
    try:
        with compat.mock_server(tmp_path, tmp_path, {}):
            if failure:
                raise subprocess.CalledProcessError(1, ["tox"])
    except subprocess.CalledProcessError:
        assert failure
    process.terminate.assert_called_once()
    process.wait.assert_called_once_with(timeout=10)
    command = start.call_args.args[0]
    assert command[0] == "node"
    assert "npx" not in command
    assert str(tmp_path / "node_modules/@typespec/http-specs/specs") in command
    assert str(tmp_path / "node_modules/@azure-tools/azure-http-specs/specs") in command


def test_mock_server_cleanup_on_startup_failure(monkeypatch, tmp_path):
    process = Mock()
    process.poll.return_value = None
    monkeypatch.setattr(compat.subprocess, "Popen", Mock(return_value=process))
    probe = Mock()
    probe.__enter__ = Mock(return_value=probe)
    probe.__exit__ = Mock(return_value=False)
    monkeypatch.setattr(compat.socket, "socket", Mock(return_value=probe))
    monkeypatch.setattr(
        compat, "wait_for_server", Mock(side_effect=RuntimeError("startup"))
    )
    process.wait.side_effect = [subprocess.TimeoutExpired("node", 10), None]
    with pytest.raises(RuntimeError, match="startup"):
        with compat.mock_server(tmp_path, tmp_path, {}):
            pytest.fail("Tests must not run after startup failure")
    process.terminate.assert_called_once()
    process.kill.assert_called_once()


def test_mock_server_refuses_occupied_port(monkeypatch, tmp_path):
    probe = Mock()
    probe.__enter__ = Mock(return_value=probe)
    probe.__exit__ = Mock(return_value=False)
    probe.bind.side_effect = OSError("Port in use")
    start = Mock()
    monkeypatch.setattr(compat.socket, "socket", Mock(return_value=probe))
    monkeypatch.setattr(compat.subprocess, "Popen", start)
    with pytest.raises(OSError, match="Port in use"):
        with compat.mock_server(tmp_path, tmp_path, {}):
            pytest.fail("Must not reuse an unrelated server")
    start.assert_not_called()


def test_mock_server_reports_exit_during_tests(monkeypatch, tmp_path):
    process = Mock()
    process.poll.return_value = 1
    monkeypatch.setattr(compat.subprocess, "Popen", Mock(return_value=process))
    probe = Mock()
    probe.__enter__ = Mock(return_value=probe)
    probe.__exit__ = Mock(return_value=False)
    monkeypatch.setattr(compat.socket, "socket", Mock(return_value=probe))
    monkeypatch.setattr(compat, "wait_for_server", Mock())
    with pytest.raises(RuntimeError, match="exited during tests"):
        with compat.mock_server(tmp_path, tmp_path, {}):
            pass
    process.terminate.assert_not_called()


@pytest.mark.parametrize("regeneration_failure", [False, True])
def test_orchestration_runs_only_after_successful_setup(
    monkeypatch, upstream, tmp_path, regeneration_failure
):
    work = tmp_path / "work"
    calls = []

    def execute(command, cwd, env):
        calls.append([str(arg) for arg in command])
        if command[:2] == ["git", "init"]:
            checkout = Path(command[2])
            checkout.mkdir()
            (checkout / "tsconfig.base.json").write_text("{}")
            compat.shutil.copytree(upstream, checkout / "packages/http-client-python")
            lock = checkout / "packages/http-client-python/package-lock.json"
            lock.write_text('{"lockfileVersion":3,"packages":{"":{}}}')
        if list(map(str, command))[1:3] == ["run", "regenerate"]:
            if regeneration_failure:
                raise subprocess.CalledProcessError(7, command)
            generated = cwd / "tests/generated/azure/client"
            generated.mkdir(parents=True)
            (generated / "pyproject.toml").write_text("")

    def create_venv(path):
        python = path / ("Scripts/python.exe" if os.name == "nt" else "bin/python")
        python.parent.mkdir(parents=True)
        python.write_text("")

    monkeypatch.setattr(compat, "run", execute)
    monkeypatch.setattr(compat.sys, "version_info", (3, 12))
    monkeypatch.setattr(compat, "feed_environment", Mock(return_value={}))
    monkeypatch.setattr(
        compat.subprocess, "check_output", Mock(return_value=compat.TYPESPEC_REF)
    )
    monkeypatch.setattr(compat.shutil, "which", Mock(return_value="npm"))
    builder = Mock()
    builder.create.side_effect = create_venv
    monkeypatch.setattr(compat.venv, "EnvBuilder", Mock(return_value=builder))
    server = Mock()
    server.__enter__ = Mock(return_value=Mock())
    server.__exit__ = Mock(return_value=False)
    start = Mock(return_value=server)
    legacy = Mock()
    monkeypatch.setattr(compat, "mock_server", start)
    monkeypatch.setattr(compat, "run_legacy", legacy)
    if regeneration_failure:
        with pytest.raises(subprocess.CalledProcessError):
            compat.run_compatibility(ROOT, work)
        start.assert_not_called()
        legacy.assert_not_called()
    else:
        compat.run_compatibility(ROOT, work)
        assert (work / "stage/tsconfig.base.json").is_file()
        assert calls[-1][1:3] == ["-m", "tox"]
        assert calls[-1][-2:] == ["-e", "test-azure"]
        assert start.call_args.args[2]["GIT_DIR"] == str(work / "typespec/.git")
        legacy.assert_called_once()
        assert (
            json.loads((work / "results/upstream.json").read_text())["commit"]
            == compat.TYPESPEC_REF
        )


def test_legacy_retains_sync_async_and_arm_paths(monkeypatch, tmp_path):
    execute = Mock()
    monkeypatch.setattr(compat, "run", execute)
    compat.run_legacy(sys.executable, tmp_path, tmp_path, {})
    commands = [" ".join(map(str, call.args[0])) for call in execute.call_args_list]
    assert len(commands) == 4
    assert "coretestserver" in commands[0]
    assert "tests/test_rest_request_backcompat.py" in commands[1]
    assert "tests/test_rest_response_backcompat.py" in commands[1]
    assert "test_rest_response_backcompat_async.py" in commands[2]
    assert "tests/test_arm_polling.py" in commands[3]
    assert "test_async_arm_polling.py" in commands[3]
    assert all("-p core_compatibility" in command for command in commands[1:])


def test_pipeline_preserves_trigger_and_wires_runner():
    # PyYAML YAML 1.1 boolean keys are irrelevant to this pipeline (no `on` key).
    pipeline = yaml.safe_load((ROOT / "eng/pipelines/autorest_checks.yml").read_text())
    assert pipeline["trigger"] == "none"
    assert pipeline["pr"] == {
        "branches": {
            "include": ["main", "feature/*", "hotfix/*", "release/*", "restapi*"]
        },
        "paths": {"include": ["sdk/core/"]},
    }
    assert pipeline["variables"]["PythonVersion"] == "3.12"
    assert pipeline["variables"]["NodeVersion"] == "24.x"
    steps = pipeline["jobs"][0]["steps"]
    templates = [step["template"] for step in steps if "template" in step]
    assert (
        "/eng/common/pipelines/templates/steps/create-authenticated-npmrc.yml"
        in templates
    )
    assert "/eng/pipelines/templates/steps/auth-dev-feed.yml" in templates
    assert (
        sum("core_compatibility.py run" in step.get("script", "") for step in steps)
        == 1
    )
    assert steps[-2]["condition"] == "succeededOrFailed()"
    assert steps[-1]["condition"] == "failed()"


def test_real_tox_uv_isolation_reinstall_and_released_core_rejection(
    upstream, tmp_path
):
    """Offline smoke using only already-installed tooling, not the upstream suite."""
    pytest.importorskip("tox_uv")
    wheels = tmp_path / "wheels"
    wheels.mkdir()
    names = [
        "setuptools",
        "wheel",
        "requests",
        "typing-extensions",
        "pytest",
        "pytest-asyncio",
        "aiohttp",
    ]
    for name in names:
        for dependency in importlib.metadata.distribution(name).requires or []:
            requirement = Requirement(dependency)
            normalized = requirement.name.lower().replace("_", "-")
            if (
                requirement.marker is None or requirement.marker.evaluate({"extra": ""})
            ) and normalized not in names:
                names.append(normalized)
    specs = []
    for name in names:
        dist = importlib.metadata.distribution(name)
        wheel_metadata = dist.read_text("WHEEL")
        tag = next(
            line.removeprefix("Tag: ")
            for line in wheel_metadata.splitlines()
            if line.startswith("Tag: ") and not line.startswith("Tag: py2-")
        )
        normalized = name.replace("-", "_")
        with zipfile.ZipFile(
            wheels / f"{normalized}-{dist.version}-{tag}.whl", "w"
        ) as archive:
            records = []
            for file in dist.files:
                if (
                    ".." not in file.parts
                    and file.name != "RECORD"
                    and dist.locate_file(file).is_file()
                ):
                    data = dist.locate_file(file).read_bytes()
                    archive.writestr(file.as_posix(), data)
                    digest = (
                        base64.urlsafe_b64encode(hashlib.sha256(data).digest())
                        .rstrip(b"=")
                        .decode()
                    )
                    records.append(f"{file.as_posix()},sha256={digest},{len(data)}")
            record = next(
                file.rsplit("/", 1)[0] + "/RECORD"
                for file in archive.namelist()
                if file.endswith("/WHEEL")
            )
            records.append(f"{record},,")
            archive.writestr(record, "\n".join(records) + "\n")
        specs.append(f"{name}=={dist.version}")

    # Same version as the PR: a version-only check must NOT accept this wheel.
    version = compat.source_version(
        compat.core_sources(ROOT)["azure-core"], "azure.core"
    )
    released = wheels / f"azure_core-{version}-py3-none-any.whl"
    for candidate in (version, "9.9.9"):
        info = f"azure_core-{candidate}.dist-info"
        with zipfile.ZipFile(
            wheels / f"azure_core-{candidate}-py3-none-any.whl", "w"
        ) as archive:
            archive.writestr("azure/core/__init__.py", f'__version__ = "{candidate}"\n')
            archive.writestr(
                f"{info}/METADATA",
                f"Metadata-Version: 2.1\nName: azure-core\nVersion: {candidate}\n",
            )
            archive.writestr(
                f"{info}/WHEEL",
                "Wheel-Version: 1.0\nRoot-Is-Purelib: true\nTag: py3-none-any\n",
            )
            archive.writestr(f"{info}/RECORD", "")

    tox_path, constraints = compat.prepare_tox(upstream, ROOT, tmp_path)
    probe = upstream / "tests/mock_api/azure"
    probe.mkdir()
    (probe / "test_managed_server.py").write_text("def test_placeholder():\n    pass\n")
    (upstream / "tests/conftest.py").write_text(
        "import pytest\n"
        "import core_compatibility\n"
        "core_compatibility.server_ready = lambda url: False\n"
        '@pytest.fixture(scope="session", autouse=True)\n'
        "def testserver():\n"
        '    raise RuntimeError("unmanaged fallback started")\n'
    )
    config = configparser.ConfigParser(interpolation=None)
    config.read(tox_path)
    target = config["testenv:test-azure"]
    target["deps"] = "\n".join(specs)
    target["allowlist_externals"] = "uv"
    target["install_command"] = (
        f"uv pip install --no-index --offline --find-links {wheels.as_posix()} {{opts}} {{packages}}"
    )
    target["setenv"] = "{[testenv]setenv}\nUV_OFFLINE = true\nUV_NO_INDEX = true"
    sources = " ".join(
        f'-e "{source.as_posix()}"' for source in compat.core_sources(ROOT).values()
    )
    install = (
        f"uv pip install --python {{envpython}} --no-index --offline "
        f"--find-links {wheels.as_posix()} --no-build-isolation {sources}"
    )
    verify = config["testenv:test-azure"]["commands"].strip().splitlines()[0]
    negative = tmp_path / "check_override.py"
    negative.write_text(
        "import os, subprocess, sys\n"
        f"guard = [sys.executable, {str(ROOT / 'eng/scripts/core_compatibility.py')!r}, "
        f"'verify', '--sdk-root', {str(ROOT)!r}]\n"
        f"fixture = subprocess.run([sys.executable, '-m', 'pytest', '-p', 'core_compatibility', {str(probe)!r}], "
        "capture_output=True, text=True)\n"
        "assert fixture.returncode != 0 and 'SDK-managed Spector is not healthy' in fixture.stdout\n"
        "assert 'unmanaged fallback started' not in fixture.stdout\n"
        "command = ['uv', 'pip', 'install', '--python', sys.executable, '--no-index', '--offline', "
        f"'--find-links', {str(wheels)!r}, '--no-build-isolation', '--no-deps', '--force-reinstall']\n"
        "override = subprocess.run(command + ['azure-core==9.9.9'], capture_output=True, text=True)\n"
        "assert override.returncode != 0, 'The local-core constraint allowed a dependency override'\n"
        "env = dict(os.environ)\n"
        "env.pop('UV_CONSTRAINT')\n"
        "env.pop('PIP_CONSTRAINT')\n"
        "subprocess.run(command + ['azure-core==9.9.9'], env=env, check=True)\n"
        f"subprocess.run(command + [{str(released)!r}], env=env, check=True)\n"
        "mismatch = subprocess.run(guard, capture_output=True, text=True)\n"
        "assert mismatch.returncode != 0 and 'not the editable SDK PR source' in mismatch.stderr\n"
        "print('PASS: real tox-uv provenance, force reinstall, constraint override rejection, "
        "same-version wheel rejection, managed-server fallback prevention')\n"
    )
    target["commands"] = "\n".join(
        [
            install,
            verify,
            install + " --force-reinstall",
            verify,
            "python -m pytest -p core_compatibility "
            f"{(ROOT / 'sdk/core/azure-mgmt-core/tests/test_arm_polling.py').as_posix()} "
            f"{(ROOT / 'sdk/core/azure-mgmt-core/tests/asynctests/test_async_arm_polling.py').as_posix()} -q",
            f"python {negative.as_posix()}",
        ]
    )
    with tox_path.open("w") as stream:
        config.write(stream)
    env = dict(
        os.environ,
        UV_OFFLINE="true",
        UV_NO_INDEX="true",
        UV_NO_CONFIG="true",
        UV_PYTHON_DOWNLOADS="never",
        UV_CACHE_DIR=str(tmp_path / "uv-cache"),
    )
    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "tox",
            "run",
            "--no-provision",
            "-c",
            str(tox_path),
            "-e",
            "test-azure",
        ],
        env=env,
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, result.stdout + result.stderr
    assert "PASS: real tox-uv provenance" in result.stdout
