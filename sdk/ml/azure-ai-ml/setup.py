# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

import os
import re
from io import open
from typing import Any, Match, cast

from setuptools import find_packages, setup

# Change the PACKAGE_NAME only to change folder and different name
PACKAGE_NAME = "azure-ai-ml"
PACKAGE_PPRINT_NAME = "Machine Learning"

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
    description="Microsoft Azure {} Client Library for Python".format(PACKAGE_PPRINT_NAME),
    long_description_content_type="text/markdown",
    long_description=readme + "\n\n" + changelog,
    license="MIT License",
    author="Microsoft Corporation",
    author_email="azuresdkengsysadmins@microsoft.com",
    url="https://github.com/Azure/azure-sdk-for-python",
    classifiers=[
        "Development Status :: 4 - Beta",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3 :: Only",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "License :: OSI Approved :: MIT License",
    ],
    zip_safe=False,
    include_package_data=True,
    packages=find_packages(
        exclude=[
            "samples",
            "tests",
            # Exclude packages that will be covered by PEP420 or nspkg
            "azure",
            "azure.ai",
        ]
    ),
    python_requires="<4.0,>=3.6",
    install_requires=[
        # NOTE: To avoid breaking changes in a major version bump, all dependencies should pin an upper bound if possible.
        "pyyaml<7.0.0,>=5.1.0",
        "azure-identity",
        "msrest>=0.6.18",
        "azure-core<2.0.0,>=1.8.0, !=1.22.0",
        "azure-mgmt-core<2.0.0,>=1.2.0",
        "marshmallow<4.0.0,>=3.5",
        "jsonschema<5.0.0,>=4.0.0",
        "tqdm<=4.63.0",
        # Used for PR 825138
        "strictyaml<=1.6.1",
        # Used for PR 718512
        "colorama<=0.4.4",
        "pyjwt<3.0.0",
        "azure-storage-blob<12.13.0,>=12.10.0",
        "azure-storage-file-share<12.9.0",
        "azure-storage-file-datalake<12.8.0",
        "pydash<=4.9.0",
        "pathspec==0.9.*",
        "isodate",
        # Used for local endpoint story.
        "docker",
        "azure-common<2.0.0,>=1.1",
        "typing-extensions>=4.0.1",
        "applicationinsights<=0.11.10",
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
