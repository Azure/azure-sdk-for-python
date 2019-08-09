#!/usr/bin/env python

# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

# Below are common methods for the devops build steps. This is the common location that will be updated with
# package targeting during release.

import glob
from pathlib import Path
from subprocess import check_call, CalledProcessError
import os
import sys

def cleanup_folder(target_folder):
    for file in os.listdir(target_folder):
        file_path = os.path.join(target_folder, file)
        try:
            if os.path.isfile(file_path):
                os.remove(file_path)
        except Exception as e:
            print(e)

DEFAULT_BUILD_PACKAGES = ['azure-keyvault', 'azure-servicebus']
OMITTED_CI_PACKAGES = ['azure-mgmt-documentdb', 'azure-servicemanagement-legacy']

# this function is where a glob string gets translated to a list of packages
# It is called by both BUILD (package) and TEST. In the future, this function will be the central location
# for handling targeting of release packages
def process_glob_string(glob_string, target_root_dir):
    if glob_string:
        individual_globs = glob_string.split(',')
    else:
        individual_globs = DEFAULT_BUILD_PACKAGES
    collected_top_level_directories = []

    for glob_string in individual_globs:
        globbed = glob.glob(os.path.join(target_root_dir, glob_string, 'setup.py')) + glob.glob(os.path.join(target_root_dir, "sdk/*/", glob_string, 'setup.py'))
        collected_top_level_directories.extend([os.path.dirname(p) for p in globbed])

    # dedup, in case we have double coverage from the glob strings. Example: "azure-mgmt-keyvault,azure-mgmt-*"
    collected_directories = list(set(collected_top_level_directories))

    # if we have individually queued this specific package, it's obvious that we want to build it specifically
    # in this case, do not honor the omission list
    if len(collected_directories) == 1:
        return collected_directories
    # however, if there are multiple packages being built, we should honor the omission list and NOT build the omitted
    # packages
    else:
        return remove_omitted_packages(collected_directories)

def remove_omitted_packages(collected_directories):
    return [package_dir for package_dir in collected_directories if
            os.path.basename(package_dir) not in OMITTED_CI_PACKAGES]


def run_check_call(command_array, working_directory, acceptable_return_codes = [], run_as_shell = False):
    try:
        if run_as_shell:
            print('Command Array: {0}, Target Working Directory: {1}'.format(' '.join(command_array), working_directory))
            check_call(' '.join(command_array), cwd = working_directory, shell = True)
        else:
            print('Command Array: {0}, Target Working Directory: {1}'.format(command_array, working_directory))
            check_call(command_array, cwd = working_directory)
    except CalledProcessError as err:
        if err.returncode not in acceptable_return_codes:
            print(err) #, file = sys.stderr
            sys.exit(1)
