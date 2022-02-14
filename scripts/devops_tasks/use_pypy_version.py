import platform
import argparse
import sys
import os
from packaging.version import Version
from packaging.version import InvalidVersion


MAX_INSTALLER_RETRY = 3
CURRENT_UBUNTU_VERSION = "20.04"  # full title is ubuntu-20.04
MAX_PRECACHED_VERSION = "3.10.0"
HOSTEDTOOLCACHE = os.getenv("AGENT_TOOLSDIRECTORY")


def walk_directory_for_pattern(spec):
    target_directory = os.path.normpath(HOSTEDTOOLCACHE)
    pypy_tool_cache = os.path.join(target_directory, "PyPy")

    print("Searching for {} in hosted tool cache {}".format(spec, target_directory))
    located_folders = []

    discovered_tool_folders = os.listdir(pypy_tool_cache)

    # walk the folders, filter to the patterns established
    for folder in discovered_tool_folders:
        path, foldername = os.path.split(folder)
        tool_version = Version(folder)

        if tool_version.major == spec.major and tool_version.minor == spec.minor:
            found_tool_location = os.path.join(pypy_tool_cache, folder)

            # logic for this location is cribbed directly from existing UsePythonVersion type script task
            # https://github.com/microsoft/azure-pipelines-tasks/blob/master/Tasks/UsePythonVersionV0/usepythonversion.ts#L32
            # Path should first be prepended by the install location, then by the executables directory.
            # The executable directory is <installDir>/bin on Ubuntu/Mac, <installDir>/Scripts on Windows
            # Additionally on windows, there are only x86 versions of the tool. on unix/mac there only exist x64 versions of the tool.
            if platform.system() == "Windows":
                install_path = os.path.join(found_tool_location, "x86")
                tool_path = os.path.join(install_path, "Scripts")

                located_folders.extend([install_path, tool_path])
            else:
                install_path = os.path.join(found_tool_location, "x64")
                tool_path = os.path.join(install_path, "bin")

                located_folders.extend([install_path, tool_path])

    return located_folders


def find_pypy_version(spec):
    discovered_locations = walk_directory_for_pattern(spec)

    if not discovered_locations:
        print(
            "Unable to locate a valid executable folder for {}. Examined folder {}".format(
                str(spec), HOSTEDTOOLCACHE
            )
        )
        exit(1)

    return discovered_locations


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="""This python script is used to discover and prepend a devops agent path with a specific pypy version. 
        It is not intended to be generic, and should not be be used in general "Use Python Version X" kind of situations."""
    )

    parser.add_argument(
        "version_spec",
        nargs="?",
        help=("The version specifier passed in to the UsePythonVersion extended task."),
    )

    args = parser.parse_args()
    max_precached_version = Version(MAX_PRECACHED_VERSION)
    try:
        version_from_spec = Version(args.version_spec.replace("pypy", ""))
    except InvalidVersion:
        print("Invalid Version '{}'. Exiting".format(args.version_spec))
        exit(1)

    discovered_installer_location = find_pypy_version(version_from_spec)

    print(
        "Path should be prepended with discovered location{} [{}]".format(
            ("s" if len(discovered_installer_location) >= 2 else ""),
            ", ".join(discovered_installer_location),
        )
    )

    for path in discovered_installer_location:
        print("##vso[task.prependpath]{}".format(path))
