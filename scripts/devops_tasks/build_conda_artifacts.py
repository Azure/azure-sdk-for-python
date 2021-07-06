#!/usr/bin/env python

# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

# Used to generate conda artifacts given a properly formatted build folder
#
#   EXAMPLE: examine the CondaArtifacts in /sdk/storage/meta.yaml
#
#   Grab the source code from each of the tags in the CondaArtifact.
#
#   Format the directory that you pass to the "build_directory" argument in this way
#   <build directory>
#       /azure-storage-blob <-- package folder from tag specified
#           /setup.py
#           /...
#       /azure-storage-queue
#       /azure-storage-file-datalake
#       /azure-storage-fileshare

import argparse
import sys
import os
import shutil
import re
import yaml

from common_tasks import process_glob_string, run_check_call, str_to_bool, parse_setup
from subprocess import check_call
from distutils.dir_util import copy_tree

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
            "--format",
            "zip",
            "-d",
            output_directory,
        ],
        cwd=pkg_directory,
    )


def create_namespace_extension(target_directory):
    with open(os.path.join(target_directory, "__init__.py"), "w") as f:
        f.write(NAMESPACE_EXTENSION_TEMPLATE)


def get_pkgs_from_build_directory(build_directory, artifact_name):
    return [
        os.path.join(build_directory, p)
        for p in os.listdir(build_directory)
        if p != artifact_name
    ]


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

    print("I see the following packages in the build directory")
    print(pkgs_for_consumption)

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


def create_setup_files(
    build_directory, common_root, artifact_name, service, meta_yaml, environment_config
):
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
        namespace_includes="\n".join(
            ["include " + ns for ns in get_manifest_includes(common_root)]
        )
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
    singular_dependency = (
        len(get_pkgs_from_build_directory(build_directory, artifact_name)) == 0
    )

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
    output_location = os.path.join(
        output_sdist_location, os.listdir(output_sdist_location)[0]
    )

    print(
        "Generated Sdist for artifact {} is present at {}".format(
            artifact_name, output_location
        )
    )
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


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Build a Conda Package, given a properly formatted build directory, and input configuration. This script assumes that the build directory has been set up w/ the necessary sdists in each location."
    )

    parser.add_argument(
        "-d",
        "--distribution-directory",
        dest="distribution_directory",
        help="The output conda sdist will be dropped into this directory under a folder named the same as argument artifact_name.",
        required=True,
    )

    parser.add_argument(
        "-b",
        "--build-directory",
        dest="build_directory",
        help="The 'working' directory. This top level path will contain all the necessary sdist code from the appropriate historical tag. EG: <build-directory>/azure-storage-blob, <build-directory/azure-storage-queue",
        required=True,
    )

    parser.add_argument(
        "-m",
        "--meta-yml",
        dest="meta_yml",
        help="The path to the meta yaml that will be used to generate this conda distribution.",
        required=True,
    )

    parser.add_argument(
        "-r",
        "--common-root",
        dest="common_root",
        help="The common root namespace. For instance, when outputting the artifact 'azure-storage', the common root will be azure/storage.",
        required=False,
    )

    parser.add_argument(
        "-n",
        "--artifact-name",
        dest="artifact_name",
        help="The name of the output conda package.",
        required=True,
    )

    parser.add_argument(
        "-s",
        "--service-name",
        dest="service",
        help="The name of the service this package is being generated for.",
        required=True,
    )

    parser.add_argument(
        "-e",
        "--environment_config",
        dest="environment_config",
        help="The location of the yml config file used to create the conda environments. This file has necessary common configuration information within.",
        required=True,
    )

    parser.add_argument(
        "-c",
        "--ci_yml",
        dest="ci_yml",
        help="The location of the ci.yml that is used to define our conda artifacts. Used when to easily grab summary information.",
        required=True,
    )

    args = parser.parse_args()
    output_source_location = create_combined_sdist(
        args.distribution_directory,
        args.build_directory,
        args.artifact_name,
        args.common_root,
        args.service,
        args.meta_yml,
        args.environment_config,
    )

    summary = get_summary(args.ci_yml, args.artifact_name)

    if output_source_location:
        print(
            "##vso[task.setvariable variable={}]{}".format(
                args.service.upper() + "_SOURCE_DISTRIBUTION", output_source_location
            )
        )

    if summary:
        print(
            "##vso[task.setvariable variable={}]{}".format(
                args.service.upper() + "_SUMMARY", summary
            )
        )
