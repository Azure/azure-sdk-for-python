#!/usr/bin/env python

# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

# This script is used to verify package dependency by importing all modules
import sys
import argparse
import logging
import os
from subprocess import check_call

from ci_tools.parsing import ParsedSetup

logging.getLogger().setLevel(logging.INFO)
root_dir = os.path.abspath(os.path.join(os.path.abspath(__file__), "..", "..", ".."))

# keyvault has dependency issue when loading private module _BearerTokenCredentialPolicyBase from azure.core.pipeline.policies
# azure.core.tracing.opencensus and azure.eventhub.checkpointstoreblob.aio are skipped due to a known issue in loading azure.core.tracing.opencensus
excluded_packages = [
    "azure",
    "azure-mgmt",
    ]

def should_run_import_all(package_name):
    return not (package_name in excluded_packages or "nspkg" in package_name)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Import all modules in package")

    parser.add_argument(
        "-t",
        "--target",
        dest="target_package",
        help="The target package directory on disk.",
        required=True,
    )

    args = parser.parse_args()

    # get target package name from target package path
    pkg_dir = os.path.abspath(args.target_package)
    pkg_details = ParsedSetup.from_path(pkg_dir)
    
    if should_run_import_all(pkg_details.name):
        # import all modules from current package
        logging.info(
            "Importing all modules from namespace [{0}] to verify dependency".format(
                pkg_details.namespace
            )
        )
        import_script_all = "from {0} import *".format(pkg_details.namespace)
        commands = [
            sys.executable,
            "-c",
            import_script_all
        ]

        check_call(commands, cwd= root_dir)
        logging.info("Verified module dependency, no issues found")
    else:
        pass
        logging.error("Package {} is excluded from dependency check".format(pkg_details.name))
