#!/usr/bin/env python

#-------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
#--------------------------------------------------------------------------

from setuptools import setup


setup(
    name='azure',
    version='3.0.0',
    description='Microsoft Azure Client Libraries for Python',
    long_description=open('README.rst', 'r').read(),
    license='MIT License',
    author='Microsoft Corporation',
    author_email='azpysdkhelp@microsoft.com',
    url='https://github.com/Azure/azure-sdk-for-python',
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'License :: OSI Approved :: MIT License',
    ],
    zip_safe=False,
    install_requires=[
        'azure-mgmt~=2.0',
        'azure-batch~=4.0',
        'azure-cosmosdb-table~=1.0',
        'azure-datalake-store~=0.0.18',
        'azure-eventgrid~=0.1.0',
        'azure-graphrbac~=0.40.0',
        'azure-keyvault~=0.3.7',
        'azure-servicebus~=0.21.1',
        'azure-servicefabric~=6.1.2.9',
        'azure-servicemanagement-legacy~=0.20.6',
        'azure-storage-blob~=1.1',
        'azure-storage-queue~=1.1',
        'azure-storage-file~=1.1',
    ],
)
