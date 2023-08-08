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
from typing import List, Any
from .CondaConfiguration import CondaConfiguration

from subprocess import check_call
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


def create_sdist_skeleton(build_directory, artifact_name, common_root):
    sdist_directory = os.path.join(build_directory, artifact_name)

    if os.path.exists(sdist_directory):
        shutil.rmtree(sdist_directory)
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


def output_workload(conda_configs: List[CondaConfiguration]) -> None:
    """Show all packages and what order they will be built in."""
    print("This build run is generating the following package configurations: ")

    for config in [config for config in conda_configs if config.in_batch]:
        print(config)


def assemble_source(json_config):
    """If given a common root/package, this function will be used to clone slices of the azure-sdk-for-python repo and to download packages as they were at release.
    If given an https:// url, will instead attempt to download and unzip a package tar.gz.
    """
    pass


def build_conda_packages(json_config):
    """Conda builds each individually assembled conda package folder."""
    pass


def entrypoint():
    parser = argparse.ArgumentParser(description="Build a set of conda packages based on a json configuration bundle.")

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

    run_configurations = [CondaConfiguration.from_json(json_config) for json_config in json_configs]

    output_workload(run_configurations)

    # assemble_source(json_config)

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
