# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
import json
import os
import logging
import shlex
import sys
import time
from typing import TYPE_CHECKING

import pytest
import subprocess

if TYPE_CHECKING:
    from typing import Optional


_LOGGER = logging.getLogger()

CONTAINER_NAME = "ambitious_azsdk_test_proxy"
LINUX_IMAGE_SOURCE_PREFIX = "azsdkengsys.azurecr.io/engsys/testproxy-lin"
WINDOWS_IMAGE_SOURCE_PREFIX = "azsdkengsys.azurecr.io/engsys/testproxy-win"

REPO_ROOT = os.path.abspath(os.path.join(os.path.abspath(__file__), "..", "..", "..", ".."))


def get_image_tag():
    # type: () -> str
    """Gets the test proxy Docker image tag from the docker-start-proxy.ps1 script in /eng/common"""
    pwsh_script_location = os.path.abspath(
        os.path.join(REPO_ROOT, os.path.relpath("eng/common/testproxy/docker-start-proxy.ps1"))
    )

    image_tag = None
    with open(pwsh_script_location, "r") as f:
        for line in f:
            if line.startswith("$SELECTED_IMAGE_TAG"):
                image_tag_with_quotes = line.split()[-1]
                image_tag = image_tag_with_quotes.strip('"')

    return image_tag


def get_container_info():
    # type: () -> Optional[dict]
    """Returns a dictionary containing the test proxy container's information, or None if the container isn't present"""
    proc = subprocess.Popen(
        shlex.split("docker container ls -a --format '{{json .}}' --filter name=" + CONTAINER_NAME),
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )

    output, stderr = proc.communicate()
    try:
        return json.loads(output)
    # We'll get a JSONDecodeError on Py3 (ValueError on Py2) if output is empty (i.e. there's no proxy container)
    except ValueError:
        return None


def create_container():
    # type: () -> None
    """Creates the test proxy Docker container"""
    # Most of the time, running this script on a Windows machine will work just fine, as Docker defaults to Linux
    # containers. However, in CI, Windows images default to _Windows_ containers. We cannot swap them. We can tell
    # if we're in a CI build by checking for the environment variable TF_BUILD.
    if sys.platform.startswith("win") and os.environ.get("TF_BUILD"):
        image_prefix = WINDOWS_IMAGE_SOURCE_PREFIX
        path_prefix = "C:"
        linux_container_args = ""
    else:
        image_prefix = LINUX_IMAGE_SOURCE_PREFIX
        path_prefix = ""
        linux_container_args = "--add-host=host.docker.internal:host-gateway"

    image_tag = get_image_tag()
    proc = subprocess.Popen(
        shlex.split(
            "docker container create -v '{}:{}/etc/testproxy' {} -p 5001:5001 -p 5000:5000 --name {} {}:{}".format(
                REPO_ROOT, path_prefix, linux_container_args, CONTAINER_NAME, image_prefix, image_tag
            )
        )
    )
    proc.communicate()


def start_test_proxy():
    # type: () -> None
    """Starts the test proxy and returns when the proxy server is ready to receive requests"""
    _LOGGER.info("Starting the test proxy container...")

    container_info = get_container_info()
    if container_info:
        _LOGGER.debug("Found an existing instance of the test proxy container.")

        if container_info["State"] == "running":
            _LOGGER.debug("Proxy container is already running. Exiting...")
            return

    else:
        _LOGGER.debug("No instance of the test proxy container found. Attempting creation...")
        create_container()

    _LOGGER.debug("Attempting to start the test proxy container...")

    proc = subprocess.Popen(shlex.split("docker container start " + CONTAINER_NAME))
    proc.communicate()
    # wait for the proxy server to become available
    time.sleep(10)


def stop_test_proxy():
    # type: () -> None
    """Stops any running instance of the test proxy"""
    _LOGGER.info("Stopping the test proxy container...")

    container_info = get_container_info()
    if container_info:
        if container_info["State"] == "running":
            _LOGGER.debug("Found a running instance of the test proxy container; shutting it down...")

            proc = subprocess.Popen(shlex.split("docker container stop " + CONTAINER_NAME))
            proc.communicate()
    else:
        _LOGGER.debug("No running instance of the test proxy container found. Exiting...")


@pytest.fixture(scope="session")
def test_proxy():
    """Pytest fixture to be used before running any tests that are recorded with the test proxy"""
    start_test_proxy()
    yield
    stop_test_proxy()
