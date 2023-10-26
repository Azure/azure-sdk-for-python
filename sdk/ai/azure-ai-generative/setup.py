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
PACKAGE_NAME = "azure-ai-generative"
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
    keywords="azure, azuresdk, azure sdk",
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
    ],
    zip_safe=False,
    include_package_data=True,
    packages=find_packages(
        exclude=[
            "tests",
            # Exclude packages that will be covered by PEP420 or nspkg
            "azure",
            "azure.ai",
            "samples",
        ]
    ),
    python_requires="<4.0,>=3.8",
    install_requires=[
        # NOTE: To avoid breaking changes in a major version bump, all dependencies should pin an upper bound if possible.
        "azure-ai-resources",
        "azureml-telemetry",
        "mlflow<3",
        "azure-mgmt-authorization",
        "opencensus-ext-azure<2.0.0",
        "opencensus-ext-logging",
    ],
    extras_require={
        "cognitive_search": [
            "azure-search-documents==11.4.0b8",
        ],
        "document_parsing": [
            "pandas>=1",
            "nltk>=3.8,<4",
            "markdown>=3.4,<4",
            "beautifulsoup4>=4.11,<5",
            "tika>=2.6,<3",
            "pypdf>=3.7,<4",
            "unstructured>=0.10,<1",
            "GitPython>=3.1,<4"
        ],
        "evaluate": [
            "azureml-metrics[generative-ai]",
            "promptflow>=0.1.0b7",
            "promptflow-tools",
        ],
        "faiss": [
            "faiss-cpu>=1.7,<1.8"
        ],
        "hugging_face": [
            "scikit-learn",
            "sentence-transformers"
        ],
        "index": [
            "azureml-dataprep[parquet]>4.11",
            "azureml-fsspec>=1",
            "azureml-mlflow",
            "fsspec>=2023.3",
            "openai>=0.27.8,<1",
            "tiktoken>=0.3,<1",
            "mmh3",
            "requests",
        ],
        "promptflow": [
            "promptflow[azure]",
            "promptflow-tools",
            "promptflow-vectordb"
        ],
        "qa_generation": [
            "openai>=0.27.8,<1"
        ],
        "simulator": [
            "aiohttp>=3.8.5,<4",
            "aiohttp_retry>=2,<3",
            "Jinja2>=3,<4",
            "json5>=0.9,<1",
            "jsonpath_ng>=1,<2",
            "msal>=1,<2",
            "pybase64>=1,<2",
            "PyYAML>=4.1,<7",
            "tiktoken>=0.3,<1",
            "websocket_client>=1,<2",
            "azure-identity>=1,<2",
            "azure-keyvault-secrets>=1,<5",
        ],
    },
    project_urls={
        "Bug Reports": "https://github.com/Azure/azure-sdk-for-python/issues",
        "Source": "https://github.com/Azure/azure-sdk-python",
    },
)
