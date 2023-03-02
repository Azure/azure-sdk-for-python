import argparse
import json
import logging
from pathlib import Path
from subprocess import check_call
import shutil
import re

from .swaggertosdk.SwaggerToSdkCore import (
    CONFIG_FILE,
)
from .generate_sdk import generate
from .generate_utils import (
    get_package_names,
    init_new_service,
    update_servicemetadata,
    judge_tag_preview,
    format_samples,
    gen_dpg,
    dpg_relative_folder,
    gen_cadl
)

_LOGGER = logging.getLogger(__name__)


def del_outdated_folder(readme: str):
    python_readme = Path(readme).parent / "readme.python.md"
    if not python_readme.exists():
        _LOGGER.info(f"do not find python configuration: {python_readme}")
        return

    with open(python_readme, "r") as file_in:
        content = file_in.readlines()
    pattern = ["$(python-sdks-folder)", "azure-mgmt-"]
    is_multiapi = "multiapi: true" in ("".join(content))
    special_service = ["azure-mgmt-resource/"]
    for line in content:
        if all(p in line for p in pattern):
            # remove generated_samples
            sdk_folder = re.findall("[a-z]+/[a-z]+-[a-z]+-[a-z]+", line)[0]
            sample_folder = Path(f"sdk/{sdk_folder}/generated_samples") 
            if sample_folder.exists():
                shutil.rmtree(sample_folder)
                _LOGGER.info(f"remove sample folder: {sample_folder}")
            else:
                _LOGGER.info(f"sample folder does not exist: {sample_folder}")
            # remove old generated SDK code
            sdk_folder = re.findall("[a-z]+/[a-z]+-[a-z]+-[a-z]+/[a-z]+/[a-z]+/[a-z]+", line)[0]
            code_folder = Path(f"sdk/{sdk_folder}") 
            if is_multiapi and code_folder.exists():
                if any(item in str(sdk_folder) for item in special_service):
                    for folder in code_folder.iterdir():
                        if folder.is_dir():
                            shutil.rmtree(folder)
                else:
                    shutil.rmtree(code_folder)
                _LOGGER.info(f"remove code folder: {code_folder}")
            else:
                _LOGGER.info(f"code folder does not exist or it is not multiapi: {code_folder}")
            return

    _LOGGER.info(f"do not find {pattern} in {python_readme}")


def main(generate_input, generate_output):
    with open(generate_input, "r") as reader:
        data = json.load(reader)

    spec_folder = data["specFolder"]
    sdk_folder = "."
    result = {}
    python_tag = data.get("python_tag")
    package_total = set()
    spec_word = "readmeMd"
    if "relatedReadmeMdFiles" in data:
        readme_files = data["relatedReadmeMdFiles"]
    elif "relatedReadmeMdFile" in data:
        input_readme = data["relatedReadmeMdFile"]
        if "specification" in spec_folder:
            spec_folder = str(Path(spec_folder.split("specification")[0]))
        if "specification" not in input_readme:
            input_readme = str(Path("specification") / input_readme)
        readme_files = [input_readme]
    else:
        # ["specification/confidentialledger/ConfientialLedger"]
        if isinstance(data["relatedCadlProjectFolder"], str):
            readme_files = [data["relatedCadlProjectFolder"]]
        else:
            readme_files = data["relatedCadlProjectFolder"]
        spec_word = "cadlProject"

    for input_readme in readme_files:
        _LOGGER.info(f"[CODEGEN]({input_readme})codegen begin")
        is_cadl = False
        if "resource-manager" in input_readme:
            relative_path_readme = str(Path(spec_folder, input_readme))
            del_outdated_folder(relative_path_readme)
            config = generate(
                CONFIG_FILE,
                sdk_folder,
                [],
                relative_path_readme,
                spec_folder,
                force_generation=True,
                python_tag=python_tag,
            )
        elif "data-plane" in input_readme:
            config = gen_dpg(input_readme, data.get("autorestConfig", ""), dpg_relative_folder(spec_folder))
        else:
            config = gen_cadl(input_readme, spec_folder)
            is_cadl = True
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
                package_entry[spec_word] = [input_readme]
                package_entry["tagIsStable"] = not judge_tag_preview(sdk_code_path)
                result[package_name] = package_entry
            else:
                result[package_name]["path"].append(folder_name)
                result[package_name][spec_word].append(input_readme)

            # Generate some necessary file for new service
            init_new_service(package_name, folder_name, is_cadl)
            format_samples(sdk_code_path)

            # Update metadata
            try:
                update_servicemetadata(
                    sdk_folder,
                    data,
                    config,
                    folder_name,
                    package_name,
                    spec_folder,
                    input_readme,
                )
            except Exception as e:
                _LOGGER.info(f"fail to update meta: {str(e)}")

            # Setup package locally
            check_call(
                f"pip install --ignore-requires-python -e {sdk_code_path}",
                shell=True,
            )

    # remove duplicates
    for value in result.values():
        value["path"] = list(set(value["path"]))
        value[spec_word] = list(set(value[spec_word]))

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
