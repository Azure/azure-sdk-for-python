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
import shutil

import pdb

CONFIG_FILE = os.path.join(
    os.path.dirname(os.path.abspath(__file__)), "./package_service_mapping.json"
)
logging.getLogger().setLevel(logging.INFO)
location = os.path.dirname(os.path.abspath(__file__))
root_dir = os.path.abspath(os.path.join(location, "..", ".."))
docs_folder = os.path.join(root_dir, '_docs')
index = os.path.join(location, 'index.rst')

TOC_TEMPLATE = """
.. toctree::
  :maxdepth: 5
  :glob:
  :caption: {category}

  {members}

"""

LANDING_START = """
{service_name_title_indicator}
{service_name}
{service_name_title_indicator}

"""

LANDING_TEMPLATE = """
{package_name_title_indicator}
{package_name}
{package_name_title_indicator}

**Published Versions**

.. raw:: html

    <embed>
        <ul id="v{package_name}"></ul>
        <script type="text/javascript">
            populateIndexList('#v{package_name}', '{package_name}')
        </script>
    </embed>

------------

"""

LANDING_PAGE_LOCATION = "ref/{}.rst"

PACKAGE_REDIRECTIONS = {
    "azure-eventhubs": "azure-eventhub",
    "azure-eventhubs-checkpointstoreblob-aio": "azure-eventhub-checkpointstoreblob-aio"
}

def read_config_file(config_path=CONFIG_FILE):
    with open(CONFIG_FILE, "r") as f:
        return json.load(f)

def check_package_against_omission(package_name):
    if "nspkg" in package_name:
        return False

    if "azure" == package_name:
        return False

    if "azure-mgmt" == package_name:
        return False

    return True

def get_repo_packages(base_dir):
    packages = [
        os.path.basename(os.path.dirname(p))
        for p in (
            glob.glob(os.path.join(base_dir, "sdk/*/azure-*", "setup.py"))
        )
    ]

    packages = [p for p in packages if check_package_against_omission(p)]

    for redirection in PACKAGE_REDIRECTIONS:
        if redirection in packages:
            packages.remove(redirection)
            packages.append(PACKAGE_REDIRECTIONS[redirection])

    return sorted(packages)

def write_landing_pages(categorized_menu_items):
    for service in categorized_menu_items:
        with open(os.path.join(docs_folder, LANDING_PAGE_LOCATION.format("-".join(service.split(' ')))), 'w') as f:
            content = LANDING_START.format(service_name = service, service_name_title_indicator = "".join(["="] * len(service)))
            for pkg in categorized_menu_items[service]:
                content += LANDING_TEMPLATE.format(package_name = pkg, package_name_title_indicator="".join(["-"] * len(pkg)))
            f.write(content)

def write_toc_tree(categorized_menu_items):
    toc_tree_contents = ""

    category_toc_contents = TOC_TEMPLATE.format(category = "Services", members = "\n  ".join([LANDING_PAGE_LOCATION.format("-".join(p.split(' '))) for p in sorted(categorized_menu_items)]))
    toc_tree_contents += category_toc_contents

    with open(os.path.join(docs_folder, 'toc_tree.rst'), 'w') as f:
        f.write(toc_tree_contents)


def get_categorized_menu_items(package_names):
    categorized_menu_items = {"Other": []}

    for pkg in package_names:
        # add to the categorized menu items
        if pkg in service_mapping:
            pkg_meta = service_mapping[pkg]
            if pkg_meta["service_name"] not in categorized_menu_items.keys():
                categorized_menu_items[pkg_meta["service_name"]] = []
            categorized_menu_items[pkg_meta["service_name"]].append(pkg)
        else:
            categorized_menu_items["Other"].append(pkg)

    return categorized_menu_items
    
def create_docs_folder():
    # delete existing
    shutil.rmtree(docs_folder, ignore_errors=True)
    
    # recreate
    os.mkdir(docs_folder)
    os.mkdir(os.path.join(docs_folder, 'ref'))

    # copy all written RST files written in the sphinx folder
    for file in [p for p in os.listdir(location) if os.path.splitext(p)[1] == ".rst"]:
        shutil.copy(file, docs_folder)

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

    create_docs_folder()

    # work up where stuff should exist in the ToC
    categorized_menu_items = get_categorized_menu_items(all_packages)

    # write all the landing pages that will reach out to the appropriate location
    write_landing_pages(categorized_menu_items)
    
    # write the ToC
    write_toc_tree(categorized_menu_items)

    # ready to run sphinx!
    logging.info('Index prepped and ready for generation. Use the command `sphinx-build -b html -c {sphinx_conf} {source_dir} {output_dir}` to generate.'.format(source_dir = docs_folder, sphinx_conf = location, output_dir = os.path.join(docs_folder, 'html')))
