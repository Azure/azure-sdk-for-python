import platform
import json
import argparse
import urllib
import urllib.request
from subprocess import check_call, CalledProcessError
import sys
import os
import zipfile
import tarfile
import time

from packaging.version import Version
from packaging.version import parse
from packaging.version import InvalidVersion

# SOURCE OF THIS FILE: https://github.com/actions/python-versions
# this is the official mapping file for gh-actions to retrieve python installers
MANIFEST_LOCATION = "https://raw.githubusercontent.com/actions/python-versions/main/versions-manifest.json"

MAX_INSTALLER_RETRY = 3
CURRENT_UBUNTU_VERSION = "18.04"  # full title is ubuntu-18.04
MAX_PRECACHED_VERSION = "3.9.0"

UNIX_INSTALL_ARRAY = ["sh", "setup.sh"]
WIN_INSTALL_ARRAY = ["pwsh", "setup.ps1"]


def download_installer(remote_path, local_path):
    retries = 0

    while True:
        try:
            urllib.request.urlretrieve(remote_path, local_path)
            break
        except Exception as e:
            print(e)
            retries += 1

            if retries >= MAX_INSTALLER_RETRY:
                print(
                    "Unable to recover after attempting to download {} {} times".format(
                        remote_path, retries
                    )
                )
                exit(1)
            time.sleep(10)


def install_selected_python_version(installer_url, installer_folder):
    current_plat = platform.system().lower()

    installer_folder = os.path.normpath(os.path.abspath(installer_folder))
    if not os.path.exists(installer_folder):
        os.mkdir(installer_folder)
    local_installer_ref = os.path.join(
        installer_folder,
        "local" + (".zip" if installer_folder.endswith("zip") else ".tar.gz"),
    )

    download_installer(installer_url, local_installer_ref)

    if current_plat == "windows":
        with zipfile.ZipFile(local_installer_ref, "r") as zip_file:
            zip_file.extractall(installer_folder)
        try:
            check_call(WIN_INSTALL_ARRAY, cwd=installer_folder)
        except CalledProcessError as err:
            print(err)
            exit(1)

    else:
        with tarfile.open(local_installer_ref) as tar_file:
            tar_file.extractall(installer_folder)
        try:
            check_call(UNIX_INSTALL_ARRAY, cwd=installer_folder)
        except CalledProcessError as err:
            print(err)
            exit(1)


def get_installer_url(requested_version, version_manifest):
    current_plat = platform.system().lower()

    print("Current Platform Is {}".format(platform.platform()))

    if version_manifest[requested_version]:
        found_installers = version_manifest[requested_version]["files"]

        # filter anything that's not x64. we don't care.
        x64_installers = [
            file_def for file_def in found_installers if file_def["arch"] == "x64"
        ]

        if current_plat == "windows":
            return [
                installer
                for installer in x64_installers
                if installer["platform"] == "win32"
            ][0]
        elif current_plat == "darwin":
            return [
                installer
                for installer in x64_installers
                if installer["platform"] == current_plat
            ][0]
        else:
            return [
                installer
                for installer in x64_installers
                if installer["platform"] == "linux"
                and installer["platform_version"] == CURRENT_UBUNTU_VERSION
            ][0]


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="This python script ensures that a requested python version is present in the hostedtoolcache on azure devops agents. It does this by retrieving new versions of python from the gh-actions python manifest."
    )

    parser.add_argument(
        "version_spec",
        nargs="?",
        help=("The version specifier passed in to the UsePythonVersion extended task."),
    )

    parser.add_argument(
        "--installer_folder",
        dest="installer_folder",
        help=(
            "The folder where the found installer will be extracted into and run from."
        ),
    )

    args = parser.parse_args()
    max_precached_version = Version(MAX_PRECACHED_VERSION)
    try:
        version_from_spec = Version(args.version_spec)
    except InvalidVersion:
        print("Invalid Version Spec. Skipping custom install.")
        exit(0)

    with urllib.request.urlopen(MANIFEST_LOCATION) as url:
        version_manifest = json.load(url)

    version_dict = {i["version"]: i for i in version_manifest}

    if version_from_spec > max_precached_version:
        print(
            "Requested version {} is newer than versions pre-cached on agent. Invoking.".format(
                args.version_spec
            )
        )
        install_file_details = get_installer_url(args.version_spec, version_dict)
        install_selected_python_version(
            install_file_details["download_url"], args.installer_folder
        )
