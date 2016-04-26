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

import os
import os.path
import copy
import sys
import runpy

root_folder = os.path.abspath(os.path.dirname(__file__))

# order is significant, start from the leaf nodes
packages = [
    'azure-nspkg',
    'azure-common',
    'azure-mgmt-nspkg',
    'azure-mgmt-authorization',
    'azure-mgmt-batch',
    'azure-mgmt-cdn',
    'azure-mgmt-compute',
    'azure-mgmt-logic',
    'azure-mgmt-graphrbac',
    'azure-mgmt-network',
    'azure-mgmt-notificationhubs',
    'azure-mgmt-redis',
    'azure-mgmt-resource',
    'azure-mgmt-scheduler',
    'azure-mgmt-storage',
    'azure-mgmt-web',
    'azure-graphrbac',
    'azure-batch',
    'azure-servicebus',
    'azure-servicemanagement-legacy',
]

for pkg_name in packages:
    pkg_setup_folder = os.path.join(root_folder, pkg_name)
    pkg_setup_path = os.path.join(pkg_setup_folder, 'setup.py')

    try:
        saved_dir = os.getcwd()
        saved_syspath = sys.path

        os.chdir(pkg_setup_folder)
        sys.path = [pkg_setup_folder] + copy.copy(saved_syspath)

        result = runpy.run_path(pkg_setup_path)
    except Exception as e:
        print(e)
    finally:
        os.chdir(saved_dir)
        sys.path = saved_syspath
