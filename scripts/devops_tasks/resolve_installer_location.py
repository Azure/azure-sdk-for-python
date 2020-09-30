import platform
import json
import argparse
import urllib
from urllib.request import urlopen
from packaging.version import Version
from packaging.version import parse
import pdb

# SOURCE OF THIS FILE: https://github.com/actions/python-versions
# this is the official mapping file for gh-actions to retrieve python installers
MANIFEST_LOCATION = "https://raw.githubusercontent.com/actions/python-versions/main/versions-manifest.json"

def get_installer_url(requested_version, version_manifest):
    current_plat = platform.system().tolower()

    print("Current Platform Is {}".format(platform.platform()))

    if version_manifest[requested_version]:
        found_installers = version_manifest[requested_version].files

        # filter anything that's not x64. we don't care.
        x64_installers = [file_def for file_def in found_installers if file_def["arch"] == "x64"]

        if current_plat == "windows":
            return [windows_installer for installer in x64_installers if installer["platform"] == "win32"][0]
        elif current_plat == "darwin":
            return [windows_installer for installer in x64_installers if installer["platform"] == current_plat][0]
        else:
            return [windows_installer for installer in x64_installers if installer["platform"] == "linux" and installer["platform_version"] =="18.04" ][0]


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Takes the incoming request and attempts to resolve the versionspec"
    )

    parser.add_argument(
        "versionSpec",
        nargs="?",
        help=(
            "The version specifier passed in to the UsePythonVersion extended task."
        ),
    )

    args = parser.parse_args()
    max_precached_version = Version('3.8.6')
    version_from_spec = Version(args.versionSpec)

    with urllib.request.urlopen(MANIFEST_LOCATION) as url:
        version_manifest = json.load(url)

    version_dict = { i['version'] : i for i in version_manifest }

    if version_from_spec > max_precached_version:
        print("Requested version {} is newer than versions pre-cached on agent. Invoking.")
        print("##vso[task.setvariable variable=_PythonNeedsInstall;]true")

        version_url = get_installer_url(args.versionSpec, version_dict)
        print("##vso[task.setvariable variable=_PythonInstallerLocation;]{}".format(version_url))
    else:
        print("##vso[task.setvariable variable=_PythonNeedsInstall;]false")



