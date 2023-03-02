# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

import argparse
import os
import shlex
import sys

try:
    from dotenv import load_dotenv

    load_dotenv()
except:
    pass

import subprocess


# This file contains a script for managing test recordings in the azure-sdk-assets repository with Docker.
#
# INSTRUCTIONS FOR USE:
#
# - Set GIT_TOKEN, GIT_COMMIT_OWNER, and GIT_COMMIT_EMAIL environment variables to authenticate git requests.
#   These can be set in-process or added to a .env file at the root of or directory above your local copy of the
#   azure-sdk-for-python repository.
# - Set your working directory to be inside your local copy of the azure-sdk-for-python repository.
# - Run the following command:
#
#     `python {path to script}/manage_recordings.py {verb} {relative path to package's assets.json file}`
#
#   For example, with the root of the azure-sdk-for-python repo as the working directory, you can push modified
#   azure-keyvault-keys recordings to the assets repo with:
#
#     `python scripts/manage_recordings.py push sdk/keyvault/azure-keyvault-keys/assets.json`
#
# - In addition to "push", you can also use the "restore" or "reset" verbs in the same command format.
#
#   * push: pushes recording updates to a new assets repo tag and updates the tag pointer in `assets.json`.
#   * restore: fetches recordings from the assets repo, based on the tag pointer in `assets.json`.
#
# For more information about how recording asset synchronization, please refer to
# https://github.com/Azure/azure-sdk-tools/blob/main/tools/test-proxy/documentation/asset-sync/README.md.

# Load environment variables from user's .env file

CONTAINER_NAME = "azsdkengsys.azurecr.io/engsys/test-proxy"
GIT_TOKEN = os.getenv("GIT_TOKEN", "")
GIT_OWNER = os.getenv("GIT_COMMIT_OWNER", "")
GIT_EMAIL = os.getenv("GIT_COMMIT_EMAIL", "")


# ----- HELPERS ----- #


discovered_roots = []


def ascend_to_root(start_dir_or_file: str) -> str:
    """
    Given a path, ascend until encountering a folder with a `.git` folder present within it. Return that directory.

    :param str start_dir_or_file: The starting directory or file. Either is acceptable.
    """
    if os.path.isfile(start_dir_or_file):
        current_dir = os.path.dirname(start_dir_or_file)
    else:
        current_dir = start_dir_or_file

    while current_dir is not None and not (os.path.dirname(current_dir) == current_dir):
        possible_root = os.path.join(current_dir, ".git")

        # we need the git check to prevent ascending out of the repo
        if os.path.exists(possible_root):
            if current_dir not in discovered_roots:
                discovered_roots.append(current_dir)
            return current_dir
        else:
            current_dir = os.path.dirname(current_dir)

    raise Exception(f'Requested target "{start_dir_or_file}" does not exist within a git repo.')


def delete_container() -> None:
    """Delete container if it remained"""
    proc = subprocess.Popen(
        shlex.split(f"docker rm -f {CONTAINER_NAME}"),
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        stdin=subprocess.DEVNULL,
    )
    output, stderr = proc.communicate(timeout=10)
    return None


def get_image_tag(repo_root: str) -> str:
    """Gets the test proxy Docker image tag from the target_version.txt file in /eng/common/testproxy"""
    version_file_location = os.path.relpath("eng/common/testproxy/target_version.txt")
    version_file_location_from_root = os.path.abspath(os.path.join(repo_root, version_file_location))

    with open(version_file_location_from_root, "r") as f:
        image_tag = f.read().strip()

    return image_tag


# ----- CORE LOGIC ----- #


if not (GIT_TOKEN and GIT_OWNER and GIT_EMAIL):
    raise ValueError(
        "GIT_TOKEN, GIT_COMMIT_OWNER, and GIT_COMMIT_EMAIL environment variables must be set, "
        "either in-process or in a .env file"
    )

# Prepare command arguments
parser = argparse.ArgumentParser(description="Script for managing recording assets with Docker.")
parser.add_argument("verb", help='The action verb for managing recordings: "push" or "restore".')
parser.add_argument(
    "path",
    default="assets.json",
    help='The *relative* path to your package\'s `assets.json` file. Default is "assets.json".',
)
args = parser.parse_args()

if args.verb and args.path:

    current_directory = os.getcwd()
    repo_root = ascend_to_root(current_directory)
    image_tag = get_image_tag(repo_root)

    root_path = os.path.abspath(repo_root)
    cwd_relpath = os.path.relpath(current_directory, root_path)
    assets_path = os.path.join(cwd_relpath, args.path).replace("\\", "/")

    delete_container()  # Delete any lingering container so a new one can be created with necessary environment variables

    subprocess.run(
        shlex.split(
            f'docker run --rm -v "{repo_root}:/srv/testproxy" '
            f'-e "GIT_TOKEN={GIT_TOKEN}" -e "GIT_COMMIT_OWNER={GIT_OWNER}" -e "GIT_COMMIT_EMAIL={GIT_EMAIL}" '
            f"{CONTAINER_NAME}:{image_tag} test-proxy {args.verb.lower()} -a {assets_path}"
        ),
        stdout=sys.stdout,
        stderr=sys.stderr,
    )
