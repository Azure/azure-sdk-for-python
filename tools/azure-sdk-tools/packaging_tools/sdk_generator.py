import sys
import time
from typing import List, Dict, Any
import argparse
import json
import logging
from pathlib import Path
from subprocess import check_call, getoutput
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
    return_origin_path,
    check_api_version_in_subfolder,
    call_build_config,
    del_outdated_generated_files,
)
from .conf import CONF_NAME
from .package_utils import create_package, change_log_generate, extract_breaking_change, get_version_info, check_file

logging.basicConfig(
    stream=sys.stdout,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %X",
)
_LOGGER = logging.getLogger(__name__)


def execute_func_with_timeout(func, timeout: int = 900) -> Any:
    """Execute function with timeout"""
    return multiprocessing.Pool(processes=1).apply_async(func).get(timeout)


def is_multiapi_package(python_md_content: List[str]) -> bool:
    for line in python_md_content:
        if re.findall(r"\s*multiapi\s*:\s*true", line):
            return True
    return False


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
    is_multiapi = is_multiapi_package(content)
    if sdk_folder:
        # remove tsp-location.yaml
        tsp_location = Path(f"sdk/{sdk_folder}/tsp-location.yaml")
        if tsp_location.exists():
            os.remove(str(tsp_location))
            _LOGGER.info(f"remove tsp-location.yaml: {tsp_location}")
        # remove generated_samples
        sample_folder = Path(f"sdk/{sdk_folder}/generated_samples")
        if sample_folder.exists():
            # rdbms is generated from different swagger folder;multiapi package may don't generate every time
            if "azure-mgmt-rdbms" not in str(sample_folder) and not is_multiapi:
                shutil.rmtree(sample_folder)
                _LOGGER.info(f"remove sample folder: {sample_folder}")
            else:
                _LOGGER.info(f"we don't remove sample folder for rdbms or multiapi package")
        else:
            _LOGGER.info(f"sample folder does not exist: {sample_folder}")
    else:
        _LOGGER.info(f"do not find valid sdk_folder in {python_readme}")


# look for fines in tag like:
# ``` yaml $(tag) == 'package-2023-05-01-preview-only'
# input-file:
# - Microsoft.Insights/preview/2023-05-01-preview/tenantActionGroups_API.json
# ```
def get_related_swagger(readme_content: List[str], tag: str) -> List[str]:
    result = []
    for idx in range(len(readme_content)):
        line = readme_content[idx]
        if tag in line and "```" in line and "tag" in line and "==" in line and "yaml" in line:
            idx += 1
            while idx < len(readme_content):
                if "```" in readme_content[idx]:
                    break
                if ".json" in readme_content[idx] and (
                    re.compile(r"\d{4}-\d{1,2}-\d{1,2}").findall(readme_content[idx])
                    or "Microsoft." in readme_content[idx]
                ):
                    result.append(readme_content[idx].strip("\n -"))
                idx += 1
            break
    return result


def get_last_commit_info(files: List[str]) -> str:
    result = [getoutput(f'git log -1 --pretty="format:%ai %H" {f}').strip("\n ") + " " + f for f in files]
    result.sort()
    return result[-1]


# input_readme: "specification/paloaltonetworks/resource-manager/readme.md"
# source: content of readme.python.md
# work directory is in root folder of azure-rest-api-specs
@return_origin_path
def choose_tag_and_update_meta(
    idx: int, source: List[str], target: List[str], input_readme: str, meta: Dict[str, Any], need_regenerate: bool
) -> int:
    os.chdir(str(Path(input_readme).parent))
    with open("readme.md", "r") as file_in:
        readme_content = file_in.readlines()

    while idx < len(source):
        if "```" in source[idx]:
            break
        if "tag:" in source[idx]:
            tag = source[idx].split("tag:")[-1].strip("\n ")
            related_files = get_related_swagger(readme_content, tag)
            if related_files:
                commit_info = get_last_commit_info(related_files)
                recorded_info = meta.get(tag, "")
                # there may be new commit after last release
                if need_regenerate or commit_info > recorded_info:
                    _LOGGER.info(f"update tag: {tag} with commit info {commit_info}")
                    meta[tag] = commit_info
                    target.append(source[idx])
                else:
                    _LOGGER.info(f"skip tag: {tag} since commit info doesn't change")
            else:
                _LOGGER.warning(f"do not find related swagger for tag: {tag}")
        else:
            target.append(source[idx])
        idx += 1
    return idx


def extract_version_info(config: Dict[str, Any]) -> str:
    autorest_version = config.get("autorest", "")
    autorest_modelerfour_version = config.get("use", [])
    return autorest_version + "".join(autorest_modelerfour_version)


def if_need_regenerate(meta: Dict[str, Any]) -> bool:
    with open(str(Path("../azure-sdk-for-python", CONFIG_FILE)), "r") as file_in:
        config = json.load(file_in)
    current_info = config["meta"]["autorest_options"]["version"] + "".join(
        sorted(config["meta"]["autorest_options"]["use"])
    )
    recorded_info = meta["autorest"] + "".join(sorted(meta["use"]))
    return recorded_info != current_info


# spec_folder: "../azure-rest-api-specs"
# input_readme: "specification/paloaltonetworks/resource-manager/readme.md"
@return_origin_path
def need_regen_for_multiapi_package(spec_folder: str, input_readme: str) -> bool:
    os.chdir(spec_folder)
    python_readme = (Path(input_readme).parent / "readme.python.md").absolute()
    if not python_readme.exists():
        _LOGGER.info(f"do not find python configuration: {python_readme}")
        return False

    with open(python_readme, "r") as file_in:
        python_md_content = file_in.readlines()
    is_multiapi = is_multiapi_package(python_md_content)
    if not is_multiapi:
        _LOGGER.info(f"do not find multiapi configuration in {python_readme}")
        return False

    after_handle = []
    for idx in range(len(python_md_content)):
        if re.findall(r"\s*clear-output-folder\s*:\s*true\s*", python_md_content[idx]):
            continue
        if re.findall(r"\s*-\s*tag\s*:", python_md_content[idx]):
            continue
        after_handle.append(python_md_content[idx])

    with open(python_readme, "w") as file_out:
        file_out.writelines(after_handle)
    return True


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
                generate_mgmt = partial(
                    generate,
                    CONFIG_FILE,
                    sdk_folder,
                    [],
                    relative_path_readme,
                    spec_folder,
                    force_generation=True,
                    python_tag=python_tag,
                )
                config = generate_mgmt()
                if need_regen_for_multiapi_package(spec_folder, readme_or_tsp):
                    generate_mgmt()
            else:
                config = gen_dpg(readme_or_tsp, data.get("autorestConfig", ""), dpg_relative_folder(spec_folder))
            _LOGGER.info(f"code generation cost time: {int(time.time() - code_generation_start_time)} seconds")
        except Exception as e:
            _LOGGER.error(f"Fail to generate sdk for {readme_or_tsp}: {str(e)}")
            for hint_message in [
                "======================================= Whant Can I do (begin) ========================================================================",
                f"Fail to generate sdk for {readme_or_tsp}. If you are from service team, please first check if the failure happens only to Python automation, or for all SDK automations. ",
                "If it happens for all SDK automations, please double check your Swagger / Typespec, and check whether there is error in ModelValidation and LintDiff. ",
                "If it happens to Python alone, you can open an issue to https://github.com/Azure/autorest.python/issues. Please include the link of this Pull Request in the issue.",
                "======================================= Whant Can I do (end) =========================================================================",
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
            try:
                package_total.add(package_name)
                sdk_code_path = str(Path(sdk_folder, folder_name, package_name))
                if package_name not in result:
                    package_entry = {}
                    package_entry["packageName"] = package_name
                    package_entry["path"] = [folder_name]
                    package_entry[spec_word] = [readme_or_tsp]
                    package_entry["tagIsStable"] = not judge_tag_preview(sdk_code_path, package_name)
                    readme_python_content = get_readme_python_content(str(Path(spec_folder) / readme_or_tsp))
                    package_entry["isMultiapi"] = is_multiapi_package(readme_python_content)
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
                update_servicemetadata(
                    sdk_folder,
                    data,
                    config,
                    folder_name,
                    package_name,
                    spec_folder,
                    readme_or_tsp,
                )
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

            # check whether multiapi package has only one api-version in per subfolder
            try:
                if result[package_name]["isMultiapi"]:
                    check_api_version_in_subfolder(sdk_code_path)
            except Exception as e:
                _LOGGER.warning(
                    f"Fail to check api version in subfolder for {package_name} in {readme_or_tsp}: {str(e)}"
                )

            # Changelog generation
            try:
                last_version, last_stable_release = get_version_info(package_name, result[package_name]["tagIsStable"])
                change_log_func = partial(
                    change_log_generate,
                    package_name,
                    last_version,
                    result[package_name]["tagIsStable"],
                    last_stable_release=last_stable_release,
                    prefolder=folder_name,
                    is_multiapi=result[package_name]["isMultiapi"],
                )

                changelog_generation_start_time = time.time()
                try:
                    if data.get("enableChangelog", True):
                        md_output = execute_func_with_timeout(change_log_func)
                    else:
                        md_output = "skip changelog generation"
                except multiprocessing.TimeoutError:
                    md_output = "change log generation was timeout!!! You need to write it manually!!!"
                except:
                    md_output = "change log generation failed!!! You need to write it manually!!!"
                finally:
                    for file in ["stable.json", "current.json"]:
                        file_path = Path(sdk_folder, folder_name, package_name, file)
                        if file_path.exists():
                            os.remove(file_path)
                            _LOGGER.info(f"Remove {file_path} which is temp file to generate changelog.")

                _LOGGER.info(
                    f"changelog generation cost time: {int(time.time() - changelog_generation_start_time)} seconds"
                )
                result[package_name]["changelog"] = {
                    "content": md_output,
                    "hasBreakingChange": "Breaking Changes" in md_output,
                    "breakingChangeItems": extract_breaking_change(md_output),
                }
                result[package_name]["version"] = last_version

                _LOGGER.info(f"[PACKAGE]({package_name})[CHANGELOG]:{md_output}")
            except Exception as e:
                _LOGGER.warning(f"Fail to generate changelog for {package_name} in {readme_or_tsp}: {str(e)}")

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
