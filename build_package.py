#!/usr/bin/env python

#-------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
#--------------------------------------------------------------------------

import argparse
import os
import sys
import re
from pathlib import Path
from subprocess import check_call

try:
    from packaging.version import parse as Version, InvalidVersion
except ImportError: # Should not happen, but at worst in most case this is the same
    from pip._vendor.packaging.version import parse as Version, InvalidVersion

DEFAULT_DEST_FOLDER = "./dist"

def create_package(name, dest_folder=DEFAULT_DEST_FOLDER):
    absdirpath = os.path.abspath(name)
    check_call(['python', 'setup.py', 'bdist_wheel', '-d', dest_folder], cwd=absdirpath)
    check_call(['python', 'setup.py', "sdist", "--format", "zip", '-d', dest_folder], cwd=absdirpath)

def travis_build_package():
    """Assumed called on Travis, to prepare a package to be deployed

    This method prints on stdout for Travis.
    Return is obj to pass to sys.exit() directly
    """
    travis_tag = os.environ.get('TRAVIS_TAG')
    if not travis_tag:
        print("TRAVIS_TAG environment variable is not present")
        return "TRAVIS_TAG environment variable is not present"

    try:
        name, version = travis_tag.split("_")
    except ValueError:
        print("TRAVIS_TAG is not '<package_name>_<version>' (tag is: {})".format(travis_tag))
        return "TRAVIS_TAG is not '<package_name>_<version>' (tag is: {})".format(travis_tag)

    try:
        version = Version(version)
    except InvalidVersion:
        print("Version must be a valid PEP440 version (version is: {})".format(version))
        return "Version must be a valid PEP440 version (version is: {})".format(version)

    abs_dist_path = Path(os.environ['TRAVIS_BUILD_DIR'], 'dist')
    create_package(name, str(abs_dist_path))

    print("Produced:\n{}".format(list(abs_dist_path.glob('*'))))

    pattern = "*{}*".format(version)
    packages = list(abs_dist_path.glob(pattern))
    if not packages:
        return "Package version does not match tag {}, abort".format(version)
    pypi_server = os.environ.get("PYPI_SERVER", "default PyPI server")
    print("Package created as expected and will be pushed to {}".format(pypi_server))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Build Azure package.')
    parser.add_argument('name', help='The package name')
    parser.add_argument('--dest', '-d', default=DEFAULT_DEST_FOLDER,
                        help='Destination folder. Relative to the package dir. [default: %(default)s]')

    args = parser.parse_args()
    create_package(args.name, args.dest)
