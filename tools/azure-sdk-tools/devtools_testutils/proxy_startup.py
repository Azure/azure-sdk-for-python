# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

import os
import logging
import shlex
import time
import signal
import platform
import shutil
import tarfile
from typing import Optional
import zipfile

import certifi
from dotenv import load_dotenv, find_dotenv
import pytest
import subprocess
from urllib3 import PoolManager, Retry
from urllib3.exceptions import SSLError

from ci_tools.variables import in_ci

from .config import PROXY_URL
from .helpers import is_live_and_not_recording
from .sanitizers import add_remove_header_sanitizer, set_custom_default_matcher


load_dotenv(find_dotenv())

_LOGGER = logging.getLogger()

CONTAINER_STARTUP_TIMEOUT = 60
PROXY_MANUALLY_STARTED = os.getenv("PROXY_MANUAL_START", False)

PROXY_CHECK_URL = PROXY_URL + "/Info/Available"
TOOL_ENV_VAR = "PROXY_PID"

AVAILABLE_TEST_PROXY_BINARIES = {
    "Windows": {
        "AMD64": {
            "system": "Windows",
            "machine": "AMD64",
            "file_name": "test-proxy-standalone-win-x64.zip",
            "executable": "Azure.Sdk.Tools.TestProxy.exe",
        },
    },
    "Linux": {
        "X86_64": {
            "system": "Linux",
            "machine": "X86_64",
            "file_name": "test-proxy-standalone-linux-x64.tar.gz",
            "executable": "Azure.Sdk.Tools.TestProxy",
        },
        "ARM64": {
            "system": "Linux",
            "machine": "ARM64",
            "file_name": "test-proxy-standalone-linux-arm64.tar.gz",
            "executable": "Azure.Sdk.Tools.TestProxy",
        },
    },
    "Darwin": {
        "X86_64": {
            "system": "Darwin",
            "machine": "X86_64",
            "file_name": "test-proxy-standalone-osx-x64.zip",
            "executable": "Azure.Sdk.Tools.TestProxy",
        },
        "ARM64": {
            "system": "Darwin",
            "machine": "ARM64",
            "file_name": "test-proxy-standalone-osx-arm64.zip",
            "executable": "Azure.Sdk.Tools.TestProxy",
        },
    },
}

PROXY_DOWNLOAD_URL = "https://github.com/Azure/azure-sdk-tools/releases/download/Azure.Sdk.Tools.TestProxy_{}/{}"

discovered_roots = []

if os.getenv("REQUESTS_CA_BUNDLE"):
    http_client = PoolManager(
        retries=Retry(total=3, raise_on_status=False),
        cert_reqs="CERT_REQUIRED",
        ca_certs=os.getenv("REQUESTS_CA_BUNDLE"),
    )
else:
    http_client = PoolManager(retries=Retry(total=1, raise_on_status=False))


def get_target_version(repo_root: str) -> str:
    """Gets the target test-proxy version from the target_version.txt file in /eng/common/testproxy"""
    version_file_location = os.path.relpath("eng/common/testproxy/target_version.txt")
    version_file_location_from_root = os.path.abspath(os.path.join(repo_root, version_file_location))

    with open(version_file_location_from_root, "r") as f:
        target_version = f.read().strip()

    return target_version


def get_downloaded_version(repo_root: str) -> Optional[str]:
    """Gets version from downloaded_version.txt within the local download folder"""

    downloaded_version_file = os.path.abspath(os.path.join(repo_root, ".proxy", "downloaded_version.txt"))

    if os.path.exists(downloaded_version_file):
        with open(downloaded_version_file, "r") as f:
            version = f.read().strip()
            return version
    else:
        return None


def ascend_to_root(start_dir_or_file: str) -> str:
    """Given a path, ascend until encountering a folder with a `.git` folder present within it. Return that directory.

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


def check_availability() -> None:
    """Attempts request to /Info/Available. If a test-proxy instance is responding, we should get a response."""
    try:
        response = http_client.request(method="GET", url=PROXY_CHECK_URL, timeout=10)
        return response.status
    # We get an SSLError if the container is started but the endpoint isn't available yet
    except SSLError as sslError:
        _LOGGER.debug(sslError)
        return 404
    except Exception as e:
        _LOGGER.debug(e)
        return 404


def check_certificate_location(repo_root: str) -> None:
    """Checks for SSL_CERT_DIR and REQUESTS_CA_BUNDLE environment variables.

    If both variables aren't set, this function configures the certificate bundle and sets these environment variables
    for the duration of the process.
    """
    ssl_cert_dir = "SSL_CERT_DIR"
    requests_ca_bundle = "REQUESTS_CA_BUNDLE"

    if PROXY_URL.startswith("https") and not (os.environ.get(ssl_cert_dir) and os.environ.get(requests_ca_bundle)):
        _LOGGER.info(
            "Missing SSL_CERT_DIR and/or REQUESTS_CA_BUNDLE environment variables. "
            "Setting these for the current session."
        )

        existing_root_pem = certifi.where()
        local_dev_cert = os.path.abspath(os.path.join(repo_root, 'eng', 'common', 'testproxy', 'dotnet-devcert.crt'))
        combined_filename = os.path.basename(local_dev_cert).split(".")[0] + ".pem"
        combined_folder = os.path.join(repo_root, '.certificate')
        combined_location = os.path.join(combined_folder, combined_filename)

        # If no local certificate folder exists, create one
        if not os.path.exists(combined_folder):
            _LOGGER.info("Missing a test proxy certificate under azure-sdk-for-python/.certificate. Creating one now.")
            os.mkdir(combined_folder)

        if not os.path.exists(combined_location):
            # Copy the dev cert's content into the new certificate bundle
            with open(local_dev_cert, "r") as f:
                data = f.read()
            with open(combined_location, "w") as f:
                f.write(data)

            # Copy the existing CA bundle contents into the repository's certificate bundle
            with open(existing_root_pem, "r") as f:
                content = f.readlines()
            with open(combined_location, "a") as f:
                f.writelines(content)

        if not os.environ.get(ssl_cert_dir):
            os.environ[ssl_cert_dir] = combined_folder
        if not os.environ.get(requests_ca_bundle):
            os.environ[requests_ca_bundle] = combined_location


def check_proxy_availability() -> None:
    """Waits for the availability of the test-proxy."""
    start = time.time()
    now = time.time()
    status_code = 0
    while now - start < CONTAINER_STARTUP_TIMEOUT and status_code != 200:
        status_code = check_availability()
        now = time.time()


def prepare_local_tool(repo_root: str) -> str:
    """Returns the path to a downloaded executable."""

    target_proxy_version = get_target_version(repo_root)

    download_folder = os.path.join(repo_root, ".proxy")

    system = platform.system()  # Darwin, Linux, Windows
    machine = platform.machine().upper()  # arm64, x86_64, AMD64

    if system in AVAILABLE_TEST_PROXY_BINARIES:
        available_for_system = AVAILABLE_TEST_PROXY_BINARIES[system]

        if machine in available_for_system:
            target_info = available_for_system[machine]

            downloaded_version = get_downloaded_version(repo_root)
            download_necessary = not downloaded_version == target_proxy_version

            if download_necessary:
                if os.path.exists(download_folder):
                    # cleanup the directory for re-download
                    shutil.rmtree(download_folder)
                os.makedirs(download_folder)

                download_url = PROXY_DOWNLOAD_URL.format(target_proxy_version, target_info["file_name"])
                download_file = os.path.join(download_folder, target_info["file_name"])

                http_client = PoolManager()
                with open(download_file, "wb") as out:
                    r = http_client.request("GET", download_url, preload_content=False)
                    shutil.copyfileobj(r, out)

                if download_file.endswith(".zip"):
                    with zipfile.ZipFile(download_file, "r") as zip_ref:
                        zip_ref.extractall(download_folder)

                if download_file.endswith(".tar.gz"):
                    with tarfile.open(download_file) as tar_ref:
                        tar_ref.extractall(download_folder)

                os.remove(download_file)  # Remove downloaded file after contents are extracted

                # Record downloaded version for later comparison with target version in repo
                with open(os.path.join(download_folder, "downloaded_version.txt"), "w") as f:
                    f.writelines([target_proxy_version])

            return os.path.abspath(os.path.join(download_folder, target_info["executable"])).replace("\\", "/")
        else:
            _LOGGER.error(f'There are no available standalone proxy binaries for platform "{machine}".')
            raise Exception(
                "Unable to download a compatible standalone proxy for the current platform. File an issue against "
                "Azure/azure-sdk-tools with this error."
            )
    else:
        _LOGGER.error(f'There are no available standalone proxy binaries for system "{system}".')
        raise Exception(
            "Unable to download a compatible standalone proxy for the current system. File an issue against "
            "Azure/azure-sdk-tools with this error."
        )


def start_test_proxy(request) -> None:
    """Starts the test proxy and returns when the proxy server is ready to receive requests.

    In regular use cases, this will auto-start the test-proxy docker container. In CI, or when environment variable
    TF_BUILD is set, this function will start the test-proxy .NET tool.
    """

    repo_root = ascend_to_root(request.node.items[0].module.__file__)
    check_certificate_location(repo_root)

    if not PROXY_MANUALLY_STARTED:
        if check_availability() == 200:
            _LOGGER.debug("Tool is responding, exiting...")
        else:
            root = os.getenv("BUILD_SOURCESDIRECTORY", repo_root)
            _LOGGER.info("{} is calculated repo root".format(root))

            # If we're in CI, allow for tox environment parallelization and write proxy output to a log file
            log = None
            if in_ci():
                envname = os.getenv("TOX_ENV_NAME", "default")
                log = open(os.path.join(root, "_proxy_log_{}.log".format(envname)), "a")

                os.environ["PROXY_ASSETS_FOLDER"] = os.path.join(root, "l", envname)
                if not os.path.exists(os.environ["PROXY_ASSETS_FOLDER"]):
                    os.makedirs(os.environ["PROXY_ASSETS_FOLDER"])

            if os.getenv("TF_BUILD"):
                _LOGGER.info("Starting the test proxy tool from dotnet tool cache...")
                tool_name = "test-proxy"
            else:
                _LOGGER.info("Downloading and starting standalone proxy executable...")
                tool_name = prepare_local_tool(root)

            # Always start the proxy with these two defaults set to allow SSL connection
            passenv = {
                "ASPNETCORE_Kestrel__Certificates__Default__Path": os.path.join(
                    root, "eng", "common", "testproxy", "dotnet-devcert.pfx"
                ),
                "ASPNETCORE_Kestrel__Certificates__Default__Password": "password",
            }
            # If they are already set, override what we give the proxy with what is in os.environ
            passenv.update(os.environ)

            proc = subprocess.Popen(
                shlex.split(f'{tool_name} start --storage-location="{root}" -- --urls "{PROXY_URL}"'),
                stdout=log or subprocess.DEVNULL,
                stderr=log or subprocess.STDOUT,
                env=passenv,
            )
            os.environ[TOOL_ENV_VAR] = str(proc.pid)

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
        _LOGGER.info("Stopping the test proxy tool...")

        try:
            os.kill(int(os.getenv(TOOL_ENV_VAR)), signal.SIGTERM)
        except:
            _LOGGER.debug("Unable to kill running test-proxy process.")


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
