"""Virtualenv and pip helpers for Azure SDK tooling.

This module centralizes all venv creation, pip install/uninstall, and
related utilities.  The backend (``uv`` vs stdlib ``pip``) is chosen
via the ``TOX_PIP_IMPL`` environment variable:

* ``"uv"``  → uses ``uv venv`` / ``uv pip``
* anything else (default ``"pip"``) → uses ``python -m venv`` / ``python -m pip``
"""

import os
import re
import subprocess
import sys
from typing import List, Optional


def get_venv_call(python_exe: Optional[str] = None, python_version: Optional[str] = None) -> List[str]:
    """Determine whether to use 'uv venv' or regular 'python -m venv' based on environment.

    :param str python_exe: The Python executable to use (if not using the default).
    :param str python_version: Optional Python version string to pass through to ``uv venv --python``.
        Only valid when the backend is ``uv``; raises if used with the ``pip`` backend.
    :return: List of command arguments for venv.
    :rtype: List[str]
    """
    pip_impl = os.environ.get("TOX_PIP_IMPL", "pip").lower()

    if python_version and pip_impl != "uv":
        raise ValueError("--python requires uv as the backend. Install uv or set TOX_PIP_IMPL=uv.")

    # soon we will change this to default to uv
    if pip_impl == "uv":
        cmd = ["uv", "venv"]
        if python_version:
            cmd += ["--python", python_version]
        return cmd
    else:
        return [python_exe if python_exe else sys.executable, "-m", "venv"]


def get_pip_command(python_exe: Optional[str] = None) -> List[str]:
    """Determine whether to use 'uv pip' or regular 'pip' based on environment.

    :param str python_exe: The Python executable to use (if not using the default).
    :return: List of command arguments for pip.
    :rtype: List[str]
    """
    # Check TOX_PIP_IMPL environment variable (aligns with tox.ini configuration)
    pip_impl = os.environ.get("TOX_PIP_IMPL", "pip").lower()

    # soon we will change this to default to uv
    if pip_impl == "uv":
        return ["uv", "pip"]
    else:
        return [python_exe if python_exe else sys.executable, "-m", "pip"]


def get_venv_python(venv_path: str) -> str:
    """Given a python venv path, identify the crossplat reference to the python executable."""
    # if we already have a path to a python executable, return it
    if os.path.isfile(venv_path) and os.access(venv_path, os.X_OK) and os.path.basename(venv_path).startswith("python"):
        return venv_path

    # cross-platform python in a venv
    bin_dir = "Scripts" if os.name == "nt" else "bin"
    python_exe = "python.exe" if os.name == "nt" else "python"
    return os.path.join(venv_path, bin_dir, python_exe)


def _is_auth_error(output: str) -> bool:
    """Return True if the output text indicates a 401 Unauthorized error from a package feed."""
    return "401" in output or "Unauthorized" in output


def install_into_venv(venv_path_or_executable: str, requirements: List[str], working_directory: str) -> None:
    """Install the requirements into an existing venv (venv_path) without activating it.

    - Uses get_pip_command(get_venv_python) per request.
    - If get_pip_command returns the 'uv' wrapper, we pass --python to target the venv reliably.
    """
    py = get_venv_python(venv_path_or_executable)
    pip_cmd = get_pip_command(py)

    install_targets = [r.strip() for r in requirements]
    cmd = pip_cmd + ["install"] + install_targets

    if pip_cmd[0] == "uv":
        cmd += ["--python", py]

    # todo: clean this up so that we're using run_logged from #42862
    result = subprocess.run(cmd, cwd=working_directory, capture_output=True, text=True)
    if result.stdout:
        print(result.stdout, end="")
    if result.stderr:
        print(result.stderr, end="", file=sys.stderr)
    if result.returncode != 0:
        if _is_auth_error(result.stderr) or _is_auth_error(result.stdout):
            raise RuntimeError(
                "Received a 401 Unauthorized error while installing packages. "
                "This may indicate missing authentication for the package feed. "
                "See https://github.com/Azure/azure-sdk-for-python/blob/main/CONTRIBUTING.md#authentication-for-upstream-pull-through"
            )
        raise subprocess.CalledProcessError(result.returncode, cmd)


def uninstall_from_venv(venv_path_or_executable: str, requirements: List[str], working_directory: str) -> None:
    """Uninstalls the requirements from an existing venv (venv_path) without activating it."""
    py = get_venv_python(venv_path_or_executable)
    pip_cmd = get_pip_command(py)

    install_targets = [r.strip() for r in requirements]
    cmd = pip_cmd + ["uninstall"]
    if pip_cmd[0] != "uv":
        cmd += ["-y"]
    cmd.extend(install_targets)

    if pip_cmd[0] == "uv":
        cmd += ["--python", py]

    subprocess.check_call(cmd, cwd=working_directory)


def pip_install(
    requirements: List[str],
    include_dependencies: bool = True,
    python_executable: Optional[str] = None,
    cwd: Optional[str] = None,
) -> bool:
    """Attempts to invoke an install operation using the invoking python's pip. Empty requirements are auto-success."""

    exe = get_pip_command(python_executable)

    command = exe + ["install"]

    if requirements:
        command.extend([req.strip() for req in requirements])
    else:
        return True

    try:
        if cwd:
            subprocess.check_call(command, cwd=cwd)
        else:
            subprocess.check_call(command)
    except subprocess.CalledProcessError as f:
        return False

    return True


def pip_uninstall(requirements: List[str], python_executable: Optional[str] = None) -> bool:
    """Attempts to invoke an uninstall operation using the invoking python's pip. Empty requirements are auto-success."""
    # use uninstall_from_venv() for uv venvs
    exe = python_executable or sys.executable
    command = [exe, "-m", "pip", "uninstall", "-y"]

    if requirements:
        command.extend([req.strip() for req in requirements])
    else:
        return True

    try:
        result = subprocess.check_call(command)
        return True
    except subprocess.CalledProcessError as f:
        return False


def pip_install_requirements_file(requirements_file: str, python_executable: Optional[str] = None) -> bool:
    return pip_install(["-r", requirements_file], True, python_executable)


def run_pip_freeze(python_executable: Optional[str] = None) -> List[str]:
    """Uses the invoking python executable to get the output from pip freeze."""
    exe = python_executable or sys.executable

    pip_cmd = get_pip_command(exe)

    # we use `freeze` because it is present on both pip and uv
    out = subprocess.Popen(
        pip_cmd + ["freeze", "--disable-pip-version-check"],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
    )

    stdout, _ = out.communicate()
    output_text = stdout.decode("utf-8") if stdout else ""

    if out.returncode != 0:
        raise Exception("pip freeze failed with return code {}: {}".format(out.returncode, output_text))

    collected_output = []
    for line in output_text.splitlines():
        if line:
            collected_output.append(line)

    return collected_output


def get_pip_list_output(python_executable: Optional[str] = None):
    """Uses the invoking python executable to get the output from pip list."""
    pip_output = run_pip_freeze(python_executable)

    collected_output = {}
    for line in pip_output:
        if "==" in line:
            package, version = re.split("==", line)
            collected_output[package] = version

    return collected_output
