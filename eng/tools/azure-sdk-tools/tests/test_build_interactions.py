import os, tempfile, shutil
import sys

import pytest

from ci_tools.build import discover_targeted_packages, build_packages, build
from ci_tools.venv import get_venv_call, get_pip_command

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


@pytest.mark.parametrize("helper,command", [(get_venv_call, ["uv", "venv"]), (get_pip_command, ["uv", "pip"])])
@pytest.mark.parametrize("backend_variable", ["AZPYSDK_PIP_IMPL", "TOX_PIP_IMPL"])
@pytest.mark.parametrize("override", [None, "0", "1"])
def test_uv_system_certificates(helper, command, backend_variable, override, monkeypatch):
    for name in ("AZPYSDK_PIP_IMPL", "TOX_PIP_IMPL", "UV_SYSTEM_CERTS"):
        monkeypatch.delenv(name, raising=False)
    monkeypatch.setenv(backend_variable, "uv")
    monkeypatch.setenv("UV_DEFAULT_INDEX", "https://example.invalid/cfs")
    monkeypatch.setenv("PIP_INDEX_URL", "https://example.invalid/cfs")
    monkeypatch.setenv("NODE_EXTRA_CA_CERTS", "unused-node-ca.pem")
    if override is not None:
        monkeypatch.setenv("UV_SYSTEM_CERTS", override)
    before = os.environ.copy()

    assert helper() == command
    assert os.environ == {**before, "UV_SYSTEM_CERTS": override if override is not None else "1"}


@pytest.mark.parametrize("helper,module", [(get_venv_call, "venv"), (get_pip_command, "pip")])
@pytest.mark.parametrize("backend", [None, "pip"])
@pytest.mark.parametrize("override", [None, "0"])
def test_pip_backend_preserves_certificate_settings(helper, module, backend, override, monkeypatch):
    for name in ("AZPYSDK_PIP_IMPL", "TOX_PIP_IMPL", "UV_SYSTEM_CERTS"):
        monkeypatch.delenv(name, raising=False)
    if backend is not None:
        monkeypatch.setenv("AZPYSDK_PIP_IMPL", backend)
        monkeypatch.setenv("TOX_PIP_IMPL", "uv")
    if override is not None:
        monkeypatch.setenv("UV_SYSTEM_CERTS", override)
    before = os.environ.copy()

    assert helper() == [sys.executable, "-m", module]
    assert os.environ == before
