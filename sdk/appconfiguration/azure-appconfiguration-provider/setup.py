#!/usr/bin/env python

# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

import sys
import re
import os.path
from io import open
from setuptools import find_packages, setup

# Change the PACKAGE_NAME only to change folder and different name
PACKAGE_NAME = "azure-appconfiguration-provider"
PACKAGE_PPRINT_NAME = "App Configuration Provider"

# a-b-c => a/b/c
package_folder_path = PACKAGE_NAME.replace("-", "/")
# a-b-c => a.b.c
namespace_name = PACKAGE_NAME.replace("-", ".")

# Version extraction inspired from 'requests'
with open(os.path.join(package_folder_path, "_version.py"), "r") as fd:
    version = re.search(r'^VERSION\s*=\s*[\'"]([^\'"]*)[\'"]', fd.read(), re.MULTILINE).group(1)

if not version:
    raise RuntimeError("Cannot find version information")

with open("README.md", encoding="utf-8") as f:
    readme = f.read()
with open("CHANGELOG.md", encoding="utf-8") as f:
    changelog = f.read()

exclude_packages = [
    "tests",
    "tests.*",
    "samples",
    # Exclude packages that will be covered by PEP420 or nspkg
    "azure",
    "azure.appconfiguration",
]
if sys.version_info < (3, 5, 3):
    exclude_packages.extend(["*.aio", "*.aio.*"])

setup(
    name=PACKAGE_NAME,
    version=version,
    include_package_data=True,
    description="Microsoft {} Library for Python".format(PACKAGE_PPRINT_NAME),
    long_description=readme + "\n\n" + changelog,
    long_description_content_type="text/markdown",
    license="MIT License",
    author="Microsoft Corporation",
    author_email="azpysdkhelp@microsoft.com",
    url="https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/appconfiguration/azure-appconfiguration-provider",
    keywords="azure, azure sdk",
    classifiers=[
        "Development Status :: 4 - Beta",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3 :: Only",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "License :: OSI Approved :: MIT License",
    ],
    zip_safe=False,
    packages=find_packages(exclude=exclude_packages),
    python_requires=">=3.6",
    install_requires=[
        "msrest>=0.6.21",
        "azure-core<2.0.0,>=1.25.0",
        "azure-appconfiguration<2.0.0,>=1.4.0",
        "azure-keyvault-secrets<5.0.0,>=4.3.0",
    ],
)
