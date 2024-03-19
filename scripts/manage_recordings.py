# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

import argparse
import os
import shlex
import subprocess
import sys

from devtools_testutils.proxy_startup import (
    ascend_to_root,
    prepare_local_tool,
)


TOOL_ENV_VAR = "PROXY_PID"


# This file contains a script for managing test recordings in the azure-sdk-assets repository.
#
# INSTRUCTIONS FOR USE:
#
# - Set your working directory to be inside your local copy of the azure-sdk-for-python repository.
# - Run the following command:
#
#     `python {path to script}/manage_recordings.py {verb} [-p {relative path to package's assets.json file}]`
#
#   For example, with the root of the azure-sdk-for-python repo as the working directory, you can push modified
#   azure-keyvault-keys recordings to the assets repo with:
#
#     `python scripts/manage_recordings.py push -p sdk/keyvault/azure-keyvault-keys/assets.json`
#
#   If this script is run from the directory containing an assets.json file, no path needs to be provided. For example,
#   with a working directory at the azure-keyvault-keys package root:
#
#     `python ../../../scripts/manage_recordings.py push`
#
# - In addition to "push", you can also use the "restore" or "reset" verbs in the same command format.
#
#   * locate: prints the location of the library's locally cached recordings.
#   * push: pushes recording updates to a new assets repo tag and updates the tag pointer in `assets.json`.
#   * show: prints the contents of the provided `assets.json` file.
#   * restore: fetches recordings from the assets repo, based on the tag pointer in `assets.json`.
#   * reset: discards any pending changes to recordings, based on the tag pointer in `assets.json`.
#
# For documentation on test recording management in Python, please refer to
# https://github.com/Azure/azure-sdk-for-python/blob/main/doc/dev/tests.md#update-test-recordings
#
# For more information about how recording asset synchronization works more generally, please refer to
# https://github.com/Azure/azure-sdk-tools/blob/main/tools/test-proxy/documentation/asset-sync/README.md.


# Prepare command arguments
parser = argparse.ArgumentParser(description="Script for managing recording assets with Docker.")
parser.add_argument(
    "verb", help='The action verb for managing recordings: "locate", "push", "show", "restore", or "reset".'
)
parser.add_argument(
    "-p",
    "--path",
    default="assets.json",
    help='The *relative* path to your package\'s `assets.json` file. Default is "assets.json".',
)
args = parser.parse_args()

if args.verb and args.path:
    normalized_path = args.path.replace("\\", "/")

    repo_root = ascend_to_root(os.getcwd())
    tool_name = prepare_local_tool(repo_root)

    config_commands = {"locate", "show"}
    if args.verb in config_commands:
        command = f"{tool_name} config {args.verb.lower()} -a {normalized_path}"
    else:
        command = f"{tool_name} {args.verb.lower()} -a {normalized_path}"
    subprocess.run(
        shlex.split(command),
        stdout=sys.stdout,
        stderr=sys.stderr,
    )
