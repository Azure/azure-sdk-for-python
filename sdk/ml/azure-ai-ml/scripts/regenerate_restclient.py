# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

from argparse import ArgumentParser
import logging
import os
from pathlib import Path
from platform import system
import subprocess
import sys
import time
from urllib.request import urlopen

from utils import print_blue, run_command

module_logger = logging.getLogger(__name__)

MULTI_API_TAG = "multiapi"


def download_file(from_url: str, to_path: Path, with_file_name: str) -> None:
    print_blue(f"- Downloading {with_file_name} from {from_url} to {to_path}")

    try:
        response = urlopen(from_url)
    except Exception:
        sys.exit(
            f"Connection error while trying to download file from {from_url}. Please try running the script again."
        )
    with open(f"{to_path}/{with_file_name}", "w") as f:
        f.write(response.read().decode("utf-8"))


def regenerate_restclient(api_tag, verbose):
    readme_path = Path("./swagger/machinelearningservices/resource-manager/readme.md")
    restclient_path = Path("./azure/ai/ml/_restclient/")
    command_args = {"shell": system() == "Windows", "stream_stdout": verbose}

    api_tag_arg = api_tag.lower() if api_tag else None
    if not api_tag_arg or api_tag_arg == MULTI_API_TAG:
        tag_arg = f"--{MULTI_API_TAG}"
    else:
        tag_arg = f"--tag={api_tag_arg}"

    commands = [
        "autorest",
        "--python",
        "--track2",
        "--version=3.6.2",
        "--use=@autorest/python@5.12.6",
        f"--python-sdks-folder={restclient_path.absolute()}",
        "--package-version=0.1.0",
        tag_arg,
        str(readme_path.absolute()),
        "--modelerfour.lenient-model-deduplication",
        '--title="Azure Machine Learning Workspaces"',
    ]
    print_blue(f"- Running autorest command: {' '.join(commands)}")
    run_command(
        commands,
        throw_on_retcode=True,
        **command_args,
    )



if __name__ == "__main__":

    parser = ArgumentParser()

    parser.add_argument(
        "-a",
        "--api-tag",
        required=False,
        help="""Specifies which API to generate using autorest. If not supplied, all APIs are targeted.
            Must match the name of a tag in the sdk/ml/azure-ai-ml/swagger/machinelearningservices/resource-manager/readme.md file.""",
    )
    parser.add_argument("-v", "--verbose", action="store_true", required=False, help="turn on verbose output")

    args = parser.parse_args()

    regenerate_restclient(args.api_tag, args.verbose)
