#!/usr/bin/env python

# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import sys
import os
import logging
import re

from subprocess import run

from code_cov_report import create_coverage_report
from common_tasks import run_check_call

logging.getLogger().setLevel(logging.INFO)

root_dir = os.path.abspath(os.path.join(os.path.abspath(__file__), "..", "..", ".."))
sdk_dir = os.path.join(root_dir, "sdk")
coverage_data_file = os.path.join(root_dir, ".coverage")
coveragerc = os.path.join(root_dir, ".coveragerc")


def find_coverage_files():
    coverage_files = []
    for root, _, files in os.walk(sdk_dir):
        coverage_files.extend(
            os.path.join(root, coverage_file)
            for coverage_file in files
            if coverage_file == ".coverage" or coverage_file.startswith(".coverage.")
        )
    return sorted(coverage_files)


def collect_coverage_files():
    coverage_version_cmd = [sys.executable, "-m", "coverage", "--version"]
    run(coverage_version_cmd, cwd=root_dir, check=True)

    logging.info("Running collect coverage files...")

    coverage_files = find_coverage_files()
    logging.info(".coverage files: {}".format(coverage_files))

    if not coverage_files:
        logging.error("No package coverage files found under {}".format(sdk_dir))
        return False

    cov_cmd_array = [sys.executable, "-m", "coverage", "combine", "--keep"]
    cov_cmd_array.extend(coverage_files)

    run(cov_cmd_array, cwd=root_dir, check=True)

    logging.info("after running coverage combine")
    for root, _, files in os.walk(root_dir):
        for f in files:
            if re.match(".coverage*", f):
                print(os.path.join(root, f))
    return True


def generate_coverage_xml():
    if os.path.exists(coverage_data_file):
        logging.info("Generating coverage XML")
        commands = ["coverage", "xml", "-i", "--rcfile", coveragerc]
        return run_check_call(commands, root_dir, always_exit=False) is None

    logging.error(
        "Coverage file is not available at {} to generate coverage XML".format(
            coverage_data_file
        )
    )
    return False


def find_package_directory(package_name):
    matches = []
    for service_name in os.listdir(sdk_dir):
        package_directory = os.path.join(sdk_dir, service_name, package_name)
        if os.path.isdir(package_directory):
            matches.append(package_directory)

    if len(matches) == 1:
        return matches[0]

    logging.warning(
        "Unable to map coverage paths for %s: expected one package directory, found %d",
        package_name,
        len(matches),
    )
    return None


def normalize_venv_paths(coverage_xml):
    package_directories = {}

    def get_package_directory(package_name):
        if package_name not in package_directories:
            package_directories[package_name] = find_package_directory(package_name)
        return package_directories[package_name]

    def replace_file_path(match):
        package_directory = get_package_directory(match.group("package"))
        if not package_directory:
            return match.group(0)

        if match.group("root"):
            return package_directory.replace(os.sep, "/")
        return os.path.relpath(package_directory, root_dir).replace(os.sep, "/")

    coverage_xml = re.sub(
        r"(?P<root>(?:[A-Za-z]:)?[^\"'<>\n]*?/)?"
        r"\.venv/(?P<package>[^/]+)/\.venv_[^/]+/"
        r"(?:lib/python[^/]+|Lib)/site-packages",
        replace_file_path,
        coverage_xml,
    )

    def replace_import_path(match):
        package_directory = get_package_directory(match.group("package"))
        if not package_directory:
            return match.group(0)

        return os.path.relpath(package_directory, root_dir).replace(os.sep, ".")

    return re.sub(
        r"\.?\.venv\.(?P<package>[^.]+)\.\.venv_[\w.]+?\.site-packages",
        replace_import_path,
        coverage_xml,
    )


def fix_coverage_xml(coverage_file):
    print("running 'fix_dot_coverage_file' on {}".format(coverage_file))

    out = None
    with open(coverage_file, encoding="utf-8") as cov_file:
        line = cov_file.read()

        # replace relative paths in folder structure pattern
        out = re.sub(r"\/\.tox\/[\s\S_]*?\/site-packages", "", line)

        # replace relative paths in python import pattern
        out = re.sub(r"\.?\.tox[\s\S\.\d]*?\.site-packages", "", out)

        # azpysdk uses repo-level virtual environments
        out = normalize_venv_paths(out)

    if out:
        with open(coverage_file, "w") as cov_file:
            cov_file.write(out)


if __name__ == "__main__":
    coverage_xml = os.path.join(root_dir, "coverage.xml")

    if collect_coverage_files() and generate_coverage_xml():
        create_coverage_report()

        if os.path.exists(coverage_xml):
            fix_coverage_xml(coverage_xml)
