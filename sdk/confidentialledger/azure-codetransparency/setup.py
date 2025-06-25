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

PACKAGE_NAME = "azure-codetransparency"
PACKAGE_PPRINT_NAME = "Code Transparency Service"

# a-b-c => a/b/c
PACKAGE_FOLDER_PATH = PACKAGE_NAME.replace("-", "/")
# a-b-c => a.b.c
NAMESPACE_NAME = PACKAGE_NAME.replace("-", ".")

# Version extraction inspired from 'requests'
with open(os.path.join(PACKAGE_FOLDER_PATH, "_version.py"), "r") as fd:
    VERSION = re.search(
        r'^VERSION\s*=\s*[\'"]([^\'"]*)[\'"]', fd.read(), re.MULTILINE
    ).group(1)

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
    description="Microsoft Azure {} Client Library for Python".format(
        PACKAGE_PPRINT_NAME
    ),
    long_description=README + "\n\n" + CHANGELOG,
    long_description_content_type="text/markdown",
    license="MIT License",
    author="Microsoft Corporation",
    author_email="azpysdkhelp@microsoft.com",
    url="https://github.com/Azure/azure-sdk-for-python",
    keywords="azure, azure sdk",
    classifiers=[
        "Development Status :: 4 - Beta",
        "Programming Language :: Python :: 3 :: Only",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Programming Language :: Python :: 3.13",
        "License :: OSI Approved :: MIT License",
    ],
    python_requires=">=3.8",
    zip_safe=False,
    packages=find_packages(
        exclude=[
            "tests",
            # Exclude packages that will be covered by PEP420 or nspkg
            "azure",
        ]
    ),
    package_data={
        'pytyped': ['py.typed'],
    },
    install_requires=[
        "azure-core<2.0.0,>=1.28.0",
        "isodate<1.0.0,>=0.6.1",
    ],
    project_urls={
        'Bug Reports': 'https://github.com/Azure/azure-sdk-for-python/issues',
        'Source': 'https://github.com/Azure/azure-sdk-for-python',
    }
)