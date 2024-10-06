#!/usr/bin/env python

# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

from setuptools import setup, find_packages
import os
from io import open
import re

# example setup.py Feel free to copy the entire "azure-template" folder into a package folder named
# with "azure-<yourpackagename>". Ensure that the below arguments to setup() are updated to reflect
# your package.

# this setup.py is set up in a specific way to keep the azure* and azure-mgmt-* namespaces WORKING all the way
# up from python 2.7. Reference here: https://github.com/Azure/azure-sdk-for-python/blob/main/doc/dev/packaging.md

PACKAGE_NAME = "azure-cloudmachine"
PACKAGE_PPRINT_NAME = "CloudMachine"

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
    long_description = f.read()

setup(
    name=PACKAGE_NAME,
    version=version,
    description="Microsoft Azure {} Library for Python".format(PACKAGE_PPRINT_NAME),
    # ensure that these are updated to reflect the package owners' information
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/Azure/azure-sdk-for-python",
    keywords="azure, azure sdk",  # update with search keywords relevant to the azure service / product
    author="Microsoft Corporation",
    author_email="azuresdkengsysadmins@microsoft.com",
    license="MIT License",
    # ensure that the development status reflects the status of your package
    classifiers=[
        "Development Status :: 1 - Planning",
        "Intended Audience :: Developers",
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
    packages=find_packages(
        exclude=[
            "tests",
            # Exclude packages that will be covered by PEP420 or nspkg
            # This means any folder structure that only consists of a __init__.py.
            # For example, for storage, this would mean adding 'azure.storage'
            # in addition to the default 'azure' that is seen here.
            "azure",
        ]
    ),
    include_package_data=True,
    package_data={
        "azure.cloudmachine": ["py.typed"],
    },
    install_requires=[
        "python-dotenv>=1.0.0",
        "azure-storage-blob>=12.1.0",
        "azure-servicebus>=7.12",
        "azure-data-tables>=12.1.0",
        "azure-identity",
        "blinker",
        "click",
    ],
    python_requires=">=3.8",
    project_urls={
        "Bug Reports": "https://github.com/Azure/azure-sdk-for-python/issues",
        "Source": "https://github.com/Azure/azure-sdk-for-python",
    },
    extras_require={
        "requests": [
            "requests"
        ],
        "httpx": [
            "httpx"
        ]
    #     "flask": [
    #         "cloudmachine-flask>=0.0.1a1",
    #     ],
    #     "quart": [
    #         "cloudmachine-quart>=0.0.1a1",
    #     ],
    #     # django
    #     # fastapi
    },
    # entry_points={
    #     'console_scripts': [
    #         "cloudmachine = cloudmachine._command:command"
    #     ],
    # },
)
