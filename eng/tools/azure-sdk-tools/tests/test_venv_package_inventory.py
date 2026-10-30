import json
import subprocess
import sys
from types import SimpleNamespace
from unittest.mock import Mock

import pytest

from ci_tools import venv
from ci_tools.scenario import generation


@pytest.fixture
def inventory_commands(monkeypatch):
    process = Mock(returncode=0)
    process.communicate.return_value = (
        b"azure-ai-agentserver-core @ file:///artifacts/core.whl\nazure-core==1.37.0\n",
        None,
    )
    monkeypatch.setattr(venv.subprocess, "Popen", Mock(return_value=process))
    command = Mock()
    monkeypatch.setattr(venv.subprocess, "check_output", command)
    return command


@pytest.mark.parametrize("backend", ["pip", "uv"])
@pytest.mark.parametrize("explicit_python", [False, True])
def test_inventory_includes_direct_and_editable_installs(
    monkeypatch, tmp_path, inventory_commands, backend, explicit_python
):
    monkeypatch.setenv("AZPYSDK_PIP_IMPL", backend)
    executable = str(tmp_path / "venv" / "python.exe") if explicit_python else None
    expected_executable = executable or sys.executable
    packages = [
        {"name": "azure-ai-agentserver-core", "version": "2.3.0b2"},
        {"name": "editable-package", "version": "1.0.0"},
        {"name": "azure-core", "version": "1.37.0"},
    ]
    inventory_commands.return_value = json.dumps(packages)

    assert venv.get_pip_list_output(executable) == {package["name"]: package["version"] for package in packages}
    expected = (
        ["uv", "pip", "list", "--format=json", "--disable-pip-version-check", "--python", expected_executable]
        if backend == "uv"
        else [expected_executable, "-m", "pip", "list", "--format=json", "--disable-pip-version-check"]
    )
    inventory_commands.assert_called_once_with(expected, text=True)


@pytest.mark.parametrize("backend", ["pip", "uv"])
def test_inventory_accepts_an_empty_environment(monkeypatch, inventory_commands, backend):
    monkeypatch.setenv("AZPYSDK_PIP_IMPL", backend)
    inventory_commands.return_value = "[]"
    assert venv.get_pip_list_output() == {}


@pytest.mark.parametrize("backend", ["pip", "uv"])
@pytest.mark.parametrize("failure", ["command", "json"])
def test_inventory_propagates_failures(monkeypatch, inventory_commands, backend, failure):
    monkeypatch.setenv("AZPYSDK_PIP_IMPL", backend)
    if failure == "command":
        inventory_commands.side_effect = subprocess.CalledProcessError(1, ["pip", "list"])
        expected = subprocess.CalledProcessError
    else:
        inventory_commands.return_value = "not json"
        expected = json.JSONDecodeError
    with pytest.raises(expected):
        venv.get_pip_list_output()


@pytest.mark.parametrize("backend", ["pip", "uv"])
def test_wheel_installer_keeps_matching_local_dependency(monkeypatch, tmp_path, inventory_commands, backend):
    monkeypatch.setenv("AZPYSDK_PIP_IMPL", backend)
    monkeypatch.delenv("PREBUILT_WHEEL_DIR", raising=False)
    monkeypatch.delenv("SETDEVVERSION", raising=False)
    inventory_commands.return_value = json.dumps([{"name": "azure-ai-agentserver-core", "version": "2.3.0b2"}])
    package = SimpleNamespace(folder=str(tmp_path), requires=["azure-ai-agentserver-core>=2.3.0b2,<3.0.0"])
    monkeypatch.setattr(generation.ParsedSetup, "from_path", lambda _: package)
    monkeypatch.setattr(generation, "discover_packages", lambda *args: ["responses.whl"])
    calls = []
    monkeypatch.setattr(generation.subprocess, "check_call", lambda command, **kwargs: calls.append(command))

    generation.create_package_and_install(
        distribution_directory=str(tmp_path / "dist"),
        target_setup=str(tmp_path),
        skip_install=False,
        cache_dir=None,
        work_dir=str(tmp_path),
        force_create=True,
        package_type="wheel",
        pre_download_disabled=False,
        python_executable=sys.executable,
    )

    assert len(calls) == 1
    assert "install" in calls[0]
    assert "download" not in calls[0]
    assert str(tmp_path / "dist" / "responses.whl") in calls[0]
