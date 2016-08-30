#!/usr/bin/env python

#-------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
#--------------------------------------------------------------------------

from setuptools import setup

# Upgrading from 0.x is not supported
# azure v0.x used to have a __version__ attribute (newer versions don't)
try:
    import azure
    try:
        ver = azure.__version__
        raise Exception(
            'Upgrading from azure=={} is not supported. '.format(ver) +
            'Uninstall it with "pip uninstall azure" before installing ' +
            'this version.'
        )
    except AttributeError:
        pass
except ImportError:
    pass

setup(
    name='azure',
    version='2.0.0rc6',
    description='Microsoft Azure Client Libraries for Python',
    long_description=open('README.rst', 'r').read(),
    license='MIT License',
    author='Microsoft Corporation',
    author_email='ptvshelp@microsoft.com',
    url='https://github.com/Azure/azure-sdk-for-python',
    classifiers=[
        'Development Status :: 5 - Production/Stable',
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
    install_requires=[
        'azure-mgmt==0.30.0rc6',
        'azure-batch==1.0.0',
        'azure-servicebus==0.20.3',
        'azure-storage==0.33.0',
        'azure-servicemanagement-legacy==0.20.4',
    ],
)
