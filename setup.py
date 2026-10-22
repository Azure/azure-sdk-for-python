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

# pull in any packages that exist in the root directory
packages = {('.', os.path.dirname(p)) for p in glob.glob('azure*/setup.py')}
# Handle the SDK folder as well
packages.update({tuple(os.path.dirname(f).rsplit(os.sep, 1)) for f in glob.glob('sdk/*/azure*/setup.py')})
# [(base_folder, package_name), ...] to {package_name: base_folder, ...}
packages = {package_name: base_folder for (base_folder, package_name) in packages}

# Extract nspkg and sort nspkg by number of "-"
nspkg_packages = [p for p in packages.keys() if "nspkg" in p]
nspkg_packages.sort(key = lambda x: len([c for c in x if c == '-']))

# Meta-packages to ignore
meta_package = ['azure-keyvault', 'azure-mgmt', 'azure', 'azure-storage']

# content packages are packages that are not meta nor nspkg
content_package = sorted([p for p in packages.keys() if p not in meta_package+nspkg_packages])

# Move azure-common at the beginning, it's important this goes first
content_package.remove("azure-common")
content_package.insert(0, "azure-common")

# Package final:
if "install" in sys.argv:
    packages_for_installation = content_package
else:
    packages_for_installation = nspkg_packages + content_package

for pkg_name in packages_for_installation:
    pkg_setup_folder = os.path.join(root_folder, packages[pkg_name], pkg_name)
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
