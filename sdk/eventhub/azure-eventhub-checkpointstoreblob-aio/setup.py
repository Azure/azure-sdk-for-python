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
PACKAGE_NAME = "azure-eventhub-checkpointstoreblob-aio"
PACKAGE_PPRINT_NAME = "Event Hubs checkpointer implementation with Blob Storage"

package_folder_path = "azure/eventhub/extensions/checkpointstoreblobaio"
namespace_name = "azure.eventhub.extensions.checkpointstoreblobaio"

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
        'samples',
        # Exclude packages that will be covered by PEP420 or nspkg
        'azure',
        'azure.eventhub',
        'azure.eventhub.extensions'
    ]

setup(
    name=PACKAGE_NAME,
    version=version,
    description='Microsoft Azure {} Client Library for Python'.format(PACKAGE_PPRINT_NAME),
    long_description=readme + '\n\n' + changelog,
    long_description_content_type='text/markdown',
    license='MIT License',
    author='Microsoft Corporation',
    author_email='azpysdkhelp@microsoft.com',
    url='https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/eventhub/azure-eventhub-checkpointstoreblob-aio',
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
    zip_safe=False,
    packages=find_packages(exclude=exclude_packages),
    include_package_data=True,
    package_data={
        'pytyped': ['py.typed'],
    },
    python_requires=">=3.7",
    install_requires=[
        # dependencies for the vendored storage blob
        "azure-core<2.0.0,>=1.20.1",
        "msrest>=0.6.18",
        "cryptography>=2.1.4",
        # end of dependencies for the vendored storage blob
        'azure-eventhub<6.0.0,>=5.0.0',
        'aiohttp<4.0,>=3.0',
    ]
)
