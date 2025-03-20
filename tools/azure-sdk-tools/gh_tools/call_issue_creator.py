# iterater through the build logs and create issues for each failure by calling the issue creator
import os
import pathlib
import argparse
import requests
import json
from vnext_issue_creator import create_vnext_issue  # Import the issue creator function

def parse_arguments():
    parser = argparse.ArgumentParser(description="Iterate through build logs and create issues for each failure.")
    parser.add_argument("--log-dir", required=True, help="Directory containing build logs")
    parser.add_argument("--issue-creator", required=True, help="Path to the issue creator script")
    return parser.parse_args()

def find_failures(package_dir):
    failures = []
    build_id = os.getenv("BUILD_BUILDID")
    timeline_link = f"https://dev.azure.com/azure-sdk/internal/_apis/build/builds/{build_id}/timeline?api-version=6.0"

    token = os.environ["SYSTEM_ACCESSTOKEN"]
    AUTH_HEADERS = {"Authorization": f"Bearer {token}"}

    try:
        package_path = pathlib.Path(package_dir)
        package_name = package_path.name

        response = requests.get(timeline_link, headers=AUTH_HEADERS)
        response_json = json.loads(response.text)
    
        for task in response_json["records"]:
            if "Run Pylint Next" in task["name"]:
                log_link = task['log']['url'] + "?api-version=6.0"
                log_output = requests.get(log_link, headers=AUTH_HEADERS)
                build_output = log_output.content.decode("utf-8")
                if f"ERROR:root:{package_name} exited with linting error" in build_output:
                    print(f"Found failure in task: {task['name']}")
                    failures.append((task["name"], build_output))
    except Exception as e:
        print(f"Exception occurred while getting build info: {e}")

    return failures

def create_issues(failures):
    for file, failure in failures:
        create_vnext_issue(file, failure)

def main():
    args = parse_arguments()
    failures = find_failures(args.log_dir)
    if failures:
        create_issues(failures)
    else:
        print("No failures found in the logs.")

if __name__ == "__main__":
    main()