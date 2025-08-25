import argparse
import os
import sys
import logging
import tempfile

from typing import Optional,List
from subprocess import check_call

from .Check import Check
from ci_tools.parsing import ParsedSetup
from ci_tools.functions import discover_targeted_packages
from ci_tools.scenario.generation import create_package_and_install

# keyvault has dependency issue when loading private module _BearerTokenCredentialPolicyBase from azure.core.pipeline.policies
# azure.core.tracing.opencensus and azure.eventhub.checkpointstoreblob.aio are skipped due to a known issue in loading azure.core.tracing.opencensus
excluded_packages = [
    "azure",
    "azure-mgmt",
    ]

def should_run_import_all(package_name: str) -> bool:
    return not (package_name in excluded_packages or "nspkg" in package_name)

class depends(Check):
    def __init__(self) -> None:
        super().__init__()

    def register(self, subparsers: "argparse._SubParsersAction", parent_parsers: Optional[List[argparse.ArgumentParser]] = None) -> None:
        """Register the `depends` check.

        `subparsers` is the object returned by ArgumentParser.add_subparsers().
        `parent_parsers` is an optional list of parent ArgumentParser objects
        that contain common arguments. Avoid mutating default arguments.
        """
        parents = parent_parsers or []
        p = subparsers.add_parser("depends", parents=parents, help="Run the depends check")
        p.set_defaults(func=self.run)
        # Add any additional arguments specific to WhlCheck here (do not re-add common args)

    # todo: figure out venv abstraction mechanism via override
    def run(self, args: argparse.Namespace) -> int:
        """Run the depends check command."""
        print("Running depends check in isolated venv...")

        # this is common. we should have an abstraction layer for this somehow
        if args.target == ".":
            targeted = [os.getcwd()]
        else:
            target_dir = os.getcwd()
            targeted = discover_targeted_packages(args.target, target_dir)

        # {[tox]pip_command} freeze
        # python {repository_root}/eng/tox/import_all.py -t {tox_root}

        outcomes: List[int] = []

        for pkg in targeted:
            parsed = ParsedSetup.from_path(pkg)

            staging_area = tempfile.mkdtemp()
            create_package_and_install(
                distribution_directory=staging_area,
                target_setup=pkg,
                skip_install=False,
                cache_dir=None,
                work_dir=staging_area,
                force_create=False,
                package_type="wheel",
                pre_download_disabled=False,
            )

            if should_run_import_all(parsed.name):
                # import all modules from current package
                logging.info(
                    "Importing all modules from namespace [{0}] to verify dependency".format(
                        parsed.namespace
                    )
                )
                import_script_all = "from {0} import *".format(parsed.namespace)
                commands = [
                    sys.executable,
                    "-c",
                    import_script_all
                ]

                outcomes.append(check_call(commands))
                logging.info("Verified module dependency, no issues found")
            else:
                logging.info("Package {} is excluded from dependency check".format(parsed.name))

        return max(outcomes) if outcomes else 0
