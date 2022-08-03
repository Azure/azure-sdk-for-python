# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
import json
import os
import logging
import requests
import shlex
import sys
import time
import signal
from typing import TYPE_CHECKING

import pytest
import subprocess

from .config import PROXY_URL
from .helpers import is_live_and_not_recording
from .sanitizers import add_remove_header_sanitizer, set_custom_default_matcher, add_general_regex_sanitizer, _send_reset_request

if TYPE_CHECKING:
    from typing import Optional


_LOGGER = logging.getLogger()

CONTAINER_NAME = "ambitious_azsdk_test_proxy"
LINUX_IMAGE_SOURCE_PREFIX = "azsdkengsys.azurecr.io/engsys/testproxy-lin"
WINDOWS_IMAGE_SOURCE_PREFIX = "azsdkengsys.azurecr.io/engsys/testproxy-win"
CONTAINER_STARTUP_TIMEOUT = 6000
PROXY_MANUALLY_STARTED = os.getenv("PROXY_MANUAL_START", False)

REPO_ROOT = os.path.abspath(os.path.join(os.path.abspath(__file__), "..", "..", "..", ".."))
PROXY_CHECK_URL = PROXY_URL.rstrip("/") + "/Info/Available"
TOOL_ENV_VAR = "PROXY_PID"


def get_image_tag() -> str:
    """Gets the test proxy Docker image tag from the target_version.txt file in /eng/common/testproxy"""
    version_file_location = os.path.relpath("eng/common/testproxy/target_version.txt")
    version_file_location_from_root = os.path.abspath(os.path.join(REPO_ROOT, version_file_location))

    try:
        with open(version_file_location_from_root, "r") as f:
            image_tag = f.read().strip()

    # In live pipeline tests the root of the repo is in a different location relative to this file
    except FileNotFoundError:
        # REPO_ROOT only gets us to /sdk/{service}/{package}/.tox/whl on Windows
        # REPO_ROOT only gets us to /sdk/{service}/{package}/.tox/whl/lib on Ubuntu
        head, tail = os.path.split(REPO_ROOT)
        while tail != "sdk":
            head, tail = os.path.split(head)

        version_file_location_from_root = os.path.abspath(os.path.join(head, version_file_location))
        with open(version_file_location_from_root, "r") as f:
            image_tag = f.read().strip()

    return image_tag


def get_container_info() -> "Optional[dict]":
    """Returns a dictionary containing the test proxy container's information, or None if the container isn't present"""
    proc = subprocess.Popen(
        shlex.split("docker container ls -a --format '{{json .}}' --filter name=" + CONTAINER_NAME),
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        stdin=subprocess.DEVNULL,
    )

    output, stderr = proc.communicate()
    try:
        # This will succeed if we found a container with CONTAINER_NAME
        return json.loads(output)
    # We'll get a JSONDecodeError on Py3 (ValueError on Py2) if output is empty (i.e. there's no proxy container)
    except ValueError:
        # Didn't find a container with CONTAINER_NAME
        return None


def check_availability() -> None:
    """Attempts request to /Info/Available. If a test-proxy instance is responding, we should get a response."""
    try:
        response = requests.get(PROXY_CHECK_URL, timeout=60)
        return response.status_code
    # We get an SSLError if the container is started but the endpoint isn't available yet
    except requests.exceptions.SSLError as sslError:
        _LOGGER.debug(sslError)
        return 404
    except Exception as e:
        _LOGGER.error(e)
        return 404


def check_proxy_availability() -> None:
    """Waits for the availability of the test-proxy."""
    start = time.time()
    now = time.time()
    status_code = 0
    while now - start < CONTAINER_STARTUP_TIMEOUT and status_code != 200:
        status_code = check_availability()
        now = time.time()


def create_container() -> None:
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
            "docker container create -v '{}:{}/srv/testproxy' {} -p 5001:5001 -p 5000:5000 --name {} {}:{}".format(
                REPO_ROOT, path_prefix, linux_container_args, CONTAINER_NAME, image_prefix, image_tag
            )
        )
    )
    proc.communicate()


def start_test_proxy() -> None:
    """Starts the test proxy and returns when the proxy server is ready to receive requests. In regular use
    cases, this will auto-start the test-proxy docker container. In CI, or when environment variable TF_BUILD is set, this
    function will start the test-proxy .NET tool."""

    if not PROXY_MANUALLY_STARTED:
        if os.getenv("TF_BUILD"):
            _LOGGER.info("Starting the test proxy tool...")
            if check_availability() == 200:
                _LOGGER.debug("Tool is responding, exiting...")
            else:
                envname = os.getenv("TOX_ENV_NAME", "default")
                root = os.getenv("BUILD_SOURCESDIRECTORY", REPO_ROOT)
                log = open(os.path.join(root, "_proxy_log_{}.log".format(envname)), "a")

                _LOGGER.info("{} is calculated repo root".format(root))
                proc = subprocess.Popen(
                    shlex.split('test-proxy --storage-location="{}" --urls "{}"'.format(root, PROXY_URL)),
                    stdout=log,
                    stderr=log,
                )
                os.environ[TOOL_ENV_VAR] = str(proc.pid)
        else:
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

    # Wait for the proxy server to become available
    check_proxy_availability()
    # Call reset to ensure default matcher and sanitizers are set
    _send_reset_request({})


def stop_test_proxy() -> None:
    """Stops any running instance of the test proxy"""

    if not PROXY_MANUALLY_STARTED:
        if os.getenv("TF_BUILD"):
            _LOGGER.info("Stopping the test proxy tool...")

            try:
                os.kill(int(os.getenv(TOOL_ENV_VAR)), signal.SIGTERM)
            except:
                _LOGGER.debug("Unable to kill running test-proxy process.")

        else:
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
def test_proxy() -> None:
    """Pytest fixture to be used before running any tests that are recorded with the test proxy"""
    if is_live_and_not_recording():
        yield
    else:
        start_test_proxy()
        # Everything before this yield will be run before fixtures that invoke this one are run
        # Everything after it will be run after invoking fixtures are done executing
        yield
        stop_test_proxy()
