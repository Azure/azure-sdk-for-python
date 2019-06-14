#!/usr/bin/env python

# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See LICENSE.txt in the project root for
# license information.
# --------------------------------------------------------------------------
# pylint:disable=missing-docstring

import re
import os.path
from io import open
from setuptools import find_packages, setup

# Change the PACKAGE_NAME only to change folder and different name
PACKAGE_NAME = "azure-security-keyvault"
PACKAGE_PPRINT_NAME = "Key Vault"

# a-b-c => a/b/c
PACKAGE_FOLDER_PATH = PACKAGE_NAME.replace("-", "/")
# a-b-c => a.b.c
NAMESPACE_NAME = PACKAGE_NAME.replace("-", ".")

# azure v0.x is not compatible with this package
# azure v0.x used to have a __version__ attribute (newer versions don't)
try:
    import azure

    try:
        VER = azure.__version__  # type: ignore
        raise Exception(
            "This package is incompatible with azure=={}. ".format(VER) + 'Uninstall it with "pip uninstall azure".'
        )
    except AttributeError:
        pass
except ImportError:
    pass

# Version extraction inspired from 'requests'
with open(os.path.join(PACKAGE_FOLDER_PATH, "version.py"), "r") as fd:
    VERSION = re.search(r'^VERSION\s*=\s*[\'"]([^\'"]*)[\'"]', fd.read(), re.MULTILINE).group(1)

if not VERSION:
    raise RuntimeError("Cannot find version information")

with open("README.md", encoding="utf-8") as f:
    README = f.read()
with open("HISTORY.md", encoding="utf-8") as f:
    HISTORY = f.read()

setup(
    name=PACKAGE_NAME,
    version=VERSION,
    description="Microsoft Azure {} Client Library for Python".format(PACKAGE_PPRINT_NAME),
    long_description=README + "\n\n" + HISTORY,
    license="MIT License",
    author="Microsoft Corporation",
    author_email="azurekeyvault@microsoft.com",
    url="https://github.com/Azure/azure-sdk-for-python",
    classifiers=[
        "Development Status :: 4 - Beta",
        "Programming Language :: Python",
        "Programming Language :: Python :: 2",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.4",
        "Programming Language :: Python :: 3.5",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "License :: OSI Approved :: MIT License",
    ],
    zip_safe=False,
    packages=find_packages(
        exclude=[
            "tests",
            # Exclude packages that will be covered by PEP420 or nspkg
            "azure",
            "azure.security",
        ]
    ),
    install_requires=[
        # "azure-core>=0.0.1"
    ],
    extras_require={":python_version<'3.0'": ["azure-security-nspkg"]},
)
