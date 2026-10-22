#!/usr/bin/env python

#-------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
#--------------------------------------------------------------------------

from setuptools import setup
import sys


message = """

Starting with v0.37.0, the 'azure-storage' meta-package is deprecated and cannot be installed anymore.
Please install the service specific packages prefixed by `azure` needed for your application.

The complete list of available packages can be found at:
https://aka.ms/azsdk/python/all

Here's a non-exhaustive list of common packages:

- [azure-storage-blob](https://pypi.org/project/azure-storage-blob) : Blob storage client
- [azure-storage-file-share](https://pypi.org/project/azure-storage-file-share) : Storage file share client
- [azure-storage-file-datalake](https://pypi.org/project/azure-storage-file-datalake) : ADLS Gen2 client
- [azure-storage-queue](https://pypi.org/project/azure-storage-queue): Queue storage client
"""

if "sdist" in sys.argv:
    setup(
        name='azure-storage',
        version='0.37.0',
        description='Microsoft Azure Storage SDK for Python',
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
