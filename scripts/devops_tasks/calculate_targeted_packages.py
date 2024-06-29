import argparse
import json
import os

from ci_tools.functions import discover_targeted_packages

root_dir = os.path.abspath(os.path.join(os.path.abspath(__file__), "..", "..", ".."))

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Calculate the targeted packages')
    parser.add_argument('input_json', type=str, help='Location of the diff.json file')
    
    args = parser.parse_args()


    with open(args.input_json, 'r') as f:
        diff = json.load(f)

    targeted_services = diff["ChangedServices"]
    all_packages = []

    for service in targeted_services:
        packages_for_service = discover_targeted_packages("*", target_root_dir=os.path.join(root_dir, "sdk", service), filter_type="Build", include_inactive=True)
        all_packages.extend([os.path.basename(p) for p in packages_for_service])

    packages = ", ".join(all_packages)

    print(f"This script sees the following packages [{packages}] for services {targeted_services}.")
    print(f"##vso[task.setvariable variable=TargetingString;]{packages}")