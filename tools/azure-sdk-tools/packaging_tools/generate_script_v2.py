import argparse
import json
import glob
import logging
import os
from pathlib import Path
import re
import runpy
from subprocess import check_call
import tempfile

from .swaggertosdk.SwaggerToSdkCore import (
    CONFIG_FILE,
)
from azure_devtools.ci_tools.git_tools import get_diff_file_list
from .generate_sdk import generate
from .change_log import main as change_log_main

_LOGGER = logging.getLogger(__name__)
_SDK_FOLDER_RE = re.compile(r"^(sdk/[\w-]+)/(azure[\w-]+)/", re.ASCII)


DEFAULT_DEST_FOLDER = "./dist"

def create_package(name, dest_folder=DEFAULT_DEST_FOLDER):
    # a package will exist in either one, or the other folder. this is why we can resolve both at the same time.
    absdirs = [os.path.dirname(package) for package in (glob.glob('{}/setup.py'.format(name)) + glob.glob('sdk/*/{}/setup.py'.format(name)))]

    absdirpath = os.path.abspath(absdirs[0])
    check_call(['python', 'setup.py', 'bdist_wheel', '-d', dest_folder], cwd=absdirpath)
    check_call(['python', 'setup.py', "sdist", "--format", "zip", '-d', dest_folder], cwd=absdirpath)


def get_package_names(sdk_folder):
    files = get_diff_file_list(sdk_folder)
    matches = {_SDK_FOLDER_RE.search(f) for f in files}
    package_names = {match.groups() for match in matches if match is not None}
    return package_names


def main(generate_input, generate_output):
    with open(generate_input, "r") as reader:
        data = json.load(reader)

    spec_folder = data['specFolder']
    sdk_folder = "."
    input_readme = data["relatedReadmeMdFiles"][0]

    relative_path_readme = str(Path(spec_folder, input_readme))

    generate(
        CONFIG_FILE,
        sdk_folder,
        [],
        relative_path_readme,
        spec_folder,
        force_generation=True
    )
    package_names = get_package_names(sdk_folder)
    result = {
        "packages": []
    }

    for folder_name, package_name in package_names:
        package_entry = {}
        package_entry['packageName'] = package_name
        package_entry["path"] = [folder_name]
        package_entry['readmeMd'] = data["relatedReadmeMdFiles"]

        # Changelog
        md_output = change_log_main(f"{package_name}:pypi", f"{package_name}:latest")
        package_entry["changelog"] = {
            "content": md_output,
            "hasBreakingChange": "Breaking changes" in md_output
        },
        # Built package
        create_package(package_name)
        dist_path = Path(sdk_folder, folder_name, package_name, "dist")
        package_entry["artifacts"] = [
            str(dist_path / package_file) for package_file in os.listdir(dist_path)
        ]
        # Installation package
        package_entry["installInstructions"] = {
            "full": "You can install the use using pip install of the artificats.",
            "lite": "pip install <package-name>"
        },
        package_entry["result"]: "success"

        result['packages'].append(package_entry)

    with open(generate_output, "w") as writer:
        json.dump(result, writer)


def generate_main():
    """Main method"""

    parser = argparse.ArgumentParser(
        description='Build SDK using Autorest, offline version.',
        formatter_class=argparse.RawTextHelpFormatter)
    parser.add_argument('generate_input',
                        help='Generate input file path')
    parser.add_argument('generate_output',
                        help='Generate output file path')
    parser.add_argument("-v", "--verbose",
                        dest="verbose", action="store_true",
                        help="Verbosity in INFO mode")
    parser.add_argument("--debug",
                        dest="debug", action="store_true",
                        help="Verbosity in DEBUG mode")

    args = parser.parse_args()
    main_logger = logging.getLogger()
    if args.verbose or args.debug:
        logging.basicConfig()
        main_logger.setLevel(logging.DEBUG if args.debug else logging.INFO)

    main(args.generate_input, args.generate_output)

if __name__ == "__main__":
    generate_main()
