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
    name='azure-mgmt-datalake-analytics',
    version='0.30.0rc3',
    description='Microsoft Azure Data Lake Analytics Management Client Library for Python',
    long_description=open('README.rst', 'r').read(),
    license='Apache License 2.0',
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
        'License :: OSI Approved :: Apache Software License',
    ],
    zip_safe=False,
    packages=[
        'azure',
        'azure.mgmt',
        'azure.mgmt.datalake',
        'azure.mgmt.datalake.analytics',
        'azure.mgmt.datalake.analytics.account',
        'azure.mgmt.datalake.analytics.account.models',
        'azure.mgmt.datalake.analytics.account.operations',
        'azure.mgmt.datalake.analytics.catalog',
        'azure.mgmt.datalake.analytics.catalog.models',
        'azure.mgmt.datalake.analytics.catalog.operations',
        'azure.mgmt.datalake.analytics.job',
        'azure.mgmt.datalake.analytics.job.models',
        'azure.mgmt.datalake.analytics.job.operations'
    ],
    install_requires=[
        'azure-mgmt-datalake-nspkg',
        'azure-common[autorest]==1.1.3',
    ],
)
