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

from distutils.core import setup

# To build:
# python setup.py sdist
#
# To install:
# python setup.py install
#
# To register (only needed once):
# python setup.py register
#
# To upload:
# python setup.py sdist upload

setup(name='azure',
      version='0.7.1',
      description='Windows Azure client APIs',
      license='Apache License 2.0',
      author='Microsoft Corporation',
      author_email='ptvshelp@microsoft.com',
      url='https://github.com/WindowsAzure/azure-sdk-for-python',
      classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.7',
        'License :: OSI Approved :: Apache Software License'],
      packages=['azure',
                'azure.http',
                'azure.servicebus',
                'azure.storage',
                'azure.servicemanagement']
     )
