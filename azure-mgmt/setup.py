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
    name='azure-mgmt',
    version='1.0.0',
    description='Microsoft Azure Resource Management Client Libraries for Python',
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
        'Programming Language :: Python :: 3.6',
        'License :: OSI Approved :: MIT License',
    ],
    zip_safe=False,
    install_requires=[
        'azure-mgmt-authorization~=0.30.0',
        'azure-mgmt-batch~=4.0.0',
        'azure-mgmt-cdn~=0.30.3',
        'azure-mgmt-cognitiveservices~=1.0.0',
        'azure-mgmt-compute~=1.0.0',
        'azure-mgmt-containerregistry~=0.2.1',
        'azure-mgmt-datalake-analytics~=0.1.4',
        'azure-mgmt-datalake-store~=0.1.4',
        'azure-mgmt-devtestlabs~=2.0.0',
        'azure-mgmt-dns~=1.0.1',
        'azure-mgmt-documentdb~=0.1.3',
        'azure-mgmt-iothub~=0.2.2',
        'azure-mgmt-keyvault~=0.31.0',
        'azure-mgmt-logic~=2.1.0',
        'azure-mgmt-monitor~=0.2.1',
        'azure-mgmt-network~=1.0.0',
        'azure-mgmt-rdbms~=0.1.0',
        'azure-mgmt-redis~=4.1.0',
        'azure-mgmt-resource~=1.1.0',
        'azure-mgmt-scheduler~=1.1.2',
        'azure-mgmt-sql~=0.5.1',
        'azure-mgmt-storage~=1.0.0',
        'azure-mgmt-trafficmanager~=0.30.0',
        'azure-mgmt-web~=0.32.0',
    ],
)
