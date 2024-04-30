#!/usr/bin/env python

# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
from setuptools import setup, find_packages

version = "1.0.0b1"

setup(
    name="coretestserver",
    version=version,
    include_package_data=True,
    description="Testserver for Python Core",
    long_description="Testserver for Python Core",
    license="MIT License",
    author="Microsoft Corporation",
    author_email="azpysdkhelp@microsoft.com",
    url="https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/core/corehttp/tests/testserver_tests/coretestserver",
    classifiers=[
        "Development Status :: 4 - Beta",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "License :: OSI Approved :: MIT License",
    ],
    packages=find_packages(),
    install_requires=[
        "flask==2.2.5",
    ],
)
