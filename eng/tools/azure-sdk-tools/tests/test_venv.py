import json
import subprocess
import sys
from types import SimpleNamespace

import pytest

from ci_tools import venv
from ci_tools.scenario import generation


@pytest.mark.parametrize("backend", ["pip", "uv"])
@pytest.mark.parametrize("explicit_python", [False, True])
@pytest.mark.parametrize(
    "packages",
    [
        [],
        [
            {"name": "azure-ai-agentserver-core", "version": "2.3.0b2"},
            {"name": "azure-core", "version": "1.37.0"},
            {"name": "azure-sdk-tools", "version": "0.0.0", "editable_project_location": "/repo/eng/tools"},
        ],
    ],
)
def test_get_pip_list_output_targets_environment_and_reads_installed_versions(
    monkeypatch, backend, explicit_python, packages
):
    monkeypatch.setenv("AZPYSDK_PIP_IMPL", backend)
    monkeypatch.setenv("VIRTUAL_ENV", "/unrelated/environment")
    executable = "/target/environment/python" if explicit_python else sys.executable
    expected = ["uv", "pip"] if backend == "uv" else [executable, "-m", "pip"]
    expected += ["list", "--format=json", "--disable-pip-version-check"]
    if backend == "uv":
        expected += ["--python", executable]

    def check_output(command, **kwargs):
        assert command == expected
        assert kwargs == {"text": True}
        return json.dumps(packages)

    monkeypatch.setattr(venv.subprocess, "check_output", check_output)
    assert venv.get_pip_list_output(executable if explicit_python else None) == {
        package["name"]: package["version"] for package in packages
    }


def test_get_pip_list_output_propagates_inventory_failure(monkeypatch):
    def check_output(command, **kwargs):
        raise subprocess.CalledProcessError(1, command)

    monkeypatch.setattr(venv.subprocess, "check_output", check_output)
    with pytest.raises(subprocess.CalledProcessError):
        venv.get_pip_list_output()


@pytest.mark.parametrize("backend", ["pip", "uv"])
def test_packaged_install_preserves_satisfied_core_artifact(monkeypatch, tmp_path, backend):
    monkeypatch.setenv("AZPYSDK_PIP_IMPL", backend)
    monkeypatch.delenv("SETDEVVERSION", raising=False)
    artifact = tmp_path / "consumer.whl"
    artifact.touch()
    monkeypatch.setenv("PREBUILT_WHEEL_DIR", str(tmp_path))
    stage = tmp_path / "stage"
    package = SimpleNamespace(folder=str(tmp_path), requires=["azure-ai-agentserver-core>=2.3.0b2,<3.0.0"])
    monkeypatch.setattr(generation.ParsedSetup, "from_path", lambda _: package)
    monkeypatch.setattr(generation, "discover_packages", lambda *args: [artifact.name])
    monkeypatch.setattr(
        venv.subprocess,
        "check_output",
        lambda *args, **kwargs: json.dumps([{"name": "azure-ai-agentserver-core", "version": "2.3.0b2"}]),
    )
    commands = []
    monkeypatch.setattr(generation.subprocess, "check_call", lambda command, **kwargs: commands.append(command))

    generation.create_package_and_install(
        distribution_directory=str(stage),
        target_setup=str(tmp_path),
        skip_install=False,
        cache_dir=None,
        work_dir=str(stage),
        force_create=False,
        package_type="wheel",
        pre_download_disabled=False,
        python_executable=sys.executable,
    )

    expected = ["uv", "pip"] if backend == "uv" else [sys.executable, "-m", "pip"]
    expected += ["install", str(artifact)]
    if backend == "uv":
        expected += ["--python", sys.executable]
    assert commands == [expected]
    assert not list((stage / "dl").iterdir())
