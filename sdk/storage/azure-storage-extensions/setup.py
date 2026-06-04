# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

# This file remains only for two things that setuptools cannot yet express
# declaratively in pyproject.toml without opting into experimental config:
#   1. Compiling the limited-API C extension(s).
#   2. Overriding bdist_wheel so wheels built against Py_LIMITED_API are
#      tagged abi3 and become reusable across CPython 3.x versions.
# Can be removed once experimental is removed from https://github.com/pypa/setuptools/blob/84ed5913724df5a12dc804e1d5efe12508e706d2/setuptools/config/pyprojecttoml.py#L135

from setuptools import setup, Extension
from setuptools.command.bdist_wheel import bdist_wheel


class bdist_wheel_abi3(bdist_wheel):
    """Override bdist_wheel tag behavior to add abi3 tag."""

    def get_tag(self):
        python, abi, plat = super().get_tag()

        if python.startswith("cp"):
            return python, "abi3", plat
        return python, abi, plat


setup(
    ext_package="azure.storage.extensions.checksums",
    ext_modules=[
        Extension(
            "crc64",
            ["azure/storage/extensions/checksums/crc64/crc64module.c"],
            define_macros=[("Py_LIMITED_API", "3")],
            py_limited_api=True,
        ),
    ],
    cmdclass={"bdist_wheel": bdist_wheel_abi3},
)
