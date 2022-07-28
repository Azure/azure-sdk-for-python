from contextlib import suppress
import json
import logging
import os
import re

from azure_devtools.ci_tools.git_tools import get_add_diff_file_list
from pathlib import Path
from subprocess import check_call
from typing import List, Dict, Any
from glob import glob
import yaml

from .swaggertosdk.autorest_tools import build_autorest_options, generate_code
from .swaggertosdk.SwaggerToSdkCore import CONFIG_FILE_DPG, read_config


_LOGGER = logging.getLogger(__name__)
_SDK_FOLDER_RE = re.compile(r"^(sdk/[\w-]+)/(azure[\w-]+)/", re.ASCII)

DEFAULT_DEST_FOLDER = "./dist"
_DPG_README = "README.md"

def dpg_relative_folder(spec_folder: str) -> str:
    return ("../" * 4) + spec_folder + "/"

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
    local_conf = config.get("projects", {}).get(readme_file, {})

    if "resource-manager" in input_readme:
        cmd = ["autorest", input_readme]
    else:
        # autorest for DPG will be executed in package folder like: sdk/deviceupdate/azure-iot-deviceupdate/swagger
        cmd = ["autorest", _DPG_README]
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
    if "resource-manager" in input_readme:
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


def add_config_title(content: str) -> str:
    return f"# autorest configuration for Python\n\n{content}"


def yaml_block(content: str, annotation: str = "", tag: str = "") -> str:
    annotation = f"{annotation}\n\n" if annotation else annotation
    return f"{annotation}" + f"``` yaml {tag}\n" + content + "```\n"


def gen_package_name(origin_config: Dict[str, Any]) -> str:
    return Path(origin_config["output-folder"]).parts[-1]


def gen_basic_config(origin_config: Dict[str, Any], spec_folder: str) -> Dict[str, Any]:
    return {
        "package-name": gen_package_name(origin_config),
        "license-header": "MICROSOFT_MIT_NO_VERSION",
        "package-version": origin_config.get("package-version", "1.0.0b1"),
        "require": [spec_root + line for line in origin_config["require"]],
        "package-mode": "dataplane",
        "output-folder": "../",
    }


def gen_general_namespace(package_name: str) -> str:
    return package_name.replace('-', '.')


def gen_dpg_config_single_client(origin_config: Dict[str, Any], spec_folder: str) -> str:
    package_name = Path(origin_config["output-folder"]).parts[-1]
    readme_config = gen_basic_config(origin_config, spec_folder)
    readme_config.update({
        "namespace": gen_general_namespace(package_name),
    })
    readme_content = yaml_block(yaml.safe_dump(readme_config), "### Settings")
    return add_config_title(readme_content)


def gen_tag_config(origin_config: Dict[str, Any]) -> Dict[str, Any]:
    tag_config = {}
    package_name = gen_package_name(origin_config)
    for tag in origin_config["batch"]:
        tag_name = tag["tag"]
        extra_part = tag_name.split("-")[-1]
        tag_config[tag_name] = {
            "namespace": gen_general_namespace(package_name) + f".{extra_part}",
        }

    return tag_config


def gen_batch_config(origin_config: Dict[str, Any]) -> Dict[str, Any]:
    batch_config = []
    for item in origin_config["batch"]:
        for _, value in item.items():
            batch_config.append({value: True})
    return {"batch": batch_config}


def gen_dpg_config_multi_client(origin_config: Dict[str, Any], spec_folder: str) -> str:
    # generate config
    basic_config = gen_basic_config(origin_config, spec_folder)
    batch_config = gen_batch_config(origin_config)
    tag_config = gen_tag_config(origin_config)

    # convert to string
    readme_content = yaml_block(yaml.dump(basic_config), "### Settings")
    readme_content += yaml_block(yaml.dump(batch_config), "\n### Python multi-client")
    for tag, value in tag_config.items():
        readme_content += yaml_block(
            yaml.dump(value),
            f"\n### Tag: {tag}",
            f"$({tag})",
        )

    return add_config_title(readme_content)


# generate swagger/README.md and return relative path based on SDK repo root path
def gen_dpg_config(autorest_config: str, spec_folder: str) -> str:
    # remove useless lines
    autorest_config = extract_yaml_content(autorest_config)
    _LOGGER.info(f"autorestConfig after remove useless lines:\n{autorest_config}")

    # make dir if not exist
    origin_config = yaml.safe_load(autorest_config)
    _LOGGER.info(f"autorestConfig: {origin_config}")
    swagger_folder = str(Path(origin_config["output-folder"], "swagger"))
    if not os.path.exists(swagger_folder):
        os.makedirs(swagger_folder)

    # generate autorest configuration
    if "batch:" in autorest_config:
        readme_content = gen_dpg_config_multi_client(origin_config, spec_folder)
    else:
        readme_content = gen_dpg_config_single_client(origin_config, spec_folder)

    # output autorest configuration
    swagger_readme = str(Path(swagger_folder, _DPG_README))
    with open(swagger_readme, "w") as file:
        file.write(readme_content)
    return swagger_readme


def lookup_swagger_readme(rest_readme_path: str) -> str:
    all_swagger_readme = glob(str(Path(f'sdk/*/*/swagger/{_DPG_README}')))
    for readme in all_swagger_readme:
        with open(readme, 'r') as file:
            content = file.read()
            if rest_readme_path in content:
                _LOGGER.info(f"find swagger readme: {readme}")
                return readme
    _LOGGER.info(f"do not find swagger readme which contains {rest_readme_path}")
    return ""


def gen_dpg(rest_readme_path: str, autorest_config: str, spec_folder: str) -> Dict[str, Any]:
    # generate or find swagger/README.md
    if autorest_config:
        swagger_readme = gen_dpg_config(autorest_config, spec_folder)
    else:
        swagger_readme = lookup_swagger_readme(rest_readme_path)
    if not swagger_readme:
        return

    # extract global config
    global_config = read_config('.', CONFIG_FILE_DPG)

    # generate code
    current_path = os.getcwd()
    os.chdir(Path(swagger_readme).parent)
    generate_code(_DPG_README, global_config["meta"], {})
    os.chdir(current_path)

    return global_config


def format_samples(sdk_code_path) -> None:
    generate_sample_path = Path(sdk_code_path) / 'generated_samples'
    if not generate_sample_path.exists():
        _LOGGER.info(f'not find generated_samples')
        return

    try:
        import black
    except Exception as e:
        check_call('pip install black', shell=True)
        import black

    _BLACK_MODE = black.Mode()
    _BLACK_MODE.line_length = 120
    files = generate_sample_path.glob('**/*.py')
    for path in files:
        with open(path, 'r') as fr:
            file_content = fr.read()

        with suppress(black.NothingChanged):
            file_content = black.format_file_contents(file_content, fast=True, mode=_BLACK_MODE)

        with open(path, 'w') as fw:
            fw.write(file_content)

    _LOGGER.info(f'format generated_samples successfully')
