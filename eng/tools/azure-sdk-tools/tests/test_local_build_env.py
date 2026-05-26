import os
import sys
import textwrap
import types
from unittest.mock import patch

from ci_tools.build import _local_build_env, build_whl_locally, create_package
from ci_tools.logging import run_logged


# ─────────────────────────────────────────────────────────────────────────────
# _local_build_env
# ─────────────────────────────────────────────────────────────────────────────


def _make_pkg(tmp_path, pyproject_body=None):
    """Create a minimal package directory with an optional pyproject.toml."""
    pkg = tmp_path / "pkg"
    pkg.mkdir()
    if pyproject_body is not None:
        (pkg / "pyproject.toml").write_text(pyproject_body, encoding="utf-8")
    return pkg


def test_local_build_env_missing_pyproject_returns_none(tmp_path):
    pkg = _make_pkg(tmp_path)  # no pyproject.toml
    assert _local_build_env(str(pkg)) is None


def test_local_build_env_pyproject_without_cibuildwheel_returns_none(tmp_path):
    pkg = _make_pkg(
        tmp_path,
        textwrap.dedent(
            """
            [build-system]
            requires = ["setuptools"]
            """
        ),
    )
    assert _local_build_env(str(pkg)) is None


def test_local_build_env_shell_style_environment(tmp_path):
    pkg = _make_pkg(
        tmp_path,
        textwrap.dedent(
            """
            [tool.cibuildwheel]
            environment = "CFLAGS='-Wno-implicit-function-declaration' FOO=bar"
            """
        ),
    )
    env = _local_build_env(str(pkg))
    assert env is not None
    # CFLAGS gets the value from the shlex-split, single-quotes stripped.
    assert env["CFLAGS"] == "-Wno-implicit-function-declaration"
    assert env["FOO"] == "bar"
    # Inherits the rest of os.environ.
    for key in os.environ:
        if key not in {"CFLAGS", "FOO"}:
            assert env.get(key) == os.environ[key]


def test_local_build_env_table_style_environment(tmp_path):
    pkg = _make_pkg(
        tmp_path,
        textwrap.dedent(
            """
            [tool.cibuildwheel.environment]
            CFLAGS = "-Wno-implicit-function-declaration"
            MY_FLAG = "value"
            """
        ),
    )
    env = _local_build_env(str(pkg))
    assert env is not None
    assert env["CFLAGS"] == "-Wno-implicit-function-declaration"
    assert env["MY_FLAG"] == "value"


def test_local_build_env_does_not_mutate_os_environ(tmp_path):
    pkg = _make_pkg(
        tmp_path,
        textwrap.dedent(
            """
            [tool.cibuildwheel]
            environment = "CFLAGS='-Wno-implicit-function-declaration'"
            """
        ),
    )
    sentinel = "__local_build_env_sentinel__"
    assert sentinel not in os.environ
    _local_build_env(str(pkg))
    assert sentinel not in os.environ
    # CFLAGS should not have been injected into the live env either.
    assert "CFLAGS" not in os.environ or os.environ.get("CFLAGS") != "-Wno-implicit-function-declaration"


# ─────────────────────────────────────────────────────────────────────────────
# build_whl_locally
# ─────────────────────────────────────────────────────────────────────────────


def _fake_parsed(folder, ext_modules=True, is_pyproject=False, requires=None):
    """Return a minimal object that quacks like ParsedSetup for create_package's needs."""
    return types.SimpleNamespace(
        folder=str(folder),
        is_pyproject=is_pyproject,
        ext_modules=ext_modules,
        requires=requires or [],
    )


def test_build_whl_locally_does_not_invoke_cibuildwheel(tmp_path):
    """build_whl_locally must never call cibuildwheel - it's the dev_req bypass."""
    pkg = _make_pkg(
        tmp_path,
        textwrap.dedent(
            """
            [tool.cibuildwheel]
            environment = "CFLAGS='-Wno-implicit-function-declaration'"
            """
        ),
    )
    parsed = _fake_parsed(pkg, ext_modules=True, requires=[])

    with patch("ci_tools.build.ParsedSetup") as mock_parse, patch("ci_tools.build.run_logged") as mock_run, patch(
        "ci_tools.build.get_pip_list_output", return_value={}
    ):
        mock_parse.from_path.return_value = parsed
        build_whl_locally(str(pkg), str(tmp_path / "dist"))

    cmds = [call.args[0] for call in mock_run.call_args_list]
    assert not any(
        "cibuildwheel" in part for cmd in cmds for part in cmd
    ), f"cibuildwheel must not run in build_whl_locally, got: {cmds}"


def test_build_whl_locally_ext_modules_applies_local_build_env(tmp_path):
    """ext_modules packages get [tool.cibuildwheel].environment applied to the `python -m build` subprocess."""
    pkg = _make_pkg(
        tmp_path,
        textwrap.dedent(
            """
            [tool.cibuildwheel]
            environment = "CFLAGS='-Wno-implicit-function-declaration'"
            """
        ),
    )
    parsed = _fake_parsed(pkg, ext_modules=True, requires=[])

    with patch("ci_tools.build.ParsedSetup") as mock_parse, patch("ci_tools.build.run_logged") as mock_run, patch(
        "ci_tools.build.get_pip_list_output", return_value={}
    ):
        mock_parse.from_path.return_value = parsed
        build_whl_locally(str(pkg), str(tmp_path / "dist"))

    build_calls = [call for call in mock_run.call_args_list if "build" in call.args[0] and "-m" in call.args[0]]
    assert build_calls, "Expected `python -m build` invocation"
    # cwd is a required positional kwarg of run_logged - guard against regressions.
    assert build_calls[0].kwargs.get("cwd") == str(pkg), f"Expected cwd={pkg}, got {build_calls[0].kwargs}"
    build_env = build_calls[0].kwargs.get("env")
    assert build_env is not None, "Expected env=<merged dict> on the `python -m build` call"
    assert build_env["CFLAGS"] == "-Wno-implicit-function-declaration"


def test_build_whl_locally_pure_python_keeps_default_env(tmp_path):
    """Pure-python dev_reqs must keep env=None so we don't perturb the subprocess env."""
    pkg = _make_pkg(tmp_path)
    parsed = _fake_parsed(pkg, ext_modules=False, requires=[])

    with patch("ci_tools.build.ParsedSetup") as mock_parse, patch("ci_tools.build.run_logged") as mock_run, patch(
        "ci_tools.build.get_pip_list_output", return_value={}
    ):
        mock_parse.from_path.return_value = parsed
        build_whl_locally(str(pkg), str(tmp_path / "dist"))

    build_calls = [call for call in mock_run.call_args_list if "build" in call.args[0] and "-m" in call.args[0]]
    assert build_calls, "Expected `python -m build` invocation"
    assert build_calls[0].kwargs.get("env") is None


# ─────────────────────────────────────────────────────────────────────────────
# create_package pyproject branch (publish path - for future ext_modules pyproject packages)
# ─────────────────────────────────────────────────────────────────────────────


def test_create_package_pyproject_ext_modules_applies_local_build_env(tmp_path):
    """Fully-pyproject packages with ext_modules must also get [tool.cibuildwheel].environment applied
    to the `python -m build` subprocess so macOS Apple Clang doesn't fail on implicit declarations."""
    pkg = _make_pkg(
        tmp_path,
        textwrap.dedent(
            """
            [tool.cibuildwheel]
            environment = "CFLAGS='-Wno-implicit-function-declaration'"
            """
        ),
    )
    parsed = _fake_parsed(pkg, ext_modules=True, is_pyproject=True, requires=[])

    with patch("ci_tools.build.ParsedSetup") as mock_parse, patch("ci_tools.build.run_logged") as mock_run, patch(
        "ci_tools.build.get_artifact_directory", side_effect=lambda x: str(x)
    ), patch("ci_tools.build.get_pip_list_output", return_value={}):
        mock_parse.from_path.return_value = parsed
        create_package(str(pkg), str(tmp_path / "dist"))

    build_calls = [call for call in mock_run.call_args_list if "build" in call.args[0] and "-m" in call.args[0]]
    assert build_calls, "Expected `python -m build` invocation"
    build_env = build_calls[0].kwargs.get("env")
    assert build_env is not None, "Expected env=<merged dict> on the `python -m build` call"
    assert build_env["CFLAGS"] == "-Wno-implicit-function-declaration"


def test_create_package_pyproject_pure_python_keeps_default_env(tmp_path):
    """Pure-python pyproject packages must keep env=None to not perturb existing behavior."""
    pkg = _make_pkg(tmp_path)
    parsed = _fake_parsed(pkg, ext_modules=False, is_pyproject=True, requires=[])

    with patch("ci_tools.build.ParsedSetup") as mock_parse, patch("ci_tools.build.run_logged") as mock_run, patch(
        "ci_tools.build.get_artifact_directory", side_effect=lambda x: str(x)
    ), patch("ci_tools.build.get_pip_list_output", return_value={}):
        mock_parse.from_path.return_value = parsed
        create_package(str(pkg), str(tmp_path / "dist"))

    build_calls = [call for call in mock_run.call_args_list if "build" in call.args[0] and "-m" in call.args[0]]
    assert build_calls, "Expected `python -m build` invocation"
    assert build_calls[0].kwargs.get("env") is None


# ─────────────────────────────────────────────────────────────────────────────
# run_logged(env=...) forwarding
# ─────────────────────────────────────────────────────────────────────────────


def test_run_logged_default_env_is_none():
    with patch("ci_tools.logging.subprocess.run") as mock_run:
        run_logged([sys.executable, "-c", "pass"], cwd=os.getcwd(), check=False, should_stream_to_console=False)
        assert mock_run.call_args.kwargs.get("env") is None


def test_run_logged_forwards_env():
    custom = {"CFLAGS": "-Wno-implicit-function-declaration", "PATH": os.environ.get("PATH", "")}
    with patch("ci_tools.logging.subprocess.run") as mock_run:
        run_logged(
            [sys.executable, "-c", "pass"],
            cwd=os.getcwd(),
            check=False,
            should_stream_to_console=True,
            env=custom,
        )
        assert mock_run.call_args.kwargs.get("env") is custom
