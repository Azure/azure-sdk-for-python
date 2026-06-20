import argparse
import logging

from ci_tools.parsing import ParsedSetup
from ci_tools.variables import in_ci
from ci_tools.environment_exclusions import is_check_enabled


def entrypoint() -> None:
    parser = argparse.ArgumentParser(
        description="""This utility checks the keywords of a targeted python package. If the keyword 'azure sdk' is not present, error.""",
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
        if not is_check_enabled(args.target, "verify_keywords"):
            logging.info(f"Package {pkg_details.name} opts-out of keyword verification check.")
            exit(0)

    if "azure sdk" not in pkg_details.keywords:
        print(
            f"Keyword 'azure sdk' not present in keywords for {pkg_details.name}. Before attempting publishing, ensure that package {pkg_details.name} has keyword 'azure sdk' present in the keyword array."
        )
        exit(1)
    else:
        exit(0)
