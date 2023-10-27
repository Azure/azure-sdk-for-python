#!/usr/bin/env python

# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

# The functions within this document are utilized through through entrypoint() function which is bound to sdk_build_conda entrypoint.

# Check CondaConfiguration.py for an larger example configuration blob that showcases all supported download methodologies.

import argparse
import sys
import os
import shutil
import re
import json
import shlex
import subprocess
import stat
import urllib3

from shutil import rmtree
from typing import List, Any
from subprocess import check_call
from ci_tools.variables import discover_repo_root, in_ci
from ci_tools.functions import unzip_file_to_directory, cleanup_directory
from ci_tools.build import create_package
from subprocess import check_call, CalledProcessError, check_output

from .CondaConfiguration import CondaConfiguration, CheckoutConfiguration

# from package disutils
from distutils.dir_util import copy_tree
import urllib.request

CONDA_ENV_NAME = "azure-build-env"

CONDA_ENV_FILE = """name: azure-build-env
channels:
  - conda-forge
  - defaults
dependencies:
  - python=3.10
  - conda-build
  - conda-verify
  - typing-extensions
"""

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
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
        'License :: OSI Approved :: MIT License',
    ],
    zip_safe=False,
    packages=find_packages(),
    install_requires=[]
)
"""

http = urllib3.PoolManager()


def resolve_assembly_folder_name(package_name: str, conda_package_name: str):
    """
    This script does a lot of moving of code automagically. In the case of assembly of a new conda package, the destination
    folder will be the _name_ of the conda package within the assembly folder.

    In some cases (azure-core), the name of the conda package and the name of one of the packages that will be used to construct
    it are _the same name_. In that case, we need to ensure that the code doesn't stomp on itself. To do that, use this
    function to resolve a different name and not accidentally stomp on ourselves.
    """
    if package_name == conda_package_name:
        return f"s{package_name}"
    else:
        return package_name


def create_namespace_extension(target_directory: str):
    with open(os.path.join(target_directory, "__init__.py"), "w") as f:
        f.write(NAMESPACE_EXTENSION_TEMPLATE)


def get_pkgs_from_build_directory(build_directory: str, artifact_name: str):
    return [os.path.join(build_directory, p) for p in os.listdir(build_directory) if p != artifact_name]


def create_sdist_skeleton(build_directory, artifact_name, common_root):
    """
    Given a properly formatted input directory, set up the skeleton for a combined package
    and transfer source code into it from the individual source packages that have been
    previously downloaded.
    """
    sdist_directory = os.path.join(build_directory, artifact_name)

    cleanup_directory(sdist_directory)

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

            if os.path.basename(pkg) == f"s{artifact_name}":
                # find all the _file_ contents of the ending directory and copy them directly _into_ the target
                # we do this because packages like azure-eventhub actually emplace a lot of user detail into the __init__ at azure/eventhub
                # even if there are further namespaces under azure/eventhub/extensions/<checkpointstoreblob/aio>
                # we need that one to live on.
                files_for_copy = [
                    file
                    for file in os.listdir(pkg_till_common_root)
                    if os.path.isfile(os.path.join(pkg_till_common_root, file))
                ]

                for file in files_for_copy:
                    src = os.path.join(pkg_till_common_root, file)
                    target = os.path.join(ns_dir, file)
                    shutil.copy(src, target)

            for directory in directories_for_copy:
                src = os.path.join(pkg_till_common_root, directory)
                dest = os.path.join(ns_dir, directory)

                shutil.copytree(src, dest, dirs_exist_ok=True)


def get_version_from_config(environment_config):
    """
    Given the conda_env.yml, get the target conda version.
    """
    with open(os.path.abspath((environment_config)), "r") as f:
        lines = f.readlines()
    for line in lines:
        result = VERSION_REGEX.match(line)
        if result:
            return result.group(1)
    return "0.0.0"


def get_manifest_includes(common_root):
    """
    Given a common root, generate the folder structure and __init__.py necessary to support it.
    """
    levels = common_root.split("/")
    breadcrumbs = []
    breadcrumb_string = ""

    for ns in levels:
        breadcrumb_string += ns + "/"
        breadcrumbs.append(breadcrumb_string + "__init__.py")

    return breadcrumbs


def create_setup_files(
    build_directory: str, common_root: str, artifact_name: str, service: str, environment_config: str
) -> None:
    """
    Drop all the necessary files to create a properly formatted python package. This includes:

     - setup.py
     - setup.cfg
     - MANIFEST.in
    """
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
    conda_build: CondaConfiguration, config_assembly_folder: str, config_assembled_folder: str
) -> str:
    """
    Given a single conda package config which has already been assembled, create a combined source distribution that combines
    all the downloaded code, then actually create that source distribution and make it available within the assembled folder.
    """

    # get the meta.yml from the conda-recipes folder for this package name
    repo_root = discover_repo_root()
    environment_config = os.path.join(repo_root, "conda", "conda-recipes", "conda_env.yml")

    singular_dependency = len(conda_build.checkout) == 1

    if not singular_dependency:
        create_sdist_skeleton(config_assembly_folder, conda_build.name, conda_build.common_root)
        create_setup_files(
            config_assembly_folder,
            conda_build.common_root,
            conda_build.name,
            conda_build.service,
            environment_config,
        )

    if conda_build.checkout[0].download_uri:
        # if we have a single dependency that is downloadable, it will be placed in final sdist location
        # by the get_package_source function. In that case, we just need to find it and return it
        if singular_dependency:
            assembled_sdist = next(
                iter(
                    [
                        os.path.join(config_assembled_folder, a)
                        for a in os.listdir(config_assembled_folder)
                        if os.path.isfile(os.path.join(config_assembled_folder, a)) and conda_build.name in a
                    ]
                )
            )
            return assembled_sdist

    targeted_folder_for_assembly = os.path.join(config_assembly_folder, conda_build.name)

    create_package(targeted_folder_for_assembly, config_assembled_folder, enable_wheel=False, enable_sdist=True)

    assembled_sdist = next(
        iter(
            [
                os.path.join(config_assembled_folder, a)
                for a in os.listdir(config_assembled_folder)
                if os.path.isfile(os.path.join(config_assembled_folder, a)) and conda_build.name in a
            ]
        )
    )

    return assembled_sdist


def get_summary(conda_config: CondaConfiguration):
    pkg_list = [f"{checkout_config.package}=={checkout_config.version}" for checkout_config in conda_config.checkout]

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
            print(f"- {config.name}")


def prep_directory(path: str) -> str:
    cleanup_directory(path)

    os.makedirs(path)
    return path


def get_output(command: str, working_directory: str) -> None:
    try:
        command = shlex.split(command)
        wd = working_directory.replace("\\", "/")

        p = subprocess.Popen(command, cwd=wd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        output, err = p.communicate()
        print(str(output.decode()))
        print(str(err.decode()))
        if p.returncode > 0:
            raise CalledProcessError(p.returncode, output=str(output) + str(err))
    except CalledProcessError as e:
        print(str(e))
        raise


def invoke_command(command: str, working_directory: str) -> None:
    try:
        command = shlex.split(command)
        wd = working_directory.replace("\\", "/")
        check_call(command, stderr=subprocess.STDOUT, cwd=wd)
    except CalledProcessError as e:
        print(e)
        raise


def get_git_source(
    assembly_area: str,
    assembled_code_area: str,
    target_package: str,
    checkout_path: str,
    target_version: str,
    conda_package_name: str,
) -> None:
    clone_folder = prep_directory(os.path.join(assembly_area, target_package))
    code_destination = os.path.join(
        assembled_code_area, resolve_assembly_folder_name(target_package, conda_package_name)
    )
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


def download_pypi_source(target_folder: str, target_uri: str) -> str:
    basename = os.path.basename(target_uri)
    file_name = os.path.join(target_folder, basename)

    if os.path.exists(file_name):
        return file_name

    with urllib.request.urlopen(target_uri) as response, open(file_name, "wb") as out_file:
        shutil.copyfileobj(response, out_file)

    return file_name


def get_package_source(
    checkout_config: CheckoutConfiguration,
    download_folder: str,
    assembly_location: str,
    output_folder: str,
    conda_build: CondaConfiguration,
) -> None:
    """
    Retrieves the source code for a specific checkout_config.
    """
    if checkout_config.download_uri or checkout_config.version:
        # if we have a single package, we can simply use the source distribution _as is_ rather than
        # repackaging it. so we download and move it directly to assembled
        if len(conda_build.checkout) == 1:
            return download_pypi_source(output_folder, checkout_config.download_uri)
        # in case of multiple external packages, we need to unzip the code into the same format as we do for a git clone
        else:
            downloaded_zip = download_pypi_source(download_folder, checkout_config.download_uri)
            unzip_staging_folder = prep_directory(os.path.join(download_folder, checkout_config.package))
            unzipped_staged = unzip_file_to_directory(downloaded_zip, unzip_staging_folder)
            assembly_location = prep_directory(
                os.path.join(assembly_location, resolve_assembly_folder_name(checkout_config.package, conda_build.name))
            )

            # During unzip, we often end up one level deeper than we intend.
            # EG: unzipping azure-core-1.29.1.zip to `assembly/azure-core/azure-core`
            # will _actually_ end up in `assembly/azure-core/azure-core/azure-core-1.29.1`.
            #
            # What we can do to counteract this is simply move all files _within_ the unzipped folder
            # to where we actually want them to live.
            for file_name in os.listdir(unzipped_staged):
                shutil.move(os.path.join(unzipped_staged, file_name), assembly_location)

            if os.path.exists(downloaded_zip):
                os.remove(downloaded_zip)

            if os.path.exists(unzipped_staged):
                shutil.rmtree(unzipped_staged)
    elif checkout_config.checkout_path:
        get_git_source(
            download_folder,
            assembly_location,
            checkout_config.package,
            checkout_config.checkout_path,
            checkout_config.version,
            conda_build.name,
        )
    else:
        raise ValueError(
            "Unable to handle a checkoutConfiguration that doesn't git clone OR download from pypi for sdist code."
        )


def assemble_source(conda_configurations: List[CondaConfiguration], repo_root: str) -> None:
    """This function takes a set of conda configurations as an input and creates the necessary artifacts to produce a successful conda build.
    The function utilizes 3 temporary directories to do this. Appearing in order of usage:

    /conda/downloaded/
        /<conda-package-name>/
            /<downloaded source or repo package 1>
            /<downloaded source or repo package 2>
            /<downloaded source or repo package 3>
    /conda/assembly/
        <conda-package-name>/
            /<downloaded source package 1>
            /<downloaded source package 2>
    /conda/assembled/
        /<conda-package-name>
            meta.yaml
        <conda-package-name>.tar.gz

    The final outcome being a completely assembled source distribution (which may or may not combine multiple package into a single sdist)
    which can be immediately built utilizing the generated `conda/conda-env` conda virtual directory.
    """
    sdist_output_dir = prep_directory(os.path.join(repo_root, "conda", "assembled"))
    sdist_assembly_area = prep_directory(os.path.join(repo_root, "conda", "assembly"))
    sdist_download_area = prep_directory(os.path.join(repo_root, "conda", "downloaded"))
    environment_config = os.path.join(repo_root, "conda", "conda-recipes", "conda_env.yml")
    version = get_version_from_config(environment_config)

    for conda_build in conda_configurations:
        print(f"Beginning processing for {conda_build.name}.")
        meta_yml = os.path.join(repo_root, "conda", "conda-recipes", conda_build.name, "meta.yaml")
        if not os.path.exists(meta_yml):
            raise ValueError(
                f"Unable to handle a targeted conda assembly which has no defined meta.yml within conda/conda-recipes/{conda_build.name}."
            )

        config_download_folder = prep_directory(os.path.join(sdist_download_area, conda_build.name))
        config_assembly_folder = prep_directory(os.path.join(sdist_assembly_area, conda_build.name))
        # our base assembled folder will contain the tar.gz list, placing the meta.yaml recipe one level
        # deeper and named for the package name
        config_assembled_folder = prep_directory(os.path.join(sdist_output_dir, conda_build.name))
        generated_yml = os.path.join(config_assembled_folder, "meta.yaml")

        # <Code Location 1> -> /conda/downloaded/run_configuration_package/<downloaded-package-name-1>/
        # <Code Location 2> -> /conda/downloaded/run_configuration_package/<downloaded-package-name-2>/
        # ...
        for checkout_config in conda_build.checkout:
            print(f" - getting code for {checkout_config.package}.")
            get_package_source(
                checkout_config,
                config_download_folder,
                config_assembly_folder,
                sdist_output_dir,
                conda_build,
            )

        # the output of above loop is the following folder structure:
        #   <sdist_assembly_area>/<conda_configuration_name>
        #       /azure-storage-blob <-- package folder from tag/pypi release download
        #           /setup.py
        #           /...
        #       /azure-storage-queue
        #       /azure-storage-file-datalake
        #       /azure-storage-fileshare
        #
        # In the case of a specified download URI, simply find it and return it
        conda_build.created_sdist_path = create_combined_sdist(
            conda_build, config_assembly_folder, sdist_output_dir
        ).replace("\\", "/")
        print(f"Generated Sdist for artifact {conda_build.name} is present at {conda_build.created_sdist_path}")

        # generate a meta.yml for each one!
        with open(meta_yml, "r", encoding="utf-8") as f:
            meta_yml_content = f.read()

        summary = get_summary(conda_build)

        sdist = os.path.basename(conda_build.created_sdist_path)

        meta_yml_content = meta_yml_content.replace("{{ environ.get('AZURESDK_CONDA_VERSION', '0.0.0') }}", version)
        meta_yml_content = re.sub(r"^\s*url\:.*", f'  url: "../{sdist}"', meta_yml_content, flags=re.MULTILINE)
        meta_yml_content = re.sub(
            r"\{\{\senviron\.get\(\'.*_SUMMARY\'\,\s\'\'\)\s*\}\}", f"{summary}", meta_yml_content, flags=re.MULTILINE
        )

        with open(generated_yml, "w", encoding="utf-8") as f:
            f.write(meta_yml_content)


def prep_and_create_environment(environment_dir: str) -> None:
    prep_directory(environment_dir)

    with open(os.path.join(environment_dir, "environment.yml"), "w", encoding="utf-8") as f:
        f.write(CONDA_ENV_FILE)

    invoke_command(f'conda env create --prefix "{environment_dir}"', environment_dir)
    invoke_command(
        f'conda install --yes --quiet --prefix "{environment_dir}" conda-build conda-verify typing-extensions conda-index',
        environment_dir,
    )


def copy_channel_files(coalescing_channel_dir: str, additional_channel_dir: str) -> None:
    artifact_directories = ["noarch", "win-64", "win-x86", "osx-64", "osx-x86", "linux-64", "linux-x86"]

    if additional_channel_dir:
        for artifact_directory in artifact_directories:
            a_dir = os.path.join(additional_channel_dir, artifact_directory)
            if os.path.exists(a_dir):
                for file in os.listdir(a_dir):
                    source = os.path.join(a_dir, file)
                    if os.path.isfile(source) and file.endswith(".tar.bz2"):
                        target_directory = os.path.join(coalescing_channel_dir, artifact_directory)
                        target_file = os.path.join(target_directory, file)

                        if not os.path.exists(target_directory):
                            os.makedirs(target_directory)
                        print(f"Moving {file} to {target_directory}")
                        shutil.move(os.path.join(a_dir, file), target_file)
    else:
        # a blank additional_channel_dir being passed indicates that we just want to initialize this folder
        # as an empty conda channel. In that case move no code.
        pass


def build_conda_packages(
    conda_configurations: List[CondaConfiguration], repo_root: str, additional_channel_folders: List[str]
):
    """Conda builds each individually assembled conda package folder."""
    conda_output_dir = prep_directory(os.path.join(repo_root, "conda", "output")).replace("\\", "/")
    conda_sdist_dir = os.path.join(repo_root, "conda", "assembled").replace("\\", "/")
    conda_env_dir = prep_directory(os.path.join(repo_root, "conda", "conda-env")).replace("\\", "/")

    prep_and_create_environment(conda_env_dir)

    if additional_channel_folders:
        for channel in additional_channel_folders:
            copy_channel_files(conda_output_dir, channel)
            invoke_command(f'conda run --prefix "{conda_env_dir}" conda index {conda_output_dir}', repo_root)
    else:
        invoke_command(f'conda run --prefix "{conda_env_dir}" conda index {conda_output_dir}', repo_root)

    for conda_build in conda_configurations:
        conda_build_folder = os.path.join(conda_sdist_dir, conda_build.name).replace("\\", "/")

        if conda_build.conda_py_versions:
            for pyversion in conda_build.conda_py_versions:
                invoke_conda_build(conda_output_dir, conda_env_dir, conda_build_folder, pyversion, conda_build.channels)
        else:
            invoke_conda_build(conda_output_dir, conda_env_dir, conda_build_folder, None, conda_build.channels)


def invoke_conda_build(
    conda_output_dir: str,
    conda_env_dir: str,
    conda_build_folder: str,
    optional_py_version: str = None,
    channels: List[str] = [],
) -> None:
    channel_suffix = " ".join([f'-c "{channel}"' for channel in channels])
    command = f'conda run --prefix "{conda_env_dir}" conda-build . --output-folder "{conda_output_dir}" -c "{conda_output_dir}" {channel_suffix}'

    if optional_py_version:
        command += f" --py {optional_py_version}"

    print(f"Calling '{command}' in folder {conda_build_folder}.")
    get_output(command, conda_build_folder)


def check_conda_config():
    try:
        invoke_command("conda --version", discover_repo_root())
    except CalledProcessError as err:
        print(
            "Before invoking sdk_build_conda, a user must ensure that conda is available on the PATH for the current machine."
        )
        exit(1)


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

    parser.add_argument("--channel", dest="channel", action="extend", nargs="+", type=str)

    args = parser.parse_args()

    json_configs = json.loads(args.config)

    check_conda_config()

    run_configurations = []
    excluded_configurations = []

    for config in [CondaConfiguration.from_json(json_config) for json_config in json_configs]:
        if config.in_batch:
            run_configurations.append(config)
        else:
            excluded_configurations.append(config)

    # dump our configuration for viewing in CI
    output_workload(run_configurations, excluded_configurations)

    if not in_ci():
        input("Press any key to continue building the above packages.")

    # download all necessary source code to create source distributions
    assemble_source(run_configurations, repo_root)

    # now build the conda packages
    build_conda_packages(run_configurations, repo_root, args.channel)
