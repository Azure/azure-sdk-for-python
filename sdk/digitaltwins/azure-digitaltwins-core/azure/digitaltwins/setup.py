#!/usr/bin/env python

# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
import sys
from setuptools import setup

PACKAGE_NAME = "azure-digitaltwins"
PACKAGE_PPRINT_NAME = "Azure DigitalTwins"
VERSION = "1.0.0"

setup(
    name=PACKAGE_NAME,
    version=VERSION,
    description="Microsoft Azure {} Client Library for Python".format(PACKAGE_PPRINT_NAME),
    long_description=README + "\n\n" + CHANGELOG,
    long_description_content_type="text/markdown",
    license="MIT License",
    author="Microsoft Corporation",
    author_email="azure-digitaltwins-core@microsoft.com",
    url="https://github.com/Azure/azure-sdk-for-python/tree/master/sdk/digitaltwins/azure-digitaltwins-core",
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Programming Language :: Python",
        "Programming Language :: Python :: 2",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.5",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        'Programming Language :: Python :: 3.8',
        "License :: OSI Approved :: MIT License",
    ],
    zip_safe=False,
    packages=['azure-digitaltwins'],
    install_requires=["azure-core<2.0.0,>=1.7.0", "cryptography>=2.1.4", "msrest>=0.6.0"],
)