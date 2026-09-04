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

from coverage import CoverageData

from code_cov_report import create_coverage_report
from common_tasks import run_check_call

logging.getLogger().setLevel(logging.INFO)

root_dir = os.path.abspath(os.path.join(os.path.abspath(__file__), "..", "..", ".."))
sdk_dir = os.path.join(root_dir, "sdk")
coverage_data_file = os.path.join(root_dir, ".coverage")
coveragerc = os.path.join(root_dir, ".coveragerc")

# Matches an installed-package location inside an isolate/tox environment. Everything
# captured after "site-packages/" is the module path relative to the package root.
_SITE_PACKAGES_MARKER = "/site-packages/"


def find_coverage_files():
    coverage_files = []
    for root, _, files in os.walk(sdk_dir):
        coverage_files.extend(
            os.path.join(root, coverage_file)
            for coverage_file in files
            if coverage_file == ".coverage" or coverage_file.startswith(".coverage.")
        )
    return sorted(coverage_files)


def relocate_measured_path(measured_path, origin_dir):
    """Rewrite an installed-package path recorded in a per-package coverage data file
    back to the repository source directory that produced it.

    ``origin_dir`` is the package directory that owns the data file being combined, so
    the mapping stays unambiguous even when the same package name is installed under
    identically named isolate environments for two different service directories (e.g.
    ``azure-ai-textanalytics`` under both ``textanalytics`` and ``cognitivelanguage``).
    Paths that do not point into an isolate environment are returned unchanged.
    """
    normalized = measured_path.replace(os.sep, "/")
    marker_index = normalized.find(_SITE_PACKAGES_MARKER)
    if marker_index == -1:
        return measured_path

    module_subpath = normalized[marker_index + len(_SITE_PACKAGES_MARKER) :]
    relative_origin = os.path.relpath(origin_dir, root_dir).replace(os.sep, "/")
    return "{}/{}".format(relative_origin, module_subpath)


def collect_coverage_files():
    coverage_version_cmd = [sys.executable, "-m", "coverage", "--version"]
    run(coverage_version_cmd, cwd=root_dir, check=True)

    logging.info("Running collect coverage files...")

    coverage_files = find_coverage_files()
    logging.info(".coverage files: {}".format(coverage_files))

    if not coverage_files:
        logging.error("No package coverage files found under {}".format(sdk_dir))
        return False

    # Combine per-package data files ourselves so each file's paths can be relocated
    # using its originating package directory before the data is merged. Relying on
    # "coverage combine" alone would collapse identically named isolate paths from
    # different service directories into a single, mis-attributed entry.
    if os.path.exists(coverage_data_file):
        os.remove(coverage_data_file)

    combined_data = CoverageData(basename=coverage_data_file)
    for coverage_file in coverage_files:
        origin_dir = os.path.dirname(coverage_file)
        package_data = CoverageData(basename=coverage_file)
        package_data.read()
        combined_data.update(
            package_data,
            map_path=lambda measured_path, origin=origin_dir: relocate_measured_path(
                measured_path, origin
            ),
        )
    combined_data.write()

    logging.info("after combining coverage data into {}".format(coverage_data_file))
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
    # Safety-net lookup for the post-XML normalization below. Real runs relocate
    # isolate paths per data file before combining (see collect_coverage_files), so
    # this only handles residual paths and intentionally returns None on ambiguity
    # rather than guessing a service directory by basename.
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
