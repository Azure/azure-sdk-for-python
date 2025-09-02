import argparse
import os
import sys
import tempfile
import shutil

from typing import Optional, List
from subprocess import CalledProcessError, check_call
from pathlib import Path

from .Check import Check
from ci_tools.parsing import ParsedSetup
from ci_tools.functions import pip_install
from ci_tools.scenario.generation import create_package_and_install
from ci_tools.variables import in_ci, set_envvar_defaults
from ci_tools.environment_exclusions import (
    is_check_enabled, is_typing_ignored
)
from ci_tools.variables import discover_repo_root

from ci_tools.logging import logger

SPHINX_VERSION = "8.2.0"

REPO_ROOT = discover_repo_root()
ci_doc_dir = os.path.join(REPO_ROOT, '_docs')
sphinx_conf_dir = os.path.join(REPO_ROOT, 'doc/sphinx')
generate_mgmt_script = os.path.join(REPO_ROOT, "doc/sphinx/generate_doc.py")

# TODO build helper functions

def move_output_and_compress(target_dir: str, package_dir: str, package_name: str) -> None:
    if not os.path.exists(ci_doc_dir):
        os.mkdir(ci_doc_dir)

    # TODO....? i think this is a bug in the original script to have package_name twice?
    individual_zip_location = os.path.join(ci_doc_dir, package_name, package_name)
    shutil.make_archive(individual_zip_location, 'gztar', target_dir)

def should_build_docs(package_name: str) -> bool:
    return not ("nspkg" in package_name or package_name in ["azure", "azure-mgmt", "azure-keyvault", "azure-documentdb", "azure-mgmt-documentdb", "azure-servicemanagement-legacy", "azure-core-tracing-opencensus"])

# apidoc helper functions

def is_mgmt_package(pkg_name: str) -> bool:
    return pkg_name != "azure-mgmt-core" and ("mgmt" in pkg_name or "cognitiveservices" in pkg_name)

def copy_existing_docs(source: str, target: str) -> None:
    for file in os.listdir(source):
        logger.info("Copying {}".format(file))
        shutil.copy(os.path.join(source, file), target)

def mgmt_apidoc(working_dir: str, target_folder: str) -> None:
    command_array = [
        sys.executable, # TODO replace with executable
        generate_mgmt_script,
        "-p",
        target_folder,
        "-o",
        working_dir,
        "--verbose",
        ]

    try:
        logger.info("Command to generate management sphinx sources: {}".format(command_array))

        check_call(
            command_array
        )
    except CalledProcessError as e:
        logger.error(
            "script failed for path {} exited with error {}".format(
                working_dir, e.returncode
            )
        )
        exit(1)

def sphinx_apidoc(working_dir: str, namespace: str) -> None:
    working_doc_folder = os.path.join(working_dir, "unzipped", "doc")
    command_array = [
            "sphinx-apidoc",
            "--no-toc",
            "--module-first",
            "-o",
            os.path.join(working_dir, "unzipped/docgen"),   # This is the output folder
            os.path.join(working_dir, "unzipped/"),         # This is the input folder
            os.path.join(working_dir, "unzipped/test*"),    # Starting here this, is excluded
            os.path.join(working_dir, "unzipped/example*"),
            os.path.join(working_dir, "unzipped/sample*"),
            os.path.join(working_dir, "unzipped/setup.py"),
        ]

    try:
        # if a `doc` folder exists, just leverage the sphinx sources found therein.
        if os.path.exists(working_doc_folder):
            logger.info("Copying files into sphinx source folder.")
            copy_existing_docs(working_doc_folder, os.path.join(working_dir, "unzipped/docgen"))

        # otherwise, we will run sphinx-apidoc to generate the sources
        else:
            logger.info("Sphinx api-doc command: {}".format(command_array))
            check_call(
                command_array
            )
            # We need to clean "azure.rst", and other RST before the main namespaces, as they are never
            # used and will log as a warning later by sphinx-build, which is blocking strict_sphinx
            base_path = Path(os.path.join(working_dir, "unzipped/docgen/"))
            namespace = namespace.rpartition('.')[0]
            while namespace:
                rst_file_to_delete = base_path / f"{namespace}.rst"
                logger.info(f"Removing {rst_file_to_delete}")
                rst_file_to_delete.unlink()
                namespace = namespace.rpartition('.')[0]
    except CalledProcessError as e:
        logger.error(
            "sphinx-apidoc failed for path {} exited with error {}".format(
                working_dir, e.returncode
            )
        )
        exit(1)

# TODO may not need these - 
# def unzip_sdist_to_directory(containing_folder: str) -> str:
#     zips = glob.glob(os.path.join(containing_folder, "*.zip"))

#     if zips:
#         return unzip_file_to_directory(zips[0], containing_folder)
#     else:
#         tars = glob.glob(os.path.join(containing_folder, "*.tar.gz"))
#         return unzip_file_to_directory(tars[0], containing_folder)

class sphinx(Check):
    def __init__(self) -> None:
        super().__init__()

    def register(self, subparsers: "argparse._SubParsersAction", parent_parsers: Optional[List[argparse.ArgumentParser]] = None) -> None:
        """Register the `sphinx` check. The sphinx check installs sphinx and and builds sphinx documentation for the target package.
        """
        parents = parent_parsers or []
        p = subparsers.add_parser("sphinx", parents=parents, help="Prepares a doc folder for consumption by sphinx, runs sphinx-apidoc against target folder and handles management generation, and run sphinx-build against target folder. Zips and moves resulting files to a root location as well.")
        p.set_defaults(func=self.run)

        p.add_argument(
            "--next",
            default=False,
            help="Next version of sphinx is being tested",
            required=False
        )

        p.add_argument(
            "-d",
            "--dist_dir",
            dest="dist_dir",
            help="The dist location on disk. Usually /dist.", # TODO? is this still needed?
            required=True,
        )

        p.add_argument(
            "-w",
            "--workingdir",
            dest="working_directory",
            help="The unzipped package directory on disk. Usually {distdir}/unzipped/",
            required=True,
        )

        p.add_argument(
            "-o",
            "--outputdir",
            dest="output_directory",
            help="The output location for the generated site. Usually {distdir}/site",
            required=True,
        )

        # TODO is this necessary?
        p.add_argument(
            "-r",
            "--root",
            dest="package_root",
            help="",
            required=True,
        )

        p.add_argument(
            "--inci",
            dest="in_ci",
            action="store_true",
            default=False
        )

    def setup_sphinx_env(self, args, package_name, package_dir):
        # unzips package sdist, sets up folders, creates index file from readme, writes package version

        # TODO directly use current directory rather than 
        if should_build_docs(package_name):
            source_location = move_and_rename(unzip_sdist_to_directory(args.dist_dir))
            doc_folder = os.path.join(source_location, "docgen")

            create_index(doc_folder, source_location, pkg_details.namespace)

            site_folder = os.path.join(args.dist_dir, "site")
            write_version(site_folder, pkg_details.version)
        else:
            logger.info("Skipping sphinx prep for {}".format(package_name.name))      

    def run_sphinx_apidoc(self, target_dir, package_dir, working_dir, output_dir, parsed):
        if should_build_docs(parsed.name):
            if is_mgmt_package(parsed.name):
                mgmt_apidoc(output_dir, parsed.folder)
            else:
                sphinx_apidoc(working_dir, parsed.namespace)            
        else:
            logger.info("Skipping sphinx source generation for {}".format(parsed.name))

    def build_sphinx(self):
        # builds html, in CI compresses and moves output to central location, reports errors
        pass

    def run(self, args: argparse.Namespace) -> int:
        """Run the sphinx check command."""
        logger.info("Running sphinx check in isolated venv...")

        set_envvar_defaults()

        targeted = self.get_targeted_directories(args)

        results: List[int] = []

        for parsed in targeted:
            package_dir = parsed.folder
            package_name = parsed.name

            executable, staging_directory = self.get_executable(args.isolate, args.command, sys.executable, package_dir)
            logger.info(f"Processing {package_name} for sphinx check")

            # install sphinx
            try:
                if (args.next):
                    pip_install(["sphinx"], True, executable, package_dir)
                else:
                    pip_install([f"sphinx=={SPHINX_VERSION}"], True, executable, package_dir)
            except CalledProcessError as e:
                logger.error("Failed to install sphinx:", e)
                return e.returncode
            
            logger.info(f"Running sphinx against {package_name}")

            output_dir = os.path.abspath(args.output_directory)
            target_dir = os.path.abspath(args.working_directory)
            package_dir = os.path.abspath(args.package_root)
            

        return max(results) if results else 0