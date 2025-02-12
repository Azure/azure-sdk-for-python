import coverage
import argparse
import os
import json
import datetime

from ci_tools.parsing import ParsedSetup
from ci_tools.variables import in_ci
from ci_tools.environment_exclusions import is_check_enabled

def get_total_coverage(coverage_file: str) -> float:
    cov = coverage.Coverage(data_file=coverage_file)
    cov.load()
    report = cov.report()

    return report


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
        print(f"Total coverage for {pkg_details.name} is {total_coverage:.2f}%")

        if in_ci():
            metric_obj = {}
            metric_obj["value"] = total_coverage / 100
            metric_obj["name"] = "test_coverage_ratio"
            metric_obj["labels"] = { "package": pkg_details.name }
            metric_obj["timestamp"] = datetime.datetime.now(datetime.timezone.utc).isoformat()
            print(f'logmetric: {json.dumps(metric_obj)}')

    if is_check_enabled(args.target_package, "cov_enforcement", False):
        print("Coverage enforcement is enabled for this package.")

