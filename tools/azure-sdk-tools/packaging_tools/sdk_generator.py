from typing import List, Dict, Any
import argparse
import json
import logging
from pathlib import Path
from subprocess import check_call, getoutput
import shutil
import re
import os
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
    init_new_service,
    update_servicemetadata,
    judge_tag_preview,
    format_samples,
    gen_dpg,
    dpg_relative_folder,
    gen_typespec,
    return_origin_path,
    check_api_version_in_subfolder,
    call_build_config,
)
from .conf import CONF_NAME

_LOGGER = logging.getLogger(__name__)


def is_multiapi_package(python_md_content: List[str]) -> bool:
    return "multiapi: true" in "".join(python_md_content)


# return relative path like: network/azure-mgmt-network
def extract_sdk_folder(python_md: List[str]) -> str:
    pattern = ["$(python-sdks-folder)", "azure-mgmt-"]
    for line in python_md:
        if all(p in line for p in pattern):
            return re.findall("[a-z]+/[a-z]+-[a-z]+-[a-z]+[-a-z]*", line)[0]
    return ""


@return_origin_path
def multiapi_combiner(sdk_code_path: str, package_name: str):
    os.chdir(sdk_code_path)
    _LOGGER.info(f"start to combine multiapi package: {package_name}")
    check_call(
        f"python {str(Path('../../../tools/azure-sdk-tools/packaging_tools/multiapi_combiner.py'))} --pkg-path={os.getcwd()}",
        shell=True,
    )
    check_call("pip install -e .", shell=True)

@return_origin_path
def after_multiapi_combiner(sdk_code_path: str, package_name: str, folder_name: str):
    toml_file = Path(sdk_code_path) / CONF_NAME
    # do not package code of v20XX_XX_XX
    exclude = lambda x: x.replace("-", ".") + ".v20*"
    if toml_file.exists():
        with open(toml_file, "rb") as file_in:
            content = toml.load(file_in)
        if package_name != "azure-mgmt-resource":
            content["packaging"]["exclude_folders"] = exclude(package_name)
        else:
            # azure-mgmt-resource has subfolders
            subfolder_path = Path(sdk_code_path) / package_name.replace("-", "/")
            subfolders_name = [s.name for s in subfolder_path.iterdir() if s.is_dir() and not s.name.startswith("_")]
            content["packaging"]["exclude_folders"] = ",".join([exclude(f"{package_name}-{s}") for s in subfolders_name])

        with open(toml_file, "wb") as file_out:
            tomlw.dump(content, file_out)
        call_build_config(package_name, folder_name)
        
        # remove .egg-info to reinstall package
        for item in Path(sdk_code_path).iterdir():
            if item.suffix == ".egg-info":
                shutil.rmtree(str(item))
        os.chdir(sdk_code_path)
        check_call("pip install -e .", shell=True)
    else:
        _LOGGER.info(f"do not find {toml_file}")


def del_outdated_folder(readme: str):
    python_readme = Path(readme).parent / "readme.python.md"
    if not python_readme.exists():
        _LOGGER.info(f"do not find python configuration: {python_readme}")
        return

    with open(python_readme, "r") as file_in:
        content = file_in.readlines()
    sdk_folder = extract_sdk_folder(content)
    is_multiapi = is_multiapi_package(content)
    if sdk_folder:
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
                if ".json" in readme_content[idx]:
                    result.append(readme_content[idx].strip("\n -"))
                idx += 1
            break
    return result


def get_last_commit_info(files: List[str]) -> str:
    result = [getoutput(f'git log -1 --pretty="format:%ai %H" {f}').strip('\n ') + " " + f for f in files]
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
    current_info = config["meta"]["autorest_options"]["version"] + "".join(sorted(config["meta"]["autorest_options"]["use"]))
    recorded_info = meta["autorest"] + "".join(sorted(meta["use"]))
    return recorded_info != current_info


# spec_folder: "../azure-rest-api-specs"
# input_readme: "specification/paloaltonetworks/resource-manager/readme.md"
@return_origin_path
def update_metadata_for_multiapi_package(spec_folder: str, input_readme: str):
    os.chdir(spec_folder)
    python_readme = (Path(input_readme).parent / "readme.python.md").absolute()
    if not python_readme.exists():
        _LOGGER.info(f"do not find python configuration: {python_readme}")
        return

    with open(python_readme, "r") as file_in:
        python_md_content = file_in.readlines()
    is_multiapi = is_multiapi_package(python_md_content)
    if not is_multiapi:
        _LOGGER.info(f"do not find multiapi configuration in {python_readme}")
        return

    sdk_folder = extract_sdk_folder(python_md_content)
    if not sdk_folder:
        _LOGGER.warning(f"don't find valid sdk folder in {python_readme}")
        return
    meta_path = Path("../azure-sdk-for-python/sdk", sdk_folder, "_meta.json")
    if not meta_path.exists():
        _LOGGER.warning(f"don't find _meta.json file: {meta_path}")
        return

    with open(meta_path, "r") as file_in:
        meta = json.load(file_in)

    need_regenerate = if_need_regenerate(meta)

    after_handle = []
    for idx in range(len(python_md_content)):
        after_handle.append(python_md_content[idx])
        if "batch:" in python_md_content[idx]:
            line_number = choose_tag_and_update_meta(
                idx + 1, python_md_content, after_handle, input_readme, meta, need_regenerate
            )
            after_handle.extend(python_md_content[line_number:])
            break

    with open(python_readme, "w") as file_out:
        file_out.writelines(after_handle)

    with open(meta_path, "w") as file_out:
        json.dump(meta, file_out, indent=2)


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
        if isinstance(data["relatedTypeSpecProjectFolder"], str):
            readme_files = [data["relatedTypeSpecProjectFolder"]]
        else:
            readme_files = data["relatedTypeSpecProjectFolder"]
        spec_word = "typespecProject"

    for input_readme in readme_files:
        _LOGGER.info(f"[CODEGEN]({input_readme})codegen begin")
        is_typespec = False
        if "resource-manager" in input_readme:
            relative_path_readme = str(Path(spec_folder, input_readme))
            update_metadata_for_multiapi_package(spec_folder, input_readme)
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
            config = gen_typespec(input_readme, spec_folder, data["headSha"], data["repoHttpsUrl"])
            is_typespec = True
        package_names = get_package_names(sdk_folder)
        _LOGGER.info(f"[CODEGEN]({input_readme})codegen end. [(packages:{str(package_names)})]")

        # folder_name: "sdk/containerservice"; package_name: "azure-mgmt-containerservice"
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
            init_new_service(package_name, folder_name, is_typespec)
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

            # check whether multiapi package has only one api-version in per subfolder
            # skip check for network for https://github.com/Azure/azure-sdk-for-python/issues/30556#issuecomment-1571341309
            if "azure-mgmt-network" not in sdk_code_path:
                check_api_version_in_subfolder(sdk_code_path)

            # use multiapi combiner to combine multiapi package
            if package_name in ("azure-mgmt-network"):
                multiapi_combiner(sdk_code_path, package_name)
                after_multiapi_combiner(sdk_code_path, package_name, folder_name)
                result[package_name]["afterMultiapiCombiner"] = True
            else:
                result[package_name]["afterMultiapiCombiner"] = False

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
