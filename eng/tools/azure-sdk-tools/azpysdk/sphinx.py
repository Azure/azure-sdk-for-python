import argparse
import os
import sys
import shutil
import glob

from typing import Optional, List
from subprocess import CalledProcessError, check_call
from pathlib import Path

from .Check import Check
from ci_tools.functions import install_into_venv
from ci_tools.scenario.generation import create_package_and_install
from ci_tools.variables import in_ci, set_envvar_defaults
from ci_tools.variables import discover_repo_root
from ci_tools.variables import in_analyze_weekly

from ci_tools.logging import logger

# dependencies
SPHINX_VERSION = "8.2.0"
SPHINX_RTD_THEME_VERSION = "3.0.2"
MYST_PARSER_VERSION = "4.0.1"
SPHINX_CONTRIB_JQUERY_VERSION = "4.1"
PYGITHUB_VERSION = "1.59.0"

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
ci_doc_dir = os.path.join(REPO_ROOT, "_docs")
sphinx_conf_dir = os.path.join(REPO_ROOT, "doc/sphinx")
generate_mgmt_script = os.path.join(REPO_ROOT, "doc/sphinx/generate_doc.py")


# env prep helper functions
def create_index_file(readme_location: str, package_rst: str) -> str:
    readme_ext = os.path.splitext(readme_location)[1]

    output = ""
    if readme_ext == ".md":
        with open(readme_location, "r") as file:
            output = file.read()
    else:
        logger.error("{} is not a valid readme type. Expecting RST or MD.".format(readme_location))

    output += RST_EXTENSION_FOR_INDEX.format(package_rst)

    return output


def create_index(doc_folder: str, source_location: str, namespace: str) -> None:
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
    with open(content_destination, "w+", encoding="utf-8") as f:
        f.write(index_content)


def write_version(site_folder: str, version: str) -> None:
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


# build helper functions
def move_output_and_compress(target_dir: str, package_dir: str, package_name: str) -> None:
    if not os.path.exists(ci_doc_dir):
        os.mkdir(ci_doc_dir)

    individual_zip_location = os.path.join(ci_doc_dir, package_dir, package_name)
    shutil.make_archive(individual_zip_location, "gztar", target_dir)


def should_build_docs(package_name: str) -> bool:
    return not (
        "nspkg" in package_name
        or package_name
        in [
            "azure",
            "azure-mgmt",
            "azure-keyvault",
            "azure-documentdb",
            "azure-mgmt-documentdb",
            "azure-servicemanagement-legacy",
            "azure-core-tracing-opencensus",
        ]
    )


class sphinx(Check):
    def __init__(self) -> None:
        super().__init__()

    def register(
        self, subparsers: "argparse._SubParsersAction", parent_parsers: Optional[List[argparse.ArgumentParser]] = None
    ) -> None:
        """Register the `sphinx` check. The sphinx check installs sphinx and and builds sphinx documentation for the target package."""
        parents = parent_parsers or []
        p = subparsers.add_parser(
            "sphinx",
            parents=parents,
            help="Prepares a doc folder for consumption by sphinx, runs sphinx-apidoc against target folder and handles management generation, and run sphinx-build against target folder. Zips and moves resulting files to a root location as well.",
        )
        p.set_defaults(func=self.run)

        p.add_argument("--next", default=False, help="Next version of sphinx is being tested", required=False)

        p.add_argument("--inci", dest="in_ci", action="store_true", default=False)

    def run(self, args: argparse.Namespace) -> int:
        """Run the sphinx check command."""
        logger.info("Running sphinx check...")

        set_envvar_defaults()

        targeted = self.get_targeted_directories(args)

        results: List[int] = []

        for parsed in targeted:
            package_dir = parsed.folder
            package_name = parsed.name

            executable, staging_directory = self.get_executable(args.isolate, args.command, sys.executable, package_dir)
            logger.info(f"Processing {package_name} for sphinx check")

            # check Python version
            if sys.version_info < (3, 11):
                logger.error("This tool requires Python 3.11 or newer. Please upgrade your Python interpreter.")
                return 1

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

            # install sphinx
            try:
                if args.next:
                    install_into_venv(
                        executable,
                        [
                            "sphinx",
                            "sphinx_rtd_theme",
                            "myst_parser",
                            "sphinxcontrib-jquery",
                            f"PyGithub=={PYGITHUB_VERSION}",
                        ],
                        package_dir,
                    )
                else:
                    install_into_venv(
                        executable,
                        [
                            f"sphinx=={SPHINX_VERSION}",
                            f"sphinx_rtd_theme=={SPHINX_RTD_THEME_VERSION}",
                            f"myst_parser=={MYST_PARSER_VERSION}",
                            f"sphinxcontrib-jquery=={SPHINX_CONTRIB_JQUERY_VERSION}",
                        ],
                        package_dir,
                    )
            except CalledProcessError as e:
                logger.error(f"Failed to install sphinx: {e}")
                return e.returncode

            logger.info(f"Running sphinx against {package_name}")

            # prep env for sphinx
            doc_folder = os.path.join(staging_directory, "docgen")
            site_folder = os.path.join(package_dir, "website")

            if should_build_docs(package_name):
                create_index(doc_folder, package_dir, parsed.namespace)

                write_version(site_folder, parsed.version)
            else:
                logger.info("Skipping sphinx prep for {}".format(package_name))

            # run apidoc
            if should_build_docs(parsed.name):
                if is_mgmt_package(parsed.name):
                    results.append(self.mgmt_apidoc(doc_folder, package_dir, executable))
                else:
                    results.append(self.sphinx_apidoc(staging_directory, package_dir, parsed.namespace, executable))
            else:
                logger.info("Skipping sphinx source generation for {}".format(parsed.name))

            # build
            if should_build_docs(package_name):
                # Only data-plane libraries run strict sphinx at the moment
                fail_on_warning = not is_mgmt_package(package_name)
                results.append(
                    # doc_folder = source
                    # site_folder  = output
                    self.sphinx_build(package_dir, doc_folder, site_folder, fail_on_warning, executable)
                )

                if in_ci() or args.in_ci:
                    move_output_and_compress(site_folder, package_dir, package_name)
                    if in_analyze_weekly():
                        from gh_tools.vnext_issue_creator import close_vnext_issue

                        close_vnext_issue(package_name, "sphinx")

            else:
                logger.info("Skipping sphinx build for {}".format(package_name))

        return max(results) if results else 0

    def sphinx_build(
        self, package_dir: str, target_dir: str, output_dir: str, fail_on_warning: bool, executable: str
    ) -> int:
        command_array = [
            "sphinx-build",
            "-b",
            "html",
            "-A",
            "include_index_link=True",
            "-c",
            sphinx_conf_dir,
            target_dir,
            output_dir,
        ]
        if fail_on_warning:
            command_array.append("-W")
            command_array.append("--keep-going")

        try:
            logger.info("Sphinx build command: {}".format(command_array))

            self.run_venv_command(executable, command_array, cwd=package_dir, check=True, append_executable=False)
        except CalledProcessError as e:
            logger.error("sphinx-build failed for path {} exited with error {}".format(target_dir, e.returncode))
            if in_analyze_weekly():
                from gh_tools.vnext_issue_creator import create_vnext_issue

                create_vnext_issue(package_dir, "sphinx")
            return 1
        return 0

    def mgmt_apidoc(self, output_dir: str, target_folder: str, executable: str) -> int:
        command_array = [
            executable,
            generate_mgmt_script,
            "-p",
            target_folder,
            "-o",
            output_dir,
            "--verbose",
        ]

        try:
            logger.info("Command to generate management sphinx sources: {}".format(command_array))

            self.run_venv_command(executable, command_array, cwd=target_folder, check=True, append_executable=False)
        except CalledProcessError as e:
            logger.error("script failed for path {} exited with error {}".format(output_dir, e.returncode))
            return 1
        return 0

    def sphinx_apidoc(self, output_dir: str, target_dir: str, namespace: str, executable: str) -> int:
        working_doc_folder = os.path.join(output_dir, "doc")
        command_array = [
            "sphinx-apidoc",
            "--no-toc",
            "--module-first",
            "-o",
            os.path.join(output_dir, "docgen"),  # This is the output folder
            os.path.join(target_dir, ""),  # This is the input folder
            os.path.join(target_dir, "test*"),  # This argument and below are "exclude" directory arguments
            os.path.join(target_dir, "example*"),
            os.path.join(target_dir, "sample*"),
            os.path.join(target_dir, "setup.py"),
            os.path.join(target_dir, "conftest.py"),
        ]

        try:
            # if a `doc` folder exists, just leverage the sphinx sources found therein.
            if os.path.exists(working_doc_folder):
                logger.info("Copying files into sphinx source folder.")
                copy_existing_docs(working_doc_folder, os.path.join(output_dir, "docgen"))

            # otherwise, we will run sphinx-apidoc to generate the sources
            else:
                logger.info("Sphinx api-doc command: {}".format(command_array))
                self.run_venv_command(executable, command_array, cwd=target_dir, check=True, append_executable=False)
                # We need to clean "azure.rst", and other RST before the main namespaces, as they are never
                # used and will log as a warning later by sphinx-build, which is blocking strict_sphinx
                base_path = Path(os.path.join(output_dir, "docgen/"))
                namespace = namespace.rpartition(".")[0]
                while namespace:
                    rst_file_to_delete = base_path / f"{namespace}.rst"
                    logger.info(f"Removing {rst_file_to_delete}")
                    rst_file_to_delete.unlink(missing_ok=True)
                    namespace = namespace.rpartition(".")[0]
        except CalledProcessError as e:
            logger.error("sphinx-apidoc failed for path {} exited with error {}".format(output_dir, e.returncode))
            return 1
        return 0
