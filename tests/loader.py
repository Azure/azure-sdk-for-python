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

import copy
import os.path
import sys

class _FakeParentPackageModuleFinder:
    '''
    Allows loading of modules from a location where some of the parent
    package folders don't have an __init__.py.

    Example of loading 'azure.storage' from this folder structure:
        azure-storage
          azure
            <no __init__.py here>
            storage
              __init__.py

    This finder will add the 'azure-storage/azure' folder to the search path,
    and import 'storage' rather than 'azure.storage', then makes it available
    as 'azure.storage'.
    '''

    def __init__(self, base_path, module_locations, parent_package_name):
        '''
        base_path:
            Absolute base path that is used in conjunction with the relative
            paths in module_locations.
        module_locations:
            Dict of (full module name, list of folder names relative to base path).
        parent_package_name:
            Name of parent package to 'skip', because it doesn't have an
            __init__.py file.
        '''

        self.base_path = base_path
        self.module_locations = module_locations
        self.parent_package_name = parent_package_name

    def find_module(self, fullname, path=None):
        if fullname in self.module_locations:
            return self
        return None

    def load_module(self, fullname):
        folders = self.module_locations.get(fullname)
        if folders:
            saved_sys_path = sys.path
            try:
                sys.path = copy.copy(sys.path)
                sys.path.append(os.path.join(self.base_path, *folders))
                relative_name = fullname[len(self.parent_package_name + '.'):]
                __import__(relative_name)
                sys.modules[fullname] = sys.modules[relative_name]
            finally:
                sys.path = saved_sys_path

            return sys.modules[fullname]
        raise ImportError('Could not import {}'.format(fullname))
