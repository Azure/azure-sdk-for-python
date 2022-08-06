#!/usr/bin/env python

# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
# pylint:disable=missing-docstring

import re
import os.path
from io import open
from setuptools import find_packages, setup

# Change the PACKAGE_NAME only to change folder and different name
PACKAGE_NAME = "azure-keyvault-secrets"
PACKAGE_PPRINT_NAME = "Key Vault Secrets"

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
    long_description=README + "\n\n" + CHANGELOG,
    long_description_content_type="text/markdown",
    license="MIT License",
    author="Microsoft Corporation",
    author_email="azurekeyvault@microsoft.com",
    url="https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/keyvault/azure-keyvault-secrets",
    classifiers=[
        "Development Status :: 4 - Beta",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3 :: Only",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "License :: OSI Approved :: MIT License",
    ],
    zip_safe=False,
    packages=find_packages(
        exclude=[
            "samples",
            "tests",
            # Exclude packages that will be covered by PEP420 or nspkg
            "azure",
            "azure.keyvault",
        ]
    ),
    python_requires=">=3.7",
    install_requires=[
        "azure-core<2.0.0,>=1.20.0",
        "msrest>=0.6.21",
        "azure-common~=1.1",
        "six>=1.11.0",
    ],
)
