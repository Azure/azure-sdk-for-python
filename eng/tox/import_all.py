#!/usr/bin/env python

# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

# This script is used to verify package dependency by importing all modules
import argparse
import logging
import os
from tox_helper_tasks import get_package_details

logging.getLogger().setLevel(logging.INFO)

# keyvault has dependency issue when loading private module _BearerTokenCredentialPolicyBase from azure.core.pipeline.policies
# azure.core.tracing.opencensus and azure.eventhub.checkpointstoreblob.aio are skipped due to a known issue in loading azure.core.tracing.opencensus
excluded_packages = [
    "azure.core.tracing.opencensus",
    "azure.eventhub.checkpointstoreblob.aio",
    "azure.identity",
    "azure.keyvault.certificates", # Github issue 7879
    "azure.keyvault.keys", # Github issue 7879
    "azure.keyvault.secrets", # Github issue 7879
    "azure.appconfiguration", # Github issue 7879. revisit and close after azure-core POST b4 is released.
    "azure.storage.blob", # Github issue 7879.
    "azure.storage.fileshare", # Github issue 7879.
    "azure.storage.queue", # Github issue 7879.
    "azure",
    "azure.mgmt",
    "azure.keyvault",
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
    pkg_name, _ = get_package_details(os.path.join(pkg_dir, 'setup.py'))
    package_name = pkg_name.replace("-", ".")

    if should_run_import_all(package_name):
        # import all modules from current package
        logging.info(
            "Importing all modules from package [{0}] to verify dependency".format(
                package_name
            )
        )
        import_script_all = "from {0} import *".format(package_name)
        exec(import_script_all)
        logging.info("Verified module dependency, no issues found")
    else:
        pass
        logging.error("Package {} is excluded from dependency check".format(package_name))
