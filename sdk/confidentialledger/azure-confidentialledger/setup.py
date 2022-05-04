#!/usr/bin/env python

# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
# pylint:disable=missing-docstring

from io import open
import os
import re
from setuptools import setup, find_packages

# example setup.py Feel free to copy the entire "azure-template" folder into a package folder named
# with "azure-<yourpackagename>". Ensure that the below arguments to setup() are updated to reflect
# your package.

PACKAGE_NAME = "azure-confidentialledger"
PACKAGE_PPRINT_NAME = "Confidential Ledger"

# a-b-c => a/b/c
PACKAGE_FOLDER_PATH = PACKAGE_NAME.replace("-", "/")
# a-b-c => a.b.c
NAMESPACE_NAME = PACKAGE_NAME.replace("-", ".")

# Version extraction inspired from 'requests'
with open(os.path.join(PACKAGE_FOLDER_PATH, "_version.py"), "r") as fd:
    VERSION = re.search(r'^VERSION\s*=\s*[\'"]([^\'"]*)[\'"]', fd.read(), re.MULTILINE).group(1)

if not VERSION:
    raise RuntimeError("Cannot find version information")

with open("README.md", encoding="utf-8") as f:
    README = f.read()
with open("CHANGELOG.md", encoding="utf-8") as f:
    CHANGELOG = f.read()

setup(
    name=PACKAGE_NAME,
    version=VERSION,
    include_package_data=True,
    description="Microsoft Azure {} Client Library for Python".format(PACKAGE_PPRINT_NAME),

    # ensure that these are updated to reflect the package owners' information
    long_description=README + "\n\n" + CHANGELOG,
    long_description_content_type="text/markdown",
    license="MIT License",
    author="Microsoft Corporation",
    author_email="accledgerdevs@microsoft.com",
    url="https://github.com/Azure/azure-sdk-for-python",
    classifiers=[
        "Development Status :: 4 - Beta",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3 :: Only",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "License :: OSI Approved :: MIT License",
    ],
    zip_safe=False,
    packages=find_packages(exclude=[
        "tests",
        # Exclude packages that will be covered by PEP420 or nspkg
        "azure"
    ]),
    python_requires=">=3.6",
    install_requires=[
        "azure-common~=1.1",
        "azure-core<2.0.0,>=1.2.2",
        "msrest>=0.6.21",
    ],
)
