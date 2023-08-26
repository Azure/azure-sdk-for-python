import argparse
import logging

from ci_tools.parsing import ParsedSetup
from ci_tools.variables import in_ci
from ci_tools.environment_exclusions import is_check_enabled

def verify_classifiers() -> None:
    parser = argparse.ArgumentParser(
        description="""This is the primary entrypoint for the "build" action. This command is used to build any package within the azure-sdk-for-python repository.""",
    )

    parser.add_argument(
        "-t",
        "--target",
        dest="target",
        help=("Directory containing a setup.py"),
    )

    args = parser.parse_args()

    pkg_details = ParsedSetup.from_path(args.target)

    if in_ci():
        if not is_check_enabled(args.target_package, "pylint"):
            logging.info(
                f"Package {pkg_details.name} opts-out of pylint check."
            )
            exit(0)

    if "azure-sdk" not in pkg_details.classifiers:
        print(f"Classifier 'azure-sdk' not present in classifers for {pkg_details.name}. Before attempting publishing, ensure that package {pkg_details.name} has classifier 'azure-sdk' present in the classifier set.")
        exit(1)
    else:
        exit(0)

