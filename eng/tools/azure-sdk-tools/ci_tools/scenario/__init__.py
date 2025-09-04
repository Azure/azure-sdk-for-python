import os
from subprocess import check_call
from .generation import prepare_and_test_optional
from .managed_virtual_env import ManagedVirtualEnv
from ci_tools.functions import (
    get_pip_command
)

from typing import Optional
# todo rename managed_virtual_env to virtual_env and move below functions there

def get_venv_python(venv_path: str) -> str:
    """
    Given a python venv path, identify the crossplat reference to the python executable.
    """
    # cross-platform python in a venv
    bin_dir = "Scripts" if os.name == "nt" else "bin"
    return os.path.join(venv_path, bin_dir, "python")

def install_into_venv(venv_path: str, package_path: str, editable: bool = True, extras: Optional[str] = None) -> None:
    """
    Install the package into an existing venv (venv_path) without activating it.

    - Uses get_pip_command(get_venv_python) per request.
    - If get_pip_command returns the 'uv' wrapper, we fall back to get_venv_python -m pip
      so installation goes into the target venv reliably.
    """
    py = get_venv_python(venv_path)
    pip_cmd = get_pip_command(py)

    install_target = package_path
    if extras:
        install_target = f"{package_path}[{extras}]"

    if editable:
        cmd = pip_cmd + ["install", "-e", install_target]
    else:
        cmd = pip_cmd + ["install", install_target]

    if pip_cmd[0] == "uv":
        cmd += ["--python", py]

    # Run the install; this will install into the interpreter referenced by `py` either by
    # the pip command or by calling uv with a target python env
    check_call(cmd)


__all__ = ["prepare_and_test_optional", "ManagedVirtualEnv", "install_into_venv", "get_venv_python"]
