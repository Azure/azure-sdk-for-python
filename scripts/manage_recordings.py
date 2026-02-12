# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

# ============================================================================
# DEPRECATION NOTICE
# ============================================================================
# This script is deprecated and maintained only for backward compatibility.
# 
# Please use the 'azpysdk recording' command instead:
#
#   azpysdk recording push -p sdk/keyvault/azure-keyvault-keys/assets.json
#   azpysdk recording restore
#   azpysdk recording reset
#   azpysdk recording locate
#   azpysdk recording show
#
# For more information, run: azpysdk recording --help
# ============================================================================

import argparse
import os
import shlex
import subprocess
import sys
import warnings

from devtools_testutils.proxy_startup import (
    ascend_to_root,
    prepare_local_tool,
)

# Emit deprecation warning
warnings.warn(
    "\n"
    "=" * 80 + "\n"
    "DEPRECATION WARNING: This script is deprecated.\n"
    "Please use 'azpysdk recording' command instead.\n"
    "\n"
    "Examples:\n"
    "  azpysdk recording push -p sdk/keyvault/azure-keyvault-keys/assets.json\n"
    "  azpysdk recording restore\n"
    "  azpysdk recording reset\n"
    "\n"
    "Run 'azpysdk recording --help' for more information.\n"
    "=" * 80,
    DeprecationWarning,
    stacklevel=2,
)


TOOL_ENV_VAR = "PROXY_PID"


# This file contains a script for managing test recordings in the azure-sdk-assets repository.
#
# ============================================================================
# DEPRECATION NOTICE: This script is deprecated. Use 'azpysdk recording' instead.
# ============================================================================
#
# LEGACY INSTRUCTIONS FOR USE (for backward compatibility only):
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
#   NEW RECOMMENDED COMMAND:
#     `azpysdk recording push -p sdk/keyvault/azure-keyvault-keys/assets.json`
#
#   If this script is run from the directory containing an assets.json file, no path needs to be provided. For example,
#   with a working directory at the azure-keyvault-keys package root:
#
#     `python ../../../scripts/manage_recordings.py push`
#
#   NEW RECOMMENDED COMMAND:
#     `azpysdk recording push`
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
