import argparse
import os
import sys
import tempfile
import shutil
import glob
import zipfile
import tarfile

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
from ci_tools.variables import in_analyze_weekly

from ci_tools.logging import logger

SPHINX_VERSION = "8.2.0"
RST_EXTENSION_FOR_INDEX = """

## Indices and tables

- {{ref}}`genindex`
- {{ref}}`modindex`
- {{ref}}`search`

```{{toctree}}
:caption: Developer Documentation
:glob: true
:maxdepth: 5

{}

```

"""
REPO_ROOT = discover_repo_root()
ci_doc_dir = os.path.join(REPO_ROOT, '_docs')
sphinx_conf_dir = os.path.join(REPO_ROOT, 'doc/sphinx')
generate_mgmt_script = os.path.join(REPO_ROOT, "doc/sphinx/generate_doc.py")

# env prep helper functions TODO is this sdist unzipping logic still needed?

def unzip_sdist_to_directory(containing_folder: str) -> str:
    zips = glob.glob(os.path.join(containing_folder, "*.zip"))

    if zips:
        return unzip_file_to_directory(zips[0], containing_folder)
    else:
        tars = glob.glob(os.path.join(containing_folder, "*.tar.gz"))
        return unzip_file_to_directory(tars[0], containing_folder)

def unzip_file_to_directory(path_to_zip_file: str, extract_location: str) -> str:
    if path_to_zip_file.endswith(".zip"):
        with zipfile.ZipFile(path_to_zip_file, "r") as zip_ref:
            zip_ref.extractall(extract_location)
            extracted_dir = os.path.basename(os.path.splitext(path_to_zip_file)[0])
            return os.path.join(extract_location, extracted_dir)
    else:
        with tarfile.open(path_to_zip_file) as tar_ref:
            tar_ref.extractall(extract_location)
            extracted_dir = os.path.basename(path_to_zip_file).replace(".tar.gz", "")
            return os.path.join(extract_location, extracted_dir)

def move_and_rename(source_location):
    new_location = os.path.join(os.path.dirname(source_location), "unzipped")

    if os.path.exists(new_location):
        shutil.rmtree(new_location)

    os.rename(source_location, new_location)
    return new_location

def create_index_file(readme_location, package_rst):
    readme_ext = os.path.splitext(readme_location)[1]

    output = ""
    if readme_ext == ".md":
        with open(readme_location, "r") as file:
            output = file.read()
    else:
        logger.error(
            "{} is not a valid readme type. Expecting RST or MD.".format(
                readme_location
            )
        )

    output += RST_EXTENSION_FOR_INDEX.format(package_rst)

    return output

def create_index(doc_folder, source_location, namespace):
    index_content = ""

    package_rst = "{}.rst".format(namespace)
    content_destination = os.path.join(doc_folder, "index.md")

    if not os.path.exists(doc_folder):
        os.mkdir(doc_folder)

    # grep all content
    markdown_readmes = glob.glob(os.path.join(source_location, "README.md"))

    # if markdown, take that, otherwise rst
    if markdown_readmes:
        index_content = create_index_file(markdown_readmes[0], package_rst)
    else:
        logger.warning("No readmes detected for this namespace {}".format(namespace))
        index_content = RST_EXTENSION_FOR_INDEX.format(package_rst)

    # write index
    with open(content_destination, "w+", encoding='utf-8') as f:
        f.write(index_content)

def write_version(site_folder, version):

    if not os.path.isdir(site_folder):
        os.mkdir(site_folder)

    with open(os.path.join(site_folder, "version.txt"), "w") as f:
        f.write(version)

# apidoc helper functions

def is_mgmt_package(pkg_name: str) -> bool:
    return pkg_name != "azure-mgmt-core" and ("mgmt" in pkg_name or "cognitiveservices" in pkg_name)

def copy_existing_docs(source: str, target: str) -> None:
    for file in os.listdir(source):
        logger.info("Copying {}".format(file))
        shutil.copy(os.path.join(source, file), target)

def mgmt_apidoc(working_dir: str, target_folder: str, executable: str) -> int:
    command_array = [
        executable,
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
        return 1
    return 0

def sphinx_apidoc(working_dir: str, namespace: str) -> int:
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
        return 1
    return 0

# build helper functions

def move_output_and_compress(target_dir: str, package_dir: str, package_name: str) -> None:
    if not os.path.exists(ci_doc_dir):
        os.mkdir(ci_doc_dir)

    # TODO....? i think this is a bug in the original script to have package_name twice?
    individual_zip_location = os.path.join(ci_doc_dir, package_name, package_name)
    shutil.make_archive(individual_zip_location, 'gztar', target_dir)

def should_build_docs(package_name: str) -> bool:
    return not ("nspkg" in package_name or package_name in ["azure", "azure-mgmt", "azure-keyvault", "azure-documentdb", "azure-mgmt-documentdb", "azure-servicemanagement-legacy", "azure-core-tracing-opencensus"])

def sphinx_build(package_dir: str, target_dir: str, output_dir: str, fail_on_warning: bool) -> int:
    command_array = [
                "sphinx-build",
                "-b",
                "html",
                "-A",
                "include_index_link=True",
                "-c",
                sphinx_conf_dir,
                target_dir,
                output_dir
            ]
    if fail_on_warning:
        command_array.append("-W")
        command_array.append("--keep-going")

    try:
        logger.info("Sphinx build command: {}".format(command_array))
        check_call(
            command_array
        )
    except CalledProcessError as e:
        logger.error(
            "sphinx-build failed for path {} exited with error {}".format(
                target_dir, e.returncode
            )
        )
        if in_analyze_weekly():
            from gh_tools.vnext_issue_creator import create_vnext_issue
            create_vnext_issue(package_dir, "sphinx")
        return 1
    return 0

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

        # TODO is this necessary? is this the same as target?
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

    def run_sphinx_apidoc(self, args: argparse.Namespace, parsed: ParsedSetup, executable: str) -> int:
        working_dir = args.working_directory 
        output_dir = os.path.join(working_dir, "unzipped/docgen")

        result: int = 0

        if should_build_docs(parsed.name):
            if is_mgmt_package(parsed.name):
                result = mgmt_apidoc(output_dir, parsed.folder, executable)
            else:
                result = sphinx_apidoc(working_dir, parsed.namespace)            
        else:
            logger.info("Skipping sphinx source generation for {}".format(parsed.name))
        return result

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

            # prep env for sphinx
            # TODO directly use current directory rather than 
            if should_build_docs(package_name):
                source_location = move_and_rename(unzip_sdist_to_directory(args.dist_dir))
                doc_folder = os.path.join(source_location, "docgen")

                create_index(doc_folder, source_location, parsed.namespace)

                site_folder = os.path.join(args.dist_dir, "site")
                write_version(site_folder, parsed.version)
            else:
                logger.info("Skipping sphinx prep for {}".format(package_name))      

            # run apidoc
            results.append(self.run_sphinx_apidoc(args, parsed, executable))
            
            # build
            if should_build_docs(package_name):
                # Only data-plane libraries run strict sphinx at the moment
                fail_on_warning = not is_mgmt_package(package_name)
                results.append(sphinx_build(
                    package_dir,
                    target_dir,
                    output_dir,
                    fail_on_warning=fail_on_warning,
                ))

                if in_ci() or args.in_ci:
                    move_output_and_compress(output_dir, package_dir, package_name)
                    if in_analyze_weekly():
                        from gh_tools.vnext_issue_creator import close_vnext_issue
                        close_vnext_issue(package_name, "sphinx")

            else:
                logger.info("Skipping sphinx build for {}".format(package_name))

        return max(results) if results else 0