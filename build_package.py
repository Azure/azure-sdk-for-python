#!/usr/bin/env python

#-------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
#--------------------------------------------------------------------------

import argparse
import os
import glob
import sys

from subprocess import check_call

DEFAULT_DEST_FOLDER = "./dist"

def create_package(name, dest_folder=DEFAULT_DEST_FOLDER):
    # a package will exist in either one, or the other folder. this is why we can resolve both at the same time.
    absdirs = [os.path.dirname(package) for package in (glob.glob('{}/setup.py'.format(name)) + glob.glob('sdk/*/{}/setup.py'.format(name)))]

    absdirpath = os.path.abspath(absdirs[0])
    check_call([sys.executable, 'setup.py', 'bdist_wheel', '-d', dest_folder], cwd=absdirpath)
    check_call([sys.executable, 'setup.py', "sdist", "--format", "zip", '-d', dest_folder], cwd=absdirpath)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Build Azure package.')
    parser.add_argument('name', help='The package name')
    parser.add_argument('--dest', '-d', default=DEFAULT_DEST_FOLDER,
                        help='Destination folder. Relative to the package dir. [default: %(default)s]')

    args = parser.parse_args()
    create_package(args.name, args.dest)
