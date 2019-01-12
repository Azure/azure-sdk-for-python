#!/usr/bin/env python

#-------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
#--------------------------------------------------------------------------

# Assumptions when running this script:
#  You are running in the root directory of azure-sdk-for-python repo

# Normally, this module will be executed as referenced as part of the devops build definitions.
# An enterprising user can easily glance over this and leverage for their own purposes.

import argparse
import sys
from pathlib import Path

from devops_common_tasks import *

root_dir = os.path.abspath(os.path.join(os.path.abspath(__file__), '..', '..', '..'))
build_packing_script_location = os.path.join(root_dir, 'build_package.py')

def build_packages(targeted_packages, distribution_directory):
    # run the build and distribution
    for package_name in targeted_packages:
        print(package_name)
        print('Generating Package Using Python {}'.format(sys.version))
        run_check_call(['python', build_packing_script_location, '--dest', distribution_directory, package_name], root_dir)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description = 'Build Azure Packages, Called from DevOps YAML Pipeline')
    parser.add_argument(
        '-g', 
        '--glob-string', 
        dest = 'glob_string', 
        default = 'azure-keyvault',
        help = 'A comma separated list of glob strings that will target the top level directories that contain packages. Examples: All == "azure-*", Single = "azure-keyvault"')

    parser.add_argument(
        '-d',
        '--distribution-directory',
        dest = 'distribution_directory',
        default = './dist',
        help = 'The path to the distribution directory. Should be passed $(Build.ArtifactStagingDirectory) from the devops yaml definition.')

    args = parser.parse_args()

    targeted_packages = process_glob_string(args.glob_string, root_dir)
    build_packages(targeted_packages, args.distribution_directory)
