#!/usr/bin/env python

# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import sys
import os
import logging
from common_tasks import run_check_call

logging.getLogger().setLevel(logging.INFO)

# This method identifies release tag for latest or oldest released version of a given package
def get_release_tag(dep_pkg_name, isLatest=True):
    # get versions from pypi and find latest
    # delayed import until sdk tools are installed on virtual env
    from pypi_tools.pypi import PyPIClient

    client = PyPIClient()
    versions = [str(v) for v in client.get_ordered_versions(dep_pkg_name)]
    logging.info("Versions for {0} is: [{1}]".format(dep_pkg_name, versions))
    if versions is None:
        logging.info(
            "Released version info for package {} is not available".format(dep_pkg_name)
        )
        # This is not a hard error. We can run into this situation when a new package is added to repo and not yet released
        return

    # find latest version
    if isLatest:
        versions.reverse()
    latestVersion = versions[0]

    # create tag in <pkg_name>_version format
    tag_name = "{0}_{1}".format(dep_pkg_name, latestVersion)
    logging.info(
        "Release tag for package [{0}] is [{1}]".format(dep_pkg_name, tag_name)
    )
    return tag_name


# This method checkouts a given tag of sdk repo
def checkout_code_repo(tag_name, working_dir):
    # fetch tags
    run_check_call(["git", "fetch", "--all", "--tags"], working_dir)

    logging.info("checkout git repo with tag {}".format(tag_name))
    commands = ["git", "checkout", "tags/{}".format(tag_name)]
    run_check_call(commands, working_dir)
    logging.info("Code with tag {} is checked out successfully".format(tag_name))


def clone_repo(dest_dir, repo_url):
    if not os.path.isdir(dest_dir):
        logging.error(
            "Invalid destination directory to clone git repo:[{}]".format(dest_dir)
        )
        sys.exit(1)

    logging.info("cloning git repo using url {}".format(repo_url))
    run_check_call(["git", "clone", "--depth=1", repo_url], dest_dir)
