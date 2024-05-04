# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""version utilities."""

from importlib.metadata import version
from contextlib import suppress


packages_versions_for_compatibility = {
    "langchain": "",
    "azure-search-documents": "",
}

for package in packages_versions_for_compatibility:
    with suppress(Exception):
        packages_versions_for_compatibility[package] = version(package)
    if not packages_versions_for_compatibility[package] or packages_versions_for_compatibility[package] == '':
        raise ValueError(f"package {package} is required but not installed.")


langchain_version = packages_versions_for_compatibility["langchain"]