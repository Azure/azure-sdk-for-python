#!/usr/bin/env python

# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

# This script is intended to be a place holder for common tasks that are requried by scripts running on tox

import sys
import logging
import argparse
import ast
import os
import platform
import textwrap
import io
import glob
import zipfile

logging.getLogger().setLevel(logging.INFO)


def get_package_details(setup_filename):
    mock_setup = textwrap.dedent(
        """\
    def setup(*args, **kwargs):
        __setup_calls__.append((args, kwargs))
    """
    )
    parsed_mock_setup = ast.parse(mock_setup, filename=setup_filename)
    with io.open(setup_filename, "r", encoding="utf-8-sig") as setup_file:
        parsed = ast.parse(setup_file.read())
        for index, node in enumerate(parsed.body[:]):
            if (
                not isinstance(node, ast.Expr)
                or not isinstance(node.value, ast.Call)
                or not hasattr(node.value.func, "id")
                or node.value.func.id != "setup"
            ):
                continue
            parsed.body[index:index] = parsed_mock_setup.body
            break

    fixed = ast.fix_missing_locations(parsed)
    codeobj = compile(fixed, setup_filename, "exec")
    local_vars = {}
    global_vars = {"__setup_calls__": []}
    current_dir = os.getcwd()
    working_dir = os.path.dirname(setup_filename)
    os.chdir(working_dir)
    exec(codeobj, global_vars, local_vars)
    os.chdir(current_dir)
    _, kwargs = global_vars["__setup_calls__"][0]

    package_name = kwargs["name"]
    # default namespace for the package
    name_space = package_name.replace('-', '.')
    if "packages" in kwargs.keys():
        packages = kwargs["packages"]
        if packages:
            name_space = packages[0]
            logging.info("Namespaces found for package {0}: {1}".format(package_name, packages))

    return package_name, name_space, kwargs["version"]

def unzip_sdist_to_directory(containing_folder):
    # grab the first one
    path_to_zip_file = glob.glob(os.path.join(containing_folder, "*.zip"))[0]
    return unzip_file_to_directory(path_to_zip_file, containing_folder)

def unzip_file_to_directory(path_to_zip_file, extract_location):
    # unzip file in given path
    # dump into given path
    with zipfile.ZipFile(path_to_zip_file, "r") as zip_ref:
        zip_ref.extractall(extract_location)
        extracted_dir = os.path.basename(os.path.splitext(path_to_zip_file)[0])
        return os.path.join(extract_location, extracted_dir)

def move_and_rename(source_location):
    new_location = os.path.join(os.path.dirname(source_location), "unzipped")
    os.rename(source_location, new_location)
    return new_location

def find_whl(whl_dir, pkg_name, pkg_version):
    # This function will find a whl for given package name
    if not os.path.exists(whl_dir):
        logging.error("whl_dir is incorrect")
        return

    if pkg_name is None:
        logging.error("Package name cannot be empty to find whl")
        return

    pkg_name_format = "{0}-{1}-*.whl".format(pkg_name.replace("-", "_"), pkg_version)
    whls = [os.path.basename(w) for w in glob.glob(os.path.join(whl_dir, pkg_name_format))]
    if not whls:
        logging.error("No whl is found in directory %s with package name format %s", whl_dir, pkg_name_format)
        logging.info("List of whls in directory: %s", glob.glob(os.path.join(whl_dir, "*.whl")))
        return

    if len(whls) > 1:
        # So we have whls specific to py version or platform since we are here
        py_version = "py{0}".format(sys.version_info.major)
        # filter whl for py version and check if we found just one whl
        whls = [w for w in whls if py_version in w]

        # if whl is platform independent then there should only be one whl in filtered list
        if len(whls) > 1:
            # if we have reached here, that means we have whl specific to platform as well.
            # for now we are failing the test if platform specific wheels are found. Todo: enhance to find platform specific whl
            logging.error("More than one whl is found in wheel directory for package {}. Platform specific whl discovery is not supported now".format(pkg_name))
            sys.exit(1)
    
    # Additional filtering based on arch type willbe required in future if that need arises.
    # for now assumption is that no arch specific whl is generated
    if len(whls) == 1:
        logging.info("Found whl {}".format(whls[0]))
        return whls[0]
    else:
        return None



