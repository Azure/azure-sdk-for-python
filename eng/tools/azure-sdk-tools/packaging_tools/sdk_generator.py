import sys
import time
from typing import List, Any
import argparse
import json
import logging
from pathlib import Path
from subprocess import check_call
import shutil
import re
import os
from functools import partial
import multiprocessing

try:
    # py 311 adds this library natively
    import tomllib as toml
except:
    # otherwise fall back to pypi package tomli
    import tomli as toml
import tomli_w as tomlw

from .swaggertosdk.SwaggerToSdkCore import (
    CONFIG_FILE,
)
from .generate_sdk import generate
from .generate_utils import (
    get_package_names,
    generate_packaging_files,
    update_servicemetadata,
    judge_tag_preview,
    format_samples_and_tests,
    gen_dpg,
    dpg_relative_folder,
    gen_typespec,
    del_outdated_generated_files,
)
from .conf import CONF_NAME
from .package_utils import create_package, change_log_generate, extract_breaking_change, get_version_info, check_file
from .sdk_changelog import main as changelog_generate

logging.basicConfig(
    stream=sys.stdout,
    format="[%(levelname)s] %(message)s",
)
_LOGGER = logging.getLogger(__name__)


def execute_func_with_timeout(func, timeout: int = 900) -> Any:
    """Execute function with timeout"""
    return multiprocessing.Pool(processes=1).apply_async(func).get(timeout)


# return relative path like: network/azure-mgmt-network
def extract_sdk_folder(python_md: List[str]) -> str:
    pattern = ["$(python-sdks-folder)", "azure-mgmt-"]
    for line in python_md:
        if all(p in line for p in pattern):
            return re.findall("[a-z]+/[a-z]+-[a-z]+-[a-z]+[-a-z]*", line)[0]
    return ""


# readme: ../azure-rest-api-specs/specification/paloaltonetworks/resource-manager/readme.md or absolute path
def get_readme_python_content(readme: str) -> List[str]:
    python_readme = Path(readme).parent / "readme.python.md"
    if not python_readme.exists():
        _LOGGER.info(f"do not find python configuration: {python_readme}")
        return []

    with open(python_readme, "r") as file_in:
        return file_in.readlines()


# readme: ../azure-rest-api-specs/specification/paloaltonetworks/resource-manager/readme.md
def del_outdated_files(readme: str):
    content = get_readme_python_content(readme)
    sdk_folder = extract_sdk_folder(content)
    if sdk_folder:
        # remove tsp-location.yaml
        tsp_location = Path(f"sdk/{sdk_folder}/tsp-location.yaml")
        if tsp_location.exists():
            os.remove(str(tsp_location))
            _LOGGER.info(f"remove tsp-location.yaml: {tsp_location}")
        # remove generated_samples
        sample_folder = Path(f"sdk/{sdk_folder}/generated_samples")
        if sample_folder.exists():
            # rdbms is generated from different swagger folder
            if "azure-mgmt-rdbms" not in str(sample_folder):
                shutil.rmtree(sample_folder)
                _LOGGER.info(f"remove sample folder: {sample_folder}")
            else:
                _LOGGER.info(f"we don't remove sample folder for rdbms")
        else:
            _LOGGER.info(f"sample folder does not exist: {sample_folder}")
    else:
        _LOGGER.info(f"do not find valid sdk_folder in readme.python.md")


def main(generate_input, generate_output):
    with open(generate_input, "r") as reader:
        data = json.load(reader)

    spec_folder = data.get("specFolder", "")
    sdk_folder = "."
    result = {}
    python_tag = data.get("python_tag")
    package_total = set()
    readme_and_tsp = [("relatedReadmeMdFiles", item) for item in data.get("relatedReadmeMdFiles", [])] + [
        ("relatedTypeSpecProjectFolder", item) for item in data.get("relatedTypeSpecProjectFolder", [])
    ]
    run_in_pipeline = data.get("runMode") is not None
    for input_type, readme_or_tsp in readme_and_tsp:
        _LOGGER.info(f"[CODEGEN]({readme_or_tsp})codegen begin")
        config = None
        try:
            code_generation_start_time = time.time()
            if input_type == "relatedTypeSpecProjectFolder":
                if run_in_pipeline:
                    del_outdated_generated_files(str(Path(spec_folder, readme_or_tsp)))
                config = gen_typespec(
                    readme_or_tsp,
                    spec_folder,
                    data["headSha"],
                    data["repoHttpsUrl"],
                    run_in_pipeline,
                    data.get("apiVersion"),
                )
            elif "resource-manager" in readme_or_tsp:
                relative_path_readme = str(Path(spec_folder, readme_or_tsp))
                del_outdated_files(relative_path_readme)
                config = generate(
                    CONFIG_FILE,
                    sdk_folder,
                    [],
                    relative_path_readme,
                    spec_folder,
                    force_generation=True,
                    python_tag=python_tag,
                )
            else:
                config = gen_dpg(readme_or_tsp, data.get("autorestConfig", ""), dpg_relative_folder(spec_folder))
            _LOGGER.info(f"code generation cost time: {int(time.time() - code_generation_start_time)} seconds")
        except Exception as e:
            _LOGGER.error(f"Fail to generate sdk for {readme_or_tsp}: {str(e)}")
            for hint_message in [
                "======================================= What Can I do (begin) ========================================================================",
                f"Fail to generate sdk for {readme_or_tsp}. If you are from service team, please first check if the failure happens only to Python automation, or for all SDK automations. ",
                "If it happens for all SDK automations, please double check your Swagger / Typespec, and check whether there is error in ModelValidation and LintDiff. ",
                "If it happens to Python alone, you can open an issue to https://github.com/microsoft/typespec/issues. Please include the link of this Pull Request in the issue.",
                "======================================= What Can I do (end) =========================================================================",
            ]:
                _LOGGER.error(hint_message)
            if len(readme_and_tsp) == 1:
                raise e

        # folder_name: "sdk/containerservice"; package_name: "azure-mgmt-containerservice"
        package_names = get_package_names(sdk_folder)
        spec_word = "readmeMd" if "readme.md" in readme_or_tsp else "typespecProject"
        for folder_name, package_name in package_names:
            if package_name in package_total:
                continue

            _LOGGER.info(
                f"[CODEGEN]({readme_or_tsp})codegen end and new package '{folder_name}/{package_name}' generated"
            )

            # remove additional files when we roll back generation to Swagger
            # NOTE: After we convert to Typespec completely, we could remove this logic block
            if "readme.md" in readme_or_tsp:
                for file_name in ["tsp-location.yaml", "_metadata.json"]:
                    file_path = Path(sdk_folder, folder_name, file_name)
                    if file_path.exists():
                        os.remove(str(file_path))
                        _LOGGER.info(f"remove additional file when roll back to swagger: {file_path}")

            try:
                package_total.add(package_name)
                sdk_code_path = str(Path(sdk_folder, folder_name, package_name))
                if package_name not in result:
                    package_entry = {}
                    package_entry["packageName"] = package_name
                    package_entry["path"] = [folder_name]
                    package_entry[spec_word] = [readme_or_tsp]
                    package_entry["tagIsStable"] = not judge_tag_preview(sdk_code_path, package_name)
                    package_entry["targetReleaseDate"] = data.get("targetReleaseDate", "")
                    package_entry["allowInvalidNextVersion"] = data.get("allowInvalidNextVersion", False)
                    result[package_name] = package_entry
                else:
                    result[package_name]["path"].append(folder_name)
                    result[package_name][spec_word].append(readme_or_tsp)
            except Exception as e:
                _LOGGER.error(f"Fail to process package {package_name} in {readme_or_tsp}: {str(e)}")
                continue

            # Generate packaging files
            try:
                generate_packaging_files(package_name, folder_name)
            except Exception as e:
                _LOGGER.warning(f"Fail to generate packaging files for {package_name} in {readme_or_tsp}: {str(e)}")

            # format samples and tests
            try:
                format_samples_and_tests(sdk_code_path)
            except Exception as e:
                _LOGGER.warning(f"Fail to format samples and tests for {package_name} in {readme_or_tsp}: {str(e)}")

            # Update metadata
            try:
                if config is not None:
                    update_servicemetadata(
                        sdk_folder,
                        data,
                        config,
                        folder_name,
                        package_name,
                        spec_folder,
                        readme_or_tsp,
                    )
                else:
                    _LOGGER.warning(f"Skip metadata update for {package_name} as config is not available")
            except Exception as e:
                _LOGGER.warning(f"Fail to update meta: {str(e)}")

            # Setup package locally
            try:
                check_call(
                    f"pip install --ignore-requires-python -e {sdk_code_path}",
                    shell=True,
                )
            except Exception as e:
                _LOGGER.warning(f"Fail to setup package {package_name} in {readme_or_tsp}: {str(e)}")

            # Changelog generation
            changelog_generate(Path(sdk_code_path).absolute(), enable_changelog=data.get("enableChangelog", True), package_result=result[package_name])

            # Generate ApiView
            if data.get("runMode") in ["spec-pull-request"]:
                apiview_start_time = time.time()
                try:
                    package_path = Path(sdk_folder, folder_name, package_name)
                    check_call(
                        [
                            "python",
                            "-m",
                            "pip",
                            "install",
                            "-r",
                            "../../../eng/apiview_reqs.txt",
                            "--index-url=https://pkgs.dev.azure.com/azure-sdk/public/_packaging/azure-sdk-for-python/pypi"
                            "/simple/",
                        ],
                        cwd=package_path,
                        timeout=600,
                    )
                    cmds = ["apistubgen", "--pkg-path", "."]
                    cross_language_mapping_path = Path(package_path, "apiview-properties.json")
                    if cross_language_mapping_path.exists():
                        cmds.extend(["--mapping-path", str(cross_language_mapping_path)])
                    check_call(cmds, cwd=package_path, timeout=600)
                    for file in os.listdir(package_path):
                        if "_python.json" in file and package_name in file:
                            result[package_name]["apiViewArtifact"] = str(Path(package_path, file))
                except Exception as e:
                    _LOGGER.debug(f"Fail to generate ApiView token file for {package_name}: {e}")
                _LOGGER.info(f"apiview generation cost time: {int(time.time() - apiview_start_time)} seconds")
            else:
                _LOGGER.info("Skip ApiView generation for package that does not run in pipeline.")

            # check generated files and update package["version"]
            if package_name.startswith("azure-mgmt-"):
                try:
                    check_file(result[package_name])
                except Exception as e:
                    _LOGGER.warning(f"Fail to check generated files for {package_name}: {e}")

            # Build artifacts for package
            try:
                create_package(result[package_name]["path"][0], package_name)
                dist_path = Path(sdk_folder, folder_name, package_name, "dist")
                result[package_name]["artifacts"] = [
                    str(dist_path / package_file) for package_file in os.listdir(dist_path)
                ]
                for artifact in result[package_name]["artifacts"]:
                    if ".whl" in artifact:
                        result[package_name]["language"] = "Python"
                        break
                _LOGGER.info(f"Built package {package_name} successfully.")
            except Exception as e:
                _LOGGER.warning(f"Fail to build package {package_name} in {readme_or_tsp}: {str(e)}")

            # update result
            result[package_name]["installInstructions"] = {
                "full": "You can use pip to install the artifacts.",
                "lite": f"pip install {package_name}",
            }
            result[package_name]["result"] = "succeeded"
            result[package_name]["packageFolder"] = result[package_name]["path"][0]

    # remove duplicates
    try:
        for value in result.values():
            value["path"] = list(set(value["path"]))
            if value.get("typespecProject"):
                value["typespecProject"] = list(set(value["typespecProject"]))
            if value.get("readmeMd"):
                value["readmeMd"] = list(set(value["readmeMd"]))
    except Exception as e:
        _LOGGER.warning(f"Fail to remove duplicates: {str(e)}")

    if len(result) == 0 and len(readme_and_tsp) > 1:
        raise Exception("No package is generated, please check the log for details")

    if len(result) == 0:
        _LOGGER.info("No packages to process, returning empty result")
    else:
        _LOGGER.info(f"Processing {len(result)} generated packages...")

    final_result = {"packages": list(result.values())}
    with open(generate_output, "w") as writer:
        json.dump(final_result, writer, indent=2)

    _LOGGER.info(
        f"Congratulations! Succeed to build package for {[p['packageName'] for p in final_result['packages']]}. And you shall be able to see the generated code when running 'git status'."
    )


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
