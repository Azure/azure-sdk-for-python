# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

import os
import re
from io import open
from typing import Any, Match, cast

import pkg_resources
from setuptools import find_packages, setup

# Change the PACKAGE_NAME only to change folder and different name
PACKAGE_NAME = "azure-ai-evaluation"
PACKAGE_PPRINT_NAME = "Evaluation"

# a-b-c => a/b/c
PACKAGE_FOLDER_PATH = PACKAGE_NAME.replace("-", "/")
# a-b-c => a.b.c
NAMESPACE_NAME = PACKAGE_NAME.replace("-", ".")

# Version extraction inspired from 'requests'
with open(os.path.join(PACKAGE_FOLDER_PATH, "_version.py"), "r") as fd:
    version = cast(Match[Any], re.search(r'^VERSION\s*=\s*[\'"]([^\'"]*)[\'"]', fd.read(), re.MULTILINE)).group(1)
if not version:
    raise RuntimeError("Cannot find version information")

with open("README.md", encoding="utf-8") as f:
    readme = f.read()
with open("CHANGELOG.md", encoding="utf-8") as f:
    changelog = f.read()

setup(
    name=PACKAGE_NAME,
    version=version,
    description="Microsoft Azure {} Library for Python".format(PACKAGE_PPRINT_NAME),
    long_description_content_type="text/markdown",
    long_description=readme + "\n\n" + changelog,
    license="MIT License",
    author="Microsoft Corporation",
    author_email="azuresdkengsysadmins@microsoft.com",
    url="https://github.com/Azure/azure-sdk-for-python",
    keywords="azure, azure sdk",
    classifiers=[
        "Development Status :: 4 - Beta",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3 :: Only",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    zip_safe=False,
    include_package_data=True,
    packages=find_packages(
        exclude=[
            "tests",
            # Exclude packages that will be covered by PEP420 or nspkg
            "azure",
            "azure.ai",
        ]
    ),
    python_requires=">=3.8",
    install_requires=[
        "promptflow-devkit>=1.15.0",
        "promptflow-core>=1.15.0",
        "websocket-client>=1.2.0",
        "jsonpath_ng>=1.5.0",
        "numpy>=1.22",
        "pyjwt>=2.8.0",
        "azure-identity",
        "azure-core>=1.30.2",
    ],
    extras_require={
        "pf-azure": [
            "promptflow-azure<2.0.0,>=1.15.0",
        ],
    },
    project_urls={
        "Bug Reports": "https://github.com/Azure/azure-sdk-for-python/issues",
        "Source": "https://github.com/Azure/azure-sdk-for-python",
    },
    package_data={
        "pytyped": ["py.typed"],
    },
)
