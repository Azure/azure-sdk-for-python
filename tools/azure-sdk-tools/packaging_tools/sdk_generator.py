import argparse
import json
import logging
from pathlib import Path
from subprocess import check_call

from .swaggertosdk.SwaggerToSdkCore import CONFIG_FILE, CONFIG_FILE_DPG
from .generate_sdk import generate
from .generate_utils import get_package_names, init_new_service, update_servicemetadata, judge_tag_preview

_LOGGER = logging.getLogger(__name__)


def main(generate_input, generate_output):
    with open(generate_input, "r") as reader:
        data = json.load(reader)
        _LOGGER.info(f"auto_package input: {data}")

    spec_folder = data["specFolder"]
    sdk_folder = "."
    result = {}
    package_total = set()
    
    input_readme = data["relatedReadmeMdFile"]
    relative_path_readme = str(Path(spec_folder, input_readme))
    _LOGGER.info(f"[CODEGEN]({input_readme})codegen begin")
    config_file = CONFIG_FILE if 'resource-manager' in input_readme else CONFIG_FILE_DPG
    config = generate(config_file, sdk_folder, [], relative_path_readme, spec_folder, force_generation=True)
    package_names = get_package_names(sdk_folder)
    _LOGGER.info(f"[CODEGEN]({input_readme})codegen end. [(packages:{str(package_names)})]")

    for folder_name, package_name in package_names:
        if package_name in package_total:
            continue

        package_total.add(package_name)
        sdk_code_path = str(Path(sdk_folder, folder_name, package_name))
        if package_name not in result:
            package_entry = {}
            package_entry["packageName"] = package_name
            package_entry["path"] = [folder_name]
            package_entry["tagIsStable"] = not judge_tag_preview(sdk_code_path)
            result[package_name] = package_entry
        else:
            result[package_name]["path"].append(folder_name)

        # Generate some necessary file for new service
        init_new_service(package_name, folder_name)

        # Update metadata
        try:
            update_servicemetadata(sdk_folder, data, config, folder_name, package_name, spec_folder, input_readme)
        except Exception as e:
            _LOGGER.info(str(e))

        # Setup package locally
        check_call(
            f"pip install --ignore-requires-python -e {sdk_code_path}",
            shell=True,
        )

    # remove duplicates
    for value in result.values():
        value["path"] = list(set(value["path"]))

    with open(generate_output, "w") as writer:
        json.dump(result, writer)


def generate_main():
    """Main method"""

    parser = argparse.ArgumentParser(
        description="Build SDK using Autorest, offline version.", formatter_class=argparse.RawTextHelpFormatter
    )
    parser.add_argument("generate_input", help="Generate input file path")
    parser.add_argument("generate_output", help="Generate output file path")
    parser.add_argument("-v", "--verbose", dest="verbose", action="store_true", help="Verbosity in INFO mode")
    parser.add_argument("--debug", dest="debug", action="store_true", help="Verbosity in DEBUG mode")
    parser.add_argument("-c", "--codegen", dest="debug", action="store_true", help="Verbosity in DEBUG mode")

    args = parser.parse_args()
    main_logger = logging.getLogger()
    logging.basicConfig()
    main_logger.setLevel(logging.DEBUG if args.verbose or args.debug else logging.INFO)

    main(args.generate_input, args.generate_output)


if __name__ == "__main__":
    generate_main()
