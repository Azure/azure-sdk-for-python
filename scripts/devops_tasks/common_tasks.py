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

DEFAULT_BUILD_PACKAGES = ['azure-keyvault', 'azure-servicebus']

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
    return list(set(collected_top_level_directories))

def run_check_call(command_array, working_directory, acceptable_return_codes = []):
    print('Command Array: {0}, Target Working Directory: {1}'.format(command_array, working_directory))
    try:
        check_call(command_array, cwd = working_directory)
    except CalledProcessError as err:
        if err.returncode not in acceptable_return_codes:
            print(err) #, file = sys.stderr
            sys.exit(1)
