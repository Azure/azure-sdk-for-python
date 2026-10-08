import os, tempfile, shutil
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

import certifi
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


@pytest.mark.parametrize("is_pyproject", [True, False])
def test_compiled_wheel_uses_proxy_environment(tmp_path, monkeypatch, is_pyproject):
    monkeypatch.setenv("NODE_EXTRA_CA_CERTS", certifi.where())
    for name in ("SSL_CERT_FILE", "REQUESTS_CA_BUNDLE", "CURL_CA_BUNDLE", "PIP_CERT"):
        monkeypatch.delenv(name, raising=False)
    monkeypatch.setattr("ci_tools.certificates.sys.platform", "win32")
    package = SimpleNamespace(is_pyproject=is_pyproject, ext_modules=True, folder=str(tmp_path))
    before = os.environ.copy()
    bundle_paths = []

    def check_build_environment(cmd, **kwargs):
        if cmd[2] == "cibuildwheel":
            env = kwargs["env"]
            bundle = Path(env["SSL_CERT_FILE"])
            assert bundle.is_file()
            assert env["REQUESTS_CA_BUNDLE"] == str(bundle)
            assert env["NODE_EXTRA_CA_CERTS"] == certifi.where()
            assert kwargs["cwd"] == package.folder
            bundle_paths.append(bundle)
        else:
            assert "env" not in kwargs
        assert os.environ == before

    with patch("ci_tools.build.ParsedSetup.from_path", return_value=package), patch(
        "ci_tools.build.run_logged", side_effect=check_build_environment
    ) as run:
        create_package(str(tmp_path), str(tmp_path / "dist"))

    assert run.call_count == 2
    assert len(bundle_paths) == 1
    assert not bundle_paths[0].exists()
    assert os.environ == before


@pytest.mark.parametrize("is_pyproject,enable_wheel", [(True, True), (False, True), (True, False), (False, False)])
def test_non_compiled_build_does_not_configure_proxy(tmp_path, is_pyproject, enable_wheel):
    package = SimpleNamespace(
        is_pyproject=is_pyproject, ext_modules=not enable_wheel, folder=str(tmp_path), requires=[]
    )
    with patch("ci_tools.build.ParsedSetup.from_path", return_value=package), patch(
        "ci_tools.build.get_pip_list_output", return_value={}
    ), patch("ci_tools.build.run_logged") as run, patch("ci_tools.build.cibuildwheel_environment") as environment:
        create_package(str(tmp_path), str(tmp_path / "dist"), enable_wheel=enable_wheel)

    environment.assert_not_called()
    assert all("env" not in call.kwargs for call in run.call_args_list)
