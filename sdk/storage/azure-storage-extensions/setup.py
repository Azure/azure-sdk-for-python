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
# This file can be removed once both experimental gates are dropped in
# https://github.com/pypa/setuptools/blob/84ed5913724df5a12dc804e1d5efe12508e706d2/setuptools/config/pyprojecttoml.py#L135

from setuptools import setup, Extension


setup(
    ext_package="azure.storage.extensions.checksums",
    ext_modules=[
        Extension(
            "crc64",
            ["azure/storage/extensions/checksums/crc64/crc64module.c"],
            define_macros=[("Py_LIMITED_API", "0x030A0000")],
            py_limited_api=True,
        ),
    ],
    options={"bdist_wheel": {"py_limited_api": "cp310"}},
)
