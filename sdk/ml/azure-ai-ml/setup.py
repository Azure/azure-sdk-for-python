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


PACKAGE_NAME = "azure-ai-ml"
PACKAGE_PPRINT_NAME = "Azure Machine Learning"

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
    description="Microsoft Azure {} Client Library for Python".format(PACKAGE_PPRINT_NAME),
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
        "Development Status :: 4 - Beta",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3 :: Only",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "License :: OSI Approved :: MIT License",
    ],
    zip_safe=False,
    include_package_data=True,
    packages=find_packages(exclude=[
        'samples',
        'tests',
        # Exclude packages that will be covered by PEP420 or nspkg
        'azure',
        'azure.ai',
    ]),
    python_requires=">=3.6",
    install_requires=[
        "azure-core<2.0.0,>=1.19.1,!=1.22.0",
        "msrest>=0.6.21",
        "azure-common~=1.1",
        # NOTE: To avoid breaking changes in a major version bump, all dependencies should pin an upper bound if possible.
        "pyyaml<7.0.0,>=5.1.0",
        "azure-identity",
        "azure-mgmt-core<2.0.0,>=1.3.0",
        "marshmallow<4.0.0,>=3.5",
        "jsonschema<5.0.0,>=4.0.0",
        "tqdm<=4.63.0",
        # Used for PR 718512
        "colorama<=0.4.4",
        "pyjwt<=2.3.0",
        "azure-storage-blob<=12.9.0,>=12.5.0",
        "azure-storage-file-share<13.0.0",
        "pydash<=4.9.0",
        "pathspec==0.9.*",
        "isodate>=0.6.0",
        # Used for local endpoint story.
        "docker>=2.0.0",
        "typing-extensions>=4.0.1",
        "applicationinsights<=0.11.10",
        "knack"
    ],
    extras_require={
        # user can run `pip install azure-ai-ml[designer]` to install mldesigner alone with this package
        # so user can submit @dsl.pipeline with @mldesigner.command_component inside it.
        "designer": [
            "mldesigner",
        ],
    },
    project_urls={
        "Bug Reports": "https://github.com/Azure/azure-sdk-for-python/issues",
        "Source": "https://github.com/Azure/azure-sdk-python",
    },
)
