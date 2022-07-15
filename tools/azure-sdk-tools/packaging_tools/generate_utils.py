from contextlib import suppress
import json
import logging
import os
import re

from azure_devtools.ci_tools.git_tools import get_add_diff_file_list
import black
from pathlib import Path
from subprocess import check_call
from typing import List

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


def format_samples(sdk_code_path) -> None:
    generate_sample_path = Path(sdk_code_path + '/generate_sample')
    if not os.path.exists(generate_sample_path):
        _LOGGER.info(f'not find generate_sample')
        return

    for root, ds, files in os.walk(generate_sample_path):
        for file in files:
            if file.suffix != '.py':
                continue
            sample = Path(root+file)

            with open(path, 'r') as fr:
                file_content = fr.read()

            with suppress(black.NothingChanged):
                file_content = read_file(path)
                file_content = black.format_file_contents(file_content, fast=True, mode=_BLACK_MODE)

            with open(path, 'w') as fw:
                fw.write(file_content)

    _LOGGER.info(f'format generate_sample successfully')
