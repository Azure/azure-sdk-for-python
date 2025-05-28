# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

# cspell:ignore ruamel

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
        "Development Status :: 5 - Production/Stable",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3 :: Only",
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
            "tests*",
            # Exclude packages that will be covered by PEP420 or nspkg
            "azure",
            "azure.ai",
        ]
    ),
    python_requires=">=3.9",
    install_requires=[
        "promptflow-devkit>=1.17.1",
        "promptflow-core>=1.17.1",
        "pyjwt>=2.8.0",
        # pickle support for credentials was added to this release
        "azure-identity>=1.16.0",
        "azure-core>=1.30.2",
        "nltk>=3.9.1",
        "azure-storage-blob>=12.10.0",
        "httpx>=0.25.1",
        # Dependencies added since Promptflow will soon be made optional
        "pandas>=2.1.2,<3.0.0",
        "openai>=1.78.0",
        "ruamel.yaml>=0.17.10,<1.0.0",
        "msrest>=0.6.21",
        "Jinja2>=3.1.6",
        "aiohttp>=3.0",
    ],
    extras_require={
        "redteam": [
            "pyrit==0.8.1"
        ]
    },
    project_urls={
        "Bug Reports": "https://github.com/Azure/azure-sdk-for-python/issues",
        "Source": "https://github.com/Azure/azure-sdk-for-python",
    },
    package_data={
        "pytyped": ["py.typed"],
        "azure.ai.evaluation.simulator._prompty": ["*.prompty"],
        "azure.ai.evaluation.simulator._data_sources": ["*.json"],
        "azure.ai.evaluation._common.raiclient": ["**/*.py"],
    },
)
