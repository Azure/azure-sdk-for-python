#!/usr/bin/env python

#-------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
#--------------------------------------------------------------------------

import re
import os.path
from io import open
from setuptools import find_packages, setup  # type: ignore

# Change the PACKAGE_NAME only to change folder and different name
PACKAGE_NAME = "azure-core-tracing-opentelemetry"
PACKAGE_PPRINT_NAME = "Azure Core OpenTelemetry plugin"

package_folder_path = "azure/core/tracing/ext/opentelemetry_span"

# Version extraction inspired from 'requests'
with open(os.path.join(package_folder_path, '_version.py'), 'r') as fd:
    version = re.search(r'^VERSION\s*=\s*[\'"]([^\'"]*)[\'"]',  # type: ignore
                        fd.read(), re.MULTILINE).group(1)

if not version:
    raise RuntimeError('Cannot find version information')

with open('README.md', encoding='utf-8') as f:
    readme = f.read()
with open('CHANGELOG.md', encoding='utf-8') as f:
    changelog = f.read()

setup(
    name=PACKAGE_NAME,
    version=version,
    description='Microsoft Azure {} Library for Python'.format(PACKAGE_PPRINT_NAME),
    long_description=readme + '\n\n' + changelog,
    long_description_content_type='text/markdown',
    license='MIT License',
    author='Microsoft Corporation',
    author_email='azpysdkhelp@microsoft.com',
    url='https://github.com/Azure/azure-sdk-for-python/tree/master/sdk/core/azure-core-tracing-opentelemetry',
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
        'Programming Language :: Python :: 3.9',
        'License :: OSI Approved :: MIT License',
    ],
    zip_safe=False,
    packages=[
        'azure.core.tracing.ext.opentelemetry_span',
    ],
    python_requires=">=3.5.0",
    install_requires=[
        'opentelemetry-api==0.17b0',
        'azure-core<2.0.0,>=1.0.0',
    ],
    extras_require={
        ":python_version<'3.5'": ['typing'],
    }
)
