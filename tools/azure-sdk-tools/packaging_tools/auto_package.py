import argparse
import json
import logging
import os
from pathlib import Path

from azure_devtools.ci_tools.git_tools import get_diff_file_list
from .package_utils import create_package, change_log_generate, extract_breaking_change

_LOGGER = logging.getLogger(__name__)


def main(generate_input, generate_output):
    with open(generate_input, "r") as reader:
        data = json.load(reader)
        _LOGGER.info(f"auto_package input: {data}")

    sdk_folder = "."
    result = {"packages": []}
    for package in data.values():
        package_name = package["packageName"]
        # Changelog
        last_version = ["first release"]
        if "azure-mgmt-" in package_name:
            md_output = change_log_generate(package_name, last_version)
        else:
            md_output = "data-plan skip changelog generation temporarily"
        package["changelog"] = {
            "content": md_output,
            "hasBreakingChange": "Breaking Changes" in md_output,
            "breakingChangeItems": extract_breaking_change(md_output),
        }
        package["version"] = last_version[-1]

        _LOGGER.info(f"[PACKAGE]({package_name})[CHANGELOG]:{md_output}")
        # Built package
        create_package(package_name)
        folder_name = package["path"][0]
        dist_path = Path(sdk_folder, folder_name, package_name, "dist")
        package["artifacts"] = [str(dist_path / package_file) for package_file in os.listdir(dist_path)]
        # Installation package
        package["installInstructions"] = {
            "full": "You can install the use using pip install of the artifacts.",
            "lite": f"pip install {package_name}",
        }
        # to distinguish with track1
        if "azure-mgmt-" in package_name:
            package["packageName"] = "track2_" + package["packageName"]
        for artifact in package["artifacts"]:
            if ".whl" in artifact:
                package["apiViewArtifact"] = artifact
                package["language"] = "Python"
                break
        result["packages"].append(package)

    with open(generate_output, "w") as writer:
        json.dump(result, writer)


def generate_main():
    """Main method"""

    parser = argparse.ArgumentParser(
        description="Build SDK using Autorest, offline version.",
        formatter_class=argparse.RawTextHelpFormatter,
    )
    parser.add_argument("generate_input", help="Generate input file path")
    parser.add_argument("generate_output", help="Generate output file path")
    parser.add_argument(
        "-v",
        "--verbose",
        dest="verbose",
        action="store_true",
        help="Verbosity in INFO mode",
    )
    parser.add_argument("--debug", dest="debug", action="store_true", help="Verbosity in DEBUG mode")
    parser.add_argument(
        "-c",
        "--codegen",
        dest="debug",
        action="store_true",
        help="Verbosity in DEBUG mode",
    )

    args = parser.parse_args()
    main_logger = logging.getLogger()
    logging.basicConfig()
    main_logger.setLevel(logging.DEBUG if args.verbose or args.debug else logging.INFO)

    main(args.generate_input, args.generate_output)


if __name__ == "__main__":
    generate_main()
