# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

# This script is used to execute ruff within a tox environment.

import subprocess
import argparse
import os
import sys
from ci_tools.parsing import ParsedSetup


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Run ruff against target folder."
    )

    parser.add_argument(
        "-t",
        "--target",
        dest="target_package",
        help="The target package directory on disk. The target module passed to ruff will be <target_package>/azure.",
        required=True,
    )

    args = parser.parse_args()

    pkg_dir = os.path.abspath(args.target_package)
    pkg_details = ParsedSetup.from_path(pkg_dir)
    top_level_module = pkg_details.namespace.split('.')[0]

    subprocess.check_call(
        [
            sys.executable,
            "-m",
            "ruff",
            "check",
            os.path.join(args.target_package, top_level_module),
        ]
    )
