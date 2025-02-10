import coverage
import argparse
import os

from ci_tools.parsing import ParsedSetup
from ci_tools.functions import discover_targeted_packages
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

    coverage_files = [os.path.join(args.target_package, f) for f in os.listdir(args.target_package) if f.startswith('.coverage')]

    for coverage_file in coverage_files:
        total_coverage = get_total_coverage(coverage_file)
        print(f"Total coverage for {pkg_details.name} is {total_coverage:.2f}%")

    if is_check_enabled(args.target_package, "cov_enforcement", False):
        print("Coverage enforcement is enabled for this package.")

