# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
from contextlib import contextmanager
import tempfile
import subprocess
import venv
import sys
from pathlib import Path


_ROOT_DIR = Path(__file__).parent


class ExtendedEnvBuilder(venv.EnvBuilder):
    """An extended env builder which saves the context, to have access
    easily to bin path and such.
    """

    def __init__(self, *args, **kwargs):
        self.context = None
        super().__init__(*args, **kwargs)

    def ensure_directories(self, env_dir):
        self.context = super(ExtendedEnvBuilder, self).ensure_directories(env_dir)
        return self.context


def create(env_dir, system_site_packages=False, clear=False,
                    symlinks=False, with_pip=False, prompt=None):
    """Create a virtual environment in a directory."""
    builder = ExtendedEnvBuilder(system_site_packages=system_site_packages,
                                 clear=clear, symlinks=symlinks, with_pip=with_pip,
                                 prompt=prompt)
    builder.create(env_dir)
    return builder.context

@contextmanager
def create_venv_with_package(packages):
    """Create a venv with these packages in a temp dir and yielf the env.

    packages should be an iterable of pip version instructio (e.g. package~=1.2.3)
    """
    with tempfile.TemporaryDirectory() as tempdir:
        myenv = create(tempdir, with_pip=True)
        pip_call = [
            myenv.env_exe,
            "-m",
            "pip",
            "install",
        ]
        subprocess.check_call(pip_call + ['-U', 'pip'])
        if packages:
            subprocess.check_call(pip_call + packages)
        yield myenv

def python_run(venv_context, module, command=None, *, additional_dir="."):
    try:
        cmd_line= [
            venv_context.env_exe,
            "-m", module
        ] + (command if command else [])
        print("Executing: {}".format(" ".join(cmd_line)))
        subprocess.run(
            cmd_line,
            cwd=_ROOT_DIR / additional_dir,
            check=True,
        )
    except subprocess.CalledProcessError as err:
        print(err)
        sys.exit(1)
