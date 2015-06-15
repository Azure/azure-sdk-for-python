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

#TODO: remove this and loader.py when we are sure we don't need it

#import os.path
#import sys

#from .loader import _FakeParentPackageModuleFinder

#base_path = os.path.dirname(__file__)

#sys.meta_path.extend(
#    [
#        _FakeParentPackageModuleFinder(
#            base_path,
#            module_locations={
#                'azure.common':
#                    ['..', 'azure-common', 'azure'],
#                'azure.mgmt':
#                    ['..', 'azure-mgmt-_core', 'azure'],
#                'azure.storage':
#                    ['..', 'azure-storage', 'azure'],
#                'azure.servicebus':
#                    ['..', 'azure-servicebus', 'azure'],
#                'azure.servicemanagement':
#                    ['..', 'azure-servicemanagement-legacy', 'azure'],
#            },
#            parent_package_name='azure',
#        ),
#        _FakeParentPackageModuleFinder(
#            base_path,
#            module_locations={
#                'azure.mgmt.storage':
#                    ['..', 'azure-mgmt-storage', 'azure', 'mgmt'],
#            },
#            parent_package_name='azure.mgmt',
#        ),
#    ]
#)
