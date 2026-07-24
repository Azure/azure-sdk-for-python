#!/usr/bin/env python

# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

# This file exists only for doc-warden compatibility.
# The actual build is handled by maturin via pyproject.toml.

import re
from pathlib import Path

from setuptools import setup

PACKAGE_NAME = "azure-storage-extensions-transfer"

version_text = Path("azure", "storage", "extensions", "transfer", "_version.py").read_text()
version = re.search(r'VERSION = "(.*?)"', version_text).group(1)

setup(
    name=PACKAGE_NAME,
    version=version,
)
