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

MANAGEMENT_PACKAGE_IDENTIFIERS = ['mgmt', 'azure-cognitiveservices-personalizer', 'azure-servicefabric']

def prep_and_run_tests(targeted_packages, python_version, test_res):
    print('running test setup for {}'.format(targeted_packages))
    run_check_call([python_version, dev_setup_script_location, '-p', ','.join([os.path.basename(p) for p in targeted_packages])], root_dir)

    # if we are targeting only packages that are management plane, it is a possibility 
    # that no tests running is an acceptable situation
    # we explicitly handle this here.
    if all(map(lambda x : any([pkg_id in x for pkg_id in MANAGEMENT_PACKAGE_IDENTIFIERS]), targeted_packages)):
        ALLOWED_RETURN_CODES.append(5)

    print('Setup complete. Running pytest for {}'.format(targeted_packages))
    command_array = [python_version, '-m', 'pytest']
    command_array.extend(test_res)
    command_array.extend(targeted_packages)
    run_check_call(command_array, root_dir, ALLOWED_RETURN_CODES, True)

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
        dest='test_results',
        help=('The folder where the test results will be stored in xml format.'
              'Example: --junitxml="junit/test-results.xml"'))

    parser.add_argument(
        '--mark_arg',
        dest='mark_arg',
        help=('The complete argument for `pytest -m "<input>"`. This can be used to exclude or include specific pytest markers.'
              '--mark_arg="not cosmosEmulator"'))

    parser.add_argument(
        '--disablecov',
        help = ('Flag that disables code coverage.'),
        action='store_true')

    parser.add_argument(
        '--service',
        help=('Name of service directory (under sdk/) to test.'
              'Example: --service applicationinsights'))

    args = parser.parse_args()

    # We need to support both CI builds of everything and individual service
    # folders. This logic allows us to do both.
    if args.service:
        service_dir = os.path.join('sdk', args.service)
        target_dir = os.path.join(root_dir, service_dir)
    else:
        target_dir = root_dir

    targeted_packages = process_glob_string(args.glob_string, target_dir)
    test_results_arg = []
    if args.test_results:
        test_results_arg.extend(['--junitxml', args.test_results])

    if args.disablecov:
        test_results_arg.append('--no-cov')

    if args.mark_arg:
        test_results_arg.extend(['-m', '"{}"'.format(args.mark_arg)])

    prep_and_run_tests(targeted_packages, args.python_version, test_results_arg)
