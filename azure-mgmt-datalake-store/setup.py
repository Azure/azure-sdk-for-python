#!/usr/bin/env python

#-------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
#--------------------------------------------------------------------------

from setuptools import setup

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

setup(
    name='azure-mgmt-datalake-store',
    version='0.30.0rc4',
    description='Microsoft Azure Data Lake Store Management Client Library for Python',
    long_description=open('README.rst', 'r').read(),
    license='MIT License',
    author='Microsoft Corporation',
    author_email='ptvshelp@microsoft.com',
    url='https://github.com/Azure/azure-sdk-for-python',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'License :: OSI Approved :: MIT License',
    ],
    zip_safe=False,
    packages=[
        'azure',
        'azure.mgmt',
        'azure.mgmt.datalake',
        'azure.mgmt.datalake.store',
        'azure.mgmt.datalake.store.account',
        'azure.mgmt.datalake.store.account.models',
        'azure.mgmt.datalake.store.account.operations',
        'azure.mgmt.datalake.store.filesystem',
        'azure.mgmt.datalake.store.filesystem.models',
        'azure.mgmt.datalake.store.filesystem.operations'
    ],
    install_requires=[
        'azure-mgmt-datalake-nspkg',
        'azure-common[autorest]==1.1.4',
    ],
)
