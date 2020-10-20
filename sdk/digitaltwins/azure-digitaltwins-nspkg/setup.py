#!/usr/bin/env python

# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
import sys
from setuptools import setup

PACKAGE_NAME = "azure-digitaltwins-nspkg"
PACKAGE_PPRINT_NAME = "Azure DigitalTwins Nspkg"
VERSION = "1.0.0"

with open("README.md", encoding="utf-8") as f:
    README = f.read()
with open("CHANGELOG.md", encoding="utf-8") as f:
    CHANGELOG = f.read()

PACKAGES = []
# Do an empty package on Python 3 and not python_requires, since not everybody is ready
# https://github.com/Azure/azure-sdk-for-python/issues/3447
# https://github.com/Azure/azure-sdk-for-python/issues/3481
if sys.version_info[0] < 3:
    PACKAGES = ['azure.digitaltwins']

setup(
    name=PACKAGE_NAME,
    version=VERSION,
    description="Microsoft Azure {} Client Library for Python".format(PACKAGE_PPRINT_NAME),
    long_description=README + "\n\n" + CHANGELOG,
    long_description_content_type="text/markdown",
    license="MIT License",
    author="Microsoft Corporation",
    author_email="azpysdkhelp@microsoft.com",
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
    install_requires=["azure-nspkg>=3.0.0"],
)