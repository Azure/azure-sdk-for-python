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
import sys

setup(
    name='azure-storage',
    version='0.20.0',
    description='Microsoft Azure Storage Client Library for Python',
    long_description=open('README.rst', 'r').read(),
    license='Apache License 2.0',
    author='Microsoft Corporation',
    author_email='ptvshelp@microsoft.com',
    url='https://github.com/Azure/azure-sdk-for-python',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'License :: OSI Approved :: Apache Software License',
    ],
    zip_safe=False,
    packages=[
        'azure',
        'azure.storage',
        'azure.storage._http',
        'azure.storage.blob',
        'azure.storage.files',
        'azure.storage.queue',
        'azure.storage.table',
    ],
    install_requires=[
        'azure-nspkg==1.0.0',
        'azure-common==0.20.0',
        'python-dateutil',
        'requests',
    ] + (['futures'] if sys.version_info < (3,0) else []),
)
