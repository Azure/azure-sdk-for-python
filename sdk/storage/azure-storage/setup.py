#!/usr/bin/env python

#-------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
#--------------------------------------------------------------------------

from setuptools import setup

with open("README.md", encoding="utf-8") as f:
    README = f.read()
with open("HISTORY.md", encoding="utf-8") as f:
    HISTORY = f.read()

setup(
    name='azure-storage',
    version='12.0.0b5',
    description='Microsoft Azure Storage Client Libraries for Python',
    long_description=README + "\n\n" + HISTORY,
    long_description_content_type="text/markdown",
    license='MIT License',
    author='Microsoft Corporation',
    author_email='ascl@microsoft.com',
    url="https://github.com/Azure/azure-sdk-for-python/tree/master/sdk/storage/azure-storage",
    classifiers=[
        "Development Status :: 4 - Beta",
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
        'azure-storage-blob==12.0.0b5',
        'azure-storage-file==12.0.0b5',
        'azure-storage-queue==12.0.0b5',
    ],
)
