#!/usr/bin/env python

# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import sys
import os
import logging
import datetime
import re

CHANGE_LOG_FILE_NAME = "history.md"
UNRELEASED_TAG = "(Unreleased)"
VERSION_REGEX = "\d+\.\d+\.\d+([^0-9\s][^\s:]+)?"


def get_version_header(version, isUnreleased):
    release_date = ""
    if isUnreleased:
        release_date = UNRELEASED_TAG
    else:
        release_date = datetime.date.today()

    version_header = "## {0} {1}\n".format(version, release_date)
    return version_header


def get_change_log_path(setup_py_location):
    # This method will add a new entry for given new version if entry is missing for that version
    change_log_path = os.path.join(setup_py_location, '..', CHANGE_LOG_FILE_NAME)
    if not os.path.exists(change_log_path):
        logging.error("Change log file [%s] is missing. Failed to add new version in change log", change_log_path)
        sys.exit(1)
    return change_log_path


def get_current_log(change_log_path):
    contents = []
    with open(change_log_path, "r") as change_log:
        contents = change_log.readlines()
    return contents


def write_change_log(change_log_path, contents):
    with open(change_log_path, "w") as change_log:
        change_log.writelines(contents)


def update_version_in_changelog(setup_py_location, new_version, add_new_entry, isUnreleased):
    # Generate new version header
    # This method will add a new entry with (Unreleased) tag when called with 'True' for add_new_entry
    # if 'add_new_entry' is false then it replaces latest version header in change log \
    # with new version. This is used when a version is set at release time to change minor or major version or \
    # to remove 'Unreleased' tag
    new_version_header = get_version_header(new_version, isUnreleased)

    # get current change log
    change_log_path = get_change_log_path(setup_py_location)
    contents = get_current_log(change_log_path)

    # find current latest version from change log
    # new version header should be added just above current vbersion log
    latest_version = next(log for log in contents if re.search(VERSION_REGEX, log))

    # find the place to add new version header
    index = contents.index(latest_version)
    contents.insert(index, new_version_header)
    # remove old entry in case of replacing version
    if not add_new_entry:
        contents.remove(contents[index+1])        

    write_change_log(change_log_path, contents)
    logging.info("Successfully updated change log")





        

