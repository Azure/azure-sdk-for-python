import coverage
import argparse
import os
import json
import datetime
import logging

from typing import Optional

from ci_tools.parsing import ParsedSetup
from ci_tools.variables import in_ci
from ci_tools.environment_exclusions import is_check_enabled
from coverage.exceptions import NoDataError

def get_total_coverage(coverage_file: str) -> Optional[float]:
    cov = coverage.Coverage(data_file=coverage_file)
    cov.load()
    try:
        report = cov.report()
        return report
    except NoDataError as e:
        logging.warning(f"This package did not generate any coverage output: {e}")
        return None
    except Exception as e:
        logging.error(f"An error occurred while generating the coverage report: {e}")
        return None

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Check coverage for a package."
    )

    parser.add_argument(
        "-t",
        "--target",
        dest="target_package",
        help="The target package directory on disk. This script looks for a .coverage file under <target_package> directory.",
        required=True,
    )

    args = parser.parse_args()
    pkg_details = ParsedSetup.from_path(args.target_package)

    possible_coverage_file = os.path.join(args.target_package, ".coverage")

    if os.path.exists(possible_coverage_file):
        total_coverage = get_total_coverage(possible_coverage_file)
        if total_coverage is not None:
            logging.info(f"Total coverage for {pkg_details.name} is {total_coverage:.2f}%")

            if in_ci():
                metric_obj = {}
                metric_obj["value"] = total_coverage / 100
                metric_obj["name"] = "test_coverage_ratio"
                metric_obj["labels"] = { "package": pkg_details.name }
                metric_obj["timestamp"] = datetime.datetime.now(datetime.timezone.utc).isoformat()
                # normally we logging.info anywhere we need to output, but these logmetric statements
                # need to be the sole value on the line, as the logmetric log parsing doesn't allow prefixes
                # before the 'logmetric' start string.
                print(f'logmetric: {json.dumps(metric_obj)}')

    if is_check_enabled(args.target_package, "cov_enforcement", False):
        logging.info("Coverage enforcement is enabled for this package.")

