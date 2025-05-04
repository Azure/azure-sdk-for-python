# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import os
import argparse
import requests
import json
import logging
from github import Github, Auth
from ci_tools.functions import discover_targeted_packages

logging.getLogger().setLevel(logging.INFO)
root_dir = os.path.abspath(os.path.join(os.path.abspath(__file__), "..", "..", "..", ".."))

def get_build_info(service_directory: str, package_name: str) -> str:
    """Get the build info from the build link."""
    build_id = os.getenv("BUILD_BUILDID")
    timeline_link =f"https://dev.azure.com/azure-sdk/internal/_apis/build/builds/{build_id}/timeline?api-version=6.0"

    token = os.environ["SYSTEM_ACCESSTOKEN"]
    AUTH_HEADERS = {"Authorization": f"Bearer {token}"}

    try:
        # Make the API request
        response = requests.get(timeline_link, headers=AUTH_HEADERS)
        response_json = json.loads(response.text)
    
        for task in response_json["records"]:
            if "Run Pylint Next" in task["name"]:
                log_link = task['log']['url'] + "?api-version=6.0"
                # Get the log file from the build link
                log_output = requests.get(log_link, headers=AUTH_HEADERS)
                build_output = log_output.content.decode("utf-8")
                new_output = (build_output.split(f"next-pylint: commands[3]> python /mnt/vss/_work/1/s/eng/tox/run_pylint.py -t {service_directory} --next=True")[1]).split(f"ERROR:root:{package_name} exited with linting error")[0]
                return new_output
    except Exception as e:
        logging.error(f"Exception occurred while getting build info: {e}")
        return "Error getting build info"

    

def main(targeted_packages):
    for package in targeted_packages:
        # iterate through the packages and find if there is an issue associated with the package
        # there may be multiple packages in the targeted_packages list
        logging.info(f"Processing package: {package}")

        # update open GitHub issues matching the package pattern
        auth = Auth.Token(os.environ["GH_TOKEN"])
        g = Github(auth=auth)
        repo = g.get_repo("Azure/azure-sdk-for-python")

        package_name = package.split("/")[-1]
        logging.info(f"Searching for issues in repo {repo.name} for package {package_name}")
        
        for issue in repo.get_issues(state="open", labels=["pylint"], creator="azure-sdk"):
            if f"{package_name} needs linting updates for pylint version" in issue.title:
                logging.info(f"Found issue for package {package_name}: {issue.title}")
                build_info = get_build_info(package, package_name)

                template = (
                        f"\n\n**Pylint Errors:**"
                        f"\n\n{build_info}"
                        f"\n"
                        f"\n\n**How to fix:**"
                        f"\n**Note:** If you are a bot. Fix the issue by fixing the above pylint errors."
                    )
                if issue.body and "**Pylint Errors:**" not in issue.body:
                    # If the issue body does not contain the Pylint Errors section, add it
                    first_section = issue.body.split("**How to fix:**")[0]
                    new_body = first_section + template + "\n" + issue.body.split("**How to fix:**")[1]
                    issue.edit(body=new_body)
                logging.info(f"Updated issue #{issue.number} for package {package_name}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="""
    This script is the single point for all checks invoked by CI within this repo. It works in two phases.
        1. Identify which packages in the repo are in scope for this script invocation, based on a glob string and a service directory.
        2. Invoke one or multiple `tox` environments for each package identified as in scope.

    In the case of an environment invoking `pytest`, results can be collected in a junit xml file, and test markers can be selected via --mark_arg.
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

    parser.add_argument("--disablecov", help=("Flag. Disables code coverage."), action="store_true")

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

    parser.add_argument(
        "-i",
        "--injected-packages",
        dest="injected_packages",
        default="",
        help="Comma or space-separated list of packages that should be installed prior to dev_requirements. If local path, should be absolute.",
    )

    parser.add_argument(
        "--filter-type",
        dest="filter_type",
        default="Build",
        help="Filter type to identify eligible packages. for e.g. packages filtered in Build can pass filter type as Build,",
        choices=["Build", "Docs", "Regression", "Omit_management", "None"],
    )


    args = parser.parse_args()

    # We need to support both CI builds of everything and individual service
    # folders. This logic allows us to do both.
    if args.service and args.service != "auto":
        service_dir = os.path.join("sdk", args.service)
        target_dir = os.path.join(root_dir, service_dir)
    else:
        target_dir = root_dir

    logging.info(f"Beginning discovery for {args.service} and root dir {root_dir}. Resolving to {target_dir}.")

    if args.filter_type == "None":
        args.filter_type = "Build"
        compatibility_filter = False
    else:
        compatibility_filter = True

    targeted_packages = discover_targeted_packages(
        args.glob_string, target_dir, "", args.filter_type, compatibility_filter
    )

    if len(targeted_packages) == 0:
        logging.info(f"No packages collected for targeting string {args.glob_string} and root dir {root_dir}. Exit 0.")
        exit(0)

    main(targeted_packages)