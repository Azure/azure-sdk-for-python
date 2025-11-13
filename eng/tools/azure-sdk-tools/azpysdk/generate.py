import argparse
import sys
from pathlib import Path

from typing import Optional, List
from subprocess import PIPE, CalledProcessError, run

from .Check import Check
from ci_tools.functions import install_into_venv
from ci_tools.variables import set_envvar_defaults
from ci_tools.logging import logger


class generate(Check):
    def __init__(self) -> None:
        super().__init__()

    def register(
        self, subparsers: "argparse._SubParsersAction", parent_parsers: Optional[List[argparse.ArgumentParser]] = None
    ) -> None:
        """Register the generate check. The generate check regenerates the code using autorest or tsp-client based on the package configuration."""
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
            raise ValueError("Didn't find swagger/README.md nor tsp-location.yaml")

    def generate_autorest(self, folder: Path) -> None:
        readme_path = folder / "swagger" / "README.md"

        try:
            run(
                ["autorest", str(readme_path), "--python-sdks-folder=../../"],
                cwd=folder,
                shell=False,
            )
        except FileNotFoundError:
            raise ValueError("autorest is not installed. Please install autorest before running this command.")
        except CalledProcessError as e:
            raise ValueError(f"autorest encountered an unexpected error: {e}")

        logger.info("Autorest done")

    def generate_typespec(self, folder: Path) -> None:
        tsp_location_path = folder / "tsp-location.yaml"

        if not tsp_location_path.exists():
            raise ValueError(
                "Didn't find a tsp-location.yaml in local directory. Please make sure a valid "
                "tsp-location.yaml file exists before running this command, for more information "
                "on how to create one, see: "
                "https://github.com/Azure/azure-sdk-tools/tree/main/tools/tsp-client/README.md"
            )

        try:
            run(["tsp-client", "update"], cwd=folder, check=True, stderr=PIPE, shell=False)
        except FileNotFoundError as e:
            raise ValueError(
                "tsp-client is not installed. Please run: npm install -g @azure-tools/typespec-client-generator-cli"
            )
        except CalledProcessError as e:
            raise ValueError(f"tsp-client encountered an unexpected error: {e}")

        logger.info("TypeSpec generate done")
