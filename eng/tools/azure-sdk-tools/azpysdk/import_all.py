import argparse
import os
import sys
import tempfile

from typing import Optional, List
from subprocess import check_call

from .Check import Check
from ci_tools.parsing import ParsedSetup
from ci_tools.functions import discover_targeted_packages
from ci_tools.scenario.generation import create_package_and_install
from ci_tools.logging import logger

# keyvault has dependency issue when loading private module _BearerTokenCredentialPolicyBase from azure.core.pipeline.policies
# azure.core.tracing.opencensus and azure.eventhub.checkpointstoreblob.aio are skipped due to a known issue in loading azure.core.tracing.opencensus
excluded_packages = [
    "azure",
    "azure-mgmt",
]


def should_run_import_all(package_name: str) -> bool:
    return not (package_name in excluded_packages or "nspkg" in package_name)


class import_all(Check):
    def __init__(self) -> None:
        super().__init__()

    def register(
        self, subparsers: "argparse._SubParsersAction", parent_parsers: Optional[List[argparse.ArgumentParser]] = None
    ) -> None:
        """Register the `import_all` check. The import_all check checks dependencies of a package
        by installing just the package + its dependencies, then attempts to import * from the base namespace.

        If it fails, there is a dependency being imported somewhere in the package namespace that doesn't
        exist in the `pyproject.toml`/`setup.py` dependencies. EG failure to import `isodate` within `azure.storage.blob.BlobClient`
        because `isodate` is not listed as a dependency for the package.
        """
        parents = parent_parsers or []
        p = subparsers.add_parser("import_all", parents=parents, help="Run the import_all check")
        p.set_defaults(func=self.run)
        # Add any additional arguments specific to WhlCheck here (do not re-add common args)

    # todo: figure out venv abstraction mechanism via override
    def run(self, args: argparse.Namespace) -> int:
        """Run the import_all check command."""
        logger.info("Running import_all check in isolated venv...")

        targeted = self.get_targeted_directories(args)

        outcomes: List[int] = []

        for parsed in targeted:
            pkg = parsed.folder
            executable, staging_directory = self.get_executable(args.isolate, args.command, sys.executable, pkg)

            self.install_dev_reqs(executable, args, pkg)

            create_package_and_install(
                distribution_directory=staging_directory,
                target_setup=pkg,
                skip_install=False,
                cache_dir=None,
                work_dir=staging_directory,
                force_create=False,
                package_type="wheel",
                pre_download_disabled=False,
                python_executable=executable,
            )

            if should_run_import_all(parsed.name):
                # import all modules from current package
                logger.info("Importing all modules from namespace [{0}] to verify dependency".format(parsed.namespace))
                import_script_all = "from {0} import *".format(parsed.namespace)
                commands = [executable, "-c", import_script_all]

                outcomes.append(check_call(commands))
                logger.info("Verified module dependency, no issues found")
            else:
                logger.info("Package {} is excluded from dependency check".format(parsed.name))

        return max(outcomes) if outcomes else 0
