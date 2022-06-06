#!/usr/bin/env python

#-------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
#--------------------------------------------------------------------------

from setuptools import setup, find_packages
import os
from io import open
import re

PACKAGE_NAME = "azure-eventhub-checkpointstoretable"
PACKAGE_PPRINT_NAME = "Event Hubs checkpointer implementation with Azure Table Storage"

# a-b-c => a/b/c
package_folder_path = "azure/eventhub/extensions/checkpointstoretable"
# a-b-c => a.b.c
namespace_name = "azure.eventhub.extensions.checkpointstoretable"

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
    description="Microsoft Azure {} Client Library for Python".format(PACKAGE_PPRINT_NAME),
    # ensure that these are updated to reflect the package owners' information
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/Azure/azure-sdk-for-python",
    author="Microsoft Corporation",
    author_email="azuresdkengsysadmins@microsoft.com",
    license="MIT License",
    # ensure that the development status reflects the status of your package
    classifiers=[
        "Development Status :: 4 - Beta",
        "Programming Language :: Python",
        "Programming Language :: Python :: 2",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        'Programming Language :: Python :: 3.10',
        "License :: OSI Approved :: MIT License",
    ],
    packages=find_packages(
        exclude=[
            "tests",
            # Exclude packages that will be covered by PEP420 or nspkg
            # This means any folder structure that only consists of a __init__.py.
            # For example, for storage, this would mean adding 'azure.storage'
            'samples',
            # Exclude packages that will be covered by PEP420 or nspkg
            'azure',
            'azure.eventhub',
            'azure.eventhub.extensions',
        ]
    ),
    include_package_data=True,
    package_data={
        'pytyped': ['py.typed'],
    },
    install_requires=[
        "azure-core<2.0.0,>=1.14.0",
        'azure-eventhub<6.0.0,>=5.0.0',
        'msrest>=0.6.21',
        'azure-eventhub<6.0.0,>=5.0.0',
    ],
    extras_require={
        ":python_version<'3.0'": ["azure-nspkg"],
        ":python_version<'3.0'": ['futures', 'azure-data-nspkg<2.0.0,>=1.0.0'],
        ":python_version<'3.4'": ['enum34>=1.0.4'],
        ":python_version<'3.5'": ["typing"],
    },
    project_urls={
        "Bug Reports": "https://github.com/Azure/azure-sdk-for-python/issues",
        "Source": "https://github.com/Azure/azure-sdk-python",
    },
)