#!/usr/bin/env python

# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import argparse
import os
import logging
import sys
import subprocess

logging.getLogger().setLevel(logging.INFO)

root_dir = os.path.abspath(os.path.join(os.path.abspath(__file__), "..", "..", ".."))
sdk_dir = os.path.join(root_dir, "sdk")

def run_black(service_dir):
    logging.info("Running black for {}".format(service_dir))

    out = subprocess.Popen([sys.executable, "-m", "black", "-l", "120", "sdk/{}".format(service_dir)],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        cwd = root_dir
    )

    stdout,stderr = out.communicate()

    if stderr:
        raise RuntimeError("black ran into some trouble during its invocation: " + stderr)

    if stdout:
        if "reformatted" in stdout.decode('utf-8'):
            return False

    return True

    
if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Run black to verify formatted code."
    )
    parser.add_argument(
        "--service_directory", help="Directory of the package being tested"
    )

    parser.add_argument(
        "--validate", help=("Flag that enables formatting validation.")
    )

    args = parser.parse_args()
    if args.validate != "False":
        if not run_black(args.service_directory):
            raise ValueError("Found difference between formatted code and current commit. Please re-generate with the latest autorest.")
        
    else:
        print("Skipping formatting validation")