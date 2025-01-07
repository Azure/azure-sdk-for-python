#!/usr/bin/env python

# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

# Below are common methods for the devops build steps. This is the common location that will be updated with
# package targeting during release.

from argparse import Namespace
import sys
import os
from os import path
import re
import logging
from typing import TYPE_CHECKING
from packaging.version import parse

from datetime import date
from ci_tools.functions import discover_targeted_packages
from ci_tools.parsing import ParsedSetup, get_version_py, VERSION_REGEX
from ci_tools.variables import discover_repo_root

from subprocess import run

VERSION_STRING = 'VERSION = "%s"'

DEV_STATUS_REGEX = r'(classifiers=\[(\s)*)(["\']Development Status :: .*["\'])'

logging.getLogger().setLevel(logging.INFO)

from typing import List

def path_excluded(path, additional_excludes):
    return (
        any([excl in path for excl in additional_excludes])
        or "tests" in os.path.normpath(path).split(os.sep)
        or ParsedSetup.from_path(path).is_metapackage
    )


def get_setup_py_paths(glob_string, base_path, additional_excludes):
    setup_paths = discover_targeted_packages(glob_string, base_path)
    filtered_paths = [p for p in setup_paths if not path_excluded(p, additional_excludes)]
    return filtered_paths


def get_packages(
    args: Namespace, package_name: str = "", additional_excludes: List[str] = [], root_dir: str = None
) -> List[ParsedSetup]:
    if root_dir is None:
        root_dir = discover_repo_root()
    # This function returns list of path to setup.py and setup info like install requires, version for all packages discovered using glob.
    if args.service:
        target_dir = path.join(root_dir, "sdk", args.service)
    else:
        target_dir = root_dir

    paths = get_setup_py_paths(args.glob_string, target_dir, additional_excludes)

    # Check if package is excluded if a package name param is passed
    if package_name and not any(filter(lambda x: package_name == os.path.basename(x), paths)):
        logging.info("Package {} is excluded from version update tool".format(package_name))
        exit(0)

    packages = []
    for setup_path in paths:
        try:
            setup_info = ParsedSetup.from_path(setup_path)
            packages.append(setup_info)
        except:
            print("Error parsing {}".format(setup_path))
            raise

    return packages


def set_version_py(setup_path, new_version):
    version_py_location = get_version_py(setup_path)

    version_contents = ""
    with open(version_py_location, "r") as version_py_file:
        version_contents = version_py_file.read()

    with open(version_py_location, "w") as version_py_file:
        replaced_version_contents = re.sub(
            VERSION_REGEX,
            VERSION_STRING % new_version,
            version_contents,
            flags=re.MULTILINE,
        )

        version_py_file.write(replaced_version_contents)


# Get classification for PyPI (https://pypi.org/classifiers/)
def get_classification(version):
    parsed_version = parse(version)
    if not parsed_version.is_prerelease:
        return "Development Status :: 5 - Production/Stable"
    else:
        return "Development Status :: 4 - Beta"


def set_dev_classifier(setup_path, version):
    classification = get_classification(version)

    setup_contents = ""
    with open(setup_path, "r+") as setup_py_file:
        setup_contents = setup_py_file.read()

        # Reset position and truncate the file for new contents
        setup_py_file.seek(0)
        setup_py_file.truncate()

        replaced_setup_contents = re.sub(DEV_STATUS_REGEX, '\g<1>"{}"'.format(classification), setup_contents)

        setup_py_file.write(replaced_setup_contents)


def update_change_log(
    setup_py_location,
    version,
    service,
    package,
    is_unreleased,
    replace_latest_entry_title,
    release_date=None,
    root_dir=None,
):
    if root_dir is None:
        root_dir = discover_repo_root()

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
        "--ChangelogPath:{}".format(changelog_path),
    ]
    if release_date is not None:
        commands.append("--ReleaseDate:{}".format(release_date))

    # Run script to update change log
    run(commands, cwd=pkg_root)
