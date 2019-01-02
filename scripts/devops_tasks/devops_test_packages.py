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
dev_setup_script_location = os.path.join(root_dir, 'scripts/dev_setup.py')

def devops_run_tests(targeted_packages, python_version):
#    for package_name in targeted_packages:
#        print('running test setup for '.format(package_name))
#        run_check_call([python_version, dev_setup_script_location, '-g', package_name], root_dir)

    print('Setup complete. Running pytest for {}'.format(targeted_packages))

    command_array = ['pytest']
    command_array.extend(targeted_packages)
    
    run_check_call(command_array, root_dir)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description = 'Build Azure Packages, Called from DevOps YAML Pipeline')
    parser.add_argument(
        '-g', 
        '--glob-string', 
        dest = 'glob_string', 
        default = 'azure-keyvault',
        help = 'A comma separated list of glob strings that will target the top level directories that contain packages. Examples: All = "azure-*", Single = "azure-keyvault", Targeted Multiple = "azure-keyvault,azure-mgmt-resource"')

    parser.add_argument(
        '-p',
        '--python-version',
        dest = 'python_version',
        default = 'python',
        help = 'The name of the python that should run the build. This is for usage in special cases like in /.azure-pipelines/specialcase.test.yml. Defaults to "python"')

    args = parser.parse_args()
    targeted_packages = process_glob_string(args.glob_string, root_dir)

    devops_run_tests(targeted_packages, args.python_version)
