#!/usr/bin/env python

# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

# This script is intended to be a place holder for common tasks that are requried by scripts running on tox

import shutil
import sys
import logging
import ast
import os
import textwrap
import io
import glob
import zipfile
import fnmatch
import subprocess
import re

from packaging.specifiers import SpecifierSet
from pkg_resources import Requirement, parse_version

logging.getLogger().setLevel(logging.INFO)


def get_pip_list_output():
    """Uses the invoking python executable to get the output from pip list."""
    out = subprocess.Popen(
        [sys.executable, "-m", "pip", "list", "--disable-pip-version-check", "--format", "freeze"],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
    )

    stdout, stderr = out.communicate()

    collected_output = {}

    if stdout and (stderr is None):
        # this should be compatible with py27 https://docs.python.org/2.7/library/stdtypes.html#str.decode
        for line in stdout.decode("utf-8").split(os.linesep)[2:]:
            if line:
                package, version = re.split("==", line)
                collected_output[package] = version
    else:
        raise Exception(stderr)

    return collected_output


def unzip_sdist_to_directory(containing_folder):
    # grab the first one
    path_to_zip_file = glob.glob(os.path.join(containing_folder, "*.zip"))[0]
    return unzip_file_to_directory(path_to_zip_file, containing_folder)


def unzip_file_to_directory(path_to_zip_file, extract_location):
    # unzip file in given path
    # dump into given path
    with zipfile.ZipFile(path_to_zip_file, "r") as zip_ref:
        zip_ref.extractall(extract_location)
        extracted_dir = os.path.basename(os.path.splitext(path_to_zip_file)[0])
        return os.path.join(extract_location, extracted_dir)


def move_and_rename(source_location):
    new_location = os.path.join(os.path.dirname(source_location), "unzipped")

    if os.path.exists(new_location):
        shutil.rmtree(new_location)

    os.rename(source_location, new_location)
    return new_location


def find_sdist(dist_dir, pkg_name, pkg_version):
    # This function will find a sdist for given package name
    if not os.path.exists(dist_dir):
        logging.error("dist_dir is incorrect")
        return

    if pkg_name is None:
        logging.error("Package name cannot be empty to find sdist")
        return

    pkg_name_format = "{0}-{1}.zip".format(pkg_name, pkg_version)
    packages = []
    for root, dirnames, filenames in os.walk(dist_dir):
        for filename in fnmatch.filter(filenames, pkg_name_format):
            packages.append(os.path.join(root, filename))

    packages = [os.path.relpath(w, dist_dir) for w in packages]

    if not packages:
        logging.error("No sdist is found in directory %s with package name format %s", dist_dir, pkg_name_format)
        return
    return packages[0]


def find_whl(whl_dir, pkg_name, pkg_version):
    # This function will find a whl for given package name
    if not os.path.exists(whl_dir):
        logging.error("whl_dir is incorrect")
        return

    if pkg_name is None:
        logging.error("Package name cannot be empty to find whl")
        return

    pkg_name_format = "{0}-{1}*.whl".format(pkg_name.replace("-", "_"), pkg_version)
    whls = []
    for root, dirnames, filenames in os.walk(whl_dir):
        for filename in fnmatch.filter(filenames, pkg_name_format):
            whls.append(os.path.join(root, filename))

    whls = [os.path.relpath(w, whl_dir) for w in whls]

    if not whls:
        logging.error("No whl is found in directory %s with package name format %s", whl_dir, pkg_name_format)
        logging.info("List of whls in directory: %s", glob.glob(os.path.join(whl_dir, "*.whl")))
        return

    if len(whls) > 1:
        # So we have whls specific to py version or platform since we are here
        py_version = "py{0}".format(sys.version_info.major)
        # filter whl for py version and check if we found just one whl
        whls = [w for w in whls if py_version in w]

        # if whl is platform independent then there should only be one whl in filtered list
        if len(whls) > 1:
            # if we have reached here, that means we have whl specific to platform as well.
            # for now we are failing the test if platform specific wheels are found. Todo: enhance to find platform specific whl
            logging.error(
                "More than one whl is found in wheel directory for package {}. Platform specific whl discovery is not supported now".format(
                    pkg_name
                )
            )
            sys.exit(1)

    # Additional filtering based on arch type willbe required in future if that need arises.
    # for now assumption is that no arch specific whl is generated
    if len(whls) == 1:
        logging.info("Found whl {}".format(whls[0]))
        return whls[0]
    else:
        return None
