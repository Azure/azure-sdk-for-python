#!/usr/bin/env python

#-------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
#--------------------------------------------------------------------------

from __future__ import print_function
import os.path
import glob
import copy
import sys
import runpy

root_folder = os.path.abspath(os.path.dirname(__file__))

packages = [os.path.dirname(p) for p in glob.glob('azure*/setup.py')]

# "install" is used by ReadTheDocs, do not install "nspkg"

# Extract nspkg and sort nspkg by number of "-"
nspkg_packages = [p for p in packages if "nspkg" in p]
nspkg_packages.sort(key = lambda x: len([c for c in x if c == '-']))

# Consider "azure-common" as a power nspkg : has to be installed first
nspkg_packages.append("azure-common")

# Manually push meta-packages at the end, in reverse dependency order
meta_package = ['azure-mgmt', 'azure']

# So content packages are:
content_package = [p for p in packages if p not in meta_package+nspkg_packages]
content_package.insert(0, "azure-common")

# Package final:
if "install" in sys.argv:
    packages = content_package
else:
    packages = nspkg_packages + content_package + meta_package

for pkg_name in packages:
    pkg_setup_folder = os.path.join(root_folder, pkg_name)
    pkg_setup_path = os.path.join(pkg_setup_folder, 'setup.py')

    try:
        saved_dir = os.getcwd()
        saved_syspath = sys.path

        os.chdir(pkg_setup_folder)
        sys.path = [pkg_setup_folder] + copy.copy(saved_syspath)

        print("Start ", pkg_setup_path)
        result = runpy.run_path(pkg_setup_path)
    except Exception as e:
        print(e, file=sys.stderr)
    finally:
        os.chdir(saved_dir)
        sys.path = saved_syspath
