# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

import argparse
import os
import shlex
import sys

from devtools_testutils.config import PROXY_URL
from devtools_testutils.proxy_startup import (
    ascend_to_root,
    check_proxy_availability,
    prepare_local_tool,
    stop_test_proxy,
)

import subprocess


TOOL_ENV_VAR = "PROXY_PID"


# This file contains a script for managing test recordings in the azure-sdk-assets repository.
#
# INSTRUCTIONS FOR USE:
#
# - Set your working directory to be inside your local copy of the azure-sdk-for-python repository.
# - Run the following command:
#
#     `python {path to script}/manage_recordings.py {verb} -p {relative path to package's assets.json file}`
#
#   For example, with the root of the azure-sdk-for-python repo as the working directory, you can push modified
#   azure-keyvault-keys recordings to the assets repo with:
#
#     `python scripts/manage_recordings.py push -p sdk/keyvault/azure-keyvault-keys/assets.json`
#
# - In addition to "push", you can also use the "restore" or "reset" verbs in the same command format.
#
#   * push: pushes recording updates to a new assets repo tag and updates the tag pointer in `assets.json`.
#   * restore: fetches recordings from the assets repo, based on the tag pointer in `assets.json`.
#   * reset: discards any pending changes to recordings, based on the tag pointer in `assets.json`.
#
# For more information about how recording asset synchronization, please refer to
# https://github.com/Azure/azure-sdk-tools/blob/main/tools/test-proxy/documentation/asset-sync/README.md.


def start_test_proxy() -> str:
    """Starts the test proxy and returns when the tool is ready to receive requests, returning the tool's local name."""
    repo_root = ascend_to_root(os.getcwd())
    tool_name = prepare_local_tool(repo_root)

    # always start the proxy with these two defaults set
    passenv = {
        "ASPNETCORE_Kestrel__Certificates__Default__Path": os.path.join(
            repo_root, "eng", "common", "testproxy", "dotnet-devcert.pfx"
        ),
        "ASPNETCORE_Kestrel__Certificates__Default__Password": "password",
    }
    # if they are already set, override with what is in os.environ
    passenv.update(os.environ)

    proc = subprocess.Popen(
        shlex.split(f'{tool_name} start --storage-location="{repo_root}" -- --urls "{PROXY_URL}"'),
        env=passenv,
    )
    os.environ[TOOL_ENV_VAR] = str(proc.pid)
    check_proxy_availability()
    return tool_name


# Prepare command arguments
parser = argparse.ArgumentParser(description="Script for managing recording assets with Docker.")
parser.add_argument("verb", help='The action verb for managing recordings: "push", "restore", or "reset".')
parser.add_argument(
    "-p",
    "--path",
    default="assets.json",
    help='The *relative* path to your package\'s `assets.json` file. Default is "assets.json".',
)
args = parser.parse_args()

if args.verb and args.path:
    try:
        normalized_path = args.path.replace("\\", "/")

        print("\nStarting the test proxy...")
        tool_name = start_test_proxy()

        print(f"\nUpdating recordings with {args.verb.lower()} operation...")
        subprocess.run(
            shlex.split(
                f"{tool_name} {args.verb.lower()} -a {normalized_path}"
            ),
            stdout=sys.stdout,
            stderr=sys.stderr,
        )

    finally:
        print("\nStopping the test proxy...")
        stop_test_proxy()
