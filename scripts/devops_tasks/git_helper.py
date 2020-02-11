#!/usr/bin/env python

# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import sys
import os
import logging
from packaging.version import parse
from common_tasks import run_check_call

logging.getLogger().setLevel(logging.INFO)

# Oldest release of SDK packages that should be skipped
EXCLUDED_PACKAGE_VERSIONS = {
    'azure-storage-file-share': ['12.0.0', '12.0.0b5'],
    'azure-storage-queue': ['0.37.0', '1.0.0', '1.1.0', '1.2.0rc1', '1.3.0', '1.4.0', '2.0.0', '2.0.1', '2.1.0'],
    'azure-storage-file': ['0.37.0', '1.0.0', '1.1.0', '1.2.0rc1', '1.3.0', '1.3.1', '1.4.0', '2.0.0', '2.0.1', '2.1.0'],
    'azure-storage-blob': ['0.37.0', '0.37.1', '1.0.0', '1.1.0', '1.2.0rc1', '1.3.0', '1.3.1', '1.4.0', '1.5.0', '2.0.0', '2.0.1', '2.1.0',],
    'azure-eventhub': ['0.2.0', '1.0.0', '1.1.0', '1.1.1', '1.2.0rc1', '1.2.0', '1.3.0', '1.3.1', '1.3.2', '1.3.3',],
    'azure-cosmos': ['3.0.0', '3.0.1', '3.0.2', '3.1.0', '3.1.1', '3.1.2'],
}

# This method identifies release tag for latest or oldest released version of a given package
def get_release_tag(dep_pkg_name, isLatest):
    # get versions from pypi and find latest
    # delayed import until sdk tools are installed on virtual env
    from pypi_tools.pypi import PyPIClient

    client = PyPIClient()
    versions = [str(v) for v in client.get_ordered_versions(dep_pkg_name)]
    logging.info("Versions for {0} is: {1}".format(dep_pkg_name, versions))

    # filter excluded versions
    if dep_pkg_name in EXCLUDED_PACKAGE_VERSIONS:
        versions = [v for v in versions if  v not in EXCLUDED_PACKAGE_VERSIONS[dep_pkg_name]]
        logging.info("Filtered versions for {0} is: {1}".format(dep_pkg_name, versions))

    if len(versions) == 0:
        logging.info(
            "Released version info for package {} is not available".format(dep_pkg_name)
        )
        # This is not a hard error. We can run into this situation when a new package is added to repo and not yet released
        return

    # find latest version
    logging.info("Looking for {} released version".format("Latest" if isLatest == True else "Oldest"))
    if isLatest == True:
        versions.reverse()
    else:
        # find oldest GA version by filtering out all preview versions
        versions = [ v for v in versions if parse(v).is_prerelease == False]
        if(len(versions) <2):
            logging.info("Only one or no released GA version found for package {}".format(dep_pkg_name))
            return

    version = versions[0]

    # create tag in <pkg_name>_version format
    tag_name = "{0}_{1}".format(dep_pkg_name, version)
    logging.info(
        "Release tag for package [{0}] is [{1}]".format(dep_pkg_name, tag_name)
    )
    return tag_name


# This method checkouts a given tag of sdk repo
def git_checkout_tag(tag_name, working_dir):
    # fetch tags
    run_check_call(["git", "fetch", "origin", "tag", tag_name], working_dir)

    logging.info("checkout git repo with tag {}".format(tag_name))
    commands = ["git", "checkout", "tags/{}".format(tag_name)]
    run_check_call(commands, working_dir)
    logging.info("Code with tag {} is checked out successfully".format(tag_name))


# This method checkouts a given tag of sdk repo
def git_checkout_branch(branch_name, working_dir):
    # fetch tags
    run_check_call(["git", "fetch", "origin", branch_name], working_dir)
    run_check_call(["git", "branch", branch_name, "FETCH_HEAD"], working_dir)
    logging.info("checkout git repo with branch {}".format(branch_name))
    commands = ["git", "checkout", branch_name]
    run_check_call(commands, working_dir)
    logging.info("Repo with branch name {} is checked out successfully".format(branch_name))


def clone_repo(dest_dir, repo_url):
    if not os.path.isdir(dest_dir):
        logging.error(
            "Invalid destination directory to clone git repo:[{}]".format(dest_dir)
        )
        sys.exit(1)

    logging.info("cloning git repo using url {}".format(repo_url))
    run_check_call(["git", "clone", "--depth=1", repo_url], dest_dir)
