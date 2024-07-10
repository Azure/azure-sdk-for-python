#!/usr/bin/env python

# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------


import os
import re

from setuptools import setup, find_packages

# Change the PACKAGE_NAME only to change folder and different name
PACKAGE_NAME = "azure-search-documents"
PACKAGE_PPRINT_NAME = "Azure Cognitive Search"

# a-b-c => a/b/c
PACKAGE_FOLDER_PATH = PACKAGE_NAME.replace("-", "/")
# a-b-c => a.b.c
NAMESPACE_NAME = PACKAGE_NAME.replace("-", ".")

# Version extraction inspired from 'requests'
with open(os.path.join(PACKAGE_FOLDER_PATH, "_version.py"), "r") as fd:
    version = re.search(r'^VERSION\s*=\s*[\'"]([^\'"]*)[\'"]', fd.read(), re.MULTILINE).group(1)

if not version:
    raise RuntimeError("Cannot find version information")

setup(
    name=PACKAGE_NAME,
    version=version,
    include_package_data=True,
    description="Microsoft {} Client Library for Python".format(PACKAGE_PPRINT_NAME),
    long_description=open("README.md", "r").read(),
    long_description_content_type="text/markdown",
    license="MIT License",
    author="Microsoft Corporation",
    author_email="ascl@microsoft.com",
    url="https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/search/azure-search-documents",
    keywords="azure, azure sdk",
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3 :: Only",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "License :: OSI Approved :: MIT License",
    ],
    zip_safe=False,
    packages=find_packages(
        exclude=[
            "samples",
            "tests",
            # Exclude packages that will be covered by PEP420 or nspkg
            "azure",
            "azure.search",
        ]
    ),
    python_requires=">=3.8",
    install_requires=[
        "azure-core>=1.28.0",
        "azure-common>=1.1",
        "isodate>=0.6.0",
        "typing-extensions>=4.6.0",
    ],
)
