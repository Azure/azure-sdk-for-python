import json
import logging
import os
import re

from azure_devtools.ci_tools.git_tools import get_add_diff_file_list
from pathlib import Path
from subprocess import check_call
from typing import List, Union
from glob import glob
import yaml

from .swaggertosdk.autorest_tools import build_autorest_options

_LOGGER = logging.getLogger(__name__)
_SDK_FOLDER_RE = re.compile(r"^(sdk/[\w-]+)/(azure[\w-]+)/", re.ASCII)

DEFAULT_DEST_FOLDER = "./dist"


def get_package_names(sdk_folder):
    files = get_add_diff_file_list(sdk_folder)
    matches = {_SDK_FOLDER_RE.search(f) for f in files}
    package_names = {match.groups() for match in matches if match is not None}
    return package_names


def init_new_service(package_name, folder_name):
    setup = Path(folder_name, package_name, "setup.py")
    if not setup.exists():
        check_call(f"python -m packaging_tools --build-conf {package_name} -o {folder_name}", shell=True)
        ci = Path(folder_name, "ci.yml")
        if not ci.exists():
            with open("ci_template.yml", "r") as file_in:
                content = file_in.readlines()
            name = package_name.replace("azure-", "").replace("mgmt-", "")
            content = [line.replace("MyService", name) for line in content]
            with open(str(ci), "w") as file_out:
                file_out.writelines(content)


def update_servicemetadata(sdk_folder, data, config, folder_name, package_name, spec_folder, input_readme):

    readme_file = str(Path(spec_folder, input_readme))
    global_conf = config["meta"]
    local_conf = config["projects"][readme_file]

    cmd = ["autorest", input_readme]
    cmd += build_autorest_options(global_conf, local_conf)

    # metadata
    metadata = {
        "autorest": global_conf["autorest_options"]["version"],
        "use": global_conf["autorest_options"]["use"],
        "commit": data["headSha"],
        "repository_url": data["repoHttpsUrl"],
        "autorest_command": " ".join(cmd),
        "readme": input_readme,
    }

    _LOGGER.info("Metadata json:\n {}".format(json.dumps(metadata, indent=2)))

    package_folder = Path(sdk_folder, folder_name, package_name).expanduser()
    if not os.path.exists(package_folder):
        _LOGGER.info(f"Package folder doesn't exist: {package_folder}")
        _LOGGER.info("Failed to save metadata.")
        return

    metadata_file_path = os.path.join(package_folder, "_meta.json")
    with open(metadata_file_path, "w") as writer:
        json.dump(metadata, writer, indent=2)
    _LOGGER.info(f"Saved metadata to {metadata_file_path}")

    # Check whether MANIFEST.in includes _meta.json
    require_meta = "include _meta.json\n"
    manifest_file = os.path.join(package_folder, "MANIFEST.in")
    if not os.path.exists(manifest_file):
        _LOGGER.info(f"MANIFEST.in doesn't exist: {manifest_file}")
        return

    includes = []
    write_flag = False
    with open(manifest_file, "r") as f:
        includes = f.readlines()
        if require_meta not in includes:
            includes = [require_meta] + includes
            write_flag = True

    if write_flag:
        with open(manifest_file, "w") as f:
            f.write("".join(includes))


# find all the files of one folder, including files in subdirectory
def all_files(path: str, files: List[str]):
    all_folder = os.listdir(path)
    for item in all_folder:
        folder = str(Path(f'{path}/{item}'))
        if os.path.isdir(folder):
            all_files(folder, files)
        else:
            files.append(folder)


def judge_tag_preview(path: str) -> bool:
    files = []
    all_files(path, files)
    default_api_version = ''  # for multi-api
    api_version = ''  # for single-api
    for file in files:
        if '.py' not in file or '.pyc' in file:
            continue
        try:
            with open(file, 'r') as file_in:
                list_in = file_in.readlines()
        except:
            _LOGGER.info(f'can not open {file}')
            continue

        for line in list_in:
            if line.find('DEFAULT_API_VERSION = ') > -1:
                default_api_version += line.split('=')[-1].strip('\n')  # collect all default api version
            if default_api_version == '' and line.find('api_version = ') > -1:
                api_version += line.split('=')[-1].strip('\n')  # collect all single api version
    if default_api_version != '':
        _LOGGER.info(f'find default api version:{default_api_version}')
        return 'preview' in default_api_version

    _LOGGER.info(f'find single api version:{api_version}')
    return 'preview' in api_version


def extract_yaml_content(autorest_config: str) -> str:
    num = []
    content = autorest_config.split('\r\n')
    for i in range(len(content)):
        if "```" in content[i]:
            num.append(i)
    if len(num) != 2:
        raise Exception(f"autorestConfig content is not valid: {autorest_config}")
    return '\n'.join(content[num[0] + 1: num[1]])


def add_yaml_title(content: str, annotation: str = "", tag: str = "") -> str:
    return f"{annotation}\n\n" + f"``` yaml {tag}\n" + content + "```\n"


def generate_dpg_config(autorest_config: str) -> str:
    # remove useless lines
    autorest_config = extract_yaml_content(autorest_config)
    _LOGGER.info(f"autoresConfig after remove useles lines:\n{autorest_config}")

    # make dir if not exist
    origin_config = yaml.safe_load(autorest_config)
    _LOGGER.info(f"autoresConfig: {origin_config}")
    swagger_folder = str(Path(origin_config["output-folder"], "swagger"))
    if not os.path.exists(swagger_folder):
        os.makedirs(swagger_folder)

    # generate autorest configuration
    package_name = Path(origin_config["output-folder"]).parts[-1]
    readme_content = {
        "package-name": package_name,
        "license-header": "MICROSOFT_MIT_NO_VERSION",
        "clear-output-folder": True,
        "no-namespace-folders": True,
        "version-tolerant": True,
        "package-version": "1.0.0b1",
        "require": ["../../../../azure-rest-api-specs/" + line for line in origin_config["require"]],
        "output-folder": "../" + package_name.replace('-', '/'),
        "namespace": package_name.replace('-', '.')
    }

    # output autorest configuration
    swagger_readme = str(Path(swagger_folder, "README.md"))
    with open(swagger_readme, "w") as file:
        file.write(add_yaml_title(yaml.safe_dump(readme_content)))
    return swagger_readme


def lookup_swagger_readme(rest_readme_path: str) -> str:
    all_swagger_readme = glob(str(Path('sdk/*/*/swagger/README.md')))
    for readme in all_swagger_readme:
        with open(readme, 'r') as file:
            content = file.read()
            if rest_readme_path in content:
                return readme
    return ""


def generate_dpg(rest_readme_path: str, autorest_config: str):
    if autorest_config:
        swagger_readme = generate_dpg_config(autorest_config)
    else:
        swagger_readme = lookup_swagger_readme(rest_readme_path)
    if not swagger_readme:
        return

    # extract global config

    # generate code
