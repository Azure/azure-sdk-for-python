import argparse
import json
import logging
from pathlib import Path
import re
from subprocess import check_call

from .swaggertosdk.SwaggerToSdkCore import (
    CONFIG_FILE,
)
from azure_devtools.ci_tools.git_tools import get_diff_file_list
from .generate_sdk import generate

_LOGGER = logging.getLogger(__name__)
_SDK_FOLDER_RE = re.compile(r"^(sdk/[\w-]+)/(azure[\w-]+)/", re.ASCII)

DEFAULT_DEST_FOLDER = "./dist"


def get_package_names(sdk_folder):
    files = get_diff_file_list(sdk_folder)
    matches = {_SDK_FOLDER_RE.search(f) for f in files}
    package_names = {match.groups() for match in matches if match is not None}
    return package_names


def init_new_service(package_name, folder_name):
    ci = Path(folder_name, 'ci.yml')
    if not ci.exists():
        check_call(f'python -m packaging_tools --build-conf {package_name} -o {folder_name}', shell=True)
        with open('ci_template.yml', 'r') as file_in:
            content = file_in.readlines()
        name = package_name.replace('azure-', '').replace('mgmt-', '')
        content = [line.replace('MyService', name) for line in content]
        with open(str(ci), 'w') as file_out:
            file_out.writelines(content)


def main(generate_input, generate_output):
    with open(generate_input, "r") as reader:
        data = json.load(reader)

    spec_folder = data['specFolder']
    sdk_folder = "."
    result = {}
    package_total = set()
    for input_readme in data["relatedReadmeMdFiles"]:
        relative_path_readme = str(Path(spec_folder, input_readme))
        _LOGGER.info(f'[CODEGEN]({input_readme})codegen begin')
        generate(CONFIG_FILE,
                 sdk_folder,
                 [],
                 relative_path_readme,
                 spec_folder,
                 force_generation=True
                 )
        package_names = get_package_names(sdk_folder)
        _LOGGER.info(f'[CODEGEN]({input_readme})codegen end. [(packages:{str(package_names)})]')

        for folder_name, package_name in package_names:
            if package_name in package_total:
                continue

            package_total.add(package_name)
            if package_name not in result:
                package_entry = {}
                package_entry['packageName'] = package_name
                package_entry["path"] = [folder_name]
                package_entry['readmeMd'] = [input_readme]
                result[package_name] = package_entry
            else:
                result[package_name]["path"].append(folder_name)
                result[package_name]["readmeMd"].append(input_readme)

            # Generate some necessary file for new service
            init_new_service(package_name, folder_name)

            # Setup package locally
            check_call(f'pip install --ignore-requires-python -e {str(Path(sdk_folder, folder_name, package_name))}',
                       shell=True)


    # remove duplicates
    for value in result.values():
        value['path'] = list(set(value['path']))
        value['readmeMd'] = list(set(value['readmeMd']))

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
    parser.add_argument("-c", "--codegen",
                        dest="debug", action="store_true",
                        help="Verbosity in DEBUG mode")

    args = parser.parse_args()
    main_logger = logging.getLogger()
    logging.basicConfig()
    main_logger.setLevel(logging.DEBUG if args.verbose or args.debug else logging.INFO)

    main(args.generate_input, args.generate_output)


if __name__ == "__main__":
    generate_main()
