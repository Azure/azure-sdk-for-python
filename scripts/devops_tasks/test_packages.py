#!/usr/bin/env python

#-------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
#--------------------------------------------------------------------------

# Assumptions when running this script:
#  Execution of this script begins in the root directory of azure-sdk-for-python repo

# Normally, this module will be executed as referenced as part of the devops build definitions.
# An enterprising user can easily glance over this and leverage for their own purposes.

import argparse
import sys
from pathlib import Path
import os

from common_tasks import process_glob_string, run_check_call

root_dir = os.path.abspath(os.path.join(os.path.abspath(__file__), '..', '..', '..'))
dev_setup_script_location = os.path.join(root_dir, 'scripts/dev_setup.py')

def prep_and_run_tests(targeted_packages, python_version):
    for package_path in targeted_packages:
        print('running test setup for {}'.format(os.path.basename(package_path)))
        run_check_call([python_version, dev_setup_script_location, '-g', os.path.basename(package_path)], root_dir)

    print('Setup complete. Running pytest for {}'.format(targeted_packages))
    command_array = [python_version, '-m', 'pytest']
    command_array.extend(targeted_packages)
    run_check_call(command_array, root_dir)

    for package_path in targeted_packages:
        print('Checking setup.py for {}'.format(os.path.join(package_path, 'setup.py')))
        run_check_call([python_version, 'setup.py', 'check', '-r', '-s'], package_path)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description = 'Install Dependencies, Install Packages, Test Azure Packages, Called from DevOps YAML Pipeline')
    parser.add_argument(
        '-g', 
        '--glob-string', 
        dest = 'glob_string', 
        help = ('A comma separated list of glob strings that will target the top level directories that contain packages. '
                'Examples: All = "azure-*", Single = "azure-keyvault", Targeted Multiple = "azure-keyvault,azure-mgmt-resource"'),
        required = True)

    parser.add_argument(
        '-p',
        '--python-version',
        dest = 'python_version',
        default = 'python',
        help = 'The name of the python that should run the build. This is for usage in special cases like in /.azure-pipelines/specialcase.test.yml. Defaults to "python"')

    args = parser.parse_args()
    targeted_packages = process_glob_string(args.glob_string, root_dir)

    prep_and_run_tests(targeted_packages, args.python_version)
