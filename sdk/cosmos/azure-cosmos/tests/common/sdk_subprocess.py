# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.
"""Builds the command for running test code in a new Python process.

Some tests cannot run inside the shared pytest process, for example when they
change settings that the SDK reads once per process, check which modules are
imported at startup, or send a real Ctrl+C. Those tests start a new process with
this command. The command makes sure the new process uses the same SDK as this
test run and can import the test helpers.
"""

import sys
from pathlib import Path

import azure.cosmos


def sdk_python_command(code: str, *args: str) -> list[str]:
    """Returns a command that runs ``code`` in a new Python process, using the same SDK as this test run.

    The process starts in isolated mode (``python -I``), so the current folder and
    PYTHONPATH cannot pick up a different copy of the SDK. The SDK is imported first,
    from wherever this test run loaded it (an installed wheel or a local build). The
    package folder and the ``tests`` folder are then added to ``sys.path`` so the code
    can import test helpers. Each value in ``args`` is passed to the code in ``sys.argv[1:]``.
    """
    sdk_root = Path(azure.cosmos.__file__).resolve().parents[2]
    package_root = Path(__file__).resolve().parents[2]
    setup_code = (
        "import sys\n"
        f"sys.path.insert(0, {str(sdk_root)!r})\n"
        "import azure.cosmos\n"
        f"sys.path[:0] = {[str(package_root), str(package_root / 'tests')]!r}\n"
    )
    return [sys.executable, "-I", "-c", setup_code + code, *args]
