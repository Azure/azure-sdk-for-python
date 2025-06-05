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


PACKAGE_NAME = "azure-projects"
PACKAGE_PPRINT_NAME = "Projects"

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
    keywords="azure, azure sdk, azure projects",  # update with search keywords relevant to the azure service / product
    author="Microsoft Corporation",
    author_email="azpysdkhelp@microsoft.com",
    license="MIT License",
    # ensure that the development status reflects the status of your package
    classifiers=[
        "Development Status :: 1 - Planning",
        "Intended Audience :: Developers",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3 :: Only",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Programming Language :: Python :: 3.13",
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
        "azure.projects": ["py.typed"],
    },
    install_requires=[
        "typing-extensions>=4.5",
        "python-dotenv>=1.0.0",
        "pyyaml>=6.0.2",
        "azure-core>=1.31.0",
        "azure-identity>=1.20",
        "azure-appconfiguration-provider>=2.0.0",  # TODO: This needs to be removed before GA.
    ],
    python_requires=">=3.8",
    entry_points={
        "console_scripts": ["azproj=azure.projects._command:command"],
    },
    extras_require={
        "mcp": [
            "mcp>=1.6",
            "makefun>=1.15",
        ],
    },
    project_urls={
        "Bug Reports": "https://github.com/Azure/azure-sdk-for-python/issues",
        "Source": "https://github.com/Azure/azure-sdk-for-python",
    },
)
