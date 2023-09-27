#!/usr/bin/env python

# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

# This script is intended to be a place holder for common tasks that are requried by scripts running on tox

import shutil
import sys
import logging
import os
import glob
import zipfile
import tarfile
import subprocess
import re

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


def unzip_sdist_to_directory(containing_folder: str) -> str:
    zips = glob.glob(os.path.join(containing_folder, "*.zip"))

    if zips:
        return unzip_file_to_directory(zips[0], containing_folder)
    else:
        tars = glob.glob(os.path.join(containing_folder, "*.tar.gz"))
        return unzip_file_to_directory(tars[0], containing_folder)


def unzip_file_to_directory(path_to_zip_file: str, extract_location: str) -> str:
    if path_to_zip_file.endswith(".zip"):
        with zipfile.ZipFile(path_to_zip_file, "r") as zip_ref:
            zip_ref.extractall(extract_location)
            extracted_dir = os.path.basename(os.path.splitext(path_to_zip_file)[0])
            return os.path.join(extract_location, extracted_dir)
    else:
        with tarfile.open(path_to_zip_file) as tar_ref:
            tar_ref.extractall(extract_location)
            extracted_dir = os.path.basename(path_to_zip_file).replace(".tar.gz", "")
            return os.path.join(extract_location, extracted_dir)


def move_and_rename(source_location):
    new_location = os.path.join(os.path.dirname(source_location), "unzipped")

    if os.path.exists(new_location):
        shutil.rmtree(new_location)

    os.rename(source_location, new_location)
    return new_location
