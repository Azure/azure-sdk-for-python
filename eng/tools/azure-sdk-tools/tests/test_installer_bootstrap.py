import importlib
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
from types import SimpleNamespace
from unittest.mock import Mock

import pytest
from packaging.requirements import Requirement
import yaml

from ci_tools import bootstrap
from ci_tools.scenario import managed_virtual_env
from packaging_tools import venvtools


REPO_ROOT = Path(__file__).resolve().parents[4]


@pytest.mark.parametrize(
    "requirements",
    [
        "eng/ci_tools.txt",
        "eng/apiview_reqs.txt",
        "eng/regression_tools.txt",
        "eng/regression_test_tools.txt",
        "common/smoketest/requirements_async.txt",
    ],
)
def test_ci_pip_requirements_preserve_newer_versions(requirements):
    lines = (REPO_ROOT / requirements).read_text().splitlines()
    pip = Requirement(next(line for line in lines if line.startswith("pip")))
    assert str(pip.specifier) == f">={bootstrap.PIP_VERSION}"
    assert "26.2.1" not in pip.specifier
    assert bootstrap.PIP_VERSION in pip.specifier
    assert "27.0" in pip.specifier


def test_smoke_pipeline_bootstraps_pip_before_reporting_version():
    path = REPO_ROOT / "eng" / "pipelines" / "templates" / "steps" / "smoke-test-steps.yml"
    template = yaml.safe_load(path.read_text())
    step = next(step for step in template["steps"] if step.get("displayName") == "Bootstrap pip and show version")
    script = step["pwsh"]
    assert "$ErrorActionPreference = 'Stop'" in script
    assert "$PSNativeCommandUseErrorActionPreference = $true" in script
    assert script.index("ci_tools/bootstrap.py") < script.index("pip --version")


@pytest.mark.parametrize(
    "workflow,job",
    [
        ("azure-sdk-tools.yml", "build-and-test"),
        ("azure-sdk-tools.yml", "static-analysis"),
        ("azure-sdk-tools.yml", "verify-azpysdk-checks"),
        ("dependency-checker.yml", "check-dependencies"),
        ("wheel-signing.yml", "test"),
    ],
)
def test_github_workflows_bootstrap_before_dependency_installs(workflow, job):
    path = REPO_ROOT / ".github" / "workflows" / workflow
    steps = yaml.safe_load(path.read_text())["jobs"][job]["steps"]
    bootstrap_step = next(index for index, step in enumerate(steps) if "ci_tools/bootstrap.py" in step.get("run", ""))
    feed_steps = [
        index for index, step in enumerate(steps) if step.get("uses") == "./.github/actions/configure-package-indexes"
    ]
    assert all(index < bootstrap_step for index in feed_steps)
    commands = "\n".join(step.get("run", "") for step in steps)
    assert commands.index("ci_tools/bootstrap.py") < commands.index("pip install")


def test_dependency_checker_installs_dependencies_once_without_changing_indexes():
    path = REPO_ROOT / ".github" / "workflows" / "dependency-checker.yml"
    steps = yaml.safe_load(path.read_text())["jobs"]["check-dependencies"]["steps"]
    commands = "\n".join(step.get("run", "") for step in steps)
    assert commands.count("pip install packaging==25.0 requests==2.32.4") == 1
    assert not any(step.get("uses") == "./.github/actions/configure-package-indexes" for step in steps)


def _pipeline_nodes(node):
    if isinstance(node, dict):
        yield node
        for value in node.values():
            yield from _pipeline_nodes(value)
    elif isinstance(node, list):
        for value in node:
            yield from _pipeline_nodes(value)


@pytest.mark.parametrize(
    "template",
    [
        "stages/release-artifact.yml",
        "stages/archetype-python-release.yml",
        "stages/archetype-sdk-tool-python.yml",
        "steps/install-rex-validation-tool.yml",
    ],
)
def test_release_dependency_installs_bootstrap_pip_first(template):
    path = REPO_ROOT / "eng" / "pipelines" / "templates" / template
    configuration = yaml.safe_load(path.read_text())
    installs = 0
    for node in _pipeline_nodes(configuration):
        if not isinstance(node.get("steps"), list):
            continue
        secured = False
        for step in _pipeline_nodes(node["steps"]):
            if step.get("task") == "UsePythonVersion@0":
                secured = False
            for shell in ("script", "pwsh"):
                script = step.get(shell, "")
                if not isinstance(script, str):
                    continue
                bootstraps = any(
                    line.strip().startswith("python ") and "bootstrap.py" in line for line in script.splitlines()
                )
                if bootstraps:
                    secured = True
                    if shell == "pwsh":
                        assert "$ErrorActionPreference = 'Stop'" in script
                        assert "$PSNativeCommandUseErrorActionPreference = $true" in script
                    elif "python -m pip install" in script:
                        assert script.index("set -e") < script.index("bootstrap.py")
                if "python -m pip install" in script:
                    installs += 1
                    assert secured
                    if bootstraps:
                        assert script.index("bootstrap.py") < script.index("python -m pip install")
    assert installs


def test_release_tag_job_secures_pip_before_versioning_templates():
    path = REPO_ROOT / "eng" / "pipelines" / "templates" / "stages" / "release-artifact.yml"
    configuration = yaml.safe_load(path.read_text())
    steps = next(node["steps"] for node in _pipeline_nodes(configuration) if node.get("job") == "TagRepository")
    bootstrap_step = next(index for index, step in enumerate(steps) if step.get("displayName") == "Bootstrap pip")
    version_step = next(
        index
        for index, step in enumerate(steps)
        if step.get("template") == "/eng/common/pipelines/templates/steps/set-test-pipeline-version.yml"
    )
    assert bootstrap_step < version_step


@pytest.mark.parametrize(
    "producer,step_name,destination,consumer,install,bootstrap_command",
    [
        (
            "steps/build-package-artifacts.yml",
            "Assemble Static Files for Release Stage",
            "$(Build.ArtifactStagingDirectory)/release_artifact/bootstrap.py",
            "stages/release-artifact.yml",
            "python -m pip install -r $(Pipeline.Workspace)/release_artifact/release_requirements.txt",
            'python "$(Pipeline.Workspace)/release_artifact/bootstrap.py"',
        ),
        (
            "stages/archetype-sdk-tool-python.yml",
            "Stage installer bootstrap",
            "$(Build.ArtifactStagingDirectory)/bootstrap.py",
            "stages/archetype-sdk-tool-python.yml",
            "python -m pip install twine",
            'python "$(Pipeline.Workspace)/${{ parameters.ArtifactName }}/bootstrap.py"',
        ),
    ],
)
def test_checkout_free_publish_uses_staged_bootstrap(
    producer, step_name, destination, consumer, install, bootstrap_command
):
    templates = REPO_ROOT / "eng" / "pipelines" / "templates"
    configuration = yaml.safe_load((templates / producer).read_text())
    stage = next(node for node in _pipeline_nodes(configuration) if node.get("displayName") == step_name)
    assert '"$(Build.SourcesDirectory)/eng/tools/azure-sdk-tools/ci_tools/bootstrap.py"' in stage["pwsh"]
    assert f'-Destination "{destination}"' in stage["pwsh"]
    configuration = yaml.safe_load((templates / consumer).read_text())
    publish = next(node["script"] for node in _pipeline_nodes(configuration) if install in node.get("script", ""))
    assert publish.index(bootstrap_command) < publish.index(install)


def test_release_bootstrap_is_staged_before_source_cleanup():
    path = REPO_ROOT / "eng" / "pipelines" / "templates" / "steps" / "build-package-artifacts.yml"
    steps = yaml.safe_load(path.read_text())["steps"]
    assemble = next(
        index
        for index, step in enumerate(steps)
        if isinstance(step, dict) and step.get("displayName") == "Assemble Static Files for Release Stage"
    )
    cleanup = next(
        index
        for index, step in enumerate(steps)
        if isinstance(step, dict) and step.get("displayName") == "Clean up repo"
    )
    assert assemble < cleanup


@pytest.mark.parametrize(
    "installed,expected",
    [
        (None, False),
        ("24.0", False),
        ("26.2.1", False),
        ("26.2.2rc1", False),
        ("26.2.2.dev1", False),
        ("26.2.2", True),
        ("26.3", True),
        ("27.0", True),
    ],
)
def test_pip_version_floor(installed, expected):
    assert bootstrap._at_least(installed, bootstrap.PIP_VERSION) is expected


def test_inspection_uses_target_interpreter(monkeypatch):
    query = Mock(return_value=json.dumps({"python": [3, 11], "version": "26.2.2"}))
    monkeypatch.setattr(bootstrap.subprocess, "check_output", query)
    assert bootstrap._inspect("target-python", "pip")["version"] == "26.2.2"
    assert query.call_args.args[0] == ["target-python", "-c", bootstrap._INSPECT, "pip"]


@pytest.mark.parametrize("version", ["26.2.2", "27.0"])
@pytest.mark.parametrize("python_version", [[3, 10], [3, 11]])
def test_current_pip_does_not_install(version, python_version, monkeypatch):
    monkeypatch.setattr(bootstrap, "_inspect", Mock(return_value={"python": python_version, "version": version}))
    install = Mock()
    monkeypatch.setattr(bootstrap.subprocess, "check_call", install)
    bootstrap.ensure_pip("target-python")
    install.assert_not_called()


@pytest.mark.parametrize("version", [None, "24.0", "26.2.2rc1"])
def test_pip_bootstrap_requires_verified_wheel(version, monkeypatch):
    monkeypatch.setattr(
        bootstrap,
        "_inspect",
        Mock(
            side_effect=[
                {"python": [3, 11], "version": version},
                {"python": [3, 11], "version": bootstrap.PIP_VERSION},
            ]
        ),
    )
    calls = []
    requirement_paths = []

    def install(command):
        calls.append(command)
        if "-r" in command:
            requirement_path = Path(command[-1])
            requirement_paths.append(requirement_path)
            assert requirement_path.read_text().strip() == (
                f"pip=={bootstrap.PIP_VERSION} --hash=sha256:{bootstrap.PIP_WHEEL_SHA256}"
            )
            assert "--require-hashes" in command
            assert "--only-binary=:all:" in command
            assert "--no-deps" in command
            assert "--index-url" not in command
            assert command[:3] == ["target-python", "-m", "pip"]

    monkeypatch.setattr(bootstrap.subprocess, "check_call", install)
    bootstrap.ensure_pip("target-python")
    assert len(calls) == (2 if version is None else 1)
    if version is None:
        assert calls[0] == ["target-python", "-m", "ensurepip", "--upgrade"]
    assert all(not path.exists() for path in requirement_paths)


def test_unsupported_python_fails_before_install(monkeypatch):
    monkeypatch.setattr(bootstrap, "_inspect", Mock(return_value={"python": [3, 9], "version": "24.0"}))
    install = Mock()
    monkeypatch.setattr(bootstrap.subprocess, "check_call", install)
    with pytest.raises(RuntimeError, match="requires Python 3.10"):
        bootstrap.ensure_pip("old-python")
    install.assert_not_called()


def test_failed_pip_upgrade_stops_setup(monkeypatch):
    monkeypatch.setattr(bootstrap, "_inspect", Mock(return_value={"python": [3, 11], "version": "24.0"}))
    monkeypatch.setattr(bootstrap.subprocess, "check_call", Mock(side_effect=subprocess.CalledProcessError(1, "pip")))
    with pytest.raises(subprocess.CalledProcessError):
        bootstrap.ensure_pip("target-python")


def test_pip_upgrade_verifies_result(monkeypatch):
    monkeypatch.setattr(bootstrap, "_inspect", Mock(return_value={"python": [3, 11], "version": "24.0"}))
    monkeypatch.setattr(bootstrap.subprocess, "check_call", Mock())
    with pytest.raises(RuntimeError, match="Expected pip >="):
        bootstrap.ensure_pip("target-python")


@pytest.mark.parametrize("version", [None, "0.13.1", "0.13.4", "0.13.5"])
def test_uv_bootstrap_secures_pip_first(version, monkeypatch):
    calls = []
    monkeypatch.setattr(bootstrap, "ensure_pip", lambda python: calls.append(["bootstrap-pip", python]))
    monkeypatch.setattr(
        bootstrap,
        "_inspect",
        Mock(
            side_effect=[
                {"version": version},
                {"version": bootstrap.UV_VERSION},
            ]
        ),
    )
    monkeypatch.setattr(bootstrap.subprocess, "check_call", lambda command: calls.append(command))
    bootstrap.ensure_uv("target-python")
    assert calls[0] == ["bootstrap-pip", "target-python"]
    if version in (None, "0.13.1"):
        assert calls[1] == ["target-python", "-m", "pip", "install", "--upgrade", f"uv=={bootstrap.UV_VERSION}"]
    else:
        assert len(calls) == 2
    assert calls[-1] == ["target-python", "-m", "uv", "--version"]


def test_uv_upgrade_verifies_result(monkeypatch):
    monkeypatch.setattr(bootstrap, "ensure_pip", Mock())
    monkeypatch.setattr(bootstrap, "_inspect", Mock(return_value={"version": "0.13.1"}))
    monkeypatch.setattr(bootstrap.subprocess, "check_call", Mock())
    with pytest.raises(RuntimeError, match="Expected uv >="):
        bootstrap.ensure_uv("target-python")


@pytest.mark.parametrize("uv", [False, True])
def test_bootstrap_cli_targets_requested_python(uv, monkeypatch):
    pip = Mock()
    uv_install = Mock()
    monkeypatch.setattr(bootstrap, "ensure_pip", pip)
    monkeypatch.setattr(bootstrap, "ensure_uv", uv_install)
    monkeypatch.setattr(sys, "argv", ["bootstrap", "--python", "target-python"] + (["--uv"] if uv else []))
    bootstrap.main()
    (uv_install if uv else pip).assert_called_once_with("target-python")
    (pip if uv else uv_install).assert_not_called()


@pytest.mark.parametrize("reused", [False, True])
def test_isolated_check_bootstraps_before_dependencies(reused, tmp_path, monkeypatch):
    module = importlib.import_module("azpysdk.Check")

    class ConcreteCheck(module.Check):
        def register(self, *args, **kwargs):
            pass

    calls = []
    location = str(tmp_path / "check-env")
    python = module.get_venv_python(location)
    if reused:
        Path(python).parent.mkdir(parents=True)
        Path(python).touch()
    monkeypatch.setattr(module, "get_venv_call", lambda *args, **kwargs: ["python", "-m", "venv"])
    monkeypatch.setattr(module.subprocess, "check_call", lambda command: calls.append("create"))
    monkeypatch.setattr(module, "ensure_pip", lambda executable: calls.append(("pip", executable)))
    monkeypatch.setattr(module, "in_ci", lambda: True)
    monkeypatch.setattr(module, "find_whl", lambda *args: "tools.whl")
    monkeypatch.setattr(module, "install_into_venv", lambda *args: calls.append("dependencies"))
    assert ConcreteCheck().create_venv(True, location) == python
    assert calls == ([("pip", python)] if reused else ["create", ("pip", python), "dependencies"])


def test_managed_environment_bootstraps_after_creation_and_clear(tmp_path, monkeypatch):
    calls = []
    environment = managed_virtual_env.ManagedVirtualEnv(str(tmp_path), "scenario")
    monkeypatch.setattr(environment, "_find_python_executable", lambda: "target-python")
    monkeypatch.setattr(managed_virtual_env.subprocess, "check_call", lambda command: calls.append(command))
    monkeypatch.setattr(managed_virtual_env, "ensure_pip", lambda python: calls.append(["bootstrap", python]))
    environment.create()
    environment.clear_venv()
    assert calls == [
        [sys.executable, "-m", "venv", environment.path],
        ["bootstrap", "target-python"],
        [sys.executable, "-m", "venv", "--clear", environment.path],
        ["bootstrap", "target-python"],
    ]


def test_api_report_environment_bootstraps_before_packages(monkeypatch):
    calls = []
    monkeypatch.setattr(venvtools, "create", lambda *args, **kwargs: SimpleNamespace(env_exe="target-python"))
    monkeypatch.setattr(venvtools, "ensure_pip", lambda python: calls.append(["bootstrap", python]))
    monkeypatch.setattr(venvtools.subprocess, "check_call", lambda command: calls.append(command))
    with venvtools.create_venv_with_package(["example==1.0"]) as environment:
        assert environment.env_exe == "target-python"
    assert calls == [
        ["bootstrap", "target-python"],
        ["target-python", "-m", "pip", "install", "example==1.0"],
    ]


def test_regression_environment_bootstraps_after_creation_and_clear(tmp_path, monkeypatch):
    monkeypatch.syspath_prepend(str(REPO_ROOT / "scripts" / "devops_tasks"))
    spec = importlib.util.spec_from_file_location(
        "bootstrap_regression", REPO_ROOT / "scripts" / "devops_tasks" / "test_regression.py"
    )
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    calls = []
    environment = module.CustomVirtualEnv(str(tmp_path))
    monkeypatch.setattr(environment, "_find_python_executable", lambda: "target-python")
    monkeypatch.setattr(environment, "_find_lib_paths", lambda: [])
    monkeypatch.setattr(module, "run_check_call", lambda command, cwd: calls.append(command))
    monkeypatch.setattr(module, "ensure_pip", lambda python: calls.append(["bootstrap", python]))
    environment.create()
    environment.clear_venv()
    assert calls == [
        [sys.executable, "-m", "venv", environment.path],
        ["bootstrap", "target-python"],
        [sys.executable, "-m", "venv", "--clear", environment.path],
        ["bootstrap", "target-python"],
    ]
