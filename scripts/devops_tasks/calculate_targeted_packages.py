import argparse
import json
import os

from ci_tools.functions import discover_targeted_packages
from typing import Dict

root_dir = os.path.abspath(os.path.join(os.path.abspath(__file__), "..", "..", ".."))

def get_package_folder_from_path(file: str) -> str:
    parts = file.split("/")

    if len(parts) < 3:
        return ""
    return os.sep.join(parts[:3])

def register(idx: Dict[str, str], key: str, value: str) -> None:
    if key in idx:
        idx[key].append(value)
    else:
        idx[key] = [value]

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Calculate the targeted packages')
    parser.add_argument('input_json', type=str, help='Location of the diff.json file')
    
    args = parser.parse_args()


    with open(args.input_json, 'r') as f:
        diff = json.load(f)

    targeted_files = diff['ChangedFiles']
    
    all_packages = {} # {package: [file]}

    for file in targeted_files:
        # register(all_packages, , file)
        package = get_package_folder_from_path(file)
        if package:
            package_directory = os.path.join(root_dir, package)
            package_name = os.path.basename(package_directory)

            if os.path.exists(os.path.join(package_directory, "pyproject.toml")) or os.path.exists(os.path.join(package_directory, "setup.py")):
                register(all_packages, package_name, file)        

    packages = ",".join(all_packages.keys())
    print(f"This script sees the following packages [{packages}].")
    print(f"##vso[task.setvariable variable=TargetingString;]{packages}")

