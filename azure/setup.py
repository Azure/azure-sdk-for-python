#!/usr/bin/env python

#-------------------------------------------------------------------------
# Copyright (c) Microsoft.  All rights reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#   http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
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
    version='2.0.0rc3',
    description='Microsoft Azure Client Libraries for Python',
    long_description=open('README.rst', 'r').read(),
    license='Apache License 2.0',
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
        'License :: OSI Approved :: Apache Software License',
    ],
    zip_safe=False,
    install_requires=[
        'azure-mgmt==0.30.0rc3',
        'azure-batch==0.30.0rc3',
        'azure-graphrbac==0.30.0rc3',
        'azure-servicebus==0.20.1',
        'azure-storage==0.31.0',
        'azure-servicemanagement-legacy==0.20.3',
    ],
)
