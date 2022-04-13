import os
import argparse

root_dir = os.path.abspath(os.path.join(os.path.abspath(__file__), "..", "..", ".."))

from common_tasks import find_packages_missing_on_pypi

if __name__ == "__main__":

    parser = argparse.ArgumentParser(
        description="This script is used during a release stage to prevent releasing packages on PyPI with missing dependencies."
    )

    parser.add_argument(
        "--package-name",
        required=True,
        help="name of package (accepts both formats: azure-service-package and azure_service_package)",
    )
    parser.add_argument(
        "--service",
        required=True,
        help="name of the service for which to set the dev build id (e.g. keyvault)",
    )

    args = parser.parse_args()

    package_name = args.package_name.replace("_", "-")
    path_to_setup = os.path.join(root_dir, "sdk", args.service, package_name, "setup.py")

    missing_packages = find_packages_missing_on_pypi(path_to_setup)

    if missing_packages:
        exit(1)
