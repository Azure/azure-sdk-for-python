import argparse
import os
from typing import List, Mapping, Any, Dict, Optional
from ci_tools.parsing import ParsedSetup, extract_package_metadata
from ci_tools.functions import verify_package_classifiers
import sys

from typing import Optional, List
from .verify_whl import (
    cleanup,
    should_verify_package,
    get_prior_version,
    verify_prior_version_metadata,
    get_path_to_zip,
    unzip_file_to_directory,
)
from ci_tools.scenario.generation import create_package_and_install
from .Check import Check
from ci_tools.variables import set_envvar_defaults
from ci_tools.logging import logger

ALLOWED_ROOT_DIRECTORIES = ["azure", "tests", "samples", "examples"]

EXCLUDED_PYTYPE_PACKAGES = ["azure-keyvault", "azure", "azure-common"]

EXCLUDED_CLASSIFICATION_PACKAGES = []


def get_root_directories_in_source(package_dir: str) -> List[str]:
    """
    Find all allowed directories in source path.
    """
    source_folders = [
        d
        for d in os.listdir(package_dir)
        if os.path.isdir(os.path.join(package_dir, d)) and d in ALLOWED_ROOT_DIRECTORIES
    ]
    return source_folders


def get_root_directories_in_sdist(dist_dir: str, version: str) -> List[str]:
    """
    Given an unzipped sdist directory, extract which directories are present.
    """
    # find sdist zip file
    path_to_zip = get_path_to_zip(dist_dir, version, package_type="*.tar.gz")
    # extract sdist and find list of directories in sdist
    extract_location = os.path.join(dist_dir, "unzipped")
    # Cleanup any files in unzipped
    cleanup(extract_location)
    unzipped_dir = unzip_file_to_directory(path_to_zip, extract_location)
    sdist_folders = [d for d in os.listdir(unzipped_dir) if os.path.isdir(os.path.join(unzipped_dir, d))]
    return sdist_folders


def verify_sdist_helper(package_dir: str, dist_dir: str, parsed_pkg: ParsedSetup, executable: str) -> bool:
    """
    Compares the root directories in source against root directories present within a sdist.
    Also verifies metadata compatibility with prior stable version.
    """
    version = parsed_pkg.version
    # Extract metadata from zip file to ensure we're checking the built package metadata
    metadata: Dict[str, Any] = extract_package_metadata(get_path_to_zip(dist_dir, version, package_type="*.tar.gz"))

    source_folders = get_root_directories_in_source(package_dir)
    sdist_folders = get_root_directories_in_sdist(dist_dir, version)

    # compare folders in source directory against unzipped sdist
    missing_folders = set(source_folders) - set(sdist_folders)
    for folder in missing_folders:
        logger.error("Source folder [%s] is not included in sdist", folder)

    if missing_folders:
        logger.info("Directories in source: %s", source_folders)
        logger.info("Directories in sdist: %s", sdist_folders)
        return False

    # Verify metadata compatibility with prior version
    prior_version = get_prior_version(parsed_pkg.name, version)
    if prior_version:
        if not verify_prior_version_metadata(
            parsed_pkg.name, prior_version, metadata, package_type="*.tar.gz", executable=executable
        ):
            return False

    return True


def verify_sdist_pytyped(
    pkg_dir: str, namespace: str, package_metadata: Mapping[str, Any], include_package_data: bool
) -> bool:
    """
    Takes a package directory and ensures that the setup.py within is correctly configured for py.typed files.
    """
    result = True
    manifest_location = os.path.join(pkg_dir, "MANIFEST.in")

    if not include_package_data:
        logger.info(
            "Ensure that the setup.py present in directory {} has kwarg 'include_package_data' defined and set to 'True'."
        )
        result = False

    if package_metadata:
        if not any([key for key in package_metadata if "py.typed" in str(package_metadata[key])]):
            logger.info(
                "At least one value in the package_metadata map should include a reference to the py.typed file."
            )
            result = False

    if os.path.exists(manifest_location):
        with open(manifest_location, "r") as f:
            lines = f.readlines()
            if not any([include for include in lines if "py.typed" in include]):
                logger.info("Ensure that the MANIFEST.in includes at least one path that leads to a py.typed file.")
                result = False

    pytyped_file_path = os.path.join(pkg_dir, *namespace.split("."), "py.typed")
    if not os.path.exists(pytyped_file_path):
        logger.info(
            "The py.typed file must exist in the base namespace for your package. Traditionally this would mean the furthest depth, EG 'azure/storage/blob/py.typed'."
        )
        result = False

    return result


class verify_sdist(Check):
    def __init__(self) -> None:
        super().__init__()

    def register(
        self, subparsers: "argparse._SubParsersAction", parent_parsers: Optional[List[argparse.ArgumentParser]] = None
    ) -> None:
        """Register the verifysdist check. Verify directories included in sdist and contents in manifest file. Also ensures that py.typed configuration is correct within the setup.py"""
        parents = parent_parsers or []
        p = subparsers.add_parser(
            "verifysdist",
            parents=parents,
            help="Verify directories included in sdist and contents in manifest file. Also ensures that py.typed configuration is correct within the setup.py.",
        )
        p.set_defaults(func=self.run)

    def run(self, args: argparse.Namespace) -> int:
        """Run the verifysdist check command."""
        logger.info("Running verifysdist check...")

        set_envvar_defaults()
        targeted = self.get_targeted_directories(args)

        results: List[int] = []

        for parsed in targeted:
            package_dir = parsed.folder
            package_name = parsed.name
            executable, staging_directory = self.get_executable(args.isolate, args.command, sys.executable, package_dir)
            logger.info(f"Processing {package_name} for verify_sdist check")

            self.install_dev_reqs(executable, args, package_dir)

            create_package_and_install(
                distribution_directory=staging_directory,
                target_setup=package_dir,
                skip_install=False,
                cache_dir=None,
                work_dir=staging_directory,
                force_create=False,
                package_type="sdist",
                pre_download_disabled=False,
                python_executable=executable,
            )

            error_occurred = False

            if should_verify_package(package_name):
                logger.info(f"Verifying sdist folders and metadata for package {package_name}")
                if verify_sdist_helper(package_dir, staging_directory, parsed, executable):
                    logger.info(f"Verified sdist folders and metadata for package {package_name}")
                else:
                    logger.error(f"Failed to verify sdist folders and metadata for package {package_name}")
                    error_occurred = True

            if (
                package_name not in EXCLUDED_PYTYPE_PACKAGES
                and "-nspkg" not in package_name
                and "-mgmt" not in package_name
            ):
                logger.info(f"Verifying presence of py.typed: {package_name}")
                if verify_sdist_pytyped(
                    package_dir, parsed.namespace, parsed.package_data, parsed.include_package_data
                ):
                    logger.info(f"Py.typed setup.py kwargs are set properly: {package_name}")
                else:
                    logger.error(f"Py.typed verification failed for package {package_name}. Check messages above.")
                    error_occurred = True

            if package_name not in EXCLUDED_CLASSIFICATION_PACKAGES and "-nspkg" not in package_name:
                logger.info(f"Verifying package classifiers: {package_name}")

                status, message = verify_package_classifiers(package_name, parsed.version, parsed.classifiers)
                if status:
                    logger.info(f"Package classifiers are set properly: {package_name}")
                else:
                    logger.error(f"{message}")
                    error_occurred = True

            if error_occurred:
                logger.error(f"{package_name} failed sdist verification. Check outputs above.")
                results.append(1)

        return max(results) if results else 0
