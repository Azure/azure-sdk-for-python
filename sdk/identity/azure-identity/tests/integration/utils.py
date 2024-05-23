# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
import subprocess
import sys


def run_command(command, exit_on_failure=True) -> str:
    try:
        result = subprocess.check_output(command, stderr=subprocess.STDOUT).decode("utf-8").strip()
        return result
    except subprocess.CalledProcessError as ex:
        result = ex.output.decode("utf-8").strip()
        if exit_on_failure:
            print(result)
            sys.exit(1)
        return result
