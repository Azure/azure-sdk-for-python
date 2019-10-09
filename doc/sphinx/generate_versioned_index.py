#!/usr/bin/env python

# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

# This script is used to generate the package index. Instead of displaying per-package documentation,
# links will be provided to relevant blob storage locations.

import argparse
import logging
import json
import os
import glob

import pdb

CONFIG_FILE = os.path.join(
    os.path.dirname(os.path.abspath(__file__)), "./package_service_mapping.json"
)
logging.getLogger().setLevel(logging.INFO)
root_dir = os.path.abspath(os.path.join(os.path.abspath(__file__), "..", "..", ".."))

TOC_TEMPLATE = """
.. toctree::
  :maxdepth: 5
  :glob:
  :caption: {category}

  {members}
"""

PACKAGE_REDIRECTIONS = {
    "azure-eventhubs": "azure-eventhub",
    "azure-eventhubs-checkpointstoreblob-aio": "azure-eventhub-checkpointstoreblob-aio"
}

def read_config_file(config_path=CONFIG_FILE):
    with open(CONFIG_FILE, "r") as f:
        return json.load(f)

def get_repo_packages(base_dir):
    packages = [
        os.path.basename(os.path.dirname(p))
        for p in (
            glob.glob(os.path.join(base_dir, "sdk/*/azure-*", "setup.py"))
        )
    ]

    for redirection in PACKAGE_REDIRECTIONS:
        if redirection in packages:
            packages.remove(redirection)
            packages.append(PACKAGE_REDIRECTIONS[redirection])

    return sorted(packages)

def write_landing_pages(categorized_menu_items):
    print(categorized_menu_items)

# output everything to the _docs
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate documentation index")
    parser.add_argument(
        "-v",
        "--verbose",
        dest="verbose",
        action="store_true",
        help="Verbosity in INFO mode",
    )

    parser.add_argument(
        "--out",
        "-o",
        dest="output_directory",
        help="The final resting place for the generated sphinx source files.",
    )
    args = parser.parse_args()

    service_mapping = read_config_file()
    all_packages = get_repo_packages(root_dir)

    write_landing_pages(all_packages)

    categorized_menu_items = {"Client": [], "Management": [], "Other": []}

    for pkg in all_packages:
        # add to the categorized menu items
        if pkg in service_mapping:
            pkg_meta = service_mapping[pkg]
            categorized_menu_items[pkg_meta["category"]].append(pkg)
        else:
            categorized_menu_items["Other"].append(pkg)

        # generate the individual landing page

