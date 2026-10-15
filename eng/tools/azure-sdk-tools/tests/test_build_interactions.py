import os, tempfile, shutil
import sys
from subprocess import CalledProcessError
from types import SimpleNamespace

import pytest

import ci_tools.build as build_module
from ci_tools.build import discover_targeted_packages, build_packages, build

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
def inherited_trust(tmp_path, monkeypatch):
    monkeypatch.setenv("SSL_CERT_FILE", str(tmp_path / "pipeline-ca-bundle.pem"))
    monkeypatch.setenv("NODE_EXTRA_CA_CERTS", str(tmp_path / "unused-node-ca.pem"))


@pytest.mark.parametrize("is_pyproject", [False, True])
@pytest.mark.parametrize("fail", [False, True])
@pytest.mark.parametrize("enable_sdist", [False, True])
def test_create_compiled_package_inherits_environment(
    inherited_trust, is_pyproject, fail, enable_sdist, tmp_path, monkeypatch
):
    package = SimpleNamespace(is_pyproject=is_pyproject, ext_modules=True, folder=str(tmp_path))
    monkeypatch.setattr(build_module.ParsedSetup, "from_path", lambda _: package)
    dist = str(tmp_path / "dist")
    monkeypatch.setattr(build_module, "get_artifact_directory", lambda _: dist)
    before = os.environ.copy()
    calls = []

    def run_build(command, **kwargs):
        calls.append(command)
        assert kwargs["cwd"] == package.folder
        assert kwargs["check"] is True
        assert "env" not in kwargs
        assert os.environ == before
        if command[2] == "cibuildwheel" and fail:
            raise CalledProcessError(1, command)

    monkeypatch.setattr(build_module, "run_logged", run_build)
    if fail:
        with pytest.raises(CalledProcessError):
            build_module.create_package(package.folder, dist, enable_sdist=enable_sdist)
    else:
        build_module.create_package(package.folder, dist, enable_sdist=enable_sdist)

    assert calls[0] == [sys.executable, "-m", "cibuildwheel", "--output-dir", dist]
    assert len(calls) == (1 if fail or not enable_sdist else 2)
    if not fail and enable_sdist:
        assert calls[1] == (
            [sys.executable, "-m", "build", "-s", "-o", dist]
            if is_pyproject
            else [sys.executable, "setup.py", "sdist", "-d", dist]
        )
    assert os.environ == before


@pytest.mark.parametrize("is_pyproject", [False, True])
@pytest.mark.parametrize("ext_modules,enable_wheel", [(False, True), (True, False)])
def test_non_cibuildwheel_builds_inherit_environment(
    inherited_trust, is_pyproject, ext_modules, enable_wheel, tmp_path, monkeypatch
):
    package = SimpleNamespace(is_pyproject=is_pyproject, ext_modules=ext_modules, folder=str(tmp_path), requires=[])
    monkeypatch.setattr(build_module.ParsedSetup, "from_path", lambda _: package)
    monkeypatch.setattr(build_module, "get_artifact_directory", lambda _: str(tmp_path / "dist"))
    monkeypatch.setattr(build_module, "get_pip_list_output", lambda _: {})
    before = os.environ.copy()
    calls = []

    def run_build(command, **kwargs):
        calls.append(command)
        assert "cibuildwheel" not in command
        assert "env" not in kwargs
        assert os.environ == before

    monkeypatch.setattr(build_module, "run_logged", run_build)
    build_module.create_package(package.folder, str(tmp_path / "dist"), enable_wheel=enable_wheel)
    assert len(calls) == (2 if is_pyproject or enable_wheel else 1)
    assert os.environ == before
