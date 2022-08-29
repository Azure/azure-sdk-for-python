#!/usr/bin/env python

# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------


import os
import re

from setuptools import setup, find_packages


# Change the PACKAGE_NAME only to change folder and different name
PACKAGE_NAME = "azure-storage-blob-changefeed"
NAMESPACE_NAME = "azure.storage.blob.changefeed"
PACKAGE_PPRINT_NAME = "Azure Storage Blob ChangeFeed"

# a-b-c => a/b/c
package_folder_path = NAMESPACE_NAME.replace('.', '/')

# azure-storage v0.36.0 and prior are not compatible with this package
try:
    import azure.storage

    try:
        ver = azure.storage.__version__
        raise Exception(
            'This package is incompatible with azure-storage=={}. '.format(ver) +
            ' Uninstall it with "pip uninstall azure-storage".'
        )
    except AttributeError:
        pass
except ImportError:
    pass

# Version extraction inspired from 'requests'
with open(os.path.join(package_folder_path, '_version.py'), 'r') as fd:
    version = re.search(r'^VERSION\s*=\s*[\'"]([^\'"]*)[\'"]',
                        fd.read(), re.MULTILINE).group(1)

if not version:
    raise RuntimeError('Cannot find version information')

setup(
    name=PACKAGE_NAME,
    version=version,
    description='Microsoft {} Client Library for Python'.format(PACKAGE_PPRINT_NAME),
    long_description=open('README.md', 'r').read(),
    long_description_content_type='text/markdown',
    license='MIT License',
    author='Microsoft Corporation',
    author_email='ascl@microsoft.com',
    url='https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/storage/azure-storage-blob-changefeed',
    classifiers=[
        "Development Status :: 4 - Beta",
        'Programming Language :: Python',
        "Programming Language :: Python :: 3 :: Only",
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'License :: OSI Approved :: MIT License',
    ],
    zip_safe=False,
    packages=[
        'azure.storage.blob.changefeed',
    ],
    include_package_data=True,
    package_data={
        'pytyped': ['py.typed'],
    },
    python_requires=">=3.7",
    install_requires=[
        "azure-storage-blob>=12.5.0,<13.0.0"
    ],
)
