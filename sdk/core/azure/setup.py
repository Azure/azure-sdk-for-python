#!/usr/bin/env python

#-------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
#--------------------------------------------------------------------------

from setuptools import setup


message = """

Starting v5.0.0, the 'azure' meta-package is deprecated and cannot be installed anymore.
Please install the service specific packages prefixed by `azure` needed for your application.

Here's a non-exhaustive list of common packages:

-  azure-mgmt-compute (https://pypi.python.org/pypi/azure-mgmt-compute) : Management of Virtual Machines, etc.
-  azure-mgmt-storage (https://pypi.python.org/pypi/azure-mgmt-storage) : Management of storage accounts.
-  azure-mgmt-resource (https://pypi.python.org/pypi/azure-mgmt-resource) : Generic package about Azure Resource Management (ARM)
-  azure-keyvault-secrets (https://pypi.python.org/pypi/azure-keyvault-secrets) : Access to secrets in Key Vault
-  azure-storage-blob (https://pypi.python.org/pypi/azure-storage-blob) : Access to blobs in storage accounts
"""

raise RuntimeError(message)

setup(
    name='azure',
    version='5.0.0',
    description='Microsoft Azure Client Libraries for Python',
    long_description=open('README.rst', 'r').read(),
    license='MIT License',
    author='Microsoft Corporation',
    author_email='azpysdkhelp@microsoft.com',
    url='https://github.com/Azure/azure-sdk-for-python',
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'License :: OSI Approved :: MIT License',
    ],
    zip_safe=False,
)
