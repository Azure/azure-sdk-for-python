# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.
"""Start test subprocesses with the same SDK package as their parent."""

import sys
from pathlib import Path

import azure.cosmos


def sdk_python_command(code: str, *args: str) -> list[str]:
    """Load the parent's SDK before exposing checkout helpers in a fresh process.

    Isolated startup prevents the working directory or PYTHONPATH from selecting
    a different SDK. The package can be an installed wheel or a local build.
    """
    sdk_root = Path(azure.cosmos.__file__).resolve().parents[2]
    package_root = Path(__file__).resolve().parents[2]
    bootstrap = (
        "import sys\n"
        f"sys.path.insert(0, {str(sdk_root)!r})\n"
        "import azure.cosmos\n"
        f"sys.path[:0] = {[str(package_root), str(package_root / 'tests')]!r}\n"
    )
    return [sys.executable, "-I", "-c", bootstrap + code, *args]
