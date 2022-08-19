#!/usr/bin/env python

#-------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
#--------------------------------------------------------------------------

import re
import os.path
import sys
from io import open
from setuptools import find_packages, setup


# Change the PACKAGE_NAME only to change folder and different name
PACKAGE_NAME = "azure-eventhub"
PACKAGE_PPRINT_NAME = "Event Hubs"

# a-b-c => a/b/c
package_folder_path = PACKAGE_NAME.replace('-', '/')
# a-b-c => a.b.c
namespace_name = PACKAGE_NAME.replace('-', '.')

# Version extraction inspired from 'requests'
with open(os.path.join(package_folder_path, '_version.py'), 'r') as fd:
    version = re.search(r'^VERSION\s*=\s*[\'"]([^\'"]*)[\'"]',
                        fd.read(), re.MULTILINE).group(1)

if not version:
    raise RuntimeError('Cannot find version information')

with open('README.md') as f:
    readme = f.read()
with open('CHANGELOG.md') as f:
    changelog = f.read()

exclude_packages = [
        'tests',
        'stress',
        'samples',
        # Exclude packages that will be covered by PEP420 or nspkg
        'azure',
    ]

setup(
    name=PACKAGE_NAME,
    version=version,
    include_package_data=True,
    description='Microsoft Azure {} Client Library for Python'.format(PACKAGE_PPRINT_NAME),
    long_description=readme + '\n\n' + changelog,
    long_description_content_type='text/markdown',
    license='MIT License',
    author='Microsoft Corporation',
    author_email='azpysdkhelp@microsoft.com',
    url='https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/eventhub/azure-eventhub',
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        'Programming Language :: Python',
        'Programming Language :: Python :: 3 :: Only',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'License :: OSI Approved :: MIT License',
    ],
    python_requires=">=3.7",
    zip_safe=False,
    packages=find_packages(exclude=exclude_packages),
    install_requires=[
        "azure-core<2.0.0,>=1.14.0",
        "uamqp>=1.5.1,<2.0.0",
        "typing-extensions>=4.0.1",
    ]
)
