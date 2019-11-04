#!/usr/bin/env python

#-------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
#--------------------------------------------------------------------------

from setuptools import setup
from io import open

with open("README.md", encoding="utf-8") as f:
    README = f.read()
with open("HISTORY.md", encoding="utf-8") as f:
    HISTORY = f.read()

setup(
    name='azure-keyvault',
    version='4.0.0',
    description='Microsoft Azure Key Vault Client Libraries for Python',
    long_description=README + "\n\n" + HISTORY,
    long_description_content_type="text/markdown",
    license='MIT License',
    author='Microsoft Corporation',
    author_email="azurekeyvault@microsoft.com",
    url="https://github.com/Azure/azure-sdk-for-python/tree/master/sdk/keyvault/azure-keyvault",
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'License :: OSI Approved :: MIT License',
    ],
    zip_safe=False,
    install_requires=[
        'azure-keyvault-secrets~=4.0',
        'azure-keyvault-keys~=4.0',
    ],
)
