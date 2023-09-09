#!/usr/bin/env python

# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
import sys
if not sys.version_info >= (3, 7, 0):
    raise Exception("Autorest for Python extension requires Python 3.7 at least")

try:
    import pip
except ImportError:
    raise Exception("Your Python installation doesn't have pip available")

try:
    import venv
except ImportError:
    raise Exception("Your Python installation doesn't have venv available")


# Now we have pip and Py >= 3.7, go to work

import subprocess
from pathlib import Path

from venvtools import ExtendedEnvBuilder, python_run

_ROOT_DIR = Path(__file__).parent


def main():
    venv_path = _ROOT_DIR / "venv"
    venv_prexists = venv_path.exists()

    if venv_prexists:
        env_builder = venv.EnvBuilder(with_pip=True)
        venv_context = env_builder.ensure_directories(venv_path)
    else:
        env_builder = ExtendedEnvBuilder(with_pip=True)
        env_builder.create(venv_path)
        venv_context = env_builder.context

        python_run(venv_context, "pip", ["install", "-U", "pip"])
        python_run(venv_context, "pip", ["install", "-r", "requirements.txt"])
        python_run(venv_context, "pip", ["install", "-e", str(_ROOT_DIR)])

if __name__ == "__main__":
    main()
