#!/usr/bin/env python

#-------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
#--------------------------------------------------------------------------

from setuptools import setup
import sys


message = """

Starting with v5.0.0, the 'azure' meta-package is deprecated and cannot be installed anymore.
Please install the service specific packages prefixed by `azure` needed for your application.

The complete list of available packages can be found at:
https://aka.ms/azsdk/python/all

Here's a non-exhaustive list of common packages:

-  azure-mgmt-compute (https://pypi.python.org/pypi/azure-mgmt-compute) : Management of Virtual Machines, etc.
-  azure-mgmt-storage (https://pypi.python.org/pypi/azure-mgmt-storage) : Management of storage accounts.
-  azure-mgmt-resource (https://pypi.python.org/pypi/azure-mgmt-resource) : Generic package about Azure Resource Management (ARM)
-  azure-keyvault-secrets (https://pypi.python.org/pypi/azure-keyvault-secrets) : Access to secrets in Key Vault
-  azure-storage-blob (https://pypi.python.org/pypi/azure-storage-blob) : Access to blobs in storage accounts

A more comprehensive discussion of the rationale for this decision can be found in the following issue:
https://github.com/Azure/azure-sdk-for-python/issues/10646

"""

if "sdist" in sys.argv:
    setup(
        name='azure',
        version='5.0.0',
        description='Microsoft Azure Client Libraries for Python',
        long_description=open('README.md', 'r').read(),
        long_description_content_type='text/markdown',
        license='MIT License',
        author='Microsoft Corporation',
        author_email='azpysdkhelp@microsoft.com',
        url='https://github.com/Azure/azure-sdk-for-python',
        keywords="azure, azure sdk",
        classifiers=[
            'Development Status :: 7 - Inactive',
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
    )
else:
    raise RuntimeError(message)
