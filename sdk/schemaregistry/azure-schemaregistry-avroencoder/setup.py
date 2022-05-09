#!/usr/bin/env python

# ------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# -------------------------------------------------------------------------

import re
import sys
import os.path
from io import open
from setuptools import find_namespace_packages, setup

# Change the PACKAGE_NAME only to change folder and different name
PACKAGE_NAME = "azure-schemaregistry-avroencoder"
PACKAGE_PPRINT_NAME = "Schema Registry Avro Encoder"

package_folder_path = "azure/schemaregistry/encoder/avroencoder"
namespace_name = "azure.schemaregistry.encoder.avroencoder"

# Version extraction inspired from 'requests'
with open(os.path.join(package_folder_path, '_version.py'), 'r') as fd:
    version = re.search(r'^VERSION\s*=\s*[\'"]([^\'"]*)[\'"]',
                        fd.read(), re.MULTILINE).group(1)

if not version:
    raise RuntimeError('Cannot find version information')

with open('README.md', encoding='utf-8') as f:
    readme = f.read()
with open('CHANGELOG.md', encoding='utf-8') as f:
    changelog = f.read()

install_packages = [
    'azure-schemaregistry>=1.0.0,<2.0.0',
    'avro>=1.11.0',
    "typing-extensions>=4.0.1",
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
    url='https://github.com/Azure/azure-sdk-for-python',
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        'Programming Language :: Python',
        'Programming Language :: Python :: 3 :: Only',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'License :: OSI Approved :: MIT License',
    ],
    python_requires=">=3.6",
    zip_safe=False,
    packages=find_namespace_packages(
        include=['azure.schemaregistry.encoder.*']  # Exclude packages that will be covered by PEP420 or nspkg
    ),
    install_requires=install_packages
)
