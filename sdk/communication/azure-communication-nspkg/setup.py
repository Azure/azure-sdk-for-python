#!/usr/bin/env python

# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

from setuptools import setup

setup(
    name='azure-communication-nspkg',
    version='0.0.0b1',
    description='Microsoft Azure Communication Namespace Package [Internal]',
    long_description=open('README.md', 'r').read(),
    license='MIT License',
    author='Microsoft Corporation',
    author_email='azurepysdk@microsoft.com',
    url='https://github.com/Azure/azure-sdk-for-python/',
    classifiers=[
        'Development Status :: 3 - Alpha',

        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'License :: OSI Approved :: MIT License',
    ],
    zip_safe=False,
    packages=[
        'azure.communication',
    ],
    install_requires=[
        'azure-nspkg>=2.0.0',
    ]
)