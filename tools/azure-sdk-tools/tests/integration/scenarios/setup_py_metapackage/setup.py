#!/usr/bin/env python

#-------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
#--------------------------------------------------------------------------

from setuptools import setup
from io import open
setup(
    name='azure-keyvault',
    version='4.2.1b1',
    description='Microsoft Azure Key Vault Client Libraries for Python',
    long_description_content_type="text/markdown",
    license='MIT License',
    author='Microsoft Corporation',
    author_email="azurekeyvault@microsoft.com",
    url="https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/keyvault/azure-keyvault",
    keywords="azure, azure sdk",
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        'Programming Language :: Python',
        'Programming Language :: Python :: 3 :: Only',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
        'Programming Language :: Python :: 3.12',
        'License :: OSI Approved :: MIT License',
    ],
    zip_safe=False,
    install_requires=[
        'azure-keyvault-certificates~=4.4',
        'azure-keyvault-secrets~=4.4',
        'azure-keyvault-keys~=4.5',
    ],
)
