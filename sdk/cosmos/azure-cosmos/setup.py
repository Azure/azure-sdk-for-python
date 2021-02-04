#!/usr/bin/env python

# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
# pylint:disable=missing-docstring

import re
import os
from io import open
from setuptools import find_packages, setup

# Change the PACKAGE_NAME only to change folder and different name
PACKAGE_NAME = "azure-cosmos"
PACKAGE_PPRINT_NAME = "Cosmos"

# a-b-c => a/b/c
PACKAGE_FOLDER_PATH = PACKAGE_NAME.replace("-", "/")
# a-b-c => a.b.c
NAMESPACE_NAME = PACKAGE_NAME.replace("-", ".")

# Version extraction inspired from 'requests'
with open(os.path.join(PACKAGE_FOLDER_PATH, '_version.py'), 'r') as fd:
    version = re.search(r'^VERSION\s*=\s*[\'"]([^\'"]*)[\'"]',
                        fd.read(), re.MULTILINE).group(1)

with open("README.md", encoding="utf-8") as f:
    readme = f.read()
with open("CHANGELOG.md", encoding="utf-8") as f:
    changelog = f.read()

setup(
    name=PACKAGE_NAME,
    version=version,
    description="Microsoft Azure {} Client Library for Python".format(PACKAGE_PPRINT_NAME),
    long_description=readme + "\n\n" + changelog,
    long_description_content_type="text/markdown",
    license="MIT License",
    author="Microsoft Corporation",
    author_email="askdocdb@microsoft.com",
    maintainer="Microsoft",
    maintainer_email="askdocdb@microsoft.com",
    url="https://github.com/Azure/azure-sdk-for-python",
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "Natural Language :: English",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Programming Language :: Python :: 2",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.5",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "License :: OSI Approved :: MIT License",
    ],
    zip_safe=False,
    packages=find_packages(
        exclude=[
            "samples",
            "test",
            # Exclude packages that will be covered by PEP420 or nspkg
            "azure",
        ]
    ),
    install_requires=[
      'six >=1.11.0',
      'azure-core<2.0.0,>=1.0.0'
    ],
    extras_require={
      ":python_version<'3.4'": ['enum34>=1.0.4'],
      ":python_version<'3.0'": ["azure-nspkg"],
      ":python_version<'3.5'": ["typing"]
    },
)