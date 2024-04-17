import argparse
import logging
import json
from pathlib import Path
import os
import glob

from typing import Dict, List

GENERATED_PACKAGES_LIST_FILE = "toc_tree.rst"

_LOGGER = logging.getLogger(__name__)


def make_title(title):
    """Create a underlined title with the correct number of =."""
    return "\n".join([title, len(title) * "="])


SUBMODULE_TEMPLATE = """{title}

.. automodule:: {namespace}.{submodule}
    :members:
    :undoc-members:
    :show-inheritance:
"""
PACKAGE_TEMPLATE = """{title}

Submodules
----------

.. toctree::

   {namespace}.models
   {namespace}.operations

Module contents
---------------

.. automodule:: {namespace}
    :members:
    :undoc-members:
    :show-inheritance:
"""


RST_AUTODOC_TOCTREE = """.. toctree::
  :maxdepth: 5
  :glob:
  :caption: Developer Documentation

  ref/azure.common
{generated_packages}
  ref/azure.servicemanagement
"""

MULTIAPI_VERSION_PACKAGE_TEMPLATE = """{title}

Module contents
---------------

.. automodule:: {namespace}
    :members:
    :undoc-members:
    :show-inheritance:

Submodules
----------

.. toctree::

"""


def get_valid_versions(api_directory: str) -> List[str]:
    glob_path = os.path.join(api_directory, "v20*/")
    return glob.glob(glob_path)


def is_subnamespace(version: str) -> bool:
    return not version.startswith("v20")


def get_package_namespaces(package_root: str) -> List[str]:
    namespace_folders = os.path.basename(package_root).split("-")
    namespace = ".".join(namespace_folders)

    # add top namespace
    namespaces = {namespace: []}

    api_directory = os.path.join(package_root, *namespace_folders)
    valid_versions = get_valid_versions(api_directory)

    # check for subnamespaces like azure.mgmt.resource.locks
    if not valid_versions:
        subnamespaces = glob.glob(f"{api_directory}/*/")
        for snp_path in subnamespaces:
            versions = get_valid_versions(snp_path)
            valid_versions.extend(versions)

    for version_path in valid_versions:
        version = os.path.relpath(version_path, start=api_directory)
        if is_subnamespace(version):
            subnamespace_name, api_version = version.split("/")
            full_namespace = ".".join([namespace, subnamespace_name, api_version])
            subnamespace = ".".join([namespace, subnamespace_name])
            if subnamespace not in namespaces[namespace]:
                namespaces[namespace].append(subnamespace)
            namespaces.setdefault(subnamespace, []).append(full_namespace)
        else:
            full_namespace = ".".join([namespace, version])
            namespaces[namespace].append(full_namespace)

    return namespaces


def write_rst(version: str, rst_path_template: str, rst_namespace_template: str, package_list_path: List[str]) -> None:
    rst_path = rst_path_template.format(version)
    with Path(rst_path).open("w") as rst_file:
        rst_file.write(PACKAGE_TEMPLATE.format(title=make_title(version + " package"), namespace=version))

    for module in ["operations", "models"]:
        with Path(rst_namespace_template.format(version, module)).open("w") as rst_file:
            rst_file.write(
                SUBMODULE_TEMPLATE.format(
                    title=make_title(version + "." + module + " module"), namespace=version, submodule=module
                )
            )
    package_list_path.append(rst_path)


def write_multiapi_rst(namespace: str, versions: List[str], rst_path_template: str, package_list_path: List[str]) -> None:
    rst_path = rst_path_template.format(namespace)
    with Path(rst_path).open("w") as rst_file:
        rst_file.write(
            MULTIAPI_VERSION_PACKAGE_TEMPLATE.format(
                title=make_title(namespace + " package"), namespace=namespace
            )
        )
        for version in versions:
            rst_file.write("   {version}\n".format(version=version))
    package_list_path.append(rst_path)


def write_toc_tree(package_list_path: List[str]) -> None:
    package_list_path.sort()
    with Path(GENERATED_PACKAGES_LIST_FILE).open("w") as generate_file_list_fd:
        lines_to_write = "\n".join(["  " + package for package in package_list_path])
        generate_file_list_fd.write(RST_AUTODOC_TOCTREE.format(generated_packages=lines_to_write))


def generate_doc(output_directory: str = "./ref/", package_root: str = None) -> None:
    # we are handed a directory that looks like <path-to-repo>/sdk/containerservice/azure-mgmt-containerservice/
    rst_path_template = os.path.join(output_directory, "{}.rst")
    rst_namespace_template = os.path.join(output_directory, "{}.{}.rst")

    namespaces = get_package_namespaces(package_root)

    package_list_path = []

    for namespace, multi_api_versions in namespaces.items():
        _LOGGER.info("Working on %s", namespace)
        if not multi_api_versions:
            write_rst(namespace, rst_path_template, rst_namespace_template, package_list_path)
            continue

        multi_api_versions.sort(reverse=True)
        write_multiapi_rst(namespace, multi_api_versions, rst_path_template, package_list_path)

        for version in multi_api_versions:
            if is_subnamespace(version.split(".")[-1]):
                # subnamespace already handled in write_multiapi_rst
                continue
            _LOGGER.info("Working on %s", version)
            write_rst(version, rst_path_template, rst_namespace_template, package_list_path)

    write_toc_tree(package_list_path)


def main():
    parser = argparse.ArgumentParser(description="Generate sphinx api stubs for one or multiple management packages.")
    parser.add_argument(
        "--project",
        "-p",
        dest="project",
        help="Want to target a specific management package? Pass the targeted package root to this argument.",
    )
    parser.add_argument("-v", "--verbose", dest="verbose", action="store_true", help="Verbosity in INFO mode")
    parser.add_argument("--debug", dest="debug", action="store_true", help="Verbosity in DEBUG mode")
    parser.add_argument(
        "--out", "-o", dest="output_directory", help="The final resting place for the generated sphinx source files."
    )

    args = parser.parse_args()

    main_logger = logging.getLogger()
    if args.verbose or args.debug:
        logging.basicConfig()
        main_logger.setLevel(logging.DEBUG if args.debug else logging.INFO)

    generate_doc(args.output_directory, args.project)


if __name__ == "__main__":
    main()
