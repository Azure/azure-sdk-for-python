import argparse
import logging
from pathlib import Path
import os
from jinja2 import Environment, FileSystemLoader
from subprocess import check_call
import time
from typing import Any

_LOGGER = logging.getLogger(__name__)

_TEMPLATE = Path(__file__).resolve().parent / "template"
_TEMPLATE_TESTS = Path(__file__).resolve().parent / "template_tests"
_TEMPLATE_SAMPLES = Path(__file__).resolve().parent / "template_samples"


def check_parameters(
        output_folder: str,
) -> None:
    # check output_folder exists or not. If not, create it.
    output = Path(output_folder)
    if not os.path.exists(output):
        _LOGGER.info(f'{output} does not exist and try to create it')
        os.makedirs(output)
        _LOGGER.info(f'{output} is created')


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
    template = env.get_template('swagger_README.md')
    result = template.render(**kwargs)
    swagger_readme = swagger_path / Path('README.md')
    with open(swagger_readme, 'w') as fd:
        fd.write(result)
    return swagger_readme


def build_package(**kwargs) -> None:
    # prepare template render parameters
    output_folder = kwargs.get("output_folder")
    package_name = kwargs.get("package_name")
    swagger_readme_output = '../' + package_name.replace('-', '/')
    kwargs['swagger_readme_output'] = swagger_readme_output
    namespace = package_name.replace('-', '.')
    kwargs['namespace'] = namespace
    kwargs['date'] = time.strftime('%Y-%m-%d', time.localtime())
    folder_list = package_name.split('-')
    kwargs['folder_first'] = folder_list[0]
    kwargs['folder_second'] = folder_list[1]
    kwargs['folder_parent'] = Path(output_folder).parts[-2]
    kwargs['test_prefix'] = folder_list[-1]

    _LOGGER.info("Build start: %s", package_name)
    check_parameters(output_folder)

    # generate swagger readme
    env = Environment(loader=FileSystemLoader(_TEMPLATE), keep_trailing_newline=True)
    swagger_readme = generate_swagger_readme(output_folder, env, **kwargs)

    # generate code with autorest and swagger readme
    _LOGGER.info("generate SDK code with autorest")
    check_call(f'autorest --version=3.4.5 --python --use=@autorest/python@5.8.4 --use=@autorest/modelerfour@4.19.2 --python-mode=update {swagger_readme}', shell=True)

    # generate necessary file(setup.py, CHANGELOG.md, etc)
    work_path = Path(output_folder)
    for template_name in env.list_templates():
        _LOGGER.info(f"generate necessary file: {template_name}")
        template = env.get_template(template_name)
        result = template.render(**kwargs)
        # __init__.py is a weird one
        if template_name == "__init__.py":
            split_package_name = package_name.split("-")[:-1]
            for i in range(len(split_package_name)):
                init_path = work_path.joinpath(*split_package_name[: i + 1], template_name)
                with open(init_path, "w") as fd:
                    fd.write(result)
        elif template_name != 'swagger_README.md':
            with open(work_path / template_name, "w") as fd:
                fd.write(result)

    # generate test framework
    generate_test_sample(_TEMPLATE_TESTS, work_path / Path('tests'), **kwargs)

    # generate sample framework
    generate_test_sample(_TEMPLATE_SAMPLES, work_path / Path('samples'), **kwargs)

    _LOGGER.info("Build complete: %s", package_name)


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
        "--credential-scope", "-c",
        dest="credential_scope",
        required=True,
        help="Each service for data plan should have specific scopes",
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
    main(**parameters)
