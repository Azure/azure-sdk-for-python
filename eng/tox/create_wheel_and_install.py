from __future__ import print_function
from subprocess import check_call
import argparse
import os

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description = 'Build a package directory into a wheel. Then install it.')
    parser.add_argument(
        '-d',
        '--distribution-directory',
        dest='distribution_directory',
        help='The path to the distribution directory. Should be passed $(Build.ArtifactStagingDirectory) from the devops yaml definition.',
        required=True)

    parser.add_argument(
        '-p',
        '--path-to-setup',
        dest='target_setup',
        help='The path to the setup.py (not including the file) for the package we want to package into a wheel and install.',
        required=True
        )

    args = parser.parse_args()

    print('Build')

    check_call(['python', os.path.join(args.target_setup, 'setup.py'), 'bdist_wheel', '--universal', '-d', args.distribution_directory])

    discovered_wheels = [f for f in os.listdir(args.distribution_directory) if os.path.isfile(os.path.join(args.distribution_directory, f))]

    for wheel in discovered_wheels:
        print('Installing {w}.'.format(w=wheel))
        check_call(['pip', 'install', os.path.join(args.distribution_directory, wheel)])