# Copyright (c) Microsoft Corporation.
# Licensed under the MIT license.
"""Root conftest — ensures the project root is on sys.path so that
``from tests._helpers import …`` works regardless of how pytest is invoked."""

import sys
from pathlib import Path

_PROJECT_ROOT = str(Path(__file__).resolve().parent.parent)
if _PROJECT_ROOT not in sys.path:
    sys.path.insert(0, _PROJECT_ROOT)
