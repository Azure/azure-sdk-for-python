#!/usr/bin/env python

# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

# Normally, this module will be executed as referenced as part of the devops build definitions.
# An enterprising user can easily glance over this and leverage for their own purposes.

import argparse
import sys
from pathlib import Path
import os

from common_tasks import process_glob_string, run_check_call

root_dir = os.path.abspath(os.path.join(os.path.abspath(__file__), '..', '..', '..'))
dev_setup_script_location = os.path.join(root_dir, 'scripts/dev_setup.py')

# a return code of 5 from pytest == no tests run
# evaluating whether we want this or not.
ALLOWED_RETURN_CODES = []
GUARANTEED_TEST_CASE = [ os.path.join(root_dir, 'scripts/devops_tasks/faketests') ]

def prep_and_run_tests(targeted_packages, python_version, test_res):
    print('running test setup for {}'.format(targeted_packages))
    run_check_call([python_version, dev_setup_script_location, '-p', ','.join([os.path.basename(p) for p in targeted_packages])], root_dir)

    print('Setup complete. Running pytest for {}'.format(targeted_packages))
    command_array = [python_version, '-m', 'pytest']
    command_array.extend(test_res)
    command_array.extend(targeted_packages + GUARANTEED_TEST_CASE)
    run_check_call(command_array, root_dir, ALLOWED_RETURN_CODES)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description = 'Install Dependencies, Install Packages, Test Azure Packages, Called from DevOps YAML Pipeline')
    parser.add_argument(
        '-p',
        '--python-version',
        dest = 'python_version',
        default = 'python',
        help = 'The name of the python that should run the build. This is for usage in special cases like the "Special_Python_Distro_Tests" Job in /.azure-pipelines/client.yml. Defaults to "python"')

    parser.add_argument(
        'glob_string',
        nargs='?',
        help = ('A comma separated list of glob strings that will target the top level directories that contain packages.'
                'Examples: All = "azure-*", Single = "azure-keyvault", Targeted Multiple = "azure-keyvault,azure-mgmt-resource"'))

    parser.add_argument(
        '--junitxml',
        dest = 'test_results',
        help = ('The folder where the test results will be stored in xml format.'
                'Example: --junitxml="junit/test-results.xml"'))

    parser.add_argument(
        '--disablecov',
        help = ('Flag that disables code coverage.'),
        action='store_true')

    args = parser.parse_args()
    targeted_packages = process_glob_string(args.glob_string, root_dir)
    test_results_arg = []
    if args.test_results:
        test_results_arg.extend(['--junitxml', args.test_results])

    if args.disablecov:
        test_results_arg.append('--no-cov')

    prep_and_run_tests(targeted_packages, args.python_version, test_results_arg)
