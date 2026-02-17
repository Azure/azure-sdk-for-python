import json
import logging
import os
import re
import sys

try:
    # py 311 adds this library natively
    import tomllib as toml
except:
    # otherwise fall back to pypi package tomli
    import tomli as toml
import tomli_w as tomlw
from functools import wraps
from typing import Optional

from ci_tools.git_tools import get_add_diff_file_list
from pathlib import Path
from subprocess import check_output, CalledProcessError, check_call, STDOUT, call
from typing import Dict, Any
from glob import glob
import yaml
import shutil

from . import build_packaging
from .swaggertosdk.autorest_tools import build_autorest_options, generate_code
from .swaggertosdk.SwaggerToSdkCore import CONFIG_FILE_DPG, read_config
from .conf import CONF_NAME, OLD_CONF_NAME
from jinja2 import Environment, FileSystemLoader


logging.basicConfig(
    stream=sys.stdout,
    format="[%(levelname)s] %(message)s",
)
_LOGGER = logging.getLogger(__name__)
_SDK_FOLDER_RE = re.compile(r"^(sdk/[\w-]+)/(azure[\w-]+)/", re.ASCII)

DEFAULT_DEST_FOLDER = "./dist"
_DPG_README = "README.md"


# tsp example: "../azure-rest-api-specs/specification/informatica/Informatica.DataManagement"
def del_outdated_generated_files(tsp: str):
    tspconfig = Path(tsp) / "tspconfig.yaml"
    if not tspconfig.exists():
        _LOGGER.info(f"do not find tspconfig.yaml: {tspconfig}")
        return

    with open(tspconfig, "r") as file_in:
        content = yaml.safe_load(file_in)
    # tspconfig.yaml example: https://github.com/Azure/azure-rest-api-specs/pull/29080/files
    typespec_python_config = content.get("options", {}).get("@azure-tools/typespec-python", {})
    emitter_output_dir = typespec_python_config.get("emitter-output-dir", "")
    emitter_output_dir_parts = emitter_output_dir.split("/")
    if "service-dir" in emitter_output_dir:
        service_dir = typespec_python_config.get("service-dir") or content.get("parameters", {}).get(
            "service-dir", {}
        ).get("default", "")
    else:
        service_dir = emitter_output_dir_parts[-2] if len(emitter_output_dir_parts) >= 2 else ""
    package_dir = emitter_output_dir_parts[-1]
    if not service_dir or not package_dir:
        _LOGGER.info(f"do not find service-dir or emitter-output-dir in tspconfig.yaml: {tspconfig}")
        return
    generated_files_dir = Path(service_dir) / package_dir / package_dir.split("-")[0]
    # remove outdated generated files
    if generated_files_dir.exists():
        shutil.rmtree(generated_files_dir)
        _LOGGER.info(f"delete all outdated generated SDK files successfully")

    # remove outdated generated samples
    for item in ["generated_samples", "generated_tests"]:
        generated_dir = Path(service_dir) / package_dir / item
        if generated_dir.exists():
            shutil.rmtree(generated_dir)
            _LOGGER.info(f"delete outdated {item} successfully")


def dpg_relative_folder(spec_folder: str) -> str:
    return ("../" * 4) + spec_folder + "/"


def return_origin_path(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        current_path = os.getcwd()
        try:
            result = func(*args, **kwargs)
        except Exception as e:
            os.chdir(current_path)
            raise e
        os.chdir(current_path)
        return result

    return wrapper


def get_package_names(sdk_folder):
    files = get_add_diff_file_list(sdk_folder)
    matches = {_SDK_FOLDER_RE.search(f) for f in files}
    package_names = {match.groups() for match in matches if match is not None}
    return package_names


def call_build_config(package_name: str, folder_name: str):
    build_packaging(
        folder_name,
        os.environ.get("GH_TOKEN", None),
        packages=[package_name],
        build_conf=True,
        template_names=["README.md", "__init__.py"],
    )
    # Replace this check_call by in process equivalent call, for better debugging
    # check_call(
    #     f"python -m packaging_tools --build-conf {package_name} -o {folder_name}",
    #     shell=True,
    # )


def generate_packaging_and_ci_files(package_path: Path):
    # replace sdk_packaging.toml with pyproject.toml
    pyproject_toml = package_path / CONF_NAME
    sdk_packaging_toml = package_path / OLD_CONF_NAME
    if sdk_packaging_toml.exists():
        if pyproject_toml.exists():
            # update related items in pyproject.toml then delete sdk_packaging.toml
            _LOGGER.info(f"update {pyproject_toml} with {sdk_packaging_toml}")

            # Read the old sdk_packaging.toml content
            with open(sdk_packaging_toml, "rb") as f:
                sdk_packaging_content = toml.load(f)

            # Read the existing pyproject.toml content
            with open(pyproject_toml, "rb") as f:
                pyproject_content = toml.load(f)

            # Update pyproject.toml with sdk_packaging.toml content
            pyproject_content.update(sdk_packaging_content)

            # Write updated content back to pyproject.toml
            with open(pyproject_toml, "wb") as f:
                tomlw.dump(pyproject_content, f)

            # Delete the old sdk_packaging.toml file
            sdk_packaging_toml.unlink()
            _LOGGER.info(f"deleted {sdk_packaging_toml}")

        else:
            # rename sdk_packaging.toml to pyproject.toml
            _LOGGER.info(f"rename {sdk_packaging_toml} to {pyproject_toml}")
            sdk_packaging_toml.rename(pyproject_toml)

    package_name = package_path.name
    if "azure-mgmt-" in package_name:
        # if codegen generate pyproject.toml instead of setup.py, we delete existing setup.py
        setup_py = package_path / "setup.py"
        if setup_py.exists():
            _LOGGER.info(f"delete {setup_py} since codegen generate pyproject.toml")
            with open(pyproject_toml, "rb") as f:
                pyproject_content = toml.load(f)
            if pyproject_content.get("project"):
                setup_py.unlink()

        call_build_config(package_name, str(package_path.parent))
    else:
        if not pyproject_toml.exists():
            with open(pyproject_toml, "w") as file_out:
                file_out.write("[packaging]\nauto_update = false")

    # add ci.yml
    generate_ci(
        template_path=Path("scripts/quickstart_tooling_dpg/template_ci"),
        folder_path=package_path.parent,
        package_name=package_name,
    )


def update_metadata_json(package_path: Path, pipeline_input, codegen_config, spec_folder, input_readme):
    if not package_path.exists():
        _LOGGER.info(f"Fail to save metadata since package folder doesn't exist: {package_path}")
        return
    for_swagger_gen = "meta" in codegen_config
    # remove old _meta.json
    old_metadata_folder = package_path / "_meta.json"
    if old_metadata_folder.exists():
        os.remove(old_metadata_folder)
        _LOGGER.info(f"Remove old metadata file: {old_metadata_folder}")

    metadata_folder = package_path / "_metadata.json"
    if metadata_folder.exists():
        with open(metadata_folder, "r") as file_in:
            metadata = json.load(file_in)
    else:
        metadata = {}

    metadata.update(
        {
            "commit": pipeline_input["headSha"],
            "repository_url": pipeline_input["repoHttpsUrl"],
        }
    )
    if for_swagger_gen:
        readme_file = str(Path(spec_folder, input_readme))
        global_conf = codegen_config["meta"]
        local_conf = codegen_config.get("projects", {}).get(readme_file, {})

        if "resource-manager" in input_readme:
            cmd = ["autorest", input_readme]
        else:
            # autorest for DPG will be executed in package folder like: sdk/deviceupdate/azure-iot-deviceupdate/swagger
            cmd = ["autorest", _DPG_README]
        cmd += build_autorest_options(global_conf, local_conf)

        # metadata
        metadata.update(
            {
                "autorest": global_conf["autorest_options"]["version"],
                "use": global_conf["autorest_options"]["use"],
                "autorest_command": " ".join(cmd),
                "readme": input_readme,
            }
        )
    else:
        metadata["typespec_src"] = input_readme
        metadata.update(codegen_config)

    _LOGGER.info("Metadata json:\n {}".format(json.dumps(metadata, indent=2)))

    metadata_file_path = package_path / "_metadata.json"
    with metadata_file_path.open("w") as writer:
        json.dump(metadata, writer, indent=2)
    _LOGGER.info(f"Saved metadata to {metadata_file_path}")


@return_origin_path
def judge_tag_preview(path: str, package_name: str) -> bool:
    os.chdir(path)
    first_level = package_name.split("-")[0]
    files = [i for i in Path(".").glob(f"{first_level}/**/*.py")]
    default_api_version = ""  # for multi-api
    api_version = ""  # for single-api
    for file in files:
        try:
            with open(file, "r") as file_in:
                list_in = file_in.readlines()
        except:
            _LOGGER.info(f"can not open {file}")
            continue

        skip_decorator_block = False
        decorator_depth = 0

        for line in list_in:
            # skip the code of decorator @api_version_validation
            stripped_line = line.strip()

            # Check if we're starting an @api_version_validation decorator block
            if "@api_version_validation" in stripped_line:
                skip_decorator_block = True
                decorator_depth = 0
                continue

            # If we're in a decorator block, track parentheses depth
            if skip_decorator_block:
                decorator_depth += stripped_line.count("(") - stripped_line.count(")")
                # If we've closed all parentheses and hit a function definition, skip until next function/class
                if decorator_depth == 0 and (
                    stripped_line.startswith("def ") or stripped_line.startswith("async def ")
                ):
                    continue
                # If we hit another decorator or function/class definition after closing parentheses, stop skipping
                if decorator_depth == 0 and (
                    stripped_line.startswith("@")
                    or stripped_line.startswith("def ")
                    or stripped_line.startswith("async def ")
                    or stripped_line.startswith("class ")
                ):
                    skip_decorator_block = False
                else:
                    continue

            if "DEFAULT_API_VERSION = " in line:
                default_api_version += line.split("=")[-1].strip("\n")  # collect all default api version
            if default_api_version == "" and "api_version" in line and "method_added_on" not in line:
                api_version += ", ".join(
                    re.findall('"\d{4}-\d{2}-\d{2}[-a-z]*"[^:]', line)
                )  # collect all single api version
    if default_api_version != "":
        _LOGGER.info(f"find default api version:{default_api_version}")
        return "preview" in default_api_version

    _LOGGER.info(f"find single api version:{api_version}")
    return "preview" in api_version


def extract_yaml_content(autorest_config: str) -> str:
    num = []
    content = autorest_config.split("\r\n")
    for i in range(len(content)):
        if "```" in content[i]:
            num.append(i)
    if len(num) != 2:
        raise Exception(f"autorestConfig content is not valid: {autorest_config}")
    return "\n".join(content[num[0] + 1 : num[1]])


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
        "require": [spec_folder + line for line in origin_config["require"]],
        "package-mode": "dataplane",
        "output-folder": "../",
    }


def gen_general_namespace(package_name: str) -> str:
    return package_name.replace("-", ".")


def gen_dpg_config_single_client(origin_config: Dict[str, Any], spec_folder: str) -> str:
    package_name = Path(origin_config["output-folder"]).parts[-1]
    readme_config = gen_basic_config(origin_config, spec_folder)
    readme_config.update(
        {
            "namespace": gen_general_namespace(package_name),
        }
    )
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
    all_swagger_readme = glob(str(Path(f"sdk/*/*/swagger/{_DPG_README}")))
    for readme in all_swagger_readme:
        with open(readme, "r") as file:
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
    global_config = read_config(".", CONFIG_FILE_DPG)

    # generate code
    current_path = os.getcwd()
    os.chdir(Path(swagger_readme).parent)
    generate_code(_DPG_README, global_config["meta"], {})
    os.chdir(current_path)

    return global_config


def format_samples_and_tests(sdk_code_path) -> None:
    try:
        import black
    except Exception as e:
        try:
            call("pip install black", shell=True)
        except:
            pass
    for item in ["generated_samples", "generated_tests"]:
        generate_path = Path(sdk_code_path) / item
        if generate_path.exists():
            try:
                call(f"black {generate_path} -l 120", shell=True)
                _LOGGER.info(f"format {generate_path} successfully")
            except Exception as e:
                _LOGGER.info(f"failed to format {generate_path}: {e}")


def generate_ci(template_path: Path, folder_path: Path, package_name: str) -> None:
    ci = Path(folder_path, "ci.yml")
    service_name = folder_path.name
    safe_name = package_name.replace("-", "")
    if not ci.exists():
        env = Environment(loader=FileSystemLoader(template_path), keep_trailing_newline=True)
        template = env.get_template("ci.yml")
        content = template.render(package_name=package_name, service_name=service_name, safe_name=safe_name)
    else:
        with open(ci, "r") as file_in:
            content = file_in.readlines()
            for line in content:
                if package_name in line:
                    return
            new_line = "" if content[-1].endswith("\n") else "\n"
            content.append(f"{new_line}    - name: {package_name}\n")
            content.append(f"      safeName: {safe_name}")
    with open(ci, "w") as file_out:
        file_out.writelines(content)


def gen_typespec(
    typespec_relative_path: str,
    spec_folder: str,
    head_sha: str,
    rest_repo_url: str,
    run_in_pipeline: bool,
    api_version: Optional[str] = None,
) -> Dict[str, Any]:
    typespec_python = "@azure-tools/typespec-python"
    # call scirpt to generate sdk
    try:
        tsp_client = "npx --no --prefix eng/common/tsp-client tsp-client"
        if spec_folder:
            tsp_dir = (Path(spec_folder) / typespec_relative_path).resolve()
            repo_url = rest_repo_url.replace("https://github.com/", "")
            tspconfig = tsp_dir / "tspconfig.yaml"
            if tspconfig.exists() and api_version:
                with open(tspconfig, "r") as file_in:
                    content = yaml.safe_load(file_in)
                    if content.get("options", {}).get("@azure-tools/typespec-python"):
                        content["options"]["@azure-tools/typespec-python"]["api-version"] = api_version
                with open(tspconfig, "w") as file_out:
                    yaml.dump(content, file_out)
            cmd = f"{tsp_client} init --update-if-exists --tsp-config {tsp_dir} --local-spec-repo {tsp_dir} --commit {head_sha} --repo {repo_url}"
        else:
            tsp_config_url = f"{rest_repo_url}/blob/{head_sha}/{typespec_relative_path}/tspconfig.yaml"
            cmd = f"{tsp_client} init --update-if-exists -c {tsp_config_url}"
        if run_in_pipeline:
            emitter_name = "@azure-tools/typespec-python"
            if not os.path.exists(f"node_modules/{emitter_name}"):
                _LOGGER.info("install dependencies only for the first run")
                check_output(f"{tsp_client} install-dependencies", stderr=STDOUT, shell=True)
            else:
                _LOGGER.info(f"skip install since {emitter_name} is already installed")
            cmd += " --skip-install --debug"
        else:
            cmd += " --debug"
        _LOGGER.info(f"generation cmd: {cmd}")
        output = check_output(cmd, stderr=STDOUT, shell=True)
    except CalledProcessError as e:
        output = e.output.decode("utf-8")
        output_lines = output.split("\n")
        try:
            start_idx = [i for i, line in enumerate(output_lines) if "error stack start" in line][0]
            end_idx = [i for i, line in enumerate(output_lines) if "error stack end" in line][0]
            error_position = "python codegen"
        except:
            start_idx = -1
            end_idx = -1
            error_position = "tsp compiler"

        _LOGGER.error(f"====== Error occurred in {error_position} (error stack start) ======")
        if start_idx != -1 and end_idx != -1:
            for item in output_lines[start_idx + 1 : end_idx]:
                _LOGGER.error(item)
        else:
            for item in output_lines:
                if "- error " in item:
                    _LOGGER.error(item)
        _LOGGER.error(f"====== Error occurred in {error_position} (error stack end) ======")

        raise e

    with open(Path("eng/emitter-package.json"), "r") as file_in:
        data = json.load(file_in)
        npm_package_version = {
            "emitterVersion": data["dependencies"][typespec_python],
        }

    return npm_package_version
