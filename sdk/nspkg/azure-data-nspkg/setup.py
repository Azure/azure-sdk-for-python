#!/usr/bin/env python

# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
import sys
from setuptools import setup

setup(
    name='azure-data-nspkg',
    version='1.0.0',
    description="Microsoft Azure Data Namespace Package [Internal]",
    long_description=open("README.md", "r").read(),
    long_description_content_type="text/markdown",
    license='MIT License',
    author="Microsoft Corporation",
    author_email="azpysdkhelp@microsoft.com",
    url="https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/tables",
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Programming Language :: Python",
        "Programming Language :: Python :: 2",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.5",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "License :: OSI Approved :: MIT License",
    ],
    zip_safe=False,
    packages=['azure.data'],
    install_requires=[
        'azure-nspkg>=3.0.0',
    ]
)
