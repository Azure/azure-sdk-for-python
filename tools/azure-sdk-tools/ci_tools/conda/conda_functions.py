#!/usr/bin/env python

# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

# Used to generate conda artifacts given a properly formatted build folder given a properly formatted
# json targeting document. Find out what one of those looks like at eng/pipelines/templates/stages/conda-sdk-client.yml#L28

import argparse
import sys
import os
import shutil
import re
import json
import shlex
import errno
import stat

from shutil import rmtree
from typing import List, Any
from subprocess import check_call
from ci_tools.variables import discover_repo_root, get_artifact_directory
from subprocess import check_call, CalledProcessError

from .CondaConfiguration import CondaConfiguration, CheckoutConfiguration

# from package disutils
from distutils.dir_util import copy_tree

# from package pyyaml
import yaml

VERSION_REGEX = re.compile(r"\s*AZURESDK_CONDA_VERSION\s*:\s*[\'](.*)[\']\s*")

SUMMARY_TEMPLATE = " - Generated from {}."

NAMESPACE_EXTENSION_TEMPLATE = """__path__ = __import__('pkgutil').extend_path(__path__, __name__)  # type: str
"""

MANIFEST_TEMPLATE = """include *.md
{namespace_includes}
recursive-include tests *.py
recursive-include samples *.py *.md
"""

SETUP_CFG = """
[bdist_wheel]
universal=1
"""

CONDA_PKG_SETUP_TEMPLATE = """from setuptools import find_packages, setup

setup(
    name=\"{conda_package_name}\",
    version=\"{version}\",
    description='Microsoft Azure SDK For Python {service} Combined Conda Library',
    long_description_content_type='text/markdown',
    license='MIT License',
    author='Microsoft Corporation',
    author_email='azpysdkhelp@microsoft.com',
    url='https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/{service}/',
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'License :: OSI Approved :: MIT License',
    ],
    zip_safe=False,
    packages=find_packages(),
    install_requires=[]
)
"""


def create_package(pkg_directory, output_directory):
    check_call(
        [
            sys.executable,
            "setup.py",
            "sdist",
            "-d",
            output_directory,
        ],
        cwd=pkg_directory,
    )


def create_namespace_extension(target_directory):
    with open(os.path.join(target_directory, "__init__.py"), "w") as f:
        f.write(NAMESPACE_EXTENSION_TEMPLATE)


def get_pkgs_from_build_directory(build_directory, artifact_name):
    return [os.path.join(build_directory, p) for p in os.listdir(build_directory) if p != artifact_name]


def error_handler_git_access(func, path, exc):
    # Is the error an access error?
    if not os.access(path, os.W_OK):
        os.chmod(path, stat.S_IWUSR)
        func(path)
    else:
        raise


def create_sdist_skeleton(build_directory, artifact_name, common_root):
    sdist_directory = os.path.join(build_directory, artifact_name)

    if os.path.exists(sdist_directory):
        shutil.rmtree(sdist_directory, ignore_errors=False, onerror=error_handler_git_access)

    os.makedirs(sdist_directory)
    namespaces = common_root.split("/")

    # after the below function, ns_dir will be the target destination for copying from our pkgs_from_consumption
    ns_dir = sdist_directory

    for ns in namespaces:
        ns_dir = os.path.join(ns_dir, ns)
        if not os.path.exists(ns_dir):
            os.mkdir(ns_dir)
        create_namespace_extension(ns_dir)

    # get all the directories in the build folder, we will pull in all of them
    pkgs_for_consumption = get_pkgs_from_build_directory(build_directory, artifact_name)

    for pkg in pkgs_for_consumption:
        pkg_till_common_root = os.path.join(pkg, common_root)

        if os.path.exists(pkg_till_common_root):
            directories_for_copy = [
                file
                for file in os.listdir(pkg_till_common_root)
                if os.path.isdir(os.path.join(pkg_till_common_root, file))
            ]

            for directory in directories_for_copy:
                src = os.path.join(pkg_till_common_root, directory)
                dest = os.path.join(ns_dir, directory)
                shutil.copytree(src, dest)


def get_version_from_config(environment_config):
    with open(os.path.abspath((environment_config)), "r") as f:
        lines = f.readlines()
    for line in lines:
        result = VERSION_REGEX.match(line)
        if result:
            return result.group(1)
    return "0.0.0"


def get_manifest_includes(common_root):
    levels = common_root.split("/")
    breadcrumbs = []
    breadcrumb_string = ""

    for ns in levels:
        breadcrumb_string += ns + "/"
        breadcrumbs.append(breadcrumb_string + "__init__.py")

    return breadcrumbs


def create_setup_files(build_directory, common_root, artifact_name, service, meta_yaml, environment_config):
    sdist_directory = os.path.join(build_directory, artifact_name)
    setup_location = os.path.join(sdist_directory, "setup.py")
    manifest_location = os.path.join(sdist_directory, "MANIFEST.in")
    cfg_location = os.path.join(sdist_directory, "setup.cfg")

    setup_template = CONDA_PKG_SETUP_TEMPLATE.format(
        conda_package_name=artifact_name,
        version=get_version_from_config(environment_config),
        service=service,
        package_excludes="'azure', 'tests', '{}'".format(common_root.replace("/", ".")),
    )

    with open(setup_location, "w") as f:
        f.write(setup_template)

    manifest_template = MANIFEST_TEMPLATE.format(
        namespace_includes="\n".join(["include " + ns for ns in get_manifest_includes(common_root)])
    )

    with open(manifest_location, "w") as f:
        f.write(manifest_template)

    with open(cfg_location, "w") as f:
        f.write(SETUP_CFG)


def create_combined_sdist(
    output_directory,
    build_directory,
    artifact_name,
    common_root,
    service,
    meta_yaml,
    environment_config,
):
    singular_dependency = len(get_pkgs_from_build_directory(build_directory, artifact_name)) == 0

    if not singular_dependency:
        create_sdist_skeleton(build_directory, artifact_name, common_root)
        create_setup_files(
            build_directory,
            common_root,
            artifact_name,
            service,
            meta_yaml,
            environment_config,
        )

    sdist_location = os.path.join(build_directory, artifact_name)

    output_sdist_location = os.path.join(output_directory, "sdist", artifact_name)

    create_package(sdist_location, output_sdist_location)
    output_location = os.path.join(output_sdist_location, os.listdir(output_sdist_location)[0])

    print("Generated Sdist for artifact {} is present at {}".format(artifact_name, output_location))
    return output_location


def get_summary(ci_yml, artifact_name):
    pkg_list = []
    with open(ci_yml, "r") as f:
        data = f.read()

    config = yaml.safe_load(data)

    conda_artifact = [
        conda_artifact
        for conda_artifact in config["extends"]["parameters"]["CondaArtifacts"]
        if conda_artifact["name"] == artifact_name
    ]

    if conda_artifact:
        dependencies = conda_artifact[0]["checkout"]

    for dep in dependencies:
        pkg_list.append("{}=={}".format(dep["package"], dep["version"]))

    return SUMMARY_TEMPLATE.format(", ".join(pkg_list))


def output_workload(
    run_configurations: List[CondaConfiguration], excluded_configurations: List[CondaConfiguration]
) -> None:
    """Show all packages and what order they will be built in."""
    print("This build run is generating the following package configurations: ")

    for config in run_configurations:
        print(config)

    if excluded_configurations:
        print("These packages have been EXCLUDED:")

        for config in excluded_configurations:
            print(config)


def prep_directory(path: str) -> str:
    if os.path.exists(path):
        rmtree(path, ignore_errors=False, onerror=error_handler_git_access)

    os.makedirs(path)
    return path


def invoke_command(command: str, working_directory: str) -> None:
    try:
        check_call(shlex.split(command), cwd=working_directory)
    except CalledProcessError as e:
        raise


def get_git_source(
    assembly_area: str, assembled_code_area: str, target_package: str, checkout_path: str, target_version: str
) -> None:
    clone_folder = prep_directory(os.path.join(assembly_area, target_package))
    code_destination = os.path.join(assembled_code_area, target_package)
    code_source = os.path.join(clone_folder, checkout_path, target_package)

    invoke_command(
        f"git clone --no-checkout --filter=tree:0 https://github.com/Azure/azure-sdk-for-python .", clone_folder
    )
    invoke_command(f"git config gc.auto 0", clone_folder)
    invoke_command(f"git sparse-checkout init", clone_folder)
    invoke_command(f"git sparse-checkout set --no-cone '/*' '!/*/' '/eng'", clone_folder)
    invoke_command(f'git sparse-checkout add "{checkout_path}"', clone_folder)
    invoke_command(f"git -c advice.detachedHead=false checkout {target_package}_{target_version}", clone_folder)

    shutil.move(code_source, code_destination)


def download_pypi_source() -> None:
    pass


def get_package_source(checkout_config: CheckoutConfiguration, assembly_area: str, assembled_code_area: str) -> None:
    if checkout_config.download_uri:
        # we need to download from pypi
        print("Must download")

    elif checkout_config.checkout_path:
        get_git_source(
            assembly_area,
            assembled_code_area,
            checkout_config.package,
            checkout_config.checkout_path,
            checkout_config.version,
        )
    else:
        raise ValueError(
            "Unable to handle a checkoutConfiguraiton that doesn't git clone OR download from pypi for sdist code."
        )

    pass


def assemble_source(run_configurations: List[CondaConfiguration], repo_root: str) -> None:
    """If given a common root/package, this function will be used to clone slices of the azure-sdk-for-python repo and to download packages as they were at release.
    If given an https:// url, will instead attempt to download and unzip a package tar.gz.
    """
    sdist_output_dir = prep_directory(os.path.join(repo_root, "conda", "assembled"))
    sdist_assembly_area = prep_directory(os.path.join(repo_root, "conda", "assembly_area"))

    for conda_build in run_configurations:
        for checkout_config in conda_build.checkout:
            print(f"Getting package code for {checkout_config.package}.")
            get_package_source(checkout_config, sdist_assembly_area, sdist_output_dir)


def build_conda_packages(run_configurations):
    """Conda builds each individually assembled conda package folder."""
    pass


def entrypoint():
    parser = argparse.ArgumentParser(description="Build a set of conda packages based on a json configuration bundle.")

    repo_root = discover_repo_root()

    parser.add_argument(
        "-c",
        "--config",
        dest="config",
        help="The json blob describing which conda packages should be assembled.",
        required=True,
    )

    parser.add_argument(
        "-w",
        "--work-folder",
        dest="work_folder",
        help="What directory will we assemble the conda packages in?",
        required=True,
    )

    args = parser.parse_args()
    json_configs = json.loads(args.config)

    run_configurations = []
    excluded_configurations = []

    for config in [CondaConfiguration.from_json(json_config) for json_config in json_configs]:
        if config.in_batch:
            run_configurations.append(config)
        else:
            excluded_configurations.append(config)

    output_workload(run_configurations, excluded_configurations)

    assemble_source(run_configurations, repo_root)

    # build_conda_packages(json_config)

    # output_source_location = create_combined_sdist(
    #     args.distribution_directory,
    #     args.build_directory,
    #     args.artifact_name,
    #     args.common_root,
    #     args.service,
    #     args.meta_yml,
    #     args.environment_config,
    # )
