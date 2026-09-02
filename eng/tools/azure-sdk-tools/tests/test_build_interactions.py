import os, tempfile, shutil

from ci_tools.build import discover_targeted_packages, build_packages, build, create_package

repo_root = os.path.join(os.path.dirname(__file__), "..", "..", "..", "..")
integration_folder = os.path.join(os.path.dirname(__file__), "integration")
pyproject_folder = os.path.join(integration_folder, "scenarios", "pyproject_build_config")
pyproject_file = os.path.join(integration_folder, "scenarios", "pyproject_build_config", "pyproject.toml")
pyproject_project_def = os.path.join(integration_folder, "scenarios", "pyproject_project_def")


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


def _record_build_commands(monkeypatch):
    """Capture the commands build() would run instead of executing them."""
    calls = []

    def fake_run_logged(command, *args, **kwargs):
        calls.append(command)

        class _Result:
            returncode = 0

        return _Result()

    monkeypatch.setattr("ci_tools.build.run_logged", fake_run_logged)
    return calls


def _tool(calls):
    """Reduce recorded commands to the build tool each one invoked."""
    return [c[c.index("-m") + 1] for c in calls if "-m" in c and c.index("-m") + 1 < len(c)]


def test_pyproject_without_extension_uses_python_build(tmp_path, monkeypatch):
    pkg = tmp_path / "pure"
    shutil.copytree(pyproject_project_def, pkg)

    calls = _record_build_commands(monkeypatch)
    create_package(str(pkg), str(tmp_path / "dist"), enable_sdist=False)

    assert "cibuildwheel" not in _tool(calls)
    assert "build" in _tool(calls)


def test_pyproject_with_cibuildwheel_table_uses_cibuildwheel(tmp_path, monkeypatch):
    """
    A package that configures [tool.cibuildwheel] but declares no ext_modules (maturin/PyO3)
    must still be routed to cibuildwheel, otherwise `python -m build` produces a wheel tagged
    for whatever interpreter and toolchain the build agent happens to have.
    """
    pkg = tmp_path / "compiled"
    shutil.copytree(pyproject_project_def, pkg)
    with open(pkg / "pyproject.toml", "a") as f:
        f.write('\n[tool.cibuildwheel]\nbuild = "cp310-*"\n')

    calls = _record_build_commands(monkeypatch)
    create_package(str(pkg), str(tmp_path / "dist"), enable_sdist=False)

    assert "cibuildwheel" in _tool(calls)
