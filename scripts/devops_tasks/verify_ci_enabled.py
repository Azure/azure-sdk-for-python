#!/usr/bin/env python

# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import argparse
import sys
import os

from ci_tools.environment_exclusions import get_config_setting

root_dir = os.path.abspath(os.path.join(os.path.abspath(__file__), "..", "..", ".."))

def verify_ci_enabled(package_name: str, package_path: str) -> None:
    """Verifies that ci_enabled=false is not present in the package's pyproject.toml.
    This prevents releasing packages that have disabled their CI.
    """

    ci_enabled = get_config_setting(package_path, "ci_enabled")
    if ci_enabled is False:
        print(
            f"ci_enabled is set to false in {package_name}/pyproject.toml. " \
            "You must remove this setting before releasing the package."
        )
        sys.exit(1)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Verifies ci_enabled=true or is not present in the package's pyproject.toml, Called from DevOps YAML Pipeline"
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
    verify_ci_enabled(package_name, path_to_setup)
