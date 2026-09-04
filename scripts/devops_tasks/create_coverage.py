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

# Maps a package name to the package directory that produced its coverage data,
# recorded as each .coverage file is discovered (see find_coverage_files below). This
# is populated from the actual originating directory of each coverage file, so it
# stays unambiguous even when the same package name exists under multiple service
# directories (e.g. "azure-ai-textanalytics" under both "textanalytics" and
# "cognitivelanguage").
package_directories = {}


def find_coverage_files():
    coverage_files = []
    for root, _, files in os.walk(sdk_dir):
        for coverage_file in files:
            if coverage_file == ".coverage" or coverage_file.startswith(".coverage."):
                coverage_files.append(os.path.join(root, coverage_file))
                package_name = os.path.basename(root)
                existing_directory = package_directories.get(package_name)
                if existing_directory and existing_directory != root:
                    logging.warning(
                        "Multiple package directories produced coverage for %s: %s and %s. "
                        "Coverage paths for this package may not map back to repository sources.",
                        package_name,
                        existing_directory,
                        root,
                    )
                else:
                    package_directories[package_name] = root
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
    package_directory = package_directories.get(package_name)
    if package_directory:
        return package_directory

    # Fall back to a filesystem search for callers that never ran
    # find_coverage_files() (e.g. normalize_venv_paths invoked directly).
    matches = []
    for service_name in os.listdir(sdk_dir):
        candidate_directory = os.path.join(sdk_dir, service_name, package_name)
        if os.path.isdir(candidate_directory):
            matches.append(candidate_directory)

    if len(matches) == 1:
        return matches[0]

    logging.warning(
        "Unable to map coverage paths for %s: expected one package directory, found %d",
        package_name,
        len(matches),
    )
    return None


def normalize_venv_paths(coverage_xml):
    def replace_file_path(match):
        package_directory = find_package_directory(match.group("package"))
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
        package_directory = find_package_directory(match.group("package"))
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
