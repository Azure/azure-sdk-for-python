#!/usr/bin/env python

# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from __future__ import print_function

import sys
import glob
import os
from subprocess import check_call, CalledProcessError

root_dir = os.path.abspath(os.path.join(os.path.abspath(__file__), '..', '..'))


def pip_command(command):
    try:
        print('Executing: ' + command)
        check_call([sys.executable, '-m', 'pip'] + command.split(), cwd=root_dir)
        print()
    except CalledProcessError as err:
        print(err, file=sys.stderr)
        sys.exit(1)

packages = [os.path.dirname(p) for p in glob.glob('azure*/setup.py')]

# Extract nspkg and sort nspkg by number of "-"
nspkg_packages = [p for p in packages if "nspkg" in p]
nspkg_packages.sort(key = lambda x: len([c for c in x if c == '-']))

# Consider "azure-common" as a power nspkg : has to be installed after nspkg
nspkg_packages.append("azure-common")

# Manually push meta-packages at the end, in reverse dependency order
meta_packages = ['azure-mgmt', 'azure']

content_packages = [p for p in packages if p not in nspkg_packages+meta_packages]

print('Running dev setup...')
print('Root directory \'{}\'\n'.format(root_dir))

# install packages
for package_list in [nspkg_packages, content_packages]:
    for package_name in package_list:
        pip_command('install -e {}'.format(package_name))

# Ensure that the site package's azure/__init__.py has the old style namespace
# package declaration by installing the old namespace package
pip_command('install --force-reinstall azure-mgmt-nspkg==1.0.0')
pip_command('install --force-reinstall azure-nspkg==1.0.0')
print('Finished dev setup.')
