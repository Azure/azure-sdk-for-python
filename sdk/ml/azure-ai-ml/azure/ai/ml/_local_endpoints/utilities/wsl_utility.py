# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------


from platform import uname
from azure.ai.ml._local_endpoints.utilities.commandline_utility import run_cli_command


def in_wsl() -> bool:
    """
    WSL is thought to be the only common Linux kernel with Microsoft in the name, per Microsoft:

    https://github.com/microsoft/WSL/issues/4071#issuecomment-496715404
    """
    return "microsoft" in uname().release.lower()


def get_wsl_path(path: str) -> bool:
    """
    Input /home/username/ for example. Output /mnt/c/users/username
    """
    windows_path = run_cli_command(["wslpath", "-w", path])
    return windows_path
