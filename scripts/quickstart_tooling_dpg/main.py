import argparse
import logging
from pathlib import Path
import os
from jinja2 import Environment, FileSystemLoader
from subprocess import check_call
from typing import Any
import json

_LOGGER = logging.getLogger(__name__)

_TEMPLATE = Path(__file__).resolve().parent / "template"
_TEMPLATE_TESTS = Path(__file__).resolve().parent / "template_tests"
_TEMPLATE_SAMPLES = Path(__file__).resolve().parent / "template_samples"
_TEMPLATE_CI = Path(__file__).resolve().parent / "template_ci"
_CONFIG_FILE = Path(__file__).resolve() / "../../../swagger_to_sdk_config_dpg.json"


def check_parameters(
        output_folder: str,
) -> None:
    # check output_folder exists or not. If not, create it.
    output = Path(output_folder)
    if not os.path.exists(output):
        _LOGGER.info(f'{output} does not exist and try to create it')
        os.makedirs(output)
        _LOGGER.info(f'{output} is created')


def generate_ci(template_path: Path, folder_path: Path, package_name: str) -> None:
    ci = Path(folder_path, "ci.yml")
    ci_template_path = template_path / 'ci.yml'
    service_name = folder_path.name
    name = package_name.split('-')[-1]
    if not ci.exists():
        with open(ci_template_path, "r") as file_in:
            content = file_in.readlines()
        content = [line.replace("ServiceName", service_name).replace('PackageName', name) for line in content]
    else:
        with open(ci, "r") as file_in:
            content = file_in.readlines()
            for line in content:
                if f'{package_name}' in line:
                    return
            content.append(f'    - name: {package_name}\n')
            content.append(f'      safeName: {package_name.replace("-", "")}\n')
    with open(ci, "w") as file_out:
        file_out.writelines(content)


def generate_test_sample(template_path: Path, target_path: Path, **kwargs: Any) -> None:
    if not os.path.exists(target_path):
        os.makedirs(target_path)
    env = Environment(loader=FileSystemLoader(template_path), keep_trailing_newline=True)
    for template_name in env.list_templates():
        _LOGGER.info(f"generate file: {template_name}")
        template = env.get_template(template_name)
        result = template.render(**kwargs)
        with open(target_path / template_name, "w") as fd:
            fd.write(result)


def generate_swagger_readme(work_path: str, env: Environment, **kwargs: Any) -> Path:
    _LOGGER.info("Building swagger readme")
    # check path exists
    swagger_path = Path(work_path) / Path('swagger')
    if not os.path.exists(swagger_path):
        os.makedirs(swagger_path)

    # render file
    template = env.get_template('README.md')
    result = template.render(**kwargs)
    swagger_readme = swagger_path / Path('README.md')
    with open(swagger_readme, 'w') as fd:
        fd.write(result)
    return swagger_readme


def get_autorest_version() -> str:
    with open(_CONFIG_FILE, 'r') as file_in:
        config = json.load(file_in)
    autorest_use = " ".join(["--use=" + item for item in config["meta"]["autorest_options"]["use"]])
    return "--version={} {}".format(config["meta"]["autorest_options"]["version"], autorest_use)


def build_package(**kwargs) -> None:
    # prepare template render parameters
    output_folder = kwargs.get("output_folder")
    package_name = kwargs.get("package_name")
    namespace = package_name.replace('-', '.')
    kwargs['namespace'] = namespace
    kwargs['test_prefix'] = package_name.split('-')[-1]

    _LOGGER.info("Build start: %s", package_name)
    check_parameters(output_folder)

    # generate ci
    generate_ci(_TEMPLATE_CI, Path(output_folder).parent, package_name)

    # generate swagger readme
    env = Environment(loader=FileSystemLoader(_TEMPLATE), keep_trailing_newline=True)
    swagger_readme = generate_swagger_readme(output_folder, env, **kwargs)

    # generate code with autorest and swagger readme
    autorest_cmd = f'autorest {swagger_readme} {get_autorest_version()} '
    _LOGGER.info(f"generate SDK code with autorest: {autorest_cmd}")
    check_call(autorest_cmd, shell=True)


    # generate test framework
    work_path = Path(output_folder)
    generate_test_sample(_TEMPLATE_TESTS, work_path / Path('tests'), **kwargs)

    # generate sample framework
    generate_test_sample(_TEMPLATE_SAMPLES, work_path / Path('samples'), **kwargs)

    _LOGGER.info("Build complete: %s", package_name)


def validate_params(**kwargs):
    if not kwargs.get("security_scope") and not kwargs.get("security_header_name"):
        raise Exception('At least one of "security-scope" and "security-header-name" is needed')


def main(**kwargs):
    build_package(**kwargs)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="build package for Azure SDK of data-plane for Python",
        formatter_class=argparse.RawTextHelpFormatter,
    )
    parser.add_argument(
        "--output-folder", "-o",
        dest="output_folder",
        required=True,
        help="absolute path where generated SDK package will be put"
    )
    parser.add_argument("--debug", dest="debug", action="store_true", help="Verbosity in DEBUG mode")
    parser.add_argument(
        "--input-file", "-f",
        dest="input_file",
        required=True,
        help="absolute path of swagger input file. For example: `https://raw.githubusercontent.com/Azure/azure-rest-api-specs/main/specification/webpubsub/data-plane/WebPubSub/stable/2021-10-01/webpubsub.json`"
             " or `D:\\azure-rest-api-specs\\specification\\webpubsub\\data-plane\\WebPubSub\\stable\\2021-10-01\\webpubsub.json`",
    )
    parser.add_argument(
        "--security-scope", "-c",
        dest="security_scope",
        required=False,
        help="If authentication is AADToken, this param is necessary",
    )
    parser.add_argument(
        "--security-header-name",
        dest="security_header_name",
        required=False,
        help="If authentication is api key, this param is necessary",
    )
    parser.add_argument(
        "--package-name", "-p",
        dest="package_name",
        required=True,
        help="package name. For example: azure-messaging-webpubsub",
    )
    parser.add_argument(
        "--package-pprint-name", "-n",
        dest="package_pprint_name",
        required=True,
        help="Print name of the package. For example: Azure Web PubSub Service",
    )
    parser.add_argument(
        "--client-name", "-t",
        dest="client_name",
        required=True,
        help="client name. For example: WebPubSubServiceClient",
    )

    args = parser.parse_args()
    main_logger = logging.getLogger()
    logging.basicConfig()
    main_logger.setLevel(logging.INFO)

    parameters = vars(args)
    validate_params(**parameters)
    main(**parameters)
