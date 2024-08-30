import os
import argparse
import logging

root_dir = os.path.abspath(os.path.join(os.path.abspath(__file__), "..", "..", ".."))
test_tools_path = os.path.join(root_dir, "eng", "test_tools.txt")
dependency_tools_path = os.path.join(root_dir, "eng", "dependency_tools.txt")

from ci_tools.functions import discover_targeted_packages
from ci_tools.scenario.generation import replace_dev_reqs


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="""
This script is a single point of access to replace relative requirements within the repo with prebuilt versions.
"""
    )

    parser.add_argument(
        "glob_string",
        nargs="?",
        help=(
            "A comma separated list of glob strings that will target the top level directories that contain packages."
            'Examples: All = "azure-*", Single = "azure-keyvault", Targeted Multiple = "azure-keyvault,azure-mgmt-resource"'
        ),
    )

    parser.add_argument(
        "--service",
        help=("Name of service directory (under sdk/) to test. Example: --service applicationinsights"),
    )

    parser.add_argument(
        "-w",
        "--wheel_dir",
        dest="wheel_dir",
        help="Location for prebuilt artifacts (if any)",
    )

    args = parser.parse_args()

    # We need to support both CI builds of everything and individual service
    # folders. This logic allows us to do both.
    if args.service and args.service != "auto":
        service_dir = os.path.join("sdk", args.service)
        target_dir = os.path.join(root_dir, service_dir)
    else:
        target_dir = root_dir

    logging.info(f"Replacing local relative requirements in {test_tools_path} and {dependency_tools_path}.")

    logging.info(f"Beginning discovery for {args.service} and root dir {root_dir}. Resolving to {target_dir}.")

    targeted_packages = discover_targeted_packages(
        args.glob_string, target_dir, "", "Build", False
    )

    for package in targeted_packages:
        dev_requirements_path = os.path.join(package, "dev_requirements.txt")

        replace_dev_reqs(test_tools_path, package, args.wheel_dir)
        replace_dev_reqs(dependency_tools_path, package, args.wheel_dir)
        replace_dev_reqs(dev_requirements_path, package, args.wheel_dir)
