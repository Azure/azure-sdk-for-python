import argparse
import sys
from pathlib import Path

from typing import Optional, List
from subprocess import PIPE, CalledProcessError, run

from .Check import Check
from ci_tools.functions import install_into_venv
from ci_tools.variables import set_envvar_defaults
from ci_tools.logging import logger

TOMLI_VERSION = "2.0.1"

class generate(Check):
    def __init__(self) -> None:
        super().__init__()

    def register(
        self, subparsers: "argparse._SubParsersAction", parent_parsers: Optional[List[argparse.ArgumentParser]] = None
    ) -> None:
        """Register the generate check. The generate check installs generate and runs generate against the target package to regenerate the code."""
        parents = parent_parsers or []
        p = subparsers.add_parser("generate", parents=parents, help="Run the generate check to regenerate the code.")
        p.set_defaults(func=self.run)

    def run(self, args: argparse.Namespace) -> int:
        """Run the generate check command."""
        logger.info("Running generate check...")

        set_envvar_defaults()
        targeted = self.get_targeted_directories(args)

        results: List[int] = []

        for parsed in targeted:
            package_dir = parsed.folder
            package_name = parsed.name
            executable, staging_directory = self.get_executable(args.isolate, args.command, sys.executable, package_dir)
            logger.info(f"Processing {package_name} for generate check")

            # install dependencies
            self.install_dev_reqs(executable, args, package_dir)

            try:
                install_into_venv(
                    executable,
                    [
                        f"tomli=={TOMLI_VERSION}"
                    ],
                    package_dir
                )
            except CalledProcessError as e:
                logger.error(f"Failed to install tomli in the virtual environment for {package_name}: {e}")
                results.append(1)
                continue

            try:
                self.generate(Path(package_dir))
            except ValueError as e:
                logger.error(f"Generation failed for {package_name}: {e}")
                results.append(1)
                continue

        return max(results) if results else 0

    def generate(self, folder: Path = Path(".")) -> None:
        if (folder / "swagger" / "README.md").exists():
            self.generate_autorest(folder)
        elif (folder / "tsp-location.yaml").exists():
            self.generate_typespec(folder)
        else:
            raise ValueError("Didn't find swagger/README.md nor tsp_location.yaml")

    def generate_autorest(self, folder: Path) -> None:
        readme_path = folder / "swagger" / "README.md"
        completed_process = run(f"autorest {readme_path} --python-sdks-folder=../../", cwd=folder, shell=True)

        if completed_process.returncode != 0:
            raise ValueError("Something happened with autorest: " + str(completed_process))
        logger.info("Autorest done")

    def generate_typespec(self, folder: Path) -> None:
        tsp_location_path = folder / "tsp-location.yaml"

        if not tsp_location_path.exists():
            raise ValueError(
                "Didn't find a tsp_location.yaml in local directory. Please make sure a valid "
                "tsp-location.yaml file exists before running this command, for more information "
                "on how to create one, see: "
                "https://github.com/Azure/azure-sdk-tools/tree/main/tools/tsp-client/README.md"
            )

        completed_process = run("tsp-client update", cwd=folder, shell=True, stderr=PIPE)
        if completed_process.returncode != 0:
            if "'tsp-client' is not recognized" in completed_process.stderr.decode("utf-8"):
                raise ValueError(
                    "tsp-client is not installed. Please run: npm install -g @azure-tools/typespec-client-generator-cli"
                )
            raise ValueError("Something happened with tsp-client update step: " + str(completed_process))

        logger.info("TypeSpec generate done")
