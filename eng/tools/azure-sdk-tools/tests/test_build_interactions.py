import os, tempfile, shutil
import subprocess
import sys

import pytest

from ci_tools.build import discover_targeted_packages, build_packages, build, create_package

repo_root = os.path.join(os.path.dirname(__file__), "..", "..", "..", "..")
integration_folder = os.path.join(os.path.dirname(__file__), "integration")
pyproject_folder = os.path.join(integration_folder, "scenarios", "pyproject_build_config")
pyproject_file = os.path.join(integration_folder, "scenarios", "pyproject_build_config", "pyproject.toml")


def test_build_core():
    pass


def test_discover_targeted_packages():
    pass


def test_build_packages():
    pass


def test_venv_helpers_importable():
    from ci_tools.venv import (
        get_venv_call,
        get_pip_command,
        get_venv_python,
        install_into_venv,
        uninstall_from_venv,
        pip_install,
        pip_uninstall,
        pip_install_requirements_file,
        run_pip_freeze,
        get_pip_list_output,
    )

    # Verify re-exports from ci_tools.functions still work
    from ci_tools.functions import get_venv_call as f_get_venv_call

    assert f_get_venv_call is get_venv_call


@pytest.fixture
def build_commands(monkeypatch):
    calls = []
    monkeypatch.setattr("ci_tools.build.run_logged", lambda command, **kwargs: calls.append((command, kwargs)))
    monkeypatch.setattr("ci_tools.build.get_pip_list_output", lambda executable: {})
    return calls


@pytest.mark.parametrize(
    "scenario,cibuildwheel_config,compiled",
    [
        ("pyproject_project_def", "", False),
        ("pyproject_project_def_with_extension", "", True),
        ("setup_py_project_def", "", False),
        ("pyproject_project_def", '\n[tool.cibuildwheel]\nbuild = "cp310-*"\n', True),
        ("setup_py_project_def", '\n[tool.cibuildwheel]\nbuild = "cp310-*"\n', True),
    ],
)
@pytest.mark.parametrize("enable_sdist", [False, True])
def test_create_package_build_routing(tmp_path, build_commands, scenario, cibuildwheel_config, compiled, enable_sdist):
    package = tmp_path / "package"
    shutil.copytree(os.path.join(integration_folder, "scenarios", scenario), package)
    if cibuildwheel_config:
        pyproject = package / "pyproject.toml"
        contents = pyproject.read_text() if pyproject.exists() else ""
        contents = contents.replace("setuptools.build_meta", "maturin")
        pyproject.write_text(contents + cibuildwheel_config)

    destination = tmp_path / "dist"
    create_package(str(package), str(destination), enable_sdist=enable_sdist)

    commands = [command for command, _ in build_commands]
    cibuildwheel_command = [sys.executable, "-m", "cibuildwheel", "--output-dir", str(destination)]
    assert (cibuildwheel_command in commands) is compiled
    assert all(options["cwd"] == str(package) for _, options in build_commands)
    assert all(options["check"] for command, options in build_commands if "pip" not in command)
    if compiled and scenario.startswith("pyproject"):
        assert commands == [cibuildwheel_command] + (
            [[sys.executable, "-m", "build", "-s", "-o", str(destination)]] if enable_sdist else []
        )
    elif not compiled and scenario.startswith("pyproject"):
        assert commands[-1] == [
            sys.executable,
            "-m",
            "build",
            "-nsw" if enable_sdist else "-nw",
            "-o",
            str(destination),
        ]
    elif not compiled:
        assert commands[0] == [sys.executable, "setup.py", "bdist_wheel", "-d", str(destination)]


def test_sdist_only_does_not_invoke_cibuildwheel(tmp_path, build_commands):
    package = tmp_path / "package"
    shutil.copytree(os.path.join(integration_folder, "scenarios", "pyproject_project_def"), package)
    with (package / "pyproject.toml").open("a") as stream:
        stream.write('\n[tool.cibuildwheel]\nbuild = "cp310-*"\n')

    create_package(str(package), str(tmp_path / "dist"), enable_wheel=False)

    assert all("cibuildwheel" not in command for command, _ in build_commands)
    assert "-ns" in build_commands[-1][0]


def test_cibuildwheel_failure_propagates(tmp_path, monkeypatch):
    package = tmp_path / "package"
    shutil.copytree(os.path.join(integration_folder, "scenarios", "pyproject_project_def_with_extension"), package)

    def fail_build(command, **kwargs):
        raise subprocess.CalledProcessError(1, command)

    monkeypatch.setattr("ci_tools.build.run_logged", fail_build)
    with pytest.raises(subprocess.CalledProcessError):
        create_package(str(package), str(tmp_path / "dist"))
