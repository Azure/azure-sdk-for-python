#!/usr/bin/env python

#-------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
#--------------------------------------------------------------------------

from io import open
from setuptools import setup, find_packages


PACKAGE_NAME = "azure-ai-translation-text"
version = "1.0.0b1"

with open('README.md', encoding='utf-8') as f:
    readme = f.read()
with open('CHANGELOG.md', encoding='utf-8') as f:
    changelog = f.read()

setup(
    name=PACKAGE_NAME,
    version=version,
    description="azure-ai-translation-text",
    author_email='azpysdkhelp@microsoft.com',
    url='https://github.com/Azure/azure-sdk-for-python',
    long_description=readme + '\n\n' + changelog,
    long_description_content_type='text/markdown'
    license='MIT License',
    author='Microsoft Corporation',
    keywords="azure, azure sdk",
    classifiers=[
        'Development Status :: 4 - Beta',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3 :: Only',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
        'License :: OSI Approved :: MIT License',
    ],
    zip_safe=False,
    packages=find_packages(exclude=[
        # Exclude packages that will be covered by PEP420 or nspkg
        'azure',
        'azure.ai',
        'azure.ai.translation'
    ]),
    include_package_data=True,
    package_data={
        'pytyped': ['py.typed'],
    },
    install_requires=[
        "msrest>=0.7.1",
        "azure-common~=1.1",
        "azure-mgmt-core>=1.3.2,<2.0.0",
        "typing-extensions>=4.3.0; python_version<'3.8.0'",
    ],
    python_requires=">=3.7"
)
