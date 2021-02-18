#!/usr/bin/env python

# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from __future__ import print_function

import sys
import glob
import os
import argparse
from collections import Counter
from subprocess import check_call, CalledProcessError

root_dir = os.path.abspath(os.path.join(os.path.abspath(__file__), "..", ".."))


def pip_command(command, additional_dir=".", error_ok=False):
    try:
        print("Executing: {} from {}".format(command, additional_dir))
        check_call(
            [sys.executable, "-m", "pip"] + command.split(),
            cwd=os.path.join(root_dir, additional_dir),
        )
        print()
    except CalledProcessError as err:
        print(err, file=sys.stderr)
        if not error_ok:
            sys.exit(1)

def select_install_type(pkg, run_develop, exceptions):
    # the default for disable_develop will be false, which means `run_develop` will be true
    argument = ""
    if run_develop:
        argument = "-e"

    if pkg in exceptions:
        # opposite of whatever our decision was
        if argument == "":
            argument = "-e"
        elif argument == "-e":
            argument = ""

    return argument

# optional argument in a situation where we want to build a variable subset of packages
parser = argparse.ArgumentParser(
    description="Set up the dev environment for selected packages."
)
parser.add_argument(
    "--packageList",
    "-p",
    dest="packageList",
    default="",
    help="Comma separated list of targeted packages. Used to limit the number of packages that dependencies will be installed for.",
)
parser.add_argument(
    "--disabledevelop",
    dest="install_in_develop_mode",
    default=True,
    action="store_false",
    help="Add this argument if you would prefer to install the package with a simple `pip install` versus `pip install -e`",
)
# this is a hack to support generating docs for the single package that doesn't support develop mode. It will be removed when we
# migrate to generating docs on a per-package cadence.
parser.add_argument(
    "--exceptionlist",
    "-e",
    dest="exception_list",
    default="",
    help="Comma separated list of packages that we want to take the 'opposite' installation method for.",
)

args = parser.parse_args()

packages = {
    tuple(os.path.dirname(f).rsplit(os.sep, 1))
    for f in glob.glob(os.path.join(root_dir, "sdk/*/azure-*/setup.py")) + glob.glob(os.path.join(root_dir, "tools/azure-*/setup.py"))
}
# [(base_folder, package_name), ...] to {package_name: base_folder, ...}
packages = {package_name: base_folder for (base_folder, package_name) in packages}

exceptions = [p.strip() for p in args.exception_list.split(',')]

# keep targeted packages separate. python2 needs the nspkgs to work properly.
if not args.packageList:
    targeted_packages = list(packages.keys())
else:
    targeted_packages = [
        os.path.relpath(x.strip()) for x in args.packageList.split(",")
    ]

# Extract nspkg and sort nspkg by number of "-"
nspkg_packages = [p for p in packages.keys() if "nspkg" in p]
nspkg_packages.sort(key=lambda x: len([c for c in x if c == "-"]))

# Meta-packages to ignore
meta_packages = ["azure-keyvault", "azure-mgmt", "azure"]

content_packages = sorted(
    [
        p
        for p in packages.keys()
        if p not in nspkg_packages + meta_packages and p in targeted_packages
    ]
)

# Install tests dep first
if "azure-devtools" in content_packages:
    content_packages.remove("azure-devtools")
content_packages.insert(0, "azure-devtools")

if "azure-sdk-tools" in content_packages:
    content_packages.remove("azure-sdk-tools")
content_packages.insert(1, "azure-sdk-tools")

# Put azure-common in front of content package
if "azure-common" in content_packages:
    content_packages.remove("azure-common")
content_packages.insert(2, "azure-common")

if 'azure-core' in content_packages:
    content_packages.remove('azure-core')
content_packages.insert(3, 'azure-core')


print("Running dev setup...")
print("Root directory '{}'\n".format(root_dir))

# install private whls if there are any
privates_dir = os.path.join(root_dir, "privates")
if os.path.isdir(privates_dir) and os.listdir(privates_dir):
    whl_list = " ".join(
        [os.path.join(privates_dir, f) for f in os.listdir(privates_dir)]
    )
    pip_command("install {}".format(whl_list))

# install nspkg only on py2, but in wheel mode (not editable mode)
if sys.version_info < (3,):
    for package_name in nspkg_packages:
        pip_command("install {}/{}/".format(packages[package_name], package_name))



# install packages
print("Packages to install: {}".format(content_packages))
for package_name in content_packages:
    print("\nInstalling {}".format(package_name))
    # if we are running dev_setup with no arguments. going after dev_requirements will be a pointless exercise
    # and waste of cycles as all the dependencies will be installed regardless.
    if os.path.isfile(
        "{}/{}/dev_requirements.txt".format(packages[package_name], package_name)
    ):
        pip_command(
            "install -r dev_requirements.txt",
            os.path.join(packages[package_name], package_name),
        )

    pip_command(
        "install --ignore-requires-python {} {}".format(
            select_install_type(package_name, args.install_in_develop_mode, exceptions),
            os.path.join(packages[package_name], package_name)
        )
    )

# On Python 3, uninstall azure-nspkg if he got installed
if sys.version_info >= (3,):
    pip_command("uninstall -y azure-nspkg", error_ok=True)

print("Finished dev setup.")

