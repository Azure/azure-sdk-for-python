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
coverage_dir = os.path.join(root_dir, "_coverage/")


def collect_tox_coverage_files():
    coverage_version_cmd = [sys.executable, "-m", "coverage", "--version"]
    run(coverage_version_cmd, cwd=root_dir)

    logging.info("Running collect tox coverage files...")

    coverage_files = []
    for root, _, files in os.walk(coverage_dir):
        for f in files:
            if re.match(".coverage_*", f):
                coverage_files.append(os.path.join(root, f))
                fix_dot_coverage_file(os.path.join(root, f))

    logging.info(".coverage files: {}".format(coverage_files))

    if len(coverage_files):
        cov_cmd_array = [sys.executable, "-m", "coverage", "combine"]
        cov_cmd_array.extend(coverage_files)

        # merge them with coverage combine and copy to root
        run(cov_cmd_array, cwd=root_dir)

        logging.info("after running coverage combine")
        for root, _, files in os.walk(root_dir):
            for f in files:
                if re.match(".coverage*", f):
                    print(os.path.join(root, f))


def generate_coverage_xml():
    if os.path.exists(coverage_dir):
        logging.info("Generating coverage XML")
        commands = ["coverage", "xml", "-i"]
        run_check_call(commands, root_dir, always_exit = False)
    else:
        logging.error("Coverage file is not available in {} to generate coverage XML".format(coverage_dir))


def fix_dot_coverage_file(coverage_file):
    print("running 'fix_dot_coverage_file' on {}".format(coverage_file))

    out = None
    with open(coverage_file) as cov_file:
        line = cov_file.read()
        out = re.sub("\/\.tox\/[\s\S]*?\/site-packages", "/", line)

    if out:
        with open(coverage_file, 'w') as cov_file:
            cov_file.write(out)


if __name__ == "__main__":
    collect_tox_coverage_files()
    generate_coverage_xml()
    create_coverage_report()