import coverage
import argparse
import os
import json
import datetime
import logging

from typing import Optional

from ci_tools.parsing import ParsedSetup, get_config_setting
from ci_tools.variables import in_ci
from ci_tools.environment_exclusions import is_check_enabled
from coverage.exceptions import NoDataError

coveragerc_file = os.path.join(os.path.dirname(__file__), "tox.ini")

def get_total_coverage(coverage_file: str, package_name: str, repo_root: str) -> Optional[float]:

    cov = coverage.Coverage(data_file=coverage_file, config_file=coveragerc_file)
    cov.load()
    original = os.getcwd()
    report = 0.0
    try:
        os.chdir(repo_root)
        report = cov.report()
    except NoDataError as e:
        logging.warning(f"Package {package_name} did not generate any coverage output: {e}")
    except Exception as e:
        logging.error(f"An error occurred while generating the coverage report for {package_name}: {e}")
    finally:
        os.chdir(original)
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

    parser.add_argument(
        "-r",
        "--root",
        dest="repo_root",
        help="The root of the directory. Source paths are relative to this.",
        required=True,
    )

    args = parser.parse_args()
    pkg_details = ParsedSetup.from_path(args.target_package)

    possible_coverage_file = os.path.join(args.target_package, ".coverage")

    if os.path.exists(possible_coverage_file):
        total_coverage = get_total_coverage(possible_coverage_file, pkg_details.name, args.repo_root)
        if total_coverage is not None:
            # log the metric for reporting before doing anything else
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

            # todo: add relative coverage comparison after we generate eng/coverages.json file in main
            # when we add that, we will call the config setting relative_cov to check if this is enabled
            # there, we will only ever compare the baseline % against the generated %

            # as a fallback, we can always check the absolute coverage % against the config setting
            # if the config setting is not set, we will not enforce any coverage
            if is_check_enabled(args.target_package, "absolute_cov", False):
                logging.info("Coverage enforcement is enabled for this package.")

                # if this threshold is not set in config setting, the default will be very high
                cov_threshold = get_config_setting(args.target_package, "absolute_cov_percent", 95.0)
                if total_coverage < float(cov_threshold):
                    logging.error(
                        f"Coverage for {pkg_details.name} is below the threshold of {cov_threshold:.2f}% (actual: {total_coverage:.2f}%)"
                    )
                    # exit(1)


