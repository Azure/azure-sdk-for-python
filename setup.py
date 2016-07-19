#!/usr/bin/env python

#-------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
#--------------------------------------------------------------------------

import os.path
import glob
import copy
import sys
import runpy

root_folder = os.path.abspath(os.path.dirname(__file__))

packages = [os.path.dirname(p) for p in glob.glob('azure*/setup.py')]

# order is significant for "install":
# - Install nspkg first
# - Then install content package
# - Then install meta-package

# Extract nspkg and sort nspkg by number of "-"
nspkg_packages = [p for p in packages if "nspkg" in p]
nspkg_packages.sort(key = lambda x: len([c for c in x if c == '-']))

# Manually push meta-packages at the end
meta_package = ['azure', 'azure-mgmt']

# So content packages are:
content_package = [p for p in packages if p not in meta_package+nspkg_packages]

# Package final order:
packages = nspkg_packages + content_package + meta_package

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
