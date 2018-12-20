#!/usr/bin/env python

#-------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
#--------------------------------------------------------------------------

# Assumptions when running this script:
#  You are running in the root directory of azure-sdk-for-python repo clone

# Normally, this module will be executed as referenced as part of the devops build definitions.
# An enterprising user can easily glance over this and leverage for their own purposes,.

import argparse
import os
import sys
import glob
from pathlib import Path
from subprocess import check_call, CalledProcessError


DEFAULT_TARGETED_PROJECTS = ['azure-keyvault']

root_dir = os.path.abspath(os.path.join(os.path.abspath(__file__), '..', '..', '..'))
build_packing_script_location = os.path.join(root_dir, 'build_package.py')

def run_check_call(command_array, working_directory):
    print('Command Array: {0}, Target Working Directory: {1}', command_array, working_directory)
    try:
        check_call(command_array, cwd = working_directory)
    except CalledProcessError as err:
        print(err, file = sys.stderr)
        sys.exit(1)

def process_glob_string(glob_string):
    individual_globs = glob_string.split(',')
    collected_top_level_directories = []

    for glob_string in individual_globs:
        globbed = glob.glob(os.path.join(root_dir, glob_string, 'setup.py'))
        collected_top_level_directories.extend([os.path.dirname(p) for p in globbed])

    # dedup, in case we have double coverage from the glob strings. Example: "azure-mgmt-keyvault,azure-mgmt-*"
    return list(set(collected_top_level_directories))

def devops_build_packages(glob_string, python_version, distribution_directory):
    targeted_packages = process_glob_string(glob_string)

    # run the build and distribution
    for package_name in targeted_packages:
        print(package_name)
        run_check_call([python_version, build_packing_script_location, '--dest', distribution_directory, package_name], root_dir)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description = 'Build Azure Packages, Called from DevOps YAML Pipeline')
    parser.add_argument(
        '-g', 
        '--glob-string', 
        dest = 'glob_string', 
        default = 'azure-keyvault',
        help = 'A comma separated list of glob strings that will target the top level directories that contain packages. Examples: All == "azure-*", Single = "azure-keyvault"')

    parser.add_argument(
        '-p',
        '--python-version',
        dest = 'python_version',
        default = 'python',
        help = 'The name of the python that should run the build. This is for usage in special cases like in /.azure-pipelines/specialcase.test.yml. Defaults to "python"')

    parser.add_argument(
        '-d',
        '--distribution-directory',
        dest = 'distribution_directory',
        default = './dist',
        help = 'The name of the python that should run the build. This is for usage in special cases like in /.azure-pipelines/specialcase.test.yml. Defaults to "python"')

    args = parser.parse_args()

    devops_build_packages(args.glob_string, args.python_version, args.distribution_directory)
