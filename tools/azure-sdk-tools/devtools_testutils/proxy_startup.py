# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

import os
import logging
import shlex
import sys
import time
import signal

import pytest
import subprocess

import urllib3

from .config import PROXY_URL
from .helpers import is_live_and_not_recording
from .sanitizers import add_remove_header_sanitizer, set_custom_default_matcher


_LOGGER = logging.getLogger()

CONTAINER_NAME = "ambitious_azsdk_test_proxy"
LINUX_IMAGE_SOURCE_PREFIX = "azsdkengsys.azurecr.io/engsys/testproxy-lin"
WINDOWS_IMAGE_SOURCE_PREFIX = "azsdkengsys.azurecr.io/engsys/testproxy-win"
CONTAINER_STARTUP_TIMEOUT = 60
PROXY_MANUALLY_STARTED = os.getenv("PROXY_MANUAL_START", False)

PROXY_CHECK_URL = PROXY_URL + "/Info/Available"
TOOL_ENV_VAR = "PROXY_PID"

discovered_roots = []

from urllib3 import PoolManager, Retry
from urllib3.exceptions import HTTPError

if os.getenv("REQUESTS_CA_BUNDLE"):
    http_client = PoolManager(
        retries=Retry(total=3, raise_on_status=False),
        cert_reqs="CERT_REQUIRED",
        ca_certs=os.getenv("REQUESTS_CA_BUNDLE"),
    )
else:
    http_client = PoolManager(retries=Retry(total=1, raise_on_status=False))


def get_image_tag(repo_root: str) -> str:
    """Gets the test proxy Docker image tag from the target_version.txt file in /eng/common/testproxy"""
    version_file_location = os.path.relpath("eng/common/testproxy/target_version.txt")
    version_file_location_from_root = os.path.abspath(os.path.join(repo_root, version_file_location))

    with open(version_file_location_from_root, "r") as f:
        image_tag = f.read().strip()

    return image_tag


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


def check_availability() -> None:
    """Attempts request to /Info/Available. If a test-proxy instance is responding, we should get a response."""
    try:
        response = http_client.request(method="GET", url=PROXY_CHECK_URL, timeout=10)
        return response.status
    # We get an SSLError if the container is started but the endpoint isn't available yet
    except urllib3.exceptions.SSLError as sslError:
        _LOGGER.debug(sslError)
        return 404
    except Exception as e:
        _LOGGER.debug(e)
        return 404


def check_system_proxy_availability() -> None:
    """Checks for SSL_CERT_DIR and REQUESTS_CA_BUNDLE environment variables."""
    ssl_cert = "SSL_CERT_DIR"
    ca_bundle = "REQUESTS_CA_BUNDLE"

    if PROXY_URL.startswith("https") and not os.environ.get(ssl_cert):
        _LOGGER.error(f"Please ensure the '{ssl_cert}' environment variable is correctly set in your test environment")
    if PROXY_URL.startswith("https") and not os.environ.get(ca_bundle):
        _LOGGER.error(f"Please ensure the '{ca_bundle}' environment variable is correctly set in your test environment")


def check_proxy_availability() -> None:
    """Waits for the availability of the test-proxy."""
    start = time.time()
    now = time.time()
    status_code = 0
    while now - start < CONTAINER_STARTUP_TIMEOUT and status_code != 200:
        status_code = check_availability()
        now = time.time()


def create_container(repo_root: str) -> None:
    """Creates the test proxy Docker container"""
    # Most of the time, running this script on a Windows machine will work just fine, as Docker defaults to Linux
    # containers. However, in CI, Windows images default to _Windows_ containers. We cannot swap them. We can tell
    # if we're in a CI build by checking for the environment variable TF_BUILD.
    delete_container()

    if sys.platform.startswith("win") and os.environ.get("TF_BUILD"):
        image_prefix = WINDOWS_IMAGE_SOURCE_PREFIX
        path_prefix = "C:"
        linux_container_args = ""
    else:
        image_prefix = LINUX_IMAGE_SOURCE_PREFIX
        path_prefix = ""
        linux_container_args = "--add-host=host.docker.internal:host-gateway"

    image_tag = get_image_tag(repo_root)
    subprocess.Popen(
        shlex.split(
            f"docker run --rm --name {CONTAINER_NAME} -v '{repo_root}:{path_prefix}/srv/testproxy' "
            f"{linux_container_args} -p 5001:5001 -p 5000:5000 {image_prefix}:{image_tag}"
        ),
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        stdin=subprocess.DEVNULL,
    )


def start_test_proxy(request) -> None:
    """Starts the test proxy and returns when the proxy server is ready to receive requests. In regular use
    cases, this will auto-start the test-proxy docker container. In CI, or when environment variable TF_BUILD is set, this
    function will start the test-proxy .NET tool."""

    repo_root = ascend_to_root(request.node.items[0].module.__file__)
    check_system_proxy_availability()

    if not PROXY_MANUALLY_STARTED:
        if os.getenv("TF_BUILD"):
            _LOGGER.info("Starting the test proxy tool...")
            if check_availability() == 200:
                _LOGGER.debug("Tool is responding, exiting...")
            else:
                envname = os.getenv("TOX_ENV_NAME", "default")
                root = os.getenv("BUILD_SOURCESDIRECTORY", repo_root)
                log = open(os.path.join(root, "_proxy_log_{}.log".format(envname)), "a")

                _LOGGER.info("{} is calculated repo root".format(root))

                os.environ["PROXY_ASSETS_FOLDER"] = os.path.join(root, "l", envname)
                if not os.path.exists(os.environ["PROXY_ASSETS_FOLDER"]):
                    os.makedirs(os.environ["PROXY_ASSETS_FOLDER"])

                proc = subprocess.Popen(
                    shlex.split('test-proxy start --storage-location="{}" -- --urls "{}"'.format(root, PROXY_URL)),
                    stdout=log,
                    stderr=log,
                )
                os.environ[TOOL_ENV_VAR] = str(proc.pid)
        else:
            _LOGGER.info("Starting the test proxy container...")
            create_container(repo_root)

    # Wait for the proxy server to become available
    check_proxy_availability()
    # remove headers from recordings if we don't need them, and ignore them if present
    # Authorization, for example, can contain sensitive info and can cause matching failures during challenge auth
    headers_to_ignore = "Authorization, x-ms-client-request-id, x-ms-request-id"
    add_remove_header_sanitizer(headers=headers_to_ignore)
    set_custom_default_matcher(excluded_headers=headers_to_ignore)


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
            subprocess.Popen(
                shlex.split(f"docker stop {CONTAINER_NAME}"),
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                stdin=subprocess.DEVNULL,
            )


@pytest.fixture(scope="session")
def test_proxy(request) -> None:
    """Pytest fixture to be used before running any tests that are recorded with the test proxy"""
    if is_live_and_not_recording():
        yield
    else:
        start_test_proxy(request)
        # Everything before this yield will be run before fixtures that invoke this one are run
        # Everything after it will be run after invoking fixtures are done executing
        yield
        stop_test_proxy()
