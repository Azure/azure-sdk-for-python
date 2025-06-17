# install `tools/azure-sdk-tools[build]` before running this script

import os, glob, json, argparse, logging

from typing import List, Tuple

from ci_tools.parsing import ParsedSetup
from ci_tools.functions import verify_package_classifiers

root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))


class ParsedPackageInfo:
    """Class that represents the parsed package information from a package_info.json file. Is used to extract the package name, version, and classifiers (from the local repo)"""

    name: str
    version: str
    classifiers: List[str]

    def __init__(self, name: str, version: str, classifiers: List[str]):
        self.name = name
        self.version = version
        self.classifiers = classifiers

    @classmethod
    def from_path(cls, specific_file: str):
        """
        Creates an instance of ParsedPackageInfo from a specific package_info.json file. Uses the local path to the file to parse the classifiers straight out of the local repo.
        """

        if not os.path.exists(specific_file):
            raise FileNotFoundError(f"File {specific_file} does not exist.")

        with open(specific_file, "r", encoding="utf-8") as f:
            data = json.load(f)

        name = data.get("Name")
        version = data.get("Version")
        directory_path = data.get("DirectoryPath")

        parsed = ParsedSetup.from_path(os.path.join(root, directory_path))

        return cls(name, version, parsed.classifiers)

    def __repr__(self) -> str:
        return f"ParsedPackageInfo(name={self.name}, version={self.version}, classifiers={self.classifiers})"


def get_targeted_packages(directory_path: str) -> List[ParsedPackageInfo]:
    """Get all packages from the package_info.json file."""

    package_info_files = glob.glob(os.path.join(directory_path, "**", "*.json"), recursive=True)
    packages = []

    for specific_file in package_info_files:
        try:
            package_info = ParsedPackageInfo.from_path(specific_file)
            packages.append(package_info)
        except FileNotFoundError as e:
            print(f"Skipping {specific_file}: {e}")

    return packages


if __name__ == "__main__":
    print(f"{root} is the root of the repository")

    parser = argparse.ArgumentParser(description="Verify package classifiers in package_info.json files")
    parser.add_argument("target_dir", help="Path to directory containing package_info.json files")
    args = parser.parse_args()

    package_failed = False

    packages = get_targeted_packages(args.target_dir)

    for package in packages:
        logging.info(
            f"Verifying package: {package.name} (version: {package.version}) with classifiers: {package.classifiers}"
        )
        classifier_result = verify_package_classifiers(package.name, package.version, package.classifiers)

        if not (classifier_result[0]):
            logging.error(classifier_result[1])
            package_filed = True

    if package_failed:
        logging.error("Some packages failed the classifier verification. Check outputs above.")
        exit(1)
