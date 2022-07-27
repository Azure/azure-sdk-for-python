import argparse
from ci_tools.variables import discover_repo_root

from ci_tools.versioning.version_shared import (
    get_packages,
    set_version_py,
    set_dev_classifier,
    update_change_log,
)


def version_set_main():
    parser = argparse.ArgumentParser(
        description="Increments version for a given package name based on the released version"
    )

    parser.add_argument(
        "--package-name",
        required=True,
        help="name of package (accetps both formats: azure-service-package and azure_service_pacage)",
    )
    parser.add_argument("--new-version", required=True, help="new package version")
    parser.add_argument(
        "--service",
        required=True,
        help="name of the service for which to set the dev build id (e.g. keyvault)",
    )
    parser.add_argument("--release-date", help='date in the format "yyyy-MM-dd"')
    parser.add_argument(
        "--replace-latest-entry-title",
        help="indicate if to replace the latest changelog entry",
    )
    parser.add_argument(
        dest="glob_string",
        nargs="?",
        help=(
            "A comma separated list of glob strings that will target the top level directories that contain packages."
            'Examples: All = "azure-*", Single = "azure-keyvault", Targeted Multiple = "azure-keyvault,azure-mgmt-resource"'
        ),
    )
    parser.add_argument(
        "--repo",
        default=None,
        dest="repo",
        help=(
            "Where is the start directory that we are building against? If not provided, the current working directory will be used. Please ensure you are within the azure-sdk-for-python repository."
        ),
    )

    args = parser.parse_args()
    root_dir = args.repo or discover_repo_root()

    package_name = args.package_name.replace("_", "-")
    new_version = args.new_version

    packages = get_packages(args, package_name, root_dir=root_dir)

    package_map = {pkg.name: pkg for pkg in packages}

    if package_name not in package_map:
        raise ValueError("Package name not found: {}".format(package_name))

    target_package = package_map[package_name]

    print("{0}: {1} -> {2}".format(package_name, target_package.version, new_version))

    set_version_py(target_package.setup_filename, new_version)
    set_dev_classifier(target_package.setup_filename, new_version)
    update_change_log(
        target_package.setup_filename,
        new_version,
        args.service,
        args.package_name,
        False,
        args.replace_latest_entry_title,
        args.release_date,
        root_dir=root_dir,
    )
