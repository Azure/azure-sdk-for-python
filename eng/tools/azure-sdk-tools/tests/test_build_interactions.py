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
@pytest.mark.parametrize("enable_wheel,enable_sdist", [(True, False), (True, True), (False, True)])
def test_create_package_build_routing(
    tmp_path, build_commands, scenario, cibuildwheel_config, compiled, enable_wheel, enable_sdist
):
    package = tmp_path / "package"
    shutil.copytree(os.path.join(integration_folder, "scenarios", scenario), package)
    if cibuildwheel_config:
        pyproject = package / "pyproject.toml"
        contents = pyproject.read_text() if pyproject.exists() else ""
        contents = contents.replace("setuptools.build_meta", "maturin")
        pyproject.write_text(contents + cibuildwheel_config)

    destination = tmp_path / "dist"
    create_package(str(package), str(destination), enable_wheel=enable_wheel, enable_sdist=enable_sdist)

    commands = [command for command, _ in build_commands]
    cibuildwheel_command = [sys.executable, "-m", "cibuildwheel", "--output-dir", str(destination)]
    assert (cibuildwheel_command in commands) is (compiled and enable_wheel)
    assert all(options["cwd"] == str(package) for _, options in build_commands)
    assert all(options["check"] for command, options in build_commands if "pip" not in command)
    if compiled and scenario.startswith("pyproject"):
        assert commands == ([cibuildwheel_command] if enable_wheel else []) + (
            [[sys.executable, "-m", "build", "-s", "-o", str(destination)]] if enable_sdist else []
        )
    elif not compiled and scenario.startswith("pyproject"):
        build_flags = "-nsw" if enable_wheel and enable_sdist else "-nw" if enable_wheel else "-ns"
        assert commands[-1] == [
            sys.executable,
            "-m",
            "build",
            build_flags,
            "-o",
            str(destination),
        ]
    else:
        expected_commands = []
        if enable_wheel:
            expected_commands.append(
                cibuildwheel_command
                if compiled
                else [sys.executable, "setup.py", "bdist_wheel", "-d", str(destination)]
            )
        if enable_sdist:
            expected_commands.append([sys.executable, "setup.py", "sdist", "-d", str(destination)])
        assert commands == expected_commands


def test_sdist_only_does_not_invoke_cibuildwheel(tmp_path, build_commands):
    package = tmp_path / "package"
    shutil.copytree(os.path.join(integration_folder, "scenarios", "pyproject_project_def"), package)
    pyproject = package / "pyproject.toml"
    contents = pyproject.read_text().replace("setuptools.build_meta", "maturin")
    contents = contents.replace('requires = ["setuptools>=61.0.0", "wheel"]', 'requires = ["maturin"]')
    pyproject.write_text(contents + '\n[tool.cibuildwheel]\nbuild = "cp310-*"\n')

    destination = tmp_path / "dist"
    create_package(str(package), str(destination), enable_wheel=False)

    assert [command for command, _ in build_commands] == [[sys.executable, "-m", "build", "-s", "-o", str(destination)]]
    assert build_commands[0][1]["check"] is True


def test_cibuildwheel_failure_propagates(tmp_path, monkeypatch):
    package = tmp_path / "package"
    shutil.copytree(os.path.join(integration_folder, "scenarios", "pyproject_project_def_with_extension"), package)

    def fail_build(command, **kwargs):
        raise subprocess.CalledProcessError(1, command)

    monkeypatch.setattr("ci_tools.build.run_logged", fail_build)
    with pytest.raises(subprocess.CalledProcessError):
        create_package(str(package), str(tmp_path / "dist"))
