# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
import sys

if sys.version_info < (3, 5, 3):
    collect_ignore_glob = ["*_async.py"]
