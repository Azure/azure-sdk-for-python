#!/usr/bin/env python

# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

# Below are common methods for the devops build steps. This is the common location that will be updated with
# package targeting during release.

import sys
import os
from os import path
import re
import logging
from packaging.version import parse

from datetime import date
from setup_parser import parse_setup

root_dir = path.abspath(path.join(path.abspath(__file__), "..", "..", ".."))
common_task_path = path.abspath(path.join(root_dir, "scripts", "devops_tasks"))
sys.path.append(common_task_path)
from common_tasks import process_glob_string, run_check_call

VERSION_PY = "_version.py"
# Auto generated code has version maintained in version.py. 
# We need to handle this old file name until generated code creates _version.py for all packages
OLD_VERSION_PY = "version.py"
VERSION_REGEX = r'^VERSION\s*=\s*[\'"]([^\'"]*)[\'"]'
VERSION_STRING = 'VERSION = "%s"'

DEV_STATUS_REGEX = r'(classifiers=\[(\s)*)(["\']Development Status :: .*["\'])'

logging.getLogger().setLevel(logging.INFO)

def path_excluded(path, additional_excludes):
    return any([excl in path for excl in additional_excludes]) or "tests" in path or is_metapackage(path)

# Metapackages do not have an 'azure' folder within them
def is_metapackage(package_path):
    dir_path = package_path if path.isdir(package_path) else path.split(package_path)[0]

    azure_path = path.join(dir_path, 'azure')
    return not path.exists(azure_path)

def get_setup_py_paths(glob_string, base_path, additional_excludes):
    setup_paths = process_glob_string(glob_string, base_path)
    filtered_paths = [path.join(p, 'setup.py') for p in setup_paths if not path_excluded(p, additional_excludes)]
    return filtered_paths


def get_packages(args, package_name = "", additional_excludes = []):
    # This function returns list of path to setup.py and setup info like install requires, version for all packages discovered using glob
    # Followiong are the list of arguements expected and parsed by this method
    # service, glob_string
    if args.service:
        target_dir = path.join(root_dir, "sdk", args.service)
    else:
        target_dir = root_dir

    paths = get_setup_py_paths(args.glob_string, target_dir, additional_excludes)

    # Check if package is excluded if a package name param is passed
    if package_name and not any(filter(lambda x: package_name == os.path.basename(os.path.dirname(x)), paths)):
        logging.info("Package {} is excluded from version update tool".format(package_name))
        exit(0)

    packages = []
    for setup_path in paths:
        try:
            setup_info = parse_setup(setup_path)
            setup_entry = (setup_path, setup_info)
            packages.append(setup_entry)
        except:
            print('Error parsing {}'.format(setup_path))
            raise

    return packages

def get_version_py(setup_py_location):
    file_path, _ = path.split(setup_py_location)
    # Find path to _version.py recursively in azure folder of package
    azure_root_path = path.join(file_path, 'azure')
    for root, _, files in os.walk(azure_root_path):
        if(VERSION_PY in files):
            return path.join(root, VERSION_PY)
        elif (OLD_VERSION_PY in files):
            return path.join(root, OLD_VERSION_PY)

def set_version_py(setup_py_location, new_version):
    version_py_location = get_version_py(setup_py_location)

    version_contents = ''
    with open(version_py_location, 'r') as version_py_file:
        version_contents = version_py_file.read()

    with open(version_py_location, 'w') as version_py_file:
        replaced_version_contents = re.sub(
            VERSION_REGEX,
            VERSION_STRING % new_version,
            version_contents,
            flags=re.MULTILINE)

        version_py_file.write(replaced_version_contents)

# Get classification for PyPI (https://pypi.org/classifiers/)
def get_classification(version):
    parsed_version = parse(version)
    if not parsed_version.is_prerelease:
        return 'Development Status :: 5 - Production/Stable'
    else:
        return 'Development Status :: 4 - Beta'

def set_dev_classifier(setup_py_location, version):
    classification = get_classification(version)

    setup_contents = ''
    with open(setup_py_location, 'r+') as setup_py_file:
        setup_contents = setup_py_file.read()

        # Reset position and truncate the file for new contents
        setup_py_file.seek(0)
        setup_py_file.truncate()

        replaced_setup_contents = re.sub(
            DEV_STATUS_REGEX,
            '\g<1>"{}"'.format(classification),
            setup_contents
        )

        setup_py_file.write(replaced_setup_contents)

def update_change_log(setup_py_location, version, service, package, is_unreleased, replace_latest_entry_title, release_date=None):
    script = os.path.join(root_dir, "eng", "common", "scripts", "Update-ChangeLog.ps1")
    pkg_root = os.path.abspath(os.path.join(setup_py_location, ".."))
    changelog_path = os.path.join(pkg_root, "CHANGELOG.md")
    commands = [
        "pwsh",
        script,
        "--Version",
        version,
        "--ServiceDirectory",
        service,
        "--PackageName",
        package,
        "--Unreleased:${}".format(is_unreleased),
        "--ReplaceLatestEntryTitle:${}".format(replace_latest_entry_title),
        "--ChangelogPath:{}".format(changelog_path)
    ]
    if release_date is not None:
        commands.append("--ReleaseDate:{}".format(release_date))

    # Run script to update change log
    run_check_call(commands, pkg_root)

