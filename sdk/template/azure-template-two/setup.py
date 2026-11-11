# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

# This file remains for two pieces of config that setuptools cannot yet
# express declaratively in pyproject.toml without opting into experimental
# config:
#   1. The limited-API C extension(s) — [tool.setuptools.ext-modules] is
#      still experimental.
#   2. The abi3 wheel tag (py_limited_api) — the equivalent
#      [tool.distutils.bdist_wheel] table is also still experimental.

import re
from pathlib import Path

from setuptools import setup, Extension

PACKAGE_NAME = "azure-template-two"

# `name` and `version` are declared in pyproject.toml (version dynamically via
# [tool.setuptools.dynamic]). They are repeated in the setup() call below only
# because doc-warden's README verification parses setup.py and requires both
# kwargs to be present. The version is read from _version.py rather than
# imported so it works under doc-warden's AST exec as well as a normal build;
# both run with the working directory set to the package root.
version_text = Path("azure", "template", "two", "_version.py").read_text()
version = re.search(r'VERSION = "(.*?)"', version_text).group(1)


setup(
    name=PACKAGE_NAME,
    version=version,
    ext_package="azure.template.two",
    ext_modules=[
        Extension(
            "istrue",
            ["azure/template/two/src/istruemodule.c"],
            define_macros=[("Py_LIMITED_API", "0x030A0000")],
            py_limited_api=True,
        ),
    ],
    options={"bdist_wheel": {"py_limited_api": "cp310"}},
)
