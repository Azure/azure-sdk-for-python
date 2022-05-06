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
PACKAGE_NAME = "azure-monitor-opentelemetry-exporter"
PACKAGE_PPRINT_NAME = "Azure Monitor Opentelemetry Exporter"

# a-b-c => a/b/c
package_folder_path = PACKAGE_NAME.replace('-', '/')


# azure v0.x is not compatible with this package
# azure v0.x used to have a __version__ attribute (newer versions don't)
try:
    import azure

    try:
        ver = azure.__version__
        raise Exception(
            'This package is incompatible with azure=={}. '.format(ver) +
            'Uninstall it with "pip uninstall azure".'
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
    url='https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/monitor/azure-monitor-opentelemetry-exporter',
    classifiers=[
        "Development Status :: 4 - Beta",
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'License :: OSI Approved :: MIT License',
    ],
    zip_safe=False,
    packages=find_packages(exclude=[
        'tests',
        'samples',
        # Exclude packages that will be covered by PEP420 or nspkg
        'azure',
        'azure.monitor',
        'azure.monitor.opentelemetry'
    ]),
    python_requires=">=3.6.0",
    install_requires=[
        "azure-core<2.0.0,>=1.23.0",
        "msrest>=0.6.10",
        "opentelemetry-api<2.0.0,>=1.11.1,!=1.10a0",
        "opentelemetry-sdk<2.0.0,>=1.11.1,!=1.10a0",
    ],
)

